# main.rb
# *******
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2015
# :license: GNU Public License version 3
#
# Provides the main loop for the Ruby patching engine
#

# This ruby script will connected as client

#dreamsavior debug
puts "Starting Ruby script".inspect
require 'net/http'
require 'uri'

def send_log(label, content)
  return
  
  url = URI.parse("http://localhost/logger/index.php?label=#{URI.encode(label)}&t=#{URI.encode(content)}")
  response = Net::HTTP.get_response(url)

  if response.is_a?(Net::HTTPSuccess)
    return response.body
  else
    return "Error: #{response.message}"
  end
end
#end of debug

socketNo = ARGV[0].to_i
if socketNo == 0
  socketNo = 27899
end

require 'socket'
if ARGV[1] != 'compile'
  $SOCK = TCPSocket.new('127.0.0.1', socketNo)
  $SOCK.setsockopt(Socket::IPPROTO_TCP, Socket::TCP_NODELAY, 1)
end

require_relative 'socketcall.rb'
require_relative 'patcher.rb'
going = true
loadedScripts = false
versionString = getVersion()
mode = nil
case versionString
when 'xp'
  mode = :xp
when 'vx'
  mode = :vx
when 'vxace'
  mode = :vxace
end

def setupLoadData(path)
  send_log("setupLoadData", path)

  path.force_encoding 'utf-8'
  loadData = "def load_data(path)\npath.force_encoding 'utf-8'\ndata = 0\nFile.open( File.join('%s', path), 'rb' ) do |datafile|\ndata=data = Marshal.load(datafile)\nend\nreturn data\nend\n" % path
  eval(loadData)
end

def loadScripts()
  send_log("loadScripts", "loading script")

  b = binding
  getScripts.each{|script|
    begin
      send_log("script", script)
      eval(script, b, script.split("\n").first)

      #eval(script)
    rescue Exception => e
      puts script
      # TODO: Some non fatal error code maybe?
      raise e
    end
  }
end

def translateFile(infile, outfile, context, mode)
  puts('working on %s' % context)
  patchFile(infile, outfile, context, mode)
  puts('translated %s (%s=>%s)' % [context, infile, outfile])
  doneTranslation(context)
end

def translateScripts(infile)
  #puts('working on Scripts')
  send_log("translateScripts", infile)
  dumpScriptsFile(infile)
  #puts('translated Scripts (%s)' % infile)
  doneTranslation('ScriptsDumped')
end

def rebuildScripts(outfile)
  value = getTranslatedScript()
  scripts = []
  while value[0].to_i > 0
    scripts.push([value[2], value[1], value[3]])
    #puts('receiving %s (magicNo:%s)' % [value[1], value[2]])
    #send_log("rebuildScript", value[2] + "\n" + value[1]+ "\n" + value[3])
    value = getTranslatedScript()
  end
  scripts.push([value[2], value[1], value[3]])
  #puts('receiving %s (magicNo:%s)' % [value[1], value[2]])
  writeScriptsFile(outfile, scripts)
  doneTranslation('Scripts')
end

while going
  values = getTaskParams()
  code = values[0]
  if code == 'quit'
    going = false
  elsif code == 'translateScripts'
    translateScripts(values[1])
  elsif code == 'translateFile'
    if loadedScripts == false
      loadedScripts = true
      loadScripts()
    end
    translateFile(values[1], values[2], values[3], mode)
  elsif code == 'rebuildScripts'
    rebuildScripts(values[1])
  elsif code == 'wait'
    sleep(1.0)
  else
    puts('ERROR')
    puts(code)
  end
end

closeConnection()
$SOCK.close()