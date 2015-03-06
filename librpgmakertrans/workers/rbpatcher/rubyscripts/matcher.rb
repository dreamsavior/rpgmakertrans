# vxschema.rb
# ***********
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2015
# :license: GNU Public License version 3
#
# Holds the schema used to translate Ruby
#

module Matcher
  extend self
  
  def matchVXTerms(data, context)
    # Matches system terms in VX
    if data.class == String and context[-2].class == Class and context[-2].name == 'RPG::System::Terms'
      return :translate
    end
  end
  
  def matchVXAceTerms(data, context)
    # Matches system terms in VX Ace
    if data.class == String and context[-3].class == Class and context[-3].name == 'RPG::System::Terms'
      return :translate
    end
  end
  
  def matchElements(data, context)
    # Match elements
    if data.class == String and ['elements', 'skill_types', 'weapon_types', 'armor_types', ].include? context[-2]
      return :translate
    end
  end
  
  def matchName(data, context)
    # This matches names, but *not* event names as these don't have to be translated.
    if data.class == String and context[-1] == 'name' and not (context[-2].class == Class and context[-2].name == 'RPG::Event')
      return :translate
    end
  end
  
  def matchStandardStrings(data, context)
    # Matches the 'standard' strings in all RPGMaker objects
    if data.class == String and context[-1].class == String and ['display_name', 'description', 'message1', 'message2', 'message3', 'message4', 'skill_name', 'game_title', 'currency_unit'].include? context[-1]
      return :translate
    end
  end
  
  def killClasses(data, context)
    # Blocks descent into classes that are of no value to translation and give false positives or computationally expensive
    if context[-1].class == Class and ['Table', 'Color', 'RPG::MapInfo', 'RPG::Tileset', 'RPG::BGS', 'RPG::BGM', 'RPG::SE', 'RPG::ME', 'RPG::Animation'].include? context[-1].name
      return :abort
    end
  end
  
  def mapTroopEvent(data, context)
    # Matches troop events
    if context[-1].class == Class and context[-1].name == 'RPG::Troop::Page'
      return :eventList
    end
  end
  
  def mapMatch(data, context)
    # Matches map events
    if context[-1].class == Class and context[-1].name == 'RPG::Event::Page'
      return :eventList
    end
  end
  
  def commonEventMatch(data, context)
    # Matches common events
    if context[-1].class == Class and context[-1].name == 'RPG::CommonEvent'
      return :eventList
    end
  end
  
  def systemMapVersion(data, context)
    # Match the system map version so it can be replaced with a new random integer
      if context[-2].class == Class and context[-2].name == 'RPG::System' and context[-1] == 'version_id'
        return :randint
      end
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
  return :continue
end