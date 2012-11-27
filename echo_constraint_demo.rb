require File.expand_path("../libprime.rb", __FILE__)

lineno = 0
c = Constraint.new(10,
                   proc { lineno > previous(lineno) },
                   proc { lineno = previous(lineno) + 1 })
c.enable
primec = Constraint.new(10,
                        proc { lineno.prime? },
                        proc { lineno = Prime.new(lineno - 1).succ })
primec.enable

puts "And now for something completely different ..."

while true do
  buf = ""
  $stdout.print "=> "

  while buf[-1] != "\n" do
    buf += $stdin.read(1)
  end

  $stdout.print("line #{lineno}: #{buf}")

  if buf == "exit\n"
    exit
  end
end
