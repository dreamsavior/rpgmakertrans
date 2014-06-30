# persist.rb
# **********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Provides a controller over STDIN/STDOUT for the Ruby patcher
#

require 'transvx'
require 'common'

def readinput
  line = STDIN.readline
  return line.chomp
end
def errout(s)
  STDERR.write(s+"\n")
  STDERR.flush()
end
def ready
  STDOUT.write("Ready\n")
  STDOUT.flush()
end
translator = Translator.new({})
line = readinput()
while line != 'QUIT'
  if line == 'PATCH'
    inbin = readinput()
    outbin = readinput()
    context = readinput()
    if context == 'Scripts'
      scriptsFile(inbin, outbin, translator, context)
    else
      patchFile(inbin, outbin, translator, context)
    end
    ready()
  elsif line == 'IMPORT'
    translator.pyRead(readinput())
    ready()
  elsif line == 'EXPORT'
    translator.pyDump(readinput())
    ready()
  end
  
  line = readinput()
end

