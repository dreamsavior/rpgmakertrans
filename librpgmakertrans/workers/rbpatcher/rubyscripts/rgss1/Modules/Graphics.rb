module Graphics

  class << self
    
    attr_accessor :frame_count
    attr_reader :frame_rate
    
    def frame_rate=(int)
      @frame_rate = [[120, int].min, 10].max
    end
  end
  
  @frame_rate = 40
  @frame_count = 0
  @frozen = false

  module_function
  
  def update
  end
  
  def transition(duration = 10, filename = "", vague = 40)
  end
  
  def frame_reset
  end
  
  def resize_screen(w, h)
  end
end