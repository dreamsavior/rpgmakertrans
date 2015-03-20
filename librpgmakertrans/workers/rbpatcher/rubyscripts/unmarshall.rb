def unmarshall(fn)
  data = nil
  while data == nil do
    begin
      File.open(fn, "rb" ) do |datafile|
        data = Marshal.load(datafile)
      end
    rescue ArgumentError => exc
      name = exc.message.split(' ').last
      puts 'examining %s' % name
      if name[name.length-2..name.length] == '::'
        name = name[0..name.length-3]
      end
      splitName = name.split('::')
      splitName.each_index { |x|
        partName = splitName[0..x].join('::')
        puts partName
        begin
          if eval('%s.name != "%s"' % [partName, partName])
            puts('defining')
            eval("class %s\nend" % partName)
          end
        rescue
          puts('defining')
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