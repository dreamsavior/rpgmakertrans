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

version = 3.0
expiry = datetime.date(2016, 4, 1)
debug = True

versionString = '%s%s' % (str(version), ' [DEBUG]' if debug else '')

def versionCheck(coms):
    """Check to see if a new version is available"""
    if expiry < datetime.date.today():
        coms.send('expired')
        return
    try:
        versionURL = 'http://rpgmakertrans.bitbucket.org/rpgmakertransversion'
        with urlopen(versionURL) as versionFile:
            versionData = versionFile.read()
        webver = float(versionData.strip())
        if webver > version:
            coms.send('newVerAvailable', webver)
    except Exception as e:
        print('error %s' % e)
        pass

if __name__ == '__main__':
    from .controllers.sender import ErrorSender
    versionCheck(ErrorSender())
