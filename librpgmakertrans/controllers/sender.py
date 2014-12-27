"""
sender
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Sender is a simple multiprocessing method of sending signals
"""
import sys

from multiprocessing.managers import BaseManager


class SenderManager(BaseManager):
    pass


class Sender:

    def __init__(self):
        self.__signals = []

    def send(self, signal, *args, **kwargs):
        self.__signals.append((signal, args, kwargs))

    def get(self):
        ret = self.__signals
        self.__signals = []
        return ret

    def __getattr__(self, key):
        def wrap(self, *args, **kwargs):
            self.send(key, *args, **kwargs)
        wrap.__name__ = 'send%s' % key
        self.key = wrap
        return self.key
    
class ErrorSender(Sender):
    def send(self, signal, *args, **kwargs):
        if signal == 'ERROR':
            if len(args) > 0:
                print(args[0], file=sys.stderr)
            else:
                print(signal, args, kwargs, file=sys.stderr)
        super().send(signal, *args, **kwargs)

SenderManager.register('Sender', Sender)
SenderManager.register('ErrorSender', ErrorSender)