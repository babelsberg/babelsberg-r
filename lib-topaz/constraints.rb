module Constraints
  def self.variable_handlers
    @variable_handlers ||= {}
  end

  def self.for_variables_of_type(klass, &block)
    variable_handlers[klass] = block
  end
end
