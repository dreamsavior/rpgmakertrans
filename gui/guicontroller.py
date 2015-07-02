"""
guicontroller
*************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

The controller for the GUI, implementing the higher level functions that
the rest of the program should interact with.

TODO: This is somewhat tied to qtui at the moment. Ideally, it should be
configurable, or in the qtui module.
TODO: Check if it would be better to wrap this into an asyncio thing
rather than headless. asyncio would be better for responsiveness, which
let's face it, is lacking.
"""
import os
import itertools
import sys

from librpgmakertrans.controllers.coreprotocol import CoreRunner, CoreProtocol
from librpgmakertrans.workers.sniffers import sniffAll, sniff
from librpgmakertrans.controllers.headless import initialiseHeadless, HeadlessConfig
from librpgmakertrans.version import versionCheck
from librpgmakertrans.controllers.coreprotocol import CoreRunner
from librpgmakertrans.workers.sniffers import sniff

from .qtui import startView, errorMsg

class IDStore(dict):
    """IDStore is basically a dict which also keeps track
    of a unique ID that can be added into the IDStore, as well
    as the inverse dict"""
    def __init__(self, reverse=True, *args, **kwargs):
        """Initialise hte ID store, creating an inverse dict if
        reverse=True"""
        super(IDStore, self).__init__(*args, **kwargs)
        self.nextid = 0
        self.reversable = reverse
        if self.reversable:
            self.reverse = {}

    def __setitem__(self, key, val):
        """Update the inverse dict if necessary"""
        if self.reversable:
            self.reverse[val] = key
        super().__setitem__(key, val)

    def add(self, item):
        """Add an item to the next available ID"""
        r = self.nextid
        self[item] = r
        self.nextid += 1
        return r


class UpdaterDict(dict):
    """Dictionary that runs a given function when an item is set"""
    def __init__(self, updateFunc, *args, **kwargs):
        """Initialise the updater dict"""
        self.__updateFunc = updateFunc
        super(UpdaterDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """Update the dict, then run the updater function"""
        super(UpdaterDict, self).__setitem__(key, value)
        self.__updateFunc()


class GUIController(CoreProtocol):
    """The GUI Controller, which handles communications between
    a GUI and the backend. Mainly a translator between headless
    and a concrete GUI like QT.
    NOTE: At some point, it may be prudent to do something like
    make the GUI be a subclass of GUIController. Creating both
    the controller and the GUI in two different processes seems
    unnecessary."""
    def __init__(self, *args, **kwargs):
        """Initialise and start the GUI controller"""
        super(GUIController, self).__init__(*args, **kwargs)
        self.setupPool('gui', processes=1)
        self.submit('gui', startView, inputcoms=self.outputcoms,
                    outputcoms=self.inputcoms)
        self.runner.setErrorHandler(errorMsg)
        self.gameDB = IDStore()
        self.patchDB = IDStore()
        self.transDB = IDStore()
        self.currentState = UpdaterDict(self.enableUI)
        self.currentState.update({'gameloc': None,
                                  'patchloc': None,
                                  'transloc': None,
                                  'create': False,
                                  'enabled': True,
                                  'bom': False,
                                  'rebuild': False})

        self.headless = None

        self.outputcoms.send('setMessage', 'Loading games, patches...')
        self.setupPool('worker', processes=1)
        sniffDataRet = self.submit('worker', sniffAllTrigger,
                                   path=os.getcwd(), coms=self.inputcoms)
        self.submit('worker', versionCheck, coms=self.inputcoms)
        self.localWaitUntil('sniffingDone', self.setUpSniffedDataMP,
                            sniffDataRet)
        self.enableUI()

    def newVerAvailable(self, version):
        """Display a message+quit if new version available"""
        newVers = str(round(version,2))
        self.outputcoms.send('displayOKKill', 'New Version Available',
            'Version ' + newVers + ' of RPGMaker Trans is available.\n'
            'Please visit http://habisain.blogspot.co.uk to download it.\n'
            'Press OK to close RPGMaker Trans')

    def expired(self):
        """Display a message+quit if too old"""
        self.outputcoms.send('displayOKKill', 'Expired Version',
            'This version of RPGMaker Trams has expired.'
            'Please visit http://habisain.blogspot.co.uk to download a new version.'
            'Press OK to close RPGMaker Trans')

    def setUpSniffedDataMP(self, sniffDataRet):
        """Put sniffed data into the GUI, after retrieving from multiprocessing"""
        sniffData = sniffDataRet.get()
        self.setUpSniffedData(sniffData)

    def setUpSniffedData(self, sniffData):
        """Put sniffed data into the GUI"""
        for item in sniffData:
            if item is False:
                pass
            elif item.maintype == 'GAME':
                self.addGame(item, select=False)
            elif item.maintype == 'PATCH':
                self.addPatch(item, select=False)
            elif item.maintype == 'TRANS':
                self.addTrans(item, select=False)
        self.outputcoms.send('setMessage', 'Ready')

    def addItem(self, sniffData, sniffDataTypes, idstore,
                signalSuffix, select, prefix=None):
        """This is the general 'add item to selector' logic"""
        if sniffData.maintype not in sniffDataTypes:
            return
        path = sniffData.canonicalpath
        name = os.path.split(path)[1]
        if prefix is not None:
            prefix = prefix % ']['.join(sniffData.subtypes)
            name = '%s %s' % (prefix, name)
        if sniffData not in idstore:
            tid = idstore.add(sniffData)
            self.outputcoms.send('add%s' % signalSuffix, name,
                                 tid, select=select)
        else:
            tid = idstore[sniffData]
            if select:
                self.outputcoms.send('select%s' % signalSuffix, tid)

    def addItemFromPath(self, path, sniffDataTypes, idStore, signalSuffix,
                        select=False, prefix=None):
        """Add an item from path"""
        sniffData = sniff(path)
        for item in sniffData:
            self.addItem(item, sniffDataTypes, idStore,
                         signalSuffix, select, prefix)

    def addGame(self, sniffData, select=False):
        """Add a game to UI"""
        self.addItem(sniffData, ['GAME', 'TRANS'], self.gameDB, 'Game',
                     select, prefix='[%s]')

    def addGameFromPath(self, gamepath, select=False):
        """Add Game from path"""
        self.addItemFromPath(gamepath, ['GAME', 'TRANS'], self.gameDB, 'Game',
                             select, prefix='[%s]')

    def addPatch(self, sniffData, select=False):
        """Add patch to UI"""
        self.addItem(sniffData, ['PATCH'], self.patchDB, 'Patch', select,
                     prefix='[%s]')

    def addPatchFromPath(self, patchpath, select=False):
        """Add patch from path to UI"""
        self.addItemFromPath(patchpath, ['PATCH'], self.patchDB, 'Patch',
                             select, prefix='[%s]')

    def addTrans(self, sniffData, select=False):
        """Add translation to UI"""
        self.addItem(sniffData, ['TRANS'], self.transDB, 'Trans', select,
                     prefix='[%s]')

    def addTransFromPath(self, transpath, select=False):
        """Add translation from path"""
        self.addItemFromPath(transpath, ['TRANS'], self.transDB, 'Trans',
                             select, prefix='[%s]')

    def selectDefaultPatch(self):
        """Given a game, figure out if we know it's default patch and
        select it"""
        if self.currentState['gameloc'] is None:
            return
        gamepath = self.gameDB.reverse[self.currentState['gameloc']]
        defaultpatchpath = gamepath.canonicalpath + '_patch'
        sniffData = sniff(defaultpatchpath, positives=['PATCH'])
        if self.currentState['create'] is False:
            sniffData = [x for x in sniffData if 'create' not in x.subtypes]
        if len(sniffData) > 0:
            for item in sniffData:
                self.addPatch(item, select=True)
        else:
            defaultzippath = defaultpatchpath + '.zip'
            zipSniff = [x for x in sniff(defaultzippath, positives=['PATCH'])
                        if 'create' not in x.subtypes]
            for item in zipSniff:
                self.addPatch(item, select=True)

    def changeSelected(self, idtoken, newid):
        """Update state when something changes"""
        if self.currentState['enabled']:
            self.currentState[idtoken] = newid
            if idtoken == 'gameloc':
                self.selectDefaultPatch()
            elif idtoken == 'patchloc':
                patchdata = self.patchDB.reverse[self.currentState['patchloc']]
                if patchdata.extraData:
                    if 'banner.html' in patchdata.extraData:
                        self.outputcoms.send('setPatchBanner', patchdata.extraData['banner.html'])
                if self.currentState['gameloc'] is not None:
                    gamepath = self.gameDB.reverse[self.currentState['gameloc']]
                    defaulttranspath = gamepath.canonicalpath + '_translated'
                    self.addTransFromPath(defaulttranspath, select=True)

    def optionChanged(self, option, value):
        """Update state when an option changes"""
        if self.currentState['enabled']:
            self.currentState[option] = value
            if option == 'create':
                self.selectDefaultPatch()
                self.outputcoms.send('setBrowsePatchDirs', value)

    def enableUI(self):
        """Enable/disable the UI based on current state. Automatically
        called when state changes"""
        state = self.currentState['enabled']
        states = {}
        states['gameloc'] = state
        states['options'] = state
        state &= self.currentState['gameloc'] is not None
        states['patchloc'] = state
        state &= self.currentState['patchloc'] is not None
        states['transloc'] = state
        state &= self.currentState['transloc'] is not None
        states['go'] = state
        self.outputcoms.send('setUI', states)

    def go(self):
        """The big GO button that starts the translation process
        based on current state"""
        self.outputcoms.send('resetNonfatalError')
        gamedata = self.gameDB.reverse[self.currentState['gameloc']]
        patchdata = self.patchDB.reverse[self.currentState['patchloc']]
        transdata = self.transDB.reverse[self.currentState['transloc']]
        useBOM = self.currentState['bom']
        rebuild = self.currentState['rebuild']
        config = HeadlessConfig(useBOM=useBOM, rebuild=rebuild)
        initialiseHeadless(self.runner, self.inputcoms, gamedata,
                           patchdata, transdata, config)
        self.currentState['enabled'] = False
        self.outputcoms.send('setMessage', 'Patching game...')

    def resniffInput(self):
        """Resniff the input"""
        gameID = self.currentState['gameloc']
        gamedata = self.gameDB.reverse[gameID]
        self.outputcoms.send('removeGame', gameID)
        self.addGameFromPath(gamedata.canonicalpath, select=True)

    def nonfatalError(self, msg):
        """Display a non fatal error message"""
        self.outputcoms.send('nonfatalError', msg)

    def displayMessage(self, message):
        """For now, alias to setMessage"""
        self.nonfatalError(message)

    def setMessage(self, message):
        """Set the message beneath the progress bar"""
        self.outputcoms.send('setMessage', message)

    def headlessFinished(self):
        """Update UI for finishing patch"""
        self.currentState['enabled'] = True
        self.currentState['gameloc'] = None
        self.setMessage('Finished')

    def patchingAborted(self):
        """Update UI when aborting patch"""
        self.currentState['enabled'] = True
        self.currentState['gameloc'] = None
        self.outputcoms.send('setMessage', 'Patching aborted')

    def setProgress(self, amount):
        """Set the progress of the UI"""
        self.outputcoms.send('setProgress', amount)

    def stop(self):
        """Do a 'really quit' box if patching"""
        if self.headless is None or not self.headless.going:
            self.outputcoms.send('quit')
        else:
            self.outputcoms.send('yesNoBox',
                                 'Patching in progress',
                                 'Patching is still in progress.\n'
                                 'Really quit?', yes='reallyStop')

    def reallyStop(self):
        """Really quit the patching if asked"""
        self.outputcoms.send('quit')


def sniffAllTrigger(path, coms):
    """Run sniffAll, send appropriate trigger when done"""
    ret = sniffAll(path)
    coms.send('trigger', 'sniffingDone')
    return ret

def launchGUI():
    """Convenience function to launch GUI"""
    runner = CoreRunner()
    guicontroller = runner.initialise(GUIController)
    sniffedData = itertools.chain.from_iterable([sniff(path) for path in sys.argv[1:]])
    if sniffedData:
        guicontroller.setUpSniffedData(sniffedData)
    runner.run()
    
if __name__ == '__main__':
    z = CoreRunner()
    x = z.initialise(GUIController)
    z.run()
