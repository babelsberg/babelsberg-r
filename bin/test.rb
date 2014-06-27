require "libz3"

colours = [:Black, :Brown, :Blue, :White]
#domain {shoes.in colours}
#domain {shirt.in colours}
#domain {pants.in colours}
#domain {hat.in colours}
#
#always {shoes == hat}
#always {shoes != pants}
#always {shoes != shirt}
#always {shirt != pants}
#
#always {shoes == :Brown | shoes == :Black}
#always {shirt == :Brown | shirt == :Blue | shirt == :White}
#always {hat == :Brown}
#
#print "shirt:#{shirt}"
#print "shoes:#{shoes}"
#print "hat:#{hat}"
#print "pants:#{pants}"
#shoes = Z3EnumerationSort.new([:Black, :Brown, :Blue, :White])
#print "#{(shoes.in colours).w_z3}"
#shoes.extend(Z3EnumerationSortMeister)
shoes = 1
always {shoes.in colours}
print "hallo"
