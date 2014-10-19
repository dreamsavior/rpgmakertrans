
$KCODE = 'UTF8'
require 'zlib'
require 'rmvx/rgss2'
require 'vxschema'
require 'common'

def scriptsFileDump(infn, outfn)
  data = nil
  File.open(infn, "r+") do |datafile|
    data = Marshal.load(datafile)
  end
  data.each_index{|x|
    magicNo = data[x][0]
    scriptName = data[x][1] 
    scriptStr = Zlib::Inflate.inflate(data[x][2])
    if scriptName != '' and scriptStr != ''
      File.open(outfn + scriptName + '.rb', 'w+') do |datafile|
        datafile.write(scriptStr)
      end
    end
  }
end

infn = ARGV[0]
outfn = ARGV[1]

scriptsFileDump(infn, outfn)