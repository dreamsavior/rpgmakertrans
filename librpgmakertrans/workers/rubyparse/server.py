'''
server
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides a simple server to perform Ruby script translations asynchronously.
'''
import time

from ...errorhook import errorWrap
from .parser import translateRuby

@errorWrap
def rbTranslationServer(inputComs, outputComs, translator):
    """A very basic server for translating Ruby scripts"""
    going = True
    while going:
        time.sleep(0.1)
        for code, args, kwargs in inputComs.get():
            if code == 'quit':
                return
            elif code == 'translateScript':
                outputComs.send('setTranslatedScript',
                                translateRuby(translationHandler=translator,
                                              *args, **kwargs))
            else:
                raise Exception('Unknown code on input bus')

@errorWrap
def rbOneOffTranslation(outputComs, errorComs, scriptName, script, translator):
    """Perform a simple Ruby translation. Should the parser blow up anywhere,
    the error message get's propagated out to the GUI"""
    try:
        tname, tscript = translateRuby(script, scriptName, translationHandler=translator)
    except Exception as excpt:
        tname, tscript = scriptName, script
        errorComs.send('nonfatalError',
                        'Error parsing Script %s: %s; leaving untranslated' %
                        (tname, str(excpt)))
    outputComs.send('setTranslatedScript', tname, tscript)