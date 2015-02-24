# vxschema.rb
# ***********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2015
# :license: GNU Public License version 3
#
# Holds the schema used to translate Ruby
#

$schema = {
  'System' => {
    'RPG::System' => {
      'elements' => {true => :translate},
      'terms' => {'RPG::System::Terms' => {true => :translate}},
    }
  },
}

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
    elsif x.class == Class and schemaLevel.member?(x.name)
      schemaLevel = schemaLevel[x.name]
    elsif schemaLevel.member?(true)
      schemaLevel = schemaLevel[true]
    else
      return :continue # Failure, do not iterate down here.
    end
  }
  if not [:translate, :eventList].include? schemaLevel
    schemaLevel = :continue
  end
  return schemaLevel
end

module Matcher
  extend self
  
  def matchStandardNames(data, context)
    if data.class == String and context[-1].class == String and ['name', 'description', 'message1', 'message2', 'message3', 'message3', 'skill_name', 'game_title'].include? context[-1]
      return :translate
    end
  end
  
  def killClasses(data, context)
    if context[-1].class == Class and ['Table', 'Color', 'RPG::BGS', 'RPG::BGM', 'RPG::SE', 'RPG::ME', 'RPG::Animation'].include? context[-1].name
      return :abort
    end
  end
  
  def mapTroopEvent(data, context)
    if context[-1].class == Class and context[-1].name == 'RPG::Troop::Page'
      return :eventList
    end
  end
  
  def mapMatch(data, context)
    if context[-1].class == Class and context[-1].name == 'RPG::Event::Page'
      return :eventList
    end
  end
  
  def commonEventMatch(data, context)
    if context[-1].class == Class and context[-1].name == 'RPG::CommonEvent'
      return :eventList
    end
  end
  
  def standardMatch(data, context)
    return schemaMatch($schema, context)
  end
end

def matchAll(data, context)
  Matcher.module_eval{
  Matcher.instance_methods.each{|funcname|
    ret = Matcher.send(funcname, data, context)
    if ret != nil
      return ret
    end
  }}
end