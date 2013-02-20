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
  end
end

Constraints.for_variables_of_type Numeric do |name, value|
  Z3::Instance.make_real_variable(value)
end
Constraints.for_variables_of_type TrueClass do |name, value|
  Z3::Instance.make_bool_variable(value)
end
Constraints.for_variables_of_type FalseClass do |name, value|
  Z3::Instance.make_bool_variable(value)
end

Constraints.register_solver Z3::Instance

puts "Z3 constraint solver loaded."
