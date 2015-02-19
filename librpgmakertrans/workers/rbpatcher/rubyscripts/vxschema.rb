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
    true => 'eventList'#{
      #RPG::CommonEvent => 'script'
    #}
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

module Matcher
  extend self
  
  def matchEvents(context)

  end
  
  def matchWeapon(context)
    if context[0].class == String and context[0].include? 'Weapons' \
       and context[2] != nil and context[2].name.include? 'Weapon' \
       and context[3].class == String and (context[3].include? 'name' or context[3].include? 'description')
        return :translate
    end
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