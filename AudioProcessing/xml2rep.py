from music21 import *
import numpy as np
import sys

#Returns the piece in a list of tuples (piano key pitch, length in quarter notes)
def convert(fname):
    c = converter.parse(fname, format='musicxml')
    partStream = c.parts.stream()
    result = []
    for x in partStream.flat.notesAndRests:
        if isinstance(x, note.Note):
            # Piano key notes are 20 less than MIDI
            result.append((x.pitch.midi-20, x.duration.quarterLength*2))
        else:
            result.append((-np.inf, x.duration.quarterLength*2))
    return result
if __name__=="__main__":
    print(convert(sys.argv[1]))

