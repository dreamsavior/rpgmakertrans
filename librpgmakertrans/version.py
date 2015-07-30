"""
version
*******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Provides functionality related to versioning, including the version check.
"""

from urllib.request import urlopen
import datetime

version = 4.201
expiry = datetime.date(2016, 8, 1)
debug = False
beta = True

versionString = '%s%s%s' % (str(round(version, 2)), ' [DEBUG]' if debug else '',
                            ' [BETA]' if beta else '')

def versionCheck(coms):
    """Check to see if a new version is available"""
    if expiry < datetime.date.today():
        coms.send('expired')
        return
    try:
        versionURL = 'http://rpgmakertrans.bitbucket.org/rpgmakertransversion'
        if beta:
            versionURL += 'beta'
        with urlopen(versionURL) as versionFile:
            versionData = versionFile.read()
        webver = float(versionData.strip())
        if webver > version:
            coms.send('newVerAvailable', webver)
    except Exception as e:
        coms.send('nonfatalError', 'Error checking version: %s' % e)

if __name__ == '__main__':
    from .controllers.sender import ErrorSender
    versionCheck(ErrorSender())
