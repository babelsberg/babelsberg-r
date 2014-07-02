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

always {shoes == hat}
always {shoes != pants}
always {shoes != shirt}
always {shirt != pants}

# Alternative
# always { (shoes == :Brown) or (shoes == :Black) }
# always { (shirt == :Blue) or (shirt == :White) or (shirt == :Brown) }

always { hat == :Brown }
always { shoes.one_of [:Brown, :Black] }
always { shirt.one_of [:White, :Blue, :Brown] }

print "shirt:\t#{shirt}\n"
print "shoes:\t#{shoes}\n"
print "hat:\t#{hat}\n"
print "pants:\t#{pants}\n"
