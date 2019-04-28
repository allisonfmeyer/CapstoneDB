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
    tempo    = 100   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    ground_truth = []
    predicted = []
    for midiNote in range(55, 83):
        MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
        MyMIDI.addTempo(track, time, tempo)

        #program = 40 # A Violin
        program = 0 # A Piano
        MyMIDI.addProgramChange(track, channel, time, program)

        #midiNote = random.randint(55,83)
        MyMIDI.addNote(track, channel, midiNote, 0, 1, volume)

        with open("singleNote.mid", "wb") as output_file:
            MyMIDI.writeFile(output_file)

        #fs = FluidSynth('./040_Florestan_String_Quartet.sf2')
        fs = FluidSynth('./sound_font.sf2')
        fs.midi_to_audio('singleNote.mid', 'output.wav')

        x, Fs = sf.read('output.wav')

        # remember to check for multi channel audio files
        if (x.ndim>1):
            x = np.average(x, axis=1)

        freqs, amps, spectrum = audio.findFrequencies([(0,False), (len(x)-1, True)],x, Fs)

        for i in range(0,len(freqs)):
            if freqs[i][0]==None: continue
            key = np.rint(12*np.log2(freqs[i]/440)+49)
        #print(np.rint(12*np.log2(np.array(freqs)/440)+49))
        freqs_new = audio.removeHarmonics(freqs, amps, spectrum, Fs)
        keynotes = np.rint(12*np.log2(freqs_new/440)+49)
        ground_truth.append(midiNote-20)
        predicted.append(keynotes[0])
    print(ground_truth)
    predicted = list(map(int, predicted))
    print(predicted)
    correct=0
    for i in range(0,len(predicted)):
        if predicted[i]==ground_truth[i]:
            correct+=1
    print(correct/len(predicted))
