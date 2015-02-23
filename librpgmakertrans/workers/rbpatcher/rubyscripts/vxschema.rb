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
  'Actors' => {
    true => {
      'RPG::Actor' => {
        'name' => :translate
      }
    }
  },
  'Armors' => {
    true => {
      'RPG::Armor' => {
        'name' => :translate,
        'description' => :translate
      }
    }
  },
  'Classes' => {
    true => {
      'RPG::Class' => {
        'name' => :translate,
        'skill_name' => :translate
      }
    }
  },
  'CommonEvents' => {
    true => 'eventList'
  },
  'Enemies' => {
    true => {
      'RPG::Enemy' => {
        'name' => :translate,
        'note' => :translate,
      }
    }
  },
  'Items' => {
    true => {
      'RPG::Item' => {
        'name' => :translate,
        'description' => :translate,
      }
    }
  },
  'Map' => {
   'RPG::Map' => {
      'events' => {
        true => {
          'RPG::Event' => {
            'pages' => {
              true => :eventList
            }
          }
        }
      }
    }
  },
  'MapInfos' => {
    true => {
      'RPG::MapInfo' => {'name' => :translate}
    }
  },
  'Scripts' => 'ScriptFile',
  'Skills' => {
    true => {
      'RPG::Skill' => {
        'name' => :translate,
        'description' => :translate,
        'message1' => :translate,
        'message2' => :translate,
      }
    }
  },
  'States' => {
    true => {
      'RPG::State' => {
        'name' => :translate,
        'message1' => :translate,
        'message2' => :translate,
        'message3' => :translate,
        'message4' => :translate,
      }
    }
  },
  'System' => {
    'RPG::System' => {
      'game_title' => :translate,
      'elements' => {true => :translate},
      'terms' => {'RPG::System::Terms' => {true => :translate}},
    }
  },
  'Troops' => {
    true => {
      'RPG::Troop' => {
        'name' => :translate,
        'pages' => {true => :eventList},
      }
    }
  },
  'Weapons' => {
    true => {
      'RPG::Weapon' => {
        'name' => :translate,
        'description' => :translate,
      }
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
  def VXAceCommonEventMatch(context)
    if context[-1].class == Class and context[-1].name == 'RPG::CommonEvent'
      puts context.to_s
      :continue
    end
  end
  
  def standardMatch(context)
    return schemaMatch($schema, context)
  end
end

def matchAll(context)
  Matcher.module_eval{
  Matcher.instance_methods.each{|funcname|
    ret = Matcher.send(funcname, context)
    if ret != nil
      return ret
    end
  }}
end