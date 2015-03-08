module Graphics

  class << self
    
    attr_accessor :frame_count
    attr_reader :brightness, :frame_rate
    
    def brightness=(int)
      @brightness = [[255, int].min, 0].max
      @draw_color.alpha = 255 - @brightness
    end
    
    def frame_rate=(int)
      @frame_rate = [[120, int].min, 10].max
      #reform_window(width, height, fullscreen?, 1.0 / @frame_rate * 1000)
    end
  end
  
  @frame_rate = 60
  @brightness = 255
  @frame_count = 0
  @frozen = false
  @draw_color = Color.new
  @draw_color.alpha = 0

  module_function
  
  def update
    @current = nil
    sleep 1.0 / frame_rate
    @frame_count += 1
    @latest = @current if !@frozen
  end
  
  def wait(duration)
    duration.times { update }
  end
  
  def fadeout(duration)
    Thread.new {
      rate = @brightness / duration.to_f
      until @brightness <= 0
        self.brightness -= rate
        sleep 1.0 / frame_rate
      end
      self.brightness = 0
    }
  end
  
  def fadein(duration)
    Thread.new { 
      rate = 255 / duration.to_f
      until @brightness >= 255
        self.brightness += rate
        sleep 1.0 / frame_rate
      end
      self.brightness = 255
    }
  end
  
  def freeze
    @frozen = true
  end
  
  def transition(duration = 10, filename = "", vague = 40)
    @frozen = false
  end
  
  def snap_to_bitmap
  end
  
  def frame_reset
  end
  
  def width
  end
  
  def height
  end
  
  def resize_screen(w, h)
  end
  
  def play_movie(filename)
  end  
end
