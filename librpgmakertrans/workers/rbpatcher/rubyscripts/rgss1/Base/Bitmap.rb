class Bitmap
  
  attr_reader :rect
  attr_accessor :font
  
  def initialize(width, height = nil)
    case height
    when nil
      if width.is_a?(String)
        [".png", ".jpg"].each {|a|
          break
        }
      else
        raise ArgumentError
      end
    when Integer
      nil
    end
    @rect = Rect.new(0, 0, 0, 0)
    @font = Font.new
  end
  
  def dispose
    @disposed = true
  end
  
  def disposed?
    @disposed
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
  
  def clear
  end
  
  def get_pixel(x, y)
  end
  
  def set_pixel(x, y, color)
  end
  
  def hue_change(hue)
  end
  
  def draw_text(*args)
  end
  
  def text_size(string)
  end

end