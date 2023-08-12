# main.rb
# *******
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2015
# :license: GNU Public License version 3
#
# Provides the main loop for the Ruby patching engine
#

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
  path.force_encoding 'utf-8'
  loadData = "def load_data(path)\npath.force_encoding 'utf-8'\ndata = 0\nFile.open( File.join('%s', path), 'rb' ) do |datafile|\ndata=data = Marshal.load(datafile)\nend\nreturn data\nend\n" % path
  eval(loadData)
end

def loadScripts()
  b = binding
  getScripts.each{|script|
    begin
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
  #puts('working on %s' % context)
  patchFile(infile, outfile, context, mode)
  #puts('translated %s (%s=>%s)' % [context, infile, outfile])
  doneTranslation(context)
end

def translateScripts(infile)
  #puts('working on Scripts')
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