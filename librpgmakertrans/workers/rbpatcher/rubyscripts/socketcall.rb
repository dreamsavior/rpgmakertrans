# socketcall.rb
# *************
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Contains the functions which allow Ruby to call Python over sockets
#

require 'socket'

def socketCall(code, args)
  #sock = TCPSocket.new('127.0.0.1', 27899)
  sock = $SOCK
  packet = ''
  packet += [code].pack('L')
  args.each do |arg|
    packet += [arg.bytesize].pack('L')
    packet += arg
  end
  sock.write([packet.length].pack('L') + packet)
  recvPacketLen = sock.recv(4).unpack('L')[0]
  recvPacket = sock.recv(recvPacketLen)
  #nargs = sock.recv(4).unpack('L')[0]
  ret = []
  pos = 4
  while pos < recvPacket.length
    argSize = recvPacket[pos, 4].unpack('L')[0]
    pos += 4
    arg = recvPacket[pos, argSize]
    ret.push(arg)
    pos += argSize
  end
  #sock.close()
  return ret
end

def closeConnection()
  $SOCK.write([4, 0].pack('LL'))
end

def debug(string)
  puts socketCall(10, [string])
end

def translate(string, context)
  return socketCall(1, [string, context])[0]
end

def sendScript(scriptName, script, magicNo)
  return socketCall(2, [scriptName, script, magicNo])
end

def getTaskParams()
  return socketCall(3, [])
end

def getVersion()
  return socketCall(4, [])
end

def setScripts(scripts)
  return socketCall(5, scripts)
end

def getTranslatedScript()
  return socketCall(6, [])
end

def doneTranslation(context)
  return socketCall(7, [context])
end