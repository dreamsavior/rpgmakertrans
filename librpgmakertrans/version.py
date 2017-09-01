"""
version
*******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2017
:license: GNU Public License version 3

Provides functionality related to versioning, including the version check.
"""

from urllib.request import urlopen, URLError
import datetime

version = 4.5
expiry = datetime.date(2500, 6, 1)
debug = False
beta = False

versionString = '4.5 Legacy'

def versionCheck(coms):
    """Check to see if a new version is available"""
    try:
        message_url = 'https://rpgmakertrans.bitbucket.io/rpgmaker_legacy_message'
        with urlopen(message_url) as message_file:
            message = message_file.read()
        if message:
            coms.send('nonfatalError', message)
    except URLError:
        pass
    except Exception as e:
        coms.send('nonfatalError', 'Unspecified error: %s' % e)


if __name__ == '__main__':
    from .controllers.sender import ErrorSender
    versionCheck(ErrorSender())
