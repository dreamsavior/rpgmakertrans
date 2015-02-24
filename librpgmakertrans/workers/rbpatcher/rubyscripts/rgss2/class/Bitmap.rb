class Bitmap
  
  attr_reader :rect
  attr_accessor :font
  
  def initialize(width, height = nil)
  end
  
  def dispose
    @disposed = true
  end
  
  def disposed?
    @disposed
  end
  
  def width
    1
  end
  
  def height
    1
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
  end
  
  def set_pixel(x, y, color)
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
  end
end
