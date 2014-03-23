'''
Created on 31 Oct 2013

@author: habisain
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime

version = 2.02
expiry = datetime.date(2015, 1, 1)

def versionCheck(coms):
    if expiry < datetime.date.today():
        coms.send('expired')
        return
    try:
        blogPage = urlopen('http://habisain.blogspot.com')
        blogData = blogPage.read()
        blogPage.close()
        blogSoup = BeautifulSoup(blogData)
        tags = blogSoup.findAll(attrs = {'class': 'rpgmaker-trans-latest-version-tag'})
        if len(tags) > 1: raise Exception
        tag = tags[0]
        webver = float(tag['versiondata'])
        if webver > version:
            coms.send('newVerAvailable', webver)
    except:
        pass
    
if __name__ == '__main__':
    from .controllers.sender import Sender
    versionCheck(Sender())
