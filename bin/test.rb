require "libz3"

shoes  = 0
hat    = 0
shirt  = 0
pants  = 0

colours = [:Black, :Brown, :Blue, :White]
always {shoes.in colours}
always {shirt.in colours}
always {pants.in colours}
always {hat.in colours}
#
always {shoes == hat}
#always {shoes != pants}
always {shoes != shirt}
#always {shirt != pants}
#
always { (shoes == :Brown) or (shoes == :Black) }
always { (shirt == :Brown) or (shirt == :Blue) or (shirt == :White) }
always { hat == :Brown }
#
print "shirt:#{shirt}\n"
print "shoes:#{shoes}\n"
print "hat:#{hat}\n"
print "pants:#{pants}\n"
#shoes = Z3EnumerationSort.new([:Black, :Brown, :Blue, :White])
#print "#{(shoes.in colours).w_z3}"
#shoes.extend(Z3EnumerationSortMeister)
#shoes = 42
#hat = 20
#always { shoes.in colours }
#always { hat.in colours }
#always { shoes != hat }

#print "hallo\n"
#print hat.to_s + "\n"
#print shoes.to_s + "\n"
