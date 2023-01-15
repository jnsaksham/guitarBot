import music21
import os, glob
import numpy as np
import musescore

# Write a function to read .mxl files
def read_mxl(file):
    return music21.converter.parse(file)

# Write a function to extract midi notes from .mxl data extracted in read_mxl()
def get_notes(file):
    notes = []
    for part in file.parts:
        for note in part.flat.notes:
            if isinstance(note, music21.note.Note):
                notes.append(str(note.pitch))
            elif isinstance(note, music21.chord.Chord):
                notes.append('.'.join(str(n) for n in note.normalOrder))
    return notes

# Write a function to play midi notes
def play_midi(notes):
    offset = 0
    output_notes = []
    for pattern in notes:
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = music21.note.Note(int(current_note))
                new_note.storedInstrument = music21.instrument.Piano()
                notes.append(new_note)
            new_chord = music21.chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            new_note = music21.note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = music21.instrument.Piano()
            output_notes.append(new_note)
        offset += 0.5
    midi_stream = music21.stream.Stream(output_notes)
    midi_stream.write('midi', fp='test_output.mid')

def play_midi_from_xml(fpath):
    s = read_mxl(fpath)
    # s.expandRepeats() 
    sp = music21.midi.realtime.StreamPlayer(s)
    sp.play()

# Write a function to play an input music21 stream
def play_stream(s):
    sp = music21.midi.realtime.StreamPlayer(s)
    sp.play()

if __name__ == '__main__':
    # outputType = 'autoharmonizer/inputs/inputs'
    # fname = 'Ahmad Jamal - Night Mist Blues.mxl'
    outputType = 'outputs-0.5'
    fname = 'Al Jolson, Billy Rose, Dave Dreyer - There\'s A Rainbow \'Round My Shoulder.mxl'
    fpath = os.path.join(outputType, fname)
    # play_midi_from_xml(fpath)
    s = read_mxl(fpath)
    # print (s)
    s.show()