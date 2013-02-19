Constraints.for_variables_of_type Fixnum do |name, value|
  Z3Expression.new(value)
end
Constraints.for_variables_of_type Float do |name, value|
  Z3Expression.new(value)
end
Constraints.for_variables_of_type TrueClass do |name, value|
  Z3Expression.new(value)
end
Constraints.for_variables_of_type FalseClass do |name, value|
  Z3Expression.new(value)
end
Constraints.register_solver Z3

puts "Z3 constraint solver loaded."
