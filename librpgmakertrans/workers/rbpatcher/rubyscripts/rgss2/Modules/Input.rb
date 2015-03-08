module Input

  @keys = []
  
  DOWN = []
  UP = []
  LEFT = []
  RIGHT = []
  A = []
  B = []
  C = []
  X = []
  Y = []
  Z = []
  L = []
  R = []
  SHIFT = []
  CTRL = []
  ALT = []
  F5 = []
  F6 = []
  F7 = []
  F8 = []
  F9 = []

  module_function
  
  def update
  end
  
  def trigger?(key)
    return key.any? {|a| @keys.include?(a) }
  end
  
  def press?(key)
  end
  
  def repeat?(key)
  end
  
  def dir4
    return 2 if press?(:DOWN)
    return 4 if press?(:LEFT)
    return 6 if press?(:RIGHT)
    return 8 if press?(:UP)
    return 0
  end
  
  def dir8
    return 1 if press?(:DOWN) && press?(:LEFT)
    return 3 if press?(:DOWN) && press?(:RIGHT)
    return 7 if press?(:UP) && press?(:LEFT)
    return 9 if press?(:UP) && press?(:RIGHT)
    return dir4
  end
end
