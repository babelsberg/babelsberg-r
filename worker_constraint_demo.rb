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

class User
  attr_accessor :birthyear, :age

  def initialize(birthyear, age)
    constrain: @birthyear == birthyear
    constrain: @age == 2013 - @birthyear
  end
end

u = User.new(2012, 11)
if 2013 - u.birthyear != u.age
  raise "Constraint solver didn't fix it for me!"
end
