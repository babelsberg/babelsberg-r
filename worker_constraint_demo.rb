# -*- coding: undecided -*-

# class Task
#   def initialize(a)
#     @a = a
#     @is_ready = true
#   end

#   def run
#     puts @a
#     @is_ready = false
#   end

#   def ready?
#     @is_ready
#   end
# end

# tasks = [1..15].map do |num|
#   Task.new(num)
# end

# task = tasks[0]

# c = Constraint.new(10) do
#   task.ready?
# end
# c.enable

# while true
#   task.run
# end

# class User
#   def initialize(birthyear, age)
#     @birthyear = birthyear
#     @age = age
#     constrain(?@age == 2013 - @birthyear)
#   end
# end

# u = User.new(2012, 11)
@age = 24
@birthyear = 1988
puts(constrain: @age == 2013 - @birthyear)
