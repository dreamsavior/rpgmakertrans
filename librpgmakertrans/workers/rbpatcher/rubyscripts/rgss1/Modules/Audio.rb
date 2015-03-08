module Audio

  module_function
  
  def setup_midi
  end
  
  def bgm_play(filename, volume = 100, pitch = 100)
    bgm_stop
    @bgm = nil
    @bgm_volume = volume / 100.0
  end
  
  def bgm_stop
    @bgm.stop if @bgm
  end
  
  def bgm_fade(time)
    return unless @bgm
    Thread.new {
      incs = @bgm_volume / time
      until @bgm_volume <= 0
        @bgm_volume -= incs
        @bgm.volume -= incs
        sleep 0.01
      end
      bgm_stop
    }
  end
  
  def bgs_play(filename, volume = 100, pitch = 100)
    bgs_stop
    @bgs = nil
    @bgs_volume = volume / 100.0
  end
  
  def bgs_stop
    @bgs.stop if @bgs
  end
  
  def bgs_fade(time)
    return unless @bgs
    Thread.new {
      incs = @bgs_volume / time
      until @bgs_volume <= 0
        @bgs_volume -= incs
        @bgs.volume -= incs
        sleep 0.01
      end
      bgs_stop
    }
  end
  
  def me_play(filename, volume = 100, pitch = 100)
    me_stop
    @bgm.pause if @bgm
    @me = nil
    @me_volume = volume / 100.0
  end
  
  def me_stop
    @me.stop if @me
    @bgm.resume if @bgm && @bgm.paused?
  end
  
  def me_fade(time)
    return unless @me
    Thread.new {
      incs = @me_volume / time
      until @me_volume <= 0
        @me_volume -= incs
        @me.volume -= incs
        sleep 0.01
      end
      me_stop
    }
  end
  
  def se_play(filename, volume = 100, pitch = 100)
    @se = [] if @se == nil
    @se << nil
  end
  
  def se_stop
    @se.each {|a| a.stop }
    @se.clear
  end
end