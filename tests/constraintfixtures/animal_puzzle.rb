require "libz3"

puts "Spend exactly 100 dollars and buy exactly 100 animals. Dogs cost"
puts "15 dollars, cats cost 1 dollar, and mice cost 25 cents each. You"
puts "have to buy at least one of each. How many of each should you buy?"

dog, cat, mouse = 0, 0, 0
always { dog >= 1 && cat >= 1 && mouse >= 1 }
always { dog + cat + mouse == 100 } # we want to buy 100 animals
always {# We have 100 dollars (10000 cents):
        #   dogs cost 15 dollars (1500 cents),
        #   cats cost 1 dollar (100 cents), and
        #   mice cost 25 cents
        dog * 1500 + cat * 100 + mouse * 25 == 10000 }
puts "Dogs: #{dog}, cats: #{cat}, mice: #{mouse}"
