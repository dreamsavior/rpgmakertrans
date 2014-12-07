'''
socketcomms
***********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Socket based communication. Intended to be used for
communicating with Ruby.
'''

import asyncio, struct

from ..errorhook import handleError

class SocketComms:
    def __init__(self, inputcoms, errorcoms, socket=None):
        self.loop = asyncio.get_event_loop()
        self.socket = 27899 if socket is None else socket
        self.inputcoms = inputcoms
        self.errorcoms = errorcoms
        self.codeHandlers = {0: self.debug}
    
    def debug(self, *args):
        print('Debug got args: %s' % args)
        
    @asyncio.coroutine
    def handleRequest(self, reader, writer):
        try:
            header = yield from reader.read(8)
            code, numberArgs = struct.unpack('II', header)
            if code not in self.codeHandlers:
                raise Exception('Unexpected Code %s' % code)
            args = []
            for _ in range(numberArgs):
                rawLength = yield from reader.read(4)
                length = struct.unpack('I', rawLength)[0]
                nextArg = yield from reader.read(length)
                args.append(nextArg)
            output = self.codeHandlers[code](*args)
            if output:
                if isinstance(output, bytes):
                    writer.write(struct.pack(len(output)))
                    writer.write(output)
                else:
                    raise Exception('Unhandled return type %s' % type(output).__name__)
                yield from writer.drain()
                
            writer.close()
        except:
            handleError()
            
    @asyncio.coroutine
    def checkForQuit(self):
        while True:
            yield from asyncio.sleep(0.1)
            if self.inputcoms:
                for signal, _, _ in self.inputcoms.get():
                    if signal == 'QUIT':
                        return
            
    def start(self):
        coro = asyncio.start_server(self.handleRequest, '127.0.0.1', self.socket, loop=self.loop)
        self.server = self.loop.run_until_complete(coro)
        # Serve requests until CTRL+c is pressed
        try: self.loop.run_until_complete(self.checkForQuit())
        except KeyboardInterrupt: pass
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()
        
if __name__ == '__main__':
    x = SocketComms(None, None)
    x.start()