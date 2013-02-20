
solver = Z3.new
Constraints.for_variables_of_type Numeric do |name, value|
  solver.make_real_variable(value)
end
Constraints.for_variables_of_type TrueClass do |name, value|
  solver.make_bool_variable(value)
end
Constraints.for_variables_of_type FalseClass do |name, value|
  solver.make_bool_variable(value)
end
Constraints.register_solver solver

puts "Z3 constraint solver loaded."
