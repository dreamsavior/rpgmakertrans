# unmarshshave.rb
# ***************
#
# :author: Aleph Fell <habisain@gmail.com>
# :copyright: 2012-2014
# :license: GNU Public License version 3
#
# A script containing extra stuff necessary to unmarshal a save
#
items = ['characters',
'frame_count',
'last_bgm',
'last_bgs',
'game_system',
'game_message',
'game_switches',
'game_variables',
'game_self_switches',
'game_actors',
'game_party',
'game_troop',
'game_map',
'game_player', ]
require 'rmvx/rgss2'
require 'yaml'

class Game_System
  attr_accessor :timer
  attr_accessor :timer_working
  attr_accessor :save_disabled
  attr_accessor :menu_disabled
  attr_accessor :encounter_disabled
  attr_accessor :save_count
  attr_accessor :version_id
  def initialize
    @timer = 0
    @timer_working = false
    @save_disabled = false
    @menu_disabled = false
    @encounter_disabled = false
    @save_count = 0
    @version_id = 0
  end
end

class Game_Message
  MAX_LINE = 4
  attr_accessor :texts
  attr_accessor :face_name
  attr_accessor :face_index
  attr_accessor :background
  attr_accessor :position
  attr_accessor :main_proc
  attr_accessor :choice_proc
  attr_accessor :choice_start
  attr_accessor :choice_max
  attr_accessor :choice_cancel_type
  attr_accessor :num_input_variable_id
  attr_accessor :num_input_digits_max
  attr_accessor :visible
  def initialize
    clear
    @visible = false
  end
  def clear
    @texts = []
    @face_name = ""
    @face_index = 0
    @background = 0
    @position = 2
    @main_proc = nil
    @choice_start = 99
    @choice_max = 0
    @choice_cancel_type = 0
    @choice_proc = nil
    @num_input_variable_id = 0
    @num_input_digits_max = 0
  end
end

class Game_Switches
  def initialize
    @data = []
  end
end

class Game_Variables
  def initialize
    @data = []
  end
end

class Game_SelfSwitches
  def initialize
    @data = {}
  end
end

class Game_Actors
  def initialize
    @data = []
  end
end

class Game_Battler
  attr_reader   :battler_name
  attr_reader   :battler_hue
  attr_reader   :hp
  attr_reader   :mp
  attr_reader   :action
  attr_accessor :hidden
  attr_accessor :immortal
  attr_accessor :animation_id
  attr_accessor :animation_mirror
  attr_accessor :white_flash
  attr_accessor :blink
  attr_accessor :collapse
  attr_reader   :skipped
  attr_reader   :missed
  attr_reader   :evaded
  attr_reader   :critical
  attr_reader   :absorbed
  attr_reader   :hp_damage
  attr_reader   :mp_damage
  def initialize
    @battler_name = ""
    @battler_hue = 0
    @hp = 0
    @mp = 0
    @action = Game_BattleAction.new(self)
    @states = []
    @state_turns = {}
    @hidden = false
    @immortal = false
    clear_extra_values
    clear_sprite_effects
    clear_action_results
  end
end
class Game_Actor < Game_Battler
  attr_reader   :name
  attr_reader   :character_name
  attr_reader   :character_index
  attr_reader   :face_name
  attr_reader   :face_index
  attr_reader   :class_id
  attr_reader   :weapon_id
  attr_reader   :armor1_id
  attr_reader   :armor2_id
  attr_reader   :armor3_id
  attr_reader   :armor4_id
  attr_reader   :level
  attr_reader   :exp
  attr_accessor :last_skill_id
  def initialize(actor_id)
    super()
    setup(actor_id)
    @last_skill_id = 0
  end
  def setup(actor_id)
    actor = $data_actors[actor_id]
    @actor_id = actor_id
    @name = actor.name
    @character_name = actor.character_name
    @character_index = actor.character_index
    @face_name = actor.face_name
    @face_index = actor.face_index
    @class_id = actor.class_id
    @weapon_id = actor.weapon_id
    @armor1_id = actor.armor1_id
    @armor2_id = actor.armor2_id
    @armor3_id = actor.armor3_id
    @armor4_id = actor.armor4_id
    @level = actor.initial_level
    @exp_list = Array.new(101)
    make_exp_list
    @exp = @exp_list[@level]
    @skills = []
    for i in self.class.learnings
      learn_skill(i.skill_id) if i.level <= @level
    end
    clear_extra_values
    recover_all
  end
end
class Game_Character
  attr_reader   :id
  attr_reader   :x
  attr_reader   :y
  attr_reader   :real_x
  attr_reader   :real_y
  attr_reader   :tile_id
  attr_reader   :character_name
  attr_reader   :character_index
  attr_reader   :opacity
  attr_reader   :blend_type
  attr_reader   :direction
  attr_reader   :pattern
  attr_reader   :move_route_forcing
  attr_reader   :priority_type
  attr_reader   :through
  attr_reader   :bush_depth
  attr_accessor :animation_id
  attr_accessor :balloon_id
  attr_accessor :transparent
  MOVE_SPEED_LIST = [0, 3, 6, 12, 24, 40, 64, 88]
  def initialize
    @id = 0
    @x = 0
    @y = 0
    @real_x = 0
    @real_y = 0
    @tile_id = 0
    @character_name = ""
    @character_index = 0
    @opacity = 255
    @blend_type = 0
    @direction = 2
    @pattern = 1
    @move_route_forcing = false
    @priority_type = 1
    @through = false
    @bush_depth = 0
    @animation_id = 0
    @balloon_id = 0
    @transparent = false
    @original_direction = 2
    @original_pattern = 1
    @move_type = 0
    @move_speed = 4
    @move_frequency = 6
    @move_route = nil
    @move_route_index = 0
    @original_move_route = nil
    @original_move_route_index = 0
    @walk_anime = true
    @step_anime = false
    @direction_fix = false
    @anime_count = 0
    @stop_count = 0
    @jump_count = 0
    @jump_peak = 0
    @wait_count = 0
    @locked = false
    @prelock_direction = 0
    @move_failed = false
  end
end
class Game_Event < Game_Character
  attr_reader   :trigger
  attr_reader   :list
  attr_reader   :starting
  def initialize(map_id, event)
    super()
    @map_id = map_id
    @event = event
    @id = @event.id
    @erased = false
    @starting = false
    @through = true
    moveto(@event.x, @event.y)
    refresh
  end
end
class Game_Player < Game_Character
  CENTER_X = (640 / 2 - 16) * 8
  CENTER_Y = (480 / 2 - 16) * 8
  attr_reader   :vehicle_type
  def initialize
    super
    @vehicle_type = -1
    @vehicle_getting_on = false
    @vehicle_getting_off = false
    @transferring = false
    @new_map_id = 0
    @new_x = 0
    @new_y = 0
    @new_direction = 0
    @walking_bgm = nil
  end
end
class Game_CommonEvent
  def initialize(common_event_id)
    @common_event_id = common_event_id
    @interpreter = nil
    refresh
  end
end
class Game_Vehicle < Game_Character
  MAX_ALTITUDE = 32
  attr_reader   :type
  attr_reader   :altitude
  attr_reader   :driving
  def initialize(type)
    super()
    @type = type
    @altitude = 0
    @driving = false
    @direction = 4
    @walk_anime = false
    @step_anime = false
    load_system_settings
  end
  def load_system_settings
    case @type
    when 0;  sys_vehicle = $data_system.boat
    when 1;  sys_vehicle = $data_system.ship
    when 2;  sys_vehicle = $data_system.airship
    else;    sys_vehicle = nil
    end
    if sys_vehicle != nil
      @character_name = sys_vehicle.character_name
      @character_index = sys_vehicle.character_index
      @bgm = sys_vehicle.bgm
      @map_id = sys_vehicle.start_map_id
      @x = sys_vehicle.start_x
      @y = sys_vehicle.start_y
    end
  end
end
class Game_BattleAction
  attr_accessor :battler
  attr_accessor :speed
  attr_accessor :kind
  attr_accessor :basic
  attr_accessor :skill_id
  attr_accessor :item_id
  attr_accessor :target_index
  attr_accessor :forcing
  attr_accessor :value
  def initialize(battler)
    @battler = battler
    clear
  end
  def clear
    @speed = 0
    @kind = 0
    @basic = -1
    @skill_id = 0
    @item_id = 0
    @target_index = -1
    @forcing = false
    @value = 0
  end
end
class Game_Unit
  def initialize
  end
end
class Game_Party < Game_Unit
  MAX_MEMBERS = 4
  attr_reader   :gold
  attr_reader   :steps
  attr_accessor :last_item_id
  attr_accessor :last_actor_index
  attr_accessor :last_target_index
  def initialize
    super
    @gold = 0
    @steps = 0
    @last_item_id = 0
    @last_actor_index = 0
    @last_target_index = 0
    @actors = []
    @items = {}
    @weapons = {}
    @armors = {}
  end
end
class Game_Troop < Game_Unit
  attr_reader   :screen
  attr_reader   :interpreter
  attr_reader   :event_flags
  attr_reader   :turn_count
  attr_reader   :name_counts
  attr_accessor :can_escape
  attr_accessor :can_lose
  attr_accessor :preemptive
  attr_accessor :surprise
  attr_accessor :turn_ending
  attr_accessor :forcing_battler
  def initialize
    super
    @screen = Game_Screen.new
    @interpreter = Game_Interpreter.new
    @event_flags = {}
    @enemies = []
    clear
  end
end
class Game_Interpreter
  def initialize(depth = 0, main = false)
    @depth = depth
    @main = main
    if @depth > 100
      print("コモンイベントの呼び出しが上限を超えました。")
      exit
    end
    clear
  end
end
class Game_Screen
  attr_reader   :brightness
  attr_reader   :tone
  attr_reader   :flash_color
  attr_reader   :shake
  attr_reader   :pictures
  attr_reader   :weather_type
  attr_reader   :weather_max
  def initialize
    clear
  end
  def clear
    @brightness = 255
    @fadeout_duration = 0
    @fadein_duration = 0
    @tone = Tone.new(0, 0, 0, 0)
    @tone_target = Tone.new(0, 0, 0, 0)
    @tone_duration = 0
    @flash_color = Color.new(0, 0, 0, 0)
    @flash_duration = 0
    @shake_power = 0
    @shake_speed = 0
    @shake_duration = 0
    @shake_direction = 1
    @shake = 0
    @pictures = []
    for i in 0..20
      @pictures.push(Game_Picture.new(i))
    end
    @weather_type = 0
    @weather_max = 0.0
    @weather_type_target = 0
    @weather_max_target = 0.0
    @weather_duration = 0
  end
end
class Game_Picture
  attr_reader   :number
  attr_reader   :name
  attr_reader   :origin
  attr_reader   :x
  attr_reader   :y
  attr_reader   :zoom_x
  attr_reader   :zoom_y
  attr_reader   :opacity
  attr_reader   :blend_type
  attr_reader   :tone
  attr_reader   :angle
  def initialize(number)
    @number = number
    @name = ""
    @origin = 0
    @x = 0.0
    @y = 0.0
    @zoom_x = 100.0
    @zoom_y = 100.0
    @opacity = 255.0
    @blend_type = 1
    @duration = 0
    @target_x = @x
    @target_y = @y
    @target_zoom_x = @zoom_x
    @target_zoom_y = @zoom_y
    @target_opacity = @opacity
    @tone = Tone.new(0, 0, 0, 0)
    @tone_target = Tone.new(0, 0, 0, 0)
    @tone_duration = 0
    @angle = 0
    @rotate_speed = 0
  end
end
class Game_Map
  attr_reader   :screen
  attr_reader   :interpreter
  attr_reader   :display_x
  attr_reader   :display_y
  attr_reader   :parallax_name
  attr_reader   :passages
  attr_reader   :events
  attr_reader   :vehicles
  attr_accessor :need_refresh
  def initialize
    @screen = Game_Screen.new
    @interpreter = Game_Interpreter.new(0, true)
    @map_id = 0
    @display_x = 0
    @display_y = 0
    create_vehicles
  end
  def setup(map_id)
    @map_id = map_id
    @map = load_data(sprintf("Data/Map%03d.rvdata", @map_id))
    @display_x = 0
    @display_y = 0
    @passages = $data_system.passages
    referesh_vehicles
    setup_events
    setup_scroll
    setup_parallax
    @need_refresh = false
  end
  def create_vehicles
    @vehicles = []
    @vehicles[0] = Game_Vehicle.new(0)
    @vehicles[1] = Game_Vehicle.new(1)
    @vehicles[2] = Game_Vehicle.new(2)
  end
end
output = {}
File.open( 'Save1.rvdata', "r+" ) do |datafile|
    items.each{|x| output[x] = Marshal.load(datafile)}
end
items.each{|x|
  puts x
  puts YAML::dump(output[x])
}
