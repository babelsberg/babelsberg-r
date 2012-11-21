# libprime
class Fixnum
  def prime?
    if self <2
      return false
    elsif self < 4
      return true
    elsif self % 2 == 0
      return false
    elsif self < 9
      return true
    elsif self % 3 == 0
      return false
    else
      r = (self ** 0.5).floor
      f = 5
      while f < r do
        f += 6
        if self % f == 0
          return false
        end
        if self % (f + 2) == 0
          return false
        end
      end
      return true
    end
  end
end

class Prime
  def initialize(start = nil)
    @last_prime = start
  end

  def succ
    if @last_prime.nil?
      @last_prime = 2
      return 2
    else
      i = @last_prime + 1
      i += 1 if i % 2 == 0
      while not i.prime?
        i += 2
      end
      @last_prime = i
      return i
    end
  end
  alias next succ

  def each
    loop do
      yield succ
    end
  end
end
