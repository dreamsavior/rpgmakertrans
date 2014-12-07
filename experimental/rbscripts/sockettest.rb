require 'socket'

sock = TCPSocket.new('localhost', 27899)

data = [0, 1].pack('LL')
sock.write(data)
td = 'testdata'
sock.write([td.bytesize].pack('L'))
sock.write(td)
sock.close()
