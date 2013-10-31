'''
Created on 31 Oct 2013

@author: habisain
'''

from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup

version = 2.0

def versionCheck(coms):
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
    import sender
    versionCheck(sender.Sender())
