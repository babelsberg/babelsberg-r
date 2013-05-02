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
  def self.for_constraint(name, value)
    Z3::Instance.make_real_variable(value)
  end
end

class TrueClass
  def self.for_constraint(name, value)
    Z3::Instance.make_bool_variable(value)
  end
end

class FalseClass
  def self.for_constraint(name, value)
    Z3::Instance.make_bool_variable(value)
  end
end

puts "Z3 constraint solver loaded."
