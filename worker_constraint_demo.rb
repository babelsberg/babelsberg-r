
class Task
  def initialize(a)
    @a = a
    @is_ready = true
  end

  def run
    puts @a
    @is_ready = false
  end

  def ready?
    @is_ready
  end
end

tasks = [1..15].map do |num|
  Task.new(num)
end

task = tasks[0]

c = Constraint.new(10) do
  task.ready?
end
c.enable

while true
  task.run
end
