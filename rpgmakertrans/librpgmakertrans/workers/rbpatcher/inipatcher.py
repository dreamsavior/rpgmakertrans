"""
inipatcher
**********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3'''

Patches the Game.ini file.
"""
import os
import shutil
import configparser
import locale

from ...errorhook import errorWrap

@errorWrap
def patchGameIni(infn, outfn, translator, errOut, inEncoding='cp932', outEncoding=None):
    """Read a patch a Games INI file, as this contains the title.
    Note that for reasons I fail to understand, this is encoded
    using the system locale rather than anything more sensible"""
    try:
        config = configparser.ConfigParser()
        config.read(infn, encoding=inEncoding)
        translation = translator.translate(config['Game']['Title'], 'GameINI/Title')
        if outEncoding is None:
            if translation == config['Game']['Title']:
                outEncoding = inEncoding
            else:
                outEncoding = locale.getdefaultlocale()[1]
        config['Game']['Title'] = translation
        with open(outfn, 'w', encoding=outEncoding) as f:
            config.write(f)
    except Exception as expt:
        errOut.send('nonfatalError', 'Could not translate Game.ini: %r; leaving untranslated' % expt)
        if os.path.isfile(outfn):
            os.remove(outfn)
        shutil.copy(infn, outfn)