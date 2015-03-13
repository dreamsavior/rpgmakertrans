class Window
  
  attr_reader :windowskin, :contents, :opacity, :back_opacity, :contents_opacity
  attr_reader :width, :height, :cursor_rect
  attr_accessor :x, :y, :z, :ox, :oy, :active, :visible, :pause, :viewport, :openness
  
  def initialize(viewport = nil)
    @viewport = viewport
    @x, @y, @z, @ox, @oy = 0, 0, 0, 0, 0
    @active = false
    @visible = true
    @pause = false
    @opacity = 255
    @back_opacity = 255
    @contents_opacity = 255
    @openness = 255
    @sprites = {
      :contents => Sprite.new,
      :back => Sprite.new,
      :border => Sprite.new,
      :arrow_left => Sprite.new,
      :arrow_up => Sprite.new,
      :arrow_right => Sprite.new,
      :arrow_down => Sprite.new,
      :pause_one => Sprite.new,
      :pause_two => Sprite.new,
      :pause_three => Sprite.new,
      :pause_four => Sprite.new,
      :cursor => Sprite.new
    }
    @sprites.values.each {|a| Graphics.remove_sprite(a) }
    Graphics.add_sprite(self)
  end
  
  def windowskin=(bit)
    @windowskin = bit
  end
  
  def contents=(bit)
    @contents = bit
  end
  
  def stretch=(bool)
    @stretch = bool
    self.windowskin = @windowskin
  end
  
  def opacity=(int)
    @opacity = int
  end
  
  def back_opacity=(int)
    @back_opacity = int
    @sprites[:back].opacity = int
  end
  
  def contents_opacity=(int)
    @contents_opacity = int
    @sprites[:contents].opacity = int
  end
  
  def cursor_rect=(rect)
    @cursor_rect = rect
    setup_cursor
  end
  
  def width=(int)
    @width = int
    setup_border
  end
  
  def height=(int)
    @height = int
    setup_border
  end
  
  def setup_background_overlay
  end
  
  def setup_arrows
  end
  
  def setup_pauses
  end
  
  def setup_border
  end
  
  def setup_cursor
  end
end
