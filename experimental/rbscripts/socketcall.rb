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
  data = [0, args.length].pack('LL')
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
  return socketCall(1, [string, context])
end

def translateScript(script, scriptName)
  return socketCall(2, [script, scriptName])
end