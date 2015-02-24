class Font
  
  class << self
    
    attr_accessor :default_name, :default_size, :default_bold
    attr_accessor :default_italic, :default_shadow
    attr_accessor :default_color
    
    def exist?(name)
      return false
    end
  end
  
  self.default_name = ["Verdana", "Arial", "Courier New"]
  self.default_size = 24
  self.default_bold = false
  self.default_italic = false
  self.default_shadow = false
  self.default_color = Color.new(255, 255, 255, 255)
  
  attr_accessor :name, :size, :bold, :italic, :shadow, :color
  
  def initialize(name = Font.default_name, size = Font.default_size)
    @name = name.dup
    @size = size
    @bold = Font.default_bold
    @italic = Font.default_italic
    @shadow = Font.default_shadow
    @color = Font.default_color.dup
  end
end
