from midiutil import MIDIFile
from midi2audio import FluidSynth
import numpy as np
import random
import audio

if __name__=="__main__":
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 100   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
              # automatically)
    MyMIDI.addTempo(track, time, tempo)

    program = 40 # A Violin
    MyMIDI.addProgramChange(track, channel, time, program)

    length = 5 #number of notes to produce
    midiNotes = [random.randint(55,83) for i in range(0,length)]  # MIDI note number
    noteTimes= [1.0, 2.0, 4.0, 8.0] # in eighth notes
    noteLengths = [random.choice(noteTimes) for i in range(0,len(midiNotes))]

    durationList = list(zip(midiNotes, noteLengths))

    rests = 2
    restList = [(-np.inf, random.choice(noteTimes)) for i in range(0,rests)]

    durationList+=restList
    random.shuffle(durationList)


    time = 0
    for pitch, duration in durationList:
        if (pitch!= -np.inf):
            MyMIDI.addNote(track, channel, pitch, time, duration/2, volume)
        time+=duration/2

    with open("major-scale.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

    fs = FluidSynth('./040_Florestan_String_Quartet.sf2')
    fs.midi_to_audio('major-scale.mid', 'output.wav')

    ground_truth = [(pitch-20, time) for (pitch, time) in durationList]
    print(ground_truth)


