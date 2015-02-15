class Bitmap
  
  attr_reader :rect
  attr_accessor :font
  
  def initialize(width, height)
    @rect = Rect.new(0, 0, 0, 0)
    @font = Font.new
  end
  
  def dispose
  end
  
  def disposed?
    false
  end
  
  def width
    0
  end
  
  def height
    0
  end
  
  def blt(x, y, src_bitmap, src_rect, opacity = 255)
  end
  
  def stretch_blt(dest_rect, src_bitmap, src_rect, opacity = 255)
  end
  
  def fill_rect(*args)
  end
  
  def gradient_fill_rect(*args)
  end
  
  def clear
  end
  
  def clear_rect(*args)
  end
  
  def get_pixel(x, y)
    Color.new(0,0,0,0)
  end
  
  def set_pixel(x, y, color)
    fill_rect(x, y, 1, 1, color)
  end
  
  def hue_change(hue)
  end
  
  def blur
  end
  
  def radial_blur(angle, division)
  end
  
  def draw_text(*args)
  end
  
  def text_size(string)
    Rect.new(0, 0, 0, 0)
  end
end
