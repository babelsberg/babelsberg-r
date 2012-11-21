
lineno = 1

c = Constraint.new(10,
                   proc { lineno > previous(lineno) },
                   proc { lineno = previous(lineno) + 1 })
c.enable

puts "And now for something completely different ..."

while true do
  buf = ""
  $stdout.print "=> "

  while buf[-1] != "\n" do
    buf += $stdin.read(1)
  end

  $stdout.print("line #{lineno}: #{buf}")

  lineno += 1

  if buf == "exit\n"
    exit
  end
end
