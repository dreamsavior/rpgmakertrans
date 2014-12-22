# transvx.rb
# **********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Script that contains most of the functions needed to translate Ruby
#

require 'zlib'
require_relative 'socketcall.rb'
require_relative 'rgss.rb'
require_relative 'vxschema.rb'

# Notes:
# Don't think animations is necessary
# Areas unknown

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

def patchPage(page, context)
  # Some notes for VX:
  # code 101 sets up / clears a dialogue box.
  # a 101 may be followed by 401s, each with a single line of dialogue
  # as their only parameter. 401s may not occur anywhere else, and will
  # *always* follow 101
  # code 102 does choices. choices are given as parameters to 102.
  # code 402 is the "resume" after a choice. It contains both a string
  # of the parameter and the index, but I don't think the string
  # absolutely has to be translated. Still, it might be a good idea to
  # do so.
  # code 108/408 are most likely dev comments. Interpreter ignores them
  # completely.
  # Note: This function TRIMs trailing newlines. This means that
  # it is not guaranteed to be an identity if it translates nothing.
  # It doesn't eliminate empty dialogue boxes
  contextString = contextStr(context)
  currentStr = ''
  numberConsecutive = 0
  if page != nil
    newPageList = []
    pageListLen = page.list.length
    currIndx = 0
    while currIndx < pageListLen
      eventCommand = page.list[currIndx]
      if eventCommand.code == 101
        currIndx += 1
        windowInit = eventCommand
        indent = windowInit.indent
        eventCommand = page.list[currIndx]
        currentStr = ''
        while eventCommand.code == 401 and currIndx < pageListLen do
          currentStr += eventCommand.parameters[0] + "\n"
          currIndx += 1
          eventCommand = page.list[currIndx] 
        end
        currentStr.rstrip!
        translatedString = translate(currentStr, contextString + 'Dialogue/')
        if translatedString == ''
          translatedString = ' '
        end
        lineCount = 0
        newPageList.push(windowInit)
        translatedString.split("\n").each {|line|
          if lineCount == 4
            lineCount = 0
            newPageList.push(windowInit)
          end
          lineCount += 1
          newPageList.push(RPG::EventCommand.new(401, indent, [line]))
        }
        
      elsif eventCommand.code == 102
        eventCommand.parameters[0].each_index{|y|
          choiceString = eventCommand.parameters[0][y]
          translatedChoice = translate(choiceString, contextString + 'Choice/')
          eventCommand.parameters[0][y] = translatedChoice
        }
        newPageList.push(eventCommand)
        currIndx += 1
      elsif eventCommand.code == 402
        translatedChoice = translate(eventCommand.parameters[1], contextString + 'Choice/')
        eventCommand.parameters[1] = translatedChoice
        newPageList.push(eventCommand)
        currIndx += 1 
      else
        newPageList.push(eventCommand)
        currIndx += 1
      end 
    end
    #if newPageList != page.list 
    #  puts contextString
    #end
    page.list = newPageList
  end
  return page
end

def patch(data, context)
  schemaMatchResult = schemaMatch($schema, context)
  if schemaMatchResult == 1
    return translate(data, contextStr(context))
  elsif schemaMatchResult == 2
    return patchPage(data, context)
  elsif schemaMatchResult == 0
    if data.class == Array
      data.each_index{|x| 
         data[x] = patch(data[x], context + [x])
      }
    elsif data.class == Hash
      data.each{|key, value| 
        data[key] = patch(value, context+[key])
      }
    else
      context += [data.class]
      data.instance_variables.each{|var|
        data.instance_variable_set(var, 
          patch(data.instance_variable_get(var), 
                context + [var.to_s.sub(/^@/,'')]))
        }
     return data
    end
  else
    return data
  end
end

def patchFile(infn, outfn, context)
  data = 0
  File.open( infn, "r+" ) do |datafile|
    data = Marshal.load(datafile)
  end
  patch(data, [context])
  File.open( outfn, "w+") do |datafile|
    Marshal.dump(data, datafile)
  end
  #puts data.ya2yaml(:syck_compatible => true)
end


def scriptsFile(infn, outfn, context)
  # TODO: This will need a lot of work.
  data = nil
  File.open(infn, "r+") do |datafile|
    data = Marshal.load(datafile)
  end
  data.each_index{|x|
    magicNo = data[x][0]
    scriptName = data[x][1]
    contextString = context + '/' + scriptName + '/' 
    scriptStr = Zlib::Inflate.inflate(data[x][2])
    if scriptName != '' and scriptStr != ''
      scriptStr2 = parseScript(scriptStr, context)
      data[x][2] = Zlib::Deflate.deflate(scriptStr2)
    end
  }
  File.open( outfn, "w+") do |datafile|
    Marshal.dump(data, datafile)
  end
end