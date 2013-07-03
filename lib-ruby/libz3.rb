Z3::Instance = Z3.new

class Z3::Z3Pointer
  def suggest_value(v)
    c = self == v
    c.enable
    Z3::Instance.solve
    c.disable
  end

  alias plain_enable enable

  def enable(preference=nil)
    plain_enable
    Z3::Instance.solve
  end
end

class Numeric
  def for_constraint(name)
    Z3::Instance.make_real_variable(self.to_f)
  end
end

class Fixnum
  def for_constraint(name)
    Z3::Instance.make_int_variable(self)
  end
end

class TrueClass
  def for_constraint(name)
    Z3::Instance.make_bool_variable(self)
  end
end

class FalseClass
  def for_constraint(name)
    Z3::Instance.make_bool_variable(self)
  end
end

class Array
  def alldifferent?
    asts = map do |element|
      case element
      when Fixnum
        Z3::Instance.make_int_variable(element)
      when Float
        Z3::Instance.make_real_variable(element)
      when true, false
        Z3::Instance.make_bool_variable(element)
      when Z3::Z3Pointer
        element
      else
        raise "Cannot solve alldifferent? on this array (no Z3 interpretation for #{element.inspect})"
      end
    end
    asts.pop.alldifferent(*asts)
  end
end

puts "Z3 constraint solver loaded."
