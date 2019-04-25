from midiutil import MIDIFile
import soundfile as sf
from midi2audio import FluidSynth
import numpy as np
import random
import audio

if __name__=="__main__":
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 80   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    correct=0
    N = 20
    for i in range(0,N):
        MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
        MyMIDI.addTempo(track, time, tempo)
        program = 40 # A Violin
        MyMIDI.addProgramChange(track, channel, time, program)

        midiNote = 69 #A 440 hz
        noteTimes= [1.0, 2.0, 4.0, 8.0] # in eighth notes
        restLength = random.choice(noteTimes)

        MyMIDI.addNote(track, channel, midiNote, time+restLength/2, 1, volume)
        MyMIDI.addNote(track, channel, midiNote, time+restLength/2+4, 1, volume)

        with open("notes.mid", "wb") as output_file:
            MyMIDI.writeFile(output_file)

        fs = FluidSynth('./040_Florestan_String_Quartet.sf2')
        fs.midi_to_audio('notes.mid', 'output.wav')

        x, Fs = sf.read('output.wav')

        # remember to check for multi channel audio files
        if (x.ndim>1):
            x = np.average(x, axis=1)

        onsets = audio.findViolinOnsets(x,Fs)
        durations = audio.findDuration(list(zip(*onsets))[0], tempo, Fs)

        durations = audio.main('output.wav',tempo, "asdf", False)
        if (durations[0][0]== -np.inf) and (durations[0][1]==restLength) and (durations[1][0]!= -np.inf):
            correct+=1
        else:
            print(durations)
            print(restLength)
    print(correct/N)
