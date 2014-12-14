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

going = False

versionString = getVersion()

while going 
  values = getTaskParams()
  code = values[0]
  if code == 'quit'
    going = False
  elsif code == 'translateFile' 
    translateFile(values[1])
  elsif code == 'rebuildScripts'
    rebuildScripts()
  elsif code == 'wait'
    sleep(1.0) 
  end
end