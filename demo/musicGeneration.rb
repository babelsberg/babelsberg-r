require "libz3"

class Note
    @@notes = [0, 2, 4, 5, 7, 9, 11, 12]
    @@lengths = [1, 2, 4, 6, 8, 12, 16]
    
    attr_accessor :height, :number, :length 
 
    def initialize(height, number)
        @height = height
        @number = number
        @length = 4
        always { @height.in @@notes }
        always { @length.in @@lengths}
    end

end

notes = []
for i in 0..48
    notes << (Note.new(0, i))
end

notes.each do |note|
    previousnote = notes[note.number-i]
    always {note.height != previousnote.height}
    always {note.height < previousnote.height + 6}
    always {note.height > previousnote.height - 6}            
end

for i in 0..notes.size/6
    note1 = notes[i]
    note2 = notes[i+1]
    note3 = notes[i+2]
    note4 = notes[i+3]
    note5 = notes[i+4]
    note6 = notes[i+5]
    
    always { (note1.length + note2.length + note3.length + note4.length + note5.length + note6.length) == 16}
end

notes.each do |note|
    print note.height
    print "#"
    print note.length
    print ";"
end


