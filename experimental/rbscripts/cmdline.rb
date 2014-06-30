# cmdline.rb
# **********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Very basic, and slow, command line based patcher. Only for testing.
#

require 'transvx'
require 'common'

if ARGV.length != 5
  puts "ERROR: Cannot parse ARGV"
else
  
  inbin = ARGV[0]
  outbin = ARGV[1]
  context = ARGV[2]
  intrans = ARGV[3]
  outtrans = ARGV[4]

  translator = Translator.new({})
  if intrans != '-'
    translator.pyRead(intrans)
  end
  if context == 'Scripts'
    scriptsFile(inbin, outbin, translator, context)
  else
    patchFile(inbin, outbin, translator, context)
  end
  if outtrans != '-'
    translator.pyDump(outtrans)
  end
end