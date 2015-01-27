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
      RPG::Actor => {
        'name' => true
      }
    }
  },
  'Armors' => {
    true => {
      RPG::Armor => {
        'name' => true,
        'description' => true
      }
    }
  },
  'Classes' => {
    true => {
      RPG::Class => {
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
      RPG::Enemy => {
        'name' => true,
        'note' => true,
      }
    }
  },
  'Items' => {
    true => {
      RPG::Item => {
        'name' => true,
        'description' => true,
      }
    }
  },
  'Map' => {
    RPG::Map => {
      'events' => {
        true => {
          RPG::Event => {
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
      RPG::MapInfo => {'name' => true}
    }
  },
  'Scripts' => 'ScriptFile',
  'Skills' => {
    true => {
      RPG::Skill => {
        'name' => true,
        'description' => true,
        'message1' => true,
        'message2' => true,
      }
    }
  },
  'States' => {
    true => {
      RPG::State => {
        'name' => true,
        'message1' => true,
        'message2' => true,
        'message3' => true,
        'message4' => true,
      }
    }
  },
  'System' => {
    RPG::System => {
      'game_title' => true,
      'elements' => {true => true},
      'terms' => {RPG::System::Terms => {true => true}},
    }
  },
  'Troops' => {
    true => {
      RPG::Troop => {
        'name' => true,
      'pages' => {true => 'eventList'},
      }
    }
  },
  'Weapons' => {
    true => {
      RPG::Weapon => {
        'name' => true,
        'description' => true,
      }
    }
  },

}
