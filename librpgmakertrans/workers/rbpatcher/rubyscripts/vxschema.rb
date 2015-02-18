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
        'name' => true
      }
    }
  },
  'Armors' => {
    true => {
      'RPG::Armor' => {
        'name' => true,
        'description' => true
      }
    }
  },
  'Classes' => {
    true => {
      'RPG::Class' => {
        'name' => true,
        'skill_name' => true
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
        'name' => true,
        'note' => true,
      }
    }
  },
  'Items' => {
    true => {
      'RPG::Item' => {
        'name' => true,
        'description' => true,
      }
    }
  },
  'Map' => {
   'RPG::Map' => {
      'events' => {
        true => {
          'RPG::Event' => {
            'pages' => {
              true => 'eventList'
            }
          }
        }
      }
    }
  },
  'MapInfos' => {
    true => {
      'RPG::MapInfo' => {'name' => true}
    }
  },
  'Scripts' => 'ScriptFile',
  'Skills' => {
    true => {
      'RPG::Skill' => {
        'name' => true,
        'description' => true,
        'message1' => true,
        'message2' => true,
      }
    }
  },
  'States' => {
    true => {
      'RPG::State' => {
        'name' => true,
        'message1' => true,
        'message2' => true,
        'message3' => true,
        'message4' => true,
      }
    }
  },
  'System' => {
    'RPG::System' => {
      'game_title' => true,
      'elements' => {true => true},
      'terms' => {'RPG::System::Terms' => {true => true}},
    }
  },
  'Troops' => {
    true => {
      'RPG::Troop' => {
        'name' => true,
      'pages' => {true => 'eventList'},
      }
    }
  },
  'Weapons' => {
    true => {
      'RPG::Weapon' => {
        'name' => true,
        'description' => true,
      }
    }
  },

}

module Matcher
  extend self
  
  def matchWeapon(context)
    if context[0].class == String and context[0].include? 'Weapons'
      if context[2] != nil and context[2].name.include? 'Weapon'
        if context[3].class == String and (context[3].include? 'name' or context[3].include? 'description')
          return :translate
        end
      end 
    end
  end
end

def matchAll(context)
  Matcher.instance_methods.each{|funcname|
    ret = Matcher.send(funcname, context)
    if ret != nil
      return ret
    end
  }
end