"""
sender
******

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Sender is a simple multiprocessing method of sending signals
"""

import sys
import uuid

from multiprocessing.managers import BaseManager

class SenderManager(BaseManager):
    """Manager for Sender objects"""

class SenderID:
    """ID for Senders"""
    def __init__(self):
        """Setup the ID"""
        self.uuid = uuid.uuid4()
        
    def __hash__(self):
        """Hash function"""
        return hash(type(self), self.uuid)
    
    def __eq__(self, other):
        """Equality operator"""
        return type(self) == type(other) and self.uuid == other.uuid

class Sender:
    """A Sender for data between processes"""
    def __init__(self):
        """Initialise the Sender"""
        self.__signals = []
        self.senderID = SenderID()

    def send(self, signal, *args, **kwargs):
        """Send a signal"""
        self.__signals.append((signal, args, kwargs))

    def get(self):
        """Get the signals in the Sender"""
        ret = self.__signals
        self.__signals = []
        return ret

    def __getattr__(self, key):
        """Method for remote calling - depreceated"""
        def wrap(self, *args, **kwargs):
            """Wrap the send function with the key"""
            self.send(key, *args, **kwargs)
        wrap.__name__ = 'send%s' % key
        self.key = wrap
        return self.key
    
class ErrorSender(Sender):
    """Version of Sender which dumps all signals to stderr"""
    def send(self, signal, *args, **kwargs):
        """Put signals onto stderr, with special handling for errors"""
        if signal == 'ERROR':
            if len(args) > 0:
                print(args[0], file=sys.stderr)
            else:
                print(signal, args, kwargs, file=sys.stderr)
        super().send(signal, *args, **kwargs)

SenderManager.register('Sender', Sender)
SenderManager.register('ErrorSender', ErrorSender)