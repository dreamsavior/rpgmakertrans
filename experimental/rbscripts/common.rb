# common.rb
# *********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Provides some common features for different experimental implemenations
# of Ruby patchers
#

require 'yaml'

class Translator
  def initialize(translations)
    @translations = translations
    @transOrder = []
  end
  def translateString(string, context)
    if string == ''
      return string
    end
    if not @transOrder.include?(string)
      @transOrder.push(string)
    end
    if not @translations.include?(string)
      
      @translations[string] = Hash.new
    end
    if not @translations[string].include?(context)
      @translations[string][context] = 0
      return string
    else
      translation = @translations[string][context]
      if translation == 0
        return string
      else
        return @translations[string][context]
      end
    end
  end
  def pyRead(infn)
    code = nil
    File.open(infn, "rb") do |datafile|
      code = datafile.read()
    end
    eval('@translations = ' + code)
  end
  def rbDump(outfn)
    data = @translations.inspect
        File.open( outfn, "wb+") do |datafile|
          datafile.write(data)
        end
      end
  def pyDump(outfn)
    data = '[{'
    @translations.each{|k,v|
      dv = '{'
      v.each{|k2, v2| dv += k2.inspect + ':' + v2.inspect + ","}
      dv += '}'
      data += k.inspect + ':' + dv + ","
    }
    data += '}, ' + @transOrder.inspect + ']'
    File.open( outfn, "wb+") do |datafile|
      datafile.write(data)
    end
  end
  def debugprint()
    @translations.each{|x, y|
      puts 'Original String'
      puts x
      puts 'Contexts'
      y.each_key{|z|
        puts z
      }
    }
  end

end


def contextStr(context)
  result = ''
  context.each{|x| result += x.to_s + '/'}
  result = result.sub('RPG::', '')
  return result
end

def schemaMatch(schema, context)
  schemaLevel = schema
  level = 0
  context.each{|x|
    level += 1
    # Match all Maps to the Map class
    if x.class == String and x[0, 3] == 'Map'
      x = 'Map'
    end
    if schemaLevel.member?(x)
      schemaLevel = schemaLevel[x]
    elsif schemaLevel.member?(true)
      schemaLevel = schemaLevel[true] 
    else
      return -1 # Failure, do not iterate down here.
    end
  }
  if schemaLevel == true
    return 1 # Success, dump this for translating
  elsif schemaLevel == 'eventList'
    return 2 # Dump an event list
  else
    return 0 # Failure, but keep iterating
  end

end
