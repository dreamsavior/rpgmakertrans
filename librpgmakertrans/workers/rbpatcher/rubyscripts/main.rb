# main.rb
# *******
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Provides the main loop for the Ruby patching engine
#

require_relative 'socketcall.rb'
require_relative 'rgss.rb'
require_relative 'transvx.rb'
going = true

versionString = getVersion()

def translateFile(infile, outfile, context)
  puts('working on %s' % context)
  patchFile(infile, outfile, context)
  puts('translated %s (%s=>%s)' % [context, infile, outfile])
end

def rebuildScripts() 
  value = getTranslatedScript()
  while value[0] > 0
    puts('rebuilding %s' % value[1])
  end
end

while going 
  values = getTaskParams()
  code = values[0]
  if code == 'quit'
    going = false
  elsif code == 'translateFile' 
    translateFile(values[1], values[2], values[3])
  elsif code == 'rebuildScripts'
    rebuildScripts()
  elsif code == 'wait'
    sleep(1.0) 
  end
end