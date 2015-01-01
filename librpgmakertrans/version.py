"""
version
*******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides functionality related to versioning, including the version check.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime

version = 3.0
expiry = datetime.date(2016, 4, 1)
debug = True

def versionCheck(coms):
    if expiry < datetime.date.today():
        coms.send('expired')
        return
    try:
        blogPage = urlopen('http://habisain.blogspot.com')
        blogData = blogPage.read()
        blogPage.close()
        blogSoup = BeautifulSoup(blogData)
        tags = blogSoup.findAll(
            attrs={'class': 'rpgmaker-trans-latest-version-tag'})
        if len(tags) > 1:
            raise Exception
        tag = tags[0]
        webver = float(tag['versiondata'])
        if webver > version:
            coms.send('newVerAvailable', webver)
    except:
        pass

if __name__ == '__main__':
    from .controllers.sender import Sender
    versionCheck(Sender())
