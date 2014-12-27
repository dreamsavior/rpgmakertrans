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
  sock = TCPSocket.new('localhost', 27899)
  data = [code, args.length].pack('LL')
  sock.write(data)
  args.each do |arg|
    sock.write([arg.bytesize].pack('L'))
    sock.write(arg)
  end
  nargs = sock.recv(4).unpack('L')[0]
  ret = []
  (1..nargs).each do |n|
    arglen = sock.recv(4).unpack('L')[0]
    ret.push(sock.recv(arglen))
  end
  sock.close()
  return ret
end

def debug(string)
  puts socketCall(0, [string])
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