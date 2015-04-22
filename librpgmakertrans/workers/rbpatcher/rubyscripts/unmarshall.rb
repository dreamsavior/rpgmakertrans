# unmarshall.rb
# **********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2015
# :license: GNU Public License version 3
#
# A universal unmarshaller. It should be able to unmarshall literally
# anything, by inspecting the exceptions for unknown classes.
# This only works with Ruby 2.1 or greater; Ruby <= 2.0 seems to
# be happy to unmarshall stuff to the wrong class without error or
# even a warning (normally referencing a top level class in this
# manner gives a warning!)
#


def unmarshall(fn)
  data = nil
  while data == nil do
    begin
      File.open(fn, "rb" ) do |datafile|
        data = Marshal.load(datafile)
      end
    rescue ArgumentError => exc
      name = exc.message.split(' ').last
      if name[name.length-2..name.length] == '::'
        name = name[0..name.length-3]
      end
      splitName = name.split('::')
      splitName.each_index { |x|
        partName = splitName[0..x].join('::')
        begin
          if eval('%s.name != "%s"' % [partName, partName])
            eval("class %s\nend" % partName)
          end
        rescue
          eval("class %s\nend" % partName)
        end
      }
    rescue TypeError => exc
      name = exc.message.split(' ')[1]
      definition = "class %s\ndef initialize data\n@marshalldata = data\nend\ndef self._load data\nnew(data)\nend\ndef _dump\n@marshalldata\nend\nend" % name
      eval(definition)
    end
  end
  return data
end