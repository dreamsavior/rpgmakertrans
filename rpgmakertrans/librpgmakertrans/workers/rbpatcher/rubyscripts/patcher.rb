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

def convert_to_crlf(input_string)
  return input_string unless input_string.is_a?(String)
  input_string.gsub(/\r?\n/, "\r\n")
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
  # #label - we don't need this
  # def match118(code, currentCommand, mode)
  #   return code == 118 ? :patch118119 : nil
  # end
  # #jump to label - we don't need this
  # def match119(code, currentCommand, mode)
  #   return code == 119 ? :patch118119 : nil
  # end
  def match355(code, currentCommand, mode)
    return code == 355 ? :patch355 : nil
  end
  #dreamsavior: scrolling text
  def match105(code, currentCommand, mode)
    return code == 105 ? :patch105 : nil
  end  
  #variable
  def match122(code, currentCommand, mode)
    return code == 122 ? :patch122 : nil
  end  
  def match324(code, currentCommand, mode)
    return code == 324 ? :patch324 : nil
  end  
  def match320(code, currentCommand, mode)
    return code == 320 ? :patch320 : nil
  end  
  def match320(code, currentCommand, mode)
    return code == 108 ? :patch108 : nil
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
    dialogueLoc = currIndx
    windowInit = pageList[currIndx]
    currIndx += 1
    indent = windowInit.instance_variable_get(:@indent)
    currentStr = ''
    while pageList[currIndx].instance_variable_get(:@code) == 401 and currIndx < pageList.length do
      currentStr += pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip + "\n"
      currIndx += 1
    end
    

    currentStr.rstrip!
    thisContextString = contextString + dialogueLoc.to_s + '/Dialogue'
    if pageList[currIndx].instance_variable_get(:@parameters)[0] == ''
      thisContextString = thisContextString+'/noPicture'
    else
      thisContextString = thisContextString+'/hasPicture'
    end

    if pageList[currIndx].instance_variable_get(:@parameters)[3] == 2
      thisContextString = thisContextString+'/bottom'
    elsif pageList[currIndx].instance_variable_get(:@parameters)[3] == 1
      thisContextString = thisContextString+'/middle'
    else
      thisContextString = thisContextString+'/top'
    end


    translatedString = translate(currentStr, thisContextString )
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

  def patch122(currIndx, contextString, pageList, newPageList, storage)
    label_param = pageList[currIndx].instance_variable_get(:@parameters)[4]
    
    if label_param && label_param.is_a?(String)
      label = label_param.rstrip
      contextStr = contextString + '%s/VariableScript' % currIndx.to_s
      translatedLabel = translate(label, contextStr)
      pageList[currIndx].instance_variable_get(:@parameters)[4] = translatedLabel
    else
      # Handle the case where label_param is nil or not a string
    end
    
    newPageList.push(pageList[currIndx])
    currIndx += 1
    return currIndx
  end

  def patch320(currIndx, contextString, pageList, newPageList, storage)
    label = pageList[currIndx].instance_variable_get(:@parameters)[1].rstrip
    contextStr = contextString + '%s/ChangeName' % currIndx.to_s
    translatedLabel = translate(label, contextStr)
    pageList[currIndx].instance_variable_get(:@parameters)[1] = translatedLabel
    newPageList.push(pageList[currIndx])
    currIndx += 1
    return currIndx
  end

  def patch324(currIndx, contextString, pageList, newPageList, storage)
    label = pageList[currIndx].instance_variable_get(:@parameters)[1].rstrip
    contextStr = contextString + '%s/ChangeNickname' % currIndx.to_s
    translatedLabel = translate(label, contextStr)
    pageList[currIndx].instance_variable_get(:@parameters)[1] = translatedLabel
    newPageList.push(pageList[currIndx])
    currIndx += 1
    return currIndx
  end


  # def patch355(currIndx, contextString, pageList, newPageList, storage)
  #   # TODO: Check if this is also different in XP
  #   line = pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip
  #   scriptPos = currIndx
  #   script = line + "\n"
  #   indent = pageList[currIndx].instance_variable_get(:@indent)
  #   currIndx += 1
  #   while pageList[currIndx].instance_variable_get(:@code) == 655 and currIndx < pageList.length do
  #     line = pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip
  #     script += line + "\n"
  #     currIndx += 1
  #   end
  #   translatedscript = translateInlineScript(script, contextString + '%s/InlineScript' % scriptPos.to_s).lines
  #   code = 355
  #   translatedscript.each { |line|
  #     line.chomp!
  #     newPageList.push(RPG::EventCommand.new(code, indent, [line]))
  #     code = 655
  #   }
  #   return currIndx
  # end

  #dreamsavior: Scrolling text handler
  #Scrolling text is any length
  def patch105(currIndx, contextString, pageList, newPageList, storage)
    dialogueLoc = currIndx
    windowInit = pageList[currIndx]
    currIndx += 1
    indent = windowInit.instance_variable_get(:@indent)
    currentStr = ''
    while pageList[currIndx].instance_variable_get(:@code) == 405 and currIndx < pageList.length do
      currentStr += pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip + "\n"
      currIndx += 1
    end
    currentStr.rstrip!
    translatedString = translate(currentStr, contextString + '%s/ScrollingText' % dialogueLoc.to_s)
    if translatedString == ''
      translatedString = ' '
    end
    lineCount = 0
    newPageList.push(windowInit)
    translatedString.split("\n").each {|line|
      if lineCount == 0
        newPageList.push(windowInit)
      end
      lineCount += 1
      newPageList.push(RPG::EventCommand.new(405, indent, [line]))
    }
    return currIndx
  end

  def patch108(currIndx, contextString, pageList, newPageList, storage)
    dialogueLoc = currIndx
    indent = pageList[currIndx].instance_variable_get(:@indent)
    currentStr = ''
    firstLine = pageList[currIndx].instance_variable_get(:@parameters)[0]
    if firstLine.class == String
      currentStr += firstLine.rstrip + "\n"
    end
    currIndx += 1
    while pageList[currIndx].instance_variable_get(:@code) == 408 and currIndx < pageList.length do
      currentStr += pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip + "\n"
      currIndx += 1
    end
    currentStr.rstrip!
    translatedString = translate(currentStr, contextString + '%s/Comment' % dialogueLoc.to_s)
    if translatedString == ''
      translatedString = ' '
    end
    lineCount = 6
    translatedString.split("\n").each {|line|
      if lineCount == 6
        lineCount = 1
        newPageList.push(RPG::EventCommand.new(108, indent, [line]))
      else
        lineCount += 1
        newPageList.push(RPG::EventCommand.new(408, indent, [line]))
      end
    }
    return currIndx
  end

  def patch355(currIndx, contextString, pageList, newPageList, storage)
    dialogueLoc = currIndx
    indent = pageList[currIndx].instance_variable_get(:@indent)
    currentStr = ''
    firstLine = pageList[currIndx].instance_variable_get(:@parameters)[0]
    if firstLine.class == String
      currentStr += firstLine.rstrip + "\n"
    end
    currIndx += 1
    while pageList[currIndx].instance_variable_get(:@code) == 655 and currIndx < pageList.length do
      currentStr += pageList[currIndx].instance_variable_get(:@parameters)[0].rstrip + "\n"
      currIndx += 1
    end
    currentStr.rstrip!
    translatedString = translate(currentStr, contextString + '%s/EventScript' % dialogueLoc.to_s)
    if translatedString == ''
      translatedString = ' '
    end
    lineCount = 27
    translatedString.split("\n").each {|line|
      if lineCount == 27
        lineCount = 1
        newPageList.push(RPG::EventCommand.new(355, indent, [line]))
      else
        lineCount += 1
        newPageList.push(RPG::EventCommand.new(655, indent, [line]))
      end
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

$priority = [:@name, :@display_name, :@description, :@message1, :@message2, :@message3, :@message4, :@note]
  
def patch(data, context, mode)
  
  matchResult = matchAll(data, context)
  
  case matchResult
  when :translate
    translation = translate(data, contextStr(context))
    #ensure translation is CRLF format
    return convert_to_crlf(translation)
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