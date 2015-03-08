class Rect
  
  attr_accessor :x, :y, :width, :height
  
  def initialize(x, y, width, height)
    set(x, y, width, height)
  end
  
  def set(x, y, width, height)
    @x, @y, @width, @height = x, y, width, height
  end
end
