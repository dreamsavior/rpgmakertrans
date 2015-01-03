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

def readPacket(packet):
    """Read data of a packet into code and byte arguments"""
    code = struct.unpack('I', packet[0:4])[0]
    args = []
    pos = 4
    while pos < len(packet):
        argSize = struct.unpack('I', packet[pos:pos+4])[0]
        args.append(packet[pos+4:pos+4+argSize])
        pos += 4 + argSize
    return code, args

def writePacket(args):
    """Write a packet of byte arguments"""
    packetLS = [struct.pack('I', len(args))]
    for arg in args:
        packetLS.extend([struct.pack('I', len(arg)), arg])
    packet = b''.join(packetLS)
    packet = struct.pack('I', len(packet)) + packet
    return packet

class SocketComms:
    def __init__(self, socket=None):
        self.loop = asyncio.get_event_loop()
        self.socket = 27899 if socket is None else socket
        self.codeHandlers = {10: self.debug}
        self.rawArgs = {0: False}
        self.tickTasks = [self.checkForQuit]

    def debug(self, *args):
        print('Debug got args: %s' % args)
        return 'Debug Test for Python'

    @asyncio.coroutine
    def handleRequest(self, reader, writer):
        while True:
            try:
                packetSizeB = yield from reader.read(4)
                packetSize = struct.unpack('I', packetSizeB)[0]
                packet = yield from reader.read(packetSize)
                code, args = readPacket(packet)
                if code == 0:
                    yield from writer.drain()
                    writer.close()
                    return
                if code not in self.codeHandlers:
                    raise Exception('Unexpected Code ' + str(code))
                rawArgs = self.rawArgs.get(code, False)
                if not rawArgs:
                    args = [arg.decode('utf-8') for arg in args]
                output = self.codeHandlers[code](*args)
                if output is None:
                    output = []
                elif isinstance(output, (bytes, str)):
                    output = [output]
                if not rawArgs:
                    output = [arg.encode('utf-8') for arg in output]
                if isinstance(output, (tuple, list)):
                    writer.write(writePacket(output))
                else:
                    raise Exception('Unhandled return type %s' % type(output).__name__)
                yield from writer.drain()
            except:
                handleError()

    @asyncio.coroutine
    def checkForQuit(self):
        """By default, this loops forever. Override for other behaviours"""
        while True:
            yield from asyncio.sleep(5)

    def start(self):
        coro = asyncio.start_server(self.handleRequest, '127.0.0.1', self.socket, loop=self.loop)
        self.server = self.loop.run_until_complete(coro)
        # Serve requests until CTRL+c is pressed
        loopCondition = asyncio.wait([coro() for coro in self.tickTasks])
        try: self.loop.run_until_complete(loopCondition)
        except KeyboardInterrupt: pass
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()

class ControlableSocketComms(SocketComms):
    def __init__(self, inputcoms, errorcoms, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inputcoms = inputcoms
        self.errorcoms = errorcoms

    @asyncio.coroutine
    def checkForQuit(self):
        while True:
            yield from asyncio.sleep(0.1)
            if self.inputcoms:
                for signal, _, _ in self.inputcoms.get():
                    if signal == 'QUIT':
                        return
if __name__ == '__main__':
    x = SocketComms()
    x.start()