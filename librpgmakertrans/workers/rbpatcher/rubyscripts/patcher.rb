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
require_relative 'unmarshall.rb'
def contextStr(context)
  result = ''
  context.each{|x| 
               if x.class != Class 
                 result += x.to_s + '/'
               end}
  return result
end

module RPG
end

class RPG::EventCommand
  def initialize(code = 0, indent = 0, parameters = [])
    @code = code
    @indent = indent
    @parameters = parameters
  end
  attr_accessor :code
  attr_accessor :indent
  attr_accessor :parameters
end

module PageMatchers
  extend self
  def match101(code, currentCommand, mode)
    if code == 101
      return mode == :xp ? :patch101xp : :patch101
    end
  end
  def match102(code, currentCommand, mode)
      return code == 102 ? :patch102 : nil
  end
  def match402(code, currentCommand, mode)
      return code == 402 ? :patch402 : nil
  end
  def match118(code, currentCommand, mode)
      return code == 118 ? :patch118119 : nil
  end
  def match119(code, currentCommand, mode)
      return code == 119 ? :patch118119 : nil
  end
  def match355(code, currentCommand, mode)
      return code == 355 ? :patch355 : nil
  end  
end

def pageMatchAll(code, currentCommand, mode)
  PageMatchers.module_eval do
    PageMatchers.instance_methods.each do |funcname|
      ret = PageMatchers.send(funcname, code, currentCommand, mode)
      if ret != nil
        return ret
      end
    end
  end
  return nil
end

module PagePatchers
  extend self
  
  def patch101(currIndx, contextString, pageList, newPageList, storage)
    # TODO: Fix for XP
    dialogueLoc = currIndx
    currIndx += 1
    windowInit = pageList[currIndx]
    indent = windowInit.instance_variable_get(:@indent)
    currentStr = ''
    while pageList[currIndx].instance_variable_get(:@code) == 401 and currIndx < pageList.length do
      currentStr += pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip + "\n"
      currIndx += 1
    end
    currentStr.rstrip!
    translatedString = translate(currentStr, contextString + '%s/Dialogue' % dialogueLoc.to_s)
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
    return currIndx
  end
  
  def patch101xp(currIndx, contextString, pageList, newPageList, storage)
    dialogueLoc = currIndx
    indent = pageList[currIndx].instance_variable_get(:@indent)
    currentStr = ''
    firstLine = pageList[currIndx].instance_variable_get(:@parameters)[0]
    if firstLine.class == String
      currentStr += firstLine.rstrip + "\n"
    end
    currIndx += 1
    while pageList[currIndx].instance_variable_get(:@code) == 401 and currIndx < pageList.length do
      currentStr += pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip + "\n"
      currIndx += 1
    end
    currentStr.rstrip!
    translatedString = translate(currentStr, contextString + '%s/Dialogue' % dialogueLoc.to_s)
    if translatedString == ''
      translatedString = ' '
    end
    lineCount = 4
    translatedString.split("\n").each {|line|
      if lineCount == 4
        lineCount = 1
        newPageList.push(RPG::EventCommand.new(101, indent, [line]))
      else
        lineCount += 1
        newPageList.push(RPG::EventCommand.new(401, indent, [line]))
      end
    }
    return currIndx
  end
  
  def patch102(currIndx, contextString, pageList, newPageList, storage)
    choicePos = currIndx
    choiceNo = 0
    pageList[currIndx].instance_variable_get(:@parameters)[0].each_index{|y|
      choiceString = pageList[currIndx].instance_variable_get(:@parameters)[0][y].rstrip
      storage[:choiceContextData][choiceString] = [choicePos, choiceNo]
      translatedChoice = translate(choiceString, contextString + '%s/Choice/%s' % [choicePos.to_s, choiceNo.to_s])
      pageList[currIndx].instance_variable_get(:@parameters)[0][y] = translatedChoice
      choiceNo += 1
    }
    newPageList.push(pageList[currIndx])
    currIndx += 1
    return currIndx    
  end
  
  def patch402(currIndx, contextString, pageList, newPageList, storage)
    choiceString = pageList[currIndx].instance_variable_get(:@parameters)[1].rstrip
    choiceData = storage[:choiceContextData][choiceString]
    translatedChoice = translate(choiceString,
                                 contextString + '%s/Choice/%s' % [choiceData[0].to_s, choiceData[1].to_s])
    pageList[currIndx].instance_variable_get(:@parameters)[1] = translatedChoice
    newPageList.push(pageList[currIndx])
    currIndx += 1
    return currIndx
  end
  
  def patch118119(currIndx, contextString, pageList, newPageList, storage)
    label = pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip
    contextStr = contextString + '%s/Label' % currIndx.to_s
    translatedLabel = translate(label, contextStr)
    pageList[currIndx].instance_variable_get(:@parameters)[0] = translatedLabel
    newPageList.push(pageList[currIndx])
    currIndx += 1
    return currIndx
  end

  def patch355(currIndx, contextString, pageList, newPageList, storage)
    # TODO: Check if this is also different in XP
    line = pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip
    scriptPos = currIndx
    script = line + "\n"
    indent = pageList[currIndx].instance_variable_get(:@indent)
    currIndx += 1
    while pageList[currIndx].instance_variable_get(:@code) == 655 and currIndx < pageList.length do
      line = pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip
      script += line + "\n"
      currIndx += 1
    end
    translatedscript = translateInlineScript(script, contextString + '%s/InlineScript' % scriptPos.to_s).lines
    code = 355
    translatedscript.each { |line|
      line.chomp!
      newPageList.push(RPG::EventCommand.new(code, indent, [line]))
      code = 655
    }
    return currIndx
  end
end

def patchPage(page, context, mode)
  # Note: This function TRIMs trailing newlines. This means that
  # it is not guaranteed to be an identity if it translates nothing.
  # It doesn't eliminate empty dialogue boxes
  contextString = contextStr(context)
  if page != nil
    newPageList = []
    pageList = page.instance_variable_get(:@list)
    currIndx = 0
    storage = {choiceContextData: {}}
    while currIndx < pageList.length
      eventCommand = pageList[currIndx]
      # TODO: Use the matchers when they are done
      code = eventCommand.instance_variable_get(:@code)
      matchedFunc = pageMatchAll(code, eventCommand, mode)
      if matchedFunc != nil
        PagePatchers.module_eval do
          currIndx = PagePatchers.send(matchedFunc, currIndx, contextString, pageList, newPageList, storage)
        end        
      else
        newPageList.push(eventCommand)
        currIndx += 1
      end
    end
    page.instance_variable_set(:@list, newPageList)
  end
  return page
end

$priority = [:@name, :@display_name, :@description, :@message1, :@message2, :@message3, :@message4]
  
def patch(data, context, mode)
  
  matchResult = matchAll(data, context)
  
  case matchResult
  when :translate
    return translate(data, contextStr(context))
  when :randint
    return rand(2**32)
  when :eventList
    return patchPage(data, context, mode)
  when :continue
    if data.class == Array
      data.each_index{|x|
         data[x] = patch(data[x], context + [x], mode)
      }
      return data
    elsif data.class == Hash
      data.sort.each{|key, value|
        data[key] = patch(value, context+[key], mode)
      }
      return data
    elsif data.class != context[-1]
      context += [data.class]
      return patch(data, context, mode)
    else
      $priority.each{|var|
        if data.instance_variables.include? var
          data.instance_variable_set(var,
                    patch(data.instance_variable_get(var),
                          context + [var.to_s.sub(/^@/,'')], mode))
        end
      }
      data.instance_variables.each{|var|
        if not $priority.include? var
          data.instance_variable_set(var,
            patch(data.instance_variable_get(var),
                  context + [var.to_s.sub(/^@/,'')], mode))
        end
      }
      return data
    end
  when :abort 
    return data
  else
    puts 'Error encountered'
    puts matchResult.to_s
    return data
  end
end

def patchFile(infn, outfn, context, mode)
  data = unmarshall(infn)
  patch(data, [context], mode)
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
    if scriptStr != ''
      sendScript(scriptName, scriptStr, magicNo.to_s)
    end
  }
end

def writeScriptsFile(outfn, data)
  data.each_index{|x|
    scriptName = data[x][1]
    scriptStr = data[x][2]
    if scriptStr != ''
      data[x][2] = Zlib::Deflate.deflate(scriptStr)
    end
  }
  File.open( outfn, "w+") do |datafile|
    Marshal.dump(data, datafile)
  end
end