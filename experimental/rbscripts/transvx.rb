# transvx.rb
# **********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# Script that contains most of the functions needed to translate Ruby
#

$KCODE = 'UTF8'
require 'zlib'
require 'rmvx/rgss2'
require 'vxschema'
require 'common'
# Notes:
# Don't think animations is necessary
# Areas unknown


def patchPage(translator, page, context)
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
        translatedString = translator.translateString(currentStr, contextString + 'Dialogue/')
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
          translatedChoice = translator.translateString(choiceString, contextString + 'Choice/')
          eventCommand.parameters[0][y] = translatedChoice
        }
        newPageList.push(eventCommand)
        currIndx += 1
      elsif eventCommand.code == 402
        translatedChoice = translator.translateString(eventCommand.parameters[1], contextString + 'Choice/')
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

def patch(translator, data, context)
  schemaMatchResult = schemaMatch($schema, context)
  if schemaMatchResult == 1
    return translator.translateString(data, contextStr(context))
  elsif schemaMatchResult == 2
    return patchPage(translator, data, context)
  elsif schemaMatchResult == 0
    if data.class == Array
      data.each_index{|x| 
         data[x] = patch(translator, data[x], context + [x])
      }
    elsif data.class == Hash
      data.each{|key, value| 
        data[key] = patch(translator, value, context+[key])
      }
    else
      context += [data.class]
      data.instance_variables.each{|var| 
        data.instance_variable_set(var, 
          patch(translator, data.instance_variable_get(var), 
                context + [var.sub(/^@/,'')]))
        }
     return data
    end
  else
    return data
  end
end

def patchFile(infn, outfn, translator, context)
  data = 0
  File.open( infn, "r+" ) do |datafile|
    data = Marshal.load(datafile)
  end
  patch(translator, data, [context])
  File.open( outfn, "w+") do |datafile|
    Marshal.dump(data, datafile)
  end
  #puts data.ya2yaml(:syck_compatible => true)
end


def parseScript(script, translator, context)
  scriptStr2 = ''
  currIndx = 0
  currBase = 0
  currMode = nil
  currTerm = nil
  escaping = false
  escapeValid = false
  scriptLen = scriptStr.length
  while currIndx < scriptLen
    char = scriptStr[currIndx, 1]
    if "'\"".include?(char)
      if currBase <= currIndx - 1
        scriptStr2 += scriptStr[currBase..currIndx-1]
      end
      currBase = currIndx
      char2 = nil
      while char2 != char
        currIndx += 1
        char2 = scriptStr[currIndx, 1]
      end
      if currBase < currIndx
        transString = scriptStr[currBase..currIndx]
        translated = translator.translateString(transString, contextString).strip
        if translated[0, 1] == '"' and translated[-1, 1] == '"'
        elsif translated[0, 1] == '\'' and translated[-1, 1] == '\''
        else 
          puts 'Ill formated string'
          puts translated
        end          
        scriptStr2 += translated
      end  
      currIndx += 1
      currBase = currIndx
      elsif char == '#'
        while char != "\n" and currIndx < scriptLen 
          currIndx += 1
          char = scriptStr[currIndx, 1]
        end
      end
      currIndx += 1  
    end
    scriptStr2 += scriptStr[currBase..currIndx]
    return scriptStr2
end

def scriptsFile(infn, outfn, translator, context)
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
      scriptStr2 = parseScript(scriptStr, translator, context)
      data[x][2] = Zlib::Deflate.deflate(scriptStr2)
    end
  }
  File.open( outfn, "w+") do |datafile|
    Marshal.dump(data, datafile)
  end
end