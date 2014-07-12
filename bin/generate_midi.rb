#! /usr/bin/env ruby
#
# usage: from_scratch.rb
#
# This script shows you how to create a new sequence from scratch and save it
# to a MIDI file. It creates a file called 'from_scratch.mid'.

# Start looking for MIDI module classes in the directory above this one.
# This forces us to use the local copy, even if there is a previously
# installed version out there somewhere.
$LOAD_PATH[0, 0] = File.join(File.dirname(__FILE__), '.', 'lib')

require 'midilib/sequence'
require 'midilib/consts'
include MIDI

ARGV.each do |arg|
    @notes = arg.scan(/(\d+)#(\d+);/).collect { |height, length| { :height => height, :length => length }}
end

for i in 0..@notes.size-1
 print @notes[i][:height].to_i
 print "#"
 print @notes[i][:length].to_i
end



seq = Sequence.new()

# Create a first track for the sequence. This holds tempo events and stuff
# like that.
track = Track.new(seq)
seq.tracks << track
track.events << Tempo.new(Tempo.bpm_to_mpq(120))
track.events << MetaEvent.new(META_SEQ_NAME, 'Sequence Name')

# Create a track to hold the notes. Add it to the sequence.
track = Track.new(seq)
seq.tracks << track

# Give the track a name and an instrument name (optional).
track.name = 'My New Track'
track.instrument = GM_PATCH_NAMES[0]

# Add a volume controller event (optional).
track.events << Controller.new(0, CC_VOLUME, 127)

# Add events to the track: a major scale. Arguments for note on and note off
# constructors are channel, note, velocity, and delta_time. Channel numbers
# start at zero. We use the new Sequence#note_to_delta method to get the
# delta time length of a single quarter note.
track.events << ProgramChange.new(0, 1, 0)
sixteenth = seq.note_to_delta('sixteenth')
eighth = seq.note_to_delta('eighth')
quarter = seq.note_to_delta('quarter')
dot_quarter = seq.note_to_delta('dottedquarter')
half = seq.note_to_delta('half')
dot_half = seq.note_to_delta('dottedhalf')
whole = seq.note_to_delta('whole')
for i in 0..@notes.size-1
  this_lenght = quarter
  track.events << NoteOn.new(0, 64 + @notes[i][:height].to_i, 127, 0)
  this_lenght = case @notes[i][:length].to_i 
    when 1 then sixteenth
    when 2 then eighth
    when 4 then quarter
    when 6 then dot_quarter
    when 8 then half
    when 12 then dot_half
    when 16 then whole
    else print "not matched " + @notes[i][:length].to_s
   end
   track.events << NoteOff.new(0, 64 + @notes[i][:height].to_i, 127, this_lenght)
end

# Calling recalc_times is not necessary, because that only sets the events'
# start times, which are not written out to the MIDI file. The delta times are
# what get written out.

# track.recalc_times

File.open('generated.mid', 'wb') { |file| seq.write(file) }
