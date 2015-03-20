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
      definition = "class %s\nend" % name
      eval(definition)
    rescue TypeError => exc
      name = exc.message.split(' ')[1]
      definition = "class %s\ndef initialize data\n@marshalldata = data\nend\ndef self._load data\nnew(data)\nend\ndef _dump\n@marshalldata\nend\nend" % name
      eval(definition)
    end
  end
  return data
end