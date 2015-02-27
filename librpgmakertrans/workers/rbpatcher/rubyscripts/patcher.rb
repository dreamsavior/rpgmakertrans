# transvx.rb
# **********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2015
# :license: GNU Public License version 3
#
# Script that contains most of the functions needed to translate Ruby
#

require 'zlib'
require_relative 'socketcall.rb'
require_relative 'matcher.rb'

def contextStr(context)
  result = ''
  context.each{|x| 
               if x.class != Class 
                 result += x.to_s + '/'
               end}
  return result
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
  # code 355/655 are inline scripts. Similar to 101/401 for dialogue
  # code 111 may also have a script, if param[0] = 12, param[1] is a
  # script. However, this is for conditional branching, and anyone putting
  # a text based script here would be mad!
  # Note: This function TRIMs trailing newlines. This means that
  # it is not guaranteed to be an identity if it translates nothing.
  # It doesn't eliminate empty dialogue boxes
  contextString = contextStr(context)
  currentStr = ''
  numberConsecutive = 0
  if page != nil
    newPageList = []
    pageListLen = page.instance_variable_get(:@list).length
    currIndx = 0
    choiceContextData = {}
    while currIndx < pageListLen
      eventCommand = page.instance_variable_get(:@list)[currIndx]
      case eventCommand.instance_variable_get(:@code)
      when 101
        dialogueLoc = currIndx
        currIndx += 1
        windowInit = eventCommand
        indent = windowInit.instance_variable_get(:@indent)
        eventCommand = page.instance_variable_get(:@list)[currIndx]
        currentStr = ''
        while eventCommand.instance_variable_get(:@code) == 401 and currIndx < pageListLen do
          currentStr += eventCommand.instance_variable_get(:@parameters)[0].rstrip + "\n"
          currIndx += 1
          eventCommand = page.instance_variable_get(:@list)[currIndx]
        end
        currentStr.rstrip!
        translatedString = translate(currentStr, contextString + 'Dialogue/' + dialogueLoc.to_s + '/')
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
      when 102
        choicePos = currIndx
        choiceNo = 0
        eventCommand.instance_variable_get(:@parameters)[0].each_index{|y|
          choiceString = eventCommand.instance_variable_get(:@parameters)[0][y].rstrip
          choiceContextData[choiceString] = [choicePos, choiceNo]
          translatedChoice = translate(choiceString, contextString + 'Choice/%s/%s' % [choicePos.to_s, choiceNo.to_s])
          eventCommand.instance_variable_get(:@parameters)[0][y] = translatedChoice
          choiceNo += 1
        }
        newPageList.push(eventCommand)
        currIndx += 1
      when 402
        choiceString = eventCommand.instance_variable_get(:@parameters)[1].rstrip
        choiceData = choiceContextData[choiceString]
        translatedChoice = translate(choiceString,
                                     contextString + 'Choice/%s/%s' % [choiceData[0].to_s, choiceData[1].to_s])
        eventCommand.instance_variable_get(:@parameters)[1] = translatedChoice
        newPageList.push(eventCommand)
        currIndx += 1
      when 355
        line = eventCommand.instance_variable_get(:@parameters)[0].rstrip
        script = line + "\n"
        indent = eventCommand.instance_variable_get(:@indent)
        currIndx += 1
        eventCommand = page.instance_variable_get(:@list)[currIndx]
        while eventCommand.instance_variable_get(:@code) == 655 and currIndx < pageListLen do
          line = eventCommand.instance_variable_get(:@parameters)[0].rstrip
          script += line + "\n"
          currIndx += 1
          eventCommand = page.instance_variable_get(:@list)[currIndx]
        end
        translatedscript = translateInlineScript(script, contextString + 'InlineScript/').lines
        code = 355
        translatedscript.each { |line|
          line.chomp!
          newPageList.push(RPG::EventCommand.new(code, indent, [line]))
          code = 655
        }
      else
        newPageList.push(eventCommand)
        currIndx += 1
      end
    end
    page.instance_variable_set(:@list, newPageList)
  end
  return page
end

def patch(data, context)
  
  matchResult = matchAll(data, context)
  
  if matchResult == :translate
    return translate(data, contextStr(context))
  elsif matchResult == :eventList
    return patchPage(data, context)
  elsif matchResult == :continue
    if data.class == Array
      data.each_index{|x|
         data[x] = patch(data[x], context + [x])
      }
      return data
    elsif data.class == Hash
      data.sort.each{|key, value|
        data[key] = patch(value, context+[key])
      }
      return data
    elsif data.class != context[-1]
      context += [data.class]
      return patch(data, context)
    else
      data.instance_variables.each{|var|
        data.instance_variable_set(var,
          patch(data.instance_variable_get(var),
                context + [var.to_s.sub(/^@/,'')]))
        }
      return data
    end
  elsif matchResult == :abort 
    return data
  else
    puts matchResult.to_s
  end
end

def patchFile(infn, outfn, context)
  data = 0
  File.open( infn, "rb" ) do |datafile|
    data = Marshal.load(datafile)
  end
  patch(data, [context])
  File.open( outfn, "wb+") do |datafile|
    Marshal.dump(data, datafile)
  end
end


def dumpScriptsFile(infn)
  data = nil
  File.open(infn, "r+") do |datafile|
    data = Marshal.load(datafile)
  end
  data.each_index{|x|
    magicNo = data[x][0]
    scriptName = data[x][1]
    scriptStr = Zlib::Inflate.inflate(data[x][2])
    if scriptName != '' and scriptStr != ''
      sendScript(scriptName, scriptStr, magicNo.to_s)
    end
  }
end

def writeScriptsFile(outfn, data)
  data.each_index{|x|
    scriptName = data[x][1]
    scriptStr = data[x][2]
    if scriptName != '' and scriptStr != ''
      data[x][2] = Zlib::Deflate.deflate(scriptStr)
    end
  }
  File.open( outfn, "w+") do |datafile|
    Marshal.dump(data, datafile)
  end
end