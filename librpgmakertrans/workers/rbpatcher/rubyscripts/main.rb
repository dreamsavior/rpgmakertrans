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
end

require_relative 'socketcall.rb'
#require_relative 'rgss.rb'
require_relative 'transvx.rb'
going = true
loadedScripts = false
versionString = getVersion()

if versionString == 'xp'
  versionSymbol = :xp
elsif versionString == 'vx'
  versionSymbol = :vx
elsif versionString == 'vxace'
  versionSymbol = :ace
end

#RGSS.setup_classes(versionSymbol, {})

def loadScripts()
  getScripts.each{|script|
    eval script
  }
end

def translateFile(infile, outfile, context)
  #puts('working on %s' % context)
  patchFile(infile, outfile, context)
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
  #puts(code)
  if code == 'quit'
    going = false
  elsif code == 'translateScripts'
    translateScripts(values[1])
  elsif code == 'translateFile'
    if loadedScripts == false
      loadedScripts = true
      loadScripts()
    end
    translateFile(values[1], values[2], values[3])
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