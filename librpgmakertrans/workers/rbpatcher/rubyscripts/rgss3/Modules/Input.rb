module Input

  @previous_keys, @keys = [], []
  
  module_function
  
  def update
    @keys = nil
  end
  
  def trigger?(key)
    if key.is_a?(Symbol)
      key = const_get(key)
    end
    return key.any? {|a| @keys.include?(a) }
  end
  
  def press?(key)
    if key.is_a?(Symbol)
      key = const_get(key)
    end
    return nil
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
