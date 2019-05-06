import soundfile as sf
import numpy as np
from scipy import signal
import sys
import math
import matplotlib.pyplot as plt
import noteable.noteMapping as nm
import noteable.verification as v

pianoNoteMap = {42:"D", 44: "E", 46: "F", 47: "G", 49: "A", 50: "_B", 51: "B",
                59: "G", 58: "F", 56:"E"}


def findRests(x, Fs, onsets, plot=False):
    # Rest Detection
    normalized = np.abs(x)/np.max(np.abs(x))

    window_size=500
    f, t, Zxx = signal.stft(normalized, fs=Fs, nperseg = window_size)
    (r,c) = Zxx.shape
    E = [0 for i in range(0,c)]
    for i in range(0,c):
        E[i] = np.sum(np.arange(r)*np.abs(Zxx[:, i])/r)
    med = signal.medfilt(E, 11)
    med = med/np.max(med)

    ma_window = 100
    ma = signal.fftconvolve(normalized, np.ones(ma_window)/ma_window)

    fc = 100 # Cut-off frequency of the filter
    w = fc / (Fs / 2) # Normalize the frequency
    b, a = signal.butter(5, w, 'low')
    output = 2*signal.filtfilt(b, a, normalized)

    interpolated = np.interp(np.arange(len(normalized)), np.arange(len(med))*window_size/2, med)
    threshold = np.min(interpolated[int(max(0, onsets[0][0]-10000)):int(onsets[0][0])])*1.01

    if (plot):
        plt.plot(normalized, color='b')
        plt.plot(interpolated, color='k')
        plt.axhline(threshold, color='r')
        plt.show()
    indicies = np.where(interpolated<=threshold)[0]

    rests = []
    if len(indicies)>0:
        start = indicies[0]
        for i in range(0,len(indicies)-1):
            if indicies[i+1]-indicies[i]>300:
                end = indicies[i]
                rests.append((int(start),int(end)))
                start = indicies[i+1]
        rests.append((int(start), int(indicies[-1])))

    new_rests = []
    if (len(rests)>0) and len(rests[0])>0:
        first =  rests[0][0]
        (LL,RR) = rests[0]
        for i in range(0,len(rests)-1):
            (L,R) = rests[i]
            (LL,RR) = rests[i+1]
            if LL-R>=2000:
                new_rests.append((first, R))
                first = LL
        new_rests.append((first,RR))

    if (plot):
        for rest in new_rests:
            (L,R) = rest
            plt.axvline(L,color='r')
            plt.axvline(R,color='g')
        plt.show()
    return [(L,True) for (L,R) in new_rests]

def findPianoOnsets(x, Fs, plot=False):
    window_size = round(int((5200/44100)*Fs))

    window = signal.gaussian(window_size, std = window_size/(6))
    edge_detector = np.ediff1d(window)


    filtered = signal.fftconvolve(np.abs(x), edge_detector)

    filtered = filtered/np.max(filtered)
    # Shift signal by half the window size to line up with onset
    filtered = filtered[window_size//2:]
    peaks, _ = signal.find_peaks(filtered, height=0.02, distance=round(window_size*1.5))

    if (plot):
        plt.plot(x)
        for peak in peaks:
            plt.axvline(peak,color='r')
        plt.show()

    peaks = list(zip(peaks,[False]*len(peaks)))
    rests = findRests(x,Fs, peaks, plot)
    onsets = sorted(peaks+rests, key=lambda x: x[0])
    '''
    plt.plot(x)
    for onset in onsets:
        plt.axvline(onset[0], color='r')
    plt.show()
    '''
    return onsets

def findViolinOnsets(x, Fs, plot=False):

    window_size = 500
    f, t, Zxx = signal.stft(x, fs=Fs, nperseg = window_size)
    (r,c) = Zxx.shape
    E = [0 for i in range(0,c)]
    for i in range(0,c):
        E[i] = np.sum(np.arange(r)*np.abs(Zxx[:, i])/r)
    med = signal.medfilt(E, 55)
    med = med/np.max(med)
    threshold = 0.1
    peaks, _ = signal.find_peaks(med, height=threshold) #, distance=00)
    dips, _ = signal.find_peaks(-med)

    minima = []
    for i in range(0,len(peaks)):
        if i==0:
            z = med[:peaks[i]]
            indicies = np.where(z<threshold)
            if len(indicies[0])>0:
                minima.append(indicies[0][-1])
            else:
                minima.append(0)
        else:
            '''
            z = med[peaks[i-1]:peaks[i]]
            index = np.argmin(z)
            minima.append(index+peaks[i-1])
            '''
            z = dips[(dips>peaks[i-1]) & (dips<peaks[i])]
            index = np.argmin(med[z])
            indicies = np.where(np.isclose(med[peaks[i-1]:peaks[i]],med[z[index]], atol=0.001))
            minima.append(peaks[i-1]+indicies[0][-1])

    peaks = [minima[i]*window_size/2 for i in range(0,len(minima))]
    peaks = list(zip(peaks,[False]*len(peaks)))
    if (plot):
        plt.plot(x)
        for peak in peaks:
            plt.axvline(peak[0],color='r')
        plt.show()
    rests = findRests(x,Fs, peaks, plot)
    # Make sure onsets and rests don't start at the same time
    rests = list(filter(lambda x: x[0] not in peaks, rests))
    onsets = sorted(peaks+rests, key=lambda x: x[0])
    '''
    plt.plot(x)
    interpolated = np.interp(np.arange(len(x)), np.arange(len(med))*window_size/2, med)
    plt.plot(interpolated)
    for onset in onsets:
        plt.axvline(onset[0], color='r')
    plt.show()
    '''

    return onsets

# Returns the duration of notes in eighth notes.
# Tempo is bpm for a quarter note
def findDuration(peaks, tempo, Fs):
    times = np.ediff1d(peaks)/Fs
    quarter = 60/tempo
    eigth = quarter/2
    return np.rint(times/eigth)

def findFrequencies(onsets,x, Fs, plot=False):
    x = x/np.max(x)
    max_frequencies = 3

    frequencies = [None for i in range(len(onsets)-1)]
    amplitudes = [None for i in range(len(onsets)-1)]

    for i in range(0, len(onsets)-1):
        (start, isRest) = onsets[i]
        (end, _) = onsets[i+1]
        if (isRest):
            frequencies[i] = [None]
            amplitudes[i] = [None]
            continue
        start = int(start)
        end = int(end)
        fft = np.fft.fft(x[start:end], 8*(end-start))
        spectrum = np.abs(fft[:int(np.ceil(len(fft)/2))])
        # square to accentuate peaks
        specturm = np.square(spectrum)
        # normalize
        spectrum = spectrum/np.max(spectrum)
        peaks, _ = signal.find_peaks(spectrum, height=0.1, distance = 700)
        peak_heights = spectrum[peaks]
        d = dict(zip(peaks, peak_heights))
        if (plot):
            plt.plot(spectrum)
            plt.plot(peaks, spectrum[peaks], 'r.')
            plt.show()

        sorted_d = sorted(d.items(), key=lambda kv: -kv[1])
        sorted_d = sorted_d[:min(max_frequencies, len(sorted_d))]
        frequencies[i], amplitudes[i] = list(list(zip(*sorted_d))[0]), list(list(zip(*sorted_d))[1])
        frequencies[i] = Fs*np.array(frequencies[i])/(2*len(spectrum))
        if len(frequencies[i])==0:
            frequencies[i] = [None]
            amplitudes[i] = [None]
    return (frequencies, amplitudes, spectrum)

# Implements two way matching algorithm to find fundamental frequency
def removeHarmonics(freqs,amps, spectrum, Fs, debug=False):
    p=0.5
    q=1.4
    r=0.5

    final_frequencies = np.zeros(len(freqs))
    for i in range(0,len(freqs)):
        if freqs[i][0] == None:
            continue
        k = len(freqs[i])
        f_max = np.max(freqs[i])
        total_error = np.zeros(k)
        for n in range(0,k):
            fund = freqs[i][n]
            N = int(np.ceil(f_max/fund))
            #harmonics
            f = np.array([j*fund for j in range(1,N+1)])
            harmonicAmps = [spectrum[int(f[j]*2*len(spectrum)/Fs)] for j in range(0, len(f))]
            a = [None for i in range(0,len(f))]
            errors = np.zeros(N)
            for j in range(0,len(f)):
                diff = np.abs(freqs[i]-f[j])
                index = diff.argmin()
                a[j] = index
                errors[j] = diff[index]
            A = np.array([amps[i][a[j]] for j in range(0,len(a))])
            error_pm = errors*np.power(f, -p) + A*(q*errors*np.power(f,-p)-r)

            a = np.zeros(k)
            errors = np.zeros(k)
            for j in range(0,k):
                diff = np.abs(f-freqs[i][j])
                index = diff.argmin()
                a[j] = index
                errors[j] = diff[index]
            A = np.array([harmonicAmps[int(a[j])] for j in range(0,len(a))])
            error_mp = errors*np.power(freqs[i], -p) + A*(q*errors*np.power(freqs[i],-p)-r)
            total_error[n] = np.sum(error_pm)/N + np.sum(error_mp)/k
        final_frequencies[i] = freqs[i][total_error.argmin()]
        if (debug):
            print("-----")
            key_no = np.rint(12*np.log2(freqs[i]/440)+49)
            print(key_no)
            print(total_error)
            print("-----")
    return final_frequencies

def convertToString(L, timeSignature, instrument, key):
    print(key)
    accidentals = nm.keyMap[key]
    result = ""
    count = 0
    measureCount = 0
    if(instrument == "piano"):
        noteMapping = nm.pianoNoteMap
    else: noteMapping = nm.violnNoteMap
    timeSignature = timeSignature.split("/")
    beats = int(timeSignature[0])
    measure = int(timeSignature[1]) 
    for (freq, duration) in L:
        num = int(duration)//2
        if(num<=0): num = 1
        count += num
        # Map -inf to a rest
        if(freq == float("-inf")): note = "z"
        else: 
            if(int(freq) in noteMapping):
                note = noteMapping[int(freq)]
            else:
                note = "z"
        if(len(note)>1):
            #print(note)
            if(note[1:] in accidentals):
                note = note[1:]
        else:
            if(note.upper() in accidentals):
                #print(note)
                note = "=" + note
        if(count >= beats):
            measureCount += 1
            if(num != 1):
                result = result + note + str(int(num)) + "|"
            else:
                result = result + note + "|"
            count = 0
        else:
            if(num != 1):
                result = result + note + str(int(num)) + " "
            else:
                result = result + note + " "
        if(measureCount == measure):
            result += "n "
            measureCount = 0
    result = result[:-2]
    result += "]n"
    return result

def convertToPitches(s, small, key, instrument):
    accidentals = nm.keyMap[key]
    if(instrument == "piano"):
        mapping = nm.notePianoMap
    else: mapping = nm.noteToViolin
    if(small == "1/4"): multiply = 2
    if s[-2:] == "]n": s = s[:-2]
    notes = s.split(" ")
    l = list()
    for note in notes:
        if("|" not in note):
            if(note == "n" or note == ""): continue 
            if(not note[-1:].isdigit()): 
                duration = 1
                curNote = note
            else:
                duration = note[-1:]
                curNote = note[:-1]
            if(curNote[0] == "="):
                #print(curNote[1:])
                pitch = mapping[curNote[1:]]
            else:
                if(curNote.upper() in accidentals):
                    curNote = "^" + curNote
                pitch = mapping[curNote]
            l.append((pitch, int(duration)*multiply))
        else: 
            newsplit = note.split("|")
            for note in newsplit:
                #print(note)
                if(note == "n"):
                    continue
                if(note == ""): continue
                else:
                    if(not note[-1:].isdigit()):   
                        duration = 1
                        curNote = note
                    else: 
                        duration = note[-1:]
                        curNote = note[:-1]
                    if(curNote[0] == "="):
                        #print(curNote[1:], "fails")
                        pitch = mapping[curNote[1:]]
                    else:
                        if(curNote.upper() in accidentals):
                            curNote = "^" + curNote
                        pitch = mapping[curNote]
                    l.append((pitch, int(duration)*multiply))
    return l



def findNoteinS(src, s):
    num = 0
    cur_line = 0
    cur_measure = 0
    cur_note = 0
    for c in s:
        if(num == src):
            return '.abcjs-v1'+'.abcjs-l'+str(cur_line)+'.abcjs-m'+str(cur_measure)+'.abcjs-n'+str(cur_note)
        if(c.isspace()):
            continue
        elif(c.isdigit()):
            continue
        elif(c == "^" or c == "_" or c == "="):
            continue
        elif(c == "|"):
            cur_measure += 1
            cur_note = -1
        elif(c == "n"):
            cur_line += 1
            cur_measure = -1
            cur_note = -1
        else:
            num += 1
            cur_note += 1
    return ""

def identifyIncorrect(L, s):
    editDis = L[0]
    incorrectTuple = L[1]
    result = list()
    for (op, src, dest) in incorrectTuple:
        #print(src, findNoteinS(src, s))
        result.append(findNoteinS(src, s))
    return result



# bleep  = [17, [('sub', 5, 5), ('sub', 6, 6), ('sub', 7, 7), ('sub', 10, 10),
#  ('sub', 11, 11), ('ins', 11, 12), ('sub', 19, 20), ('sub', 20, 21),
#   ('sub', 21, 22), ('sub', 25, 26), ('sub', 26, 27), ('sub', 27, 28), 
#   ('del', 28, 28), ('sub', 38, 38), ('sub', 39, 39), ('sub', 41, 41), ('del', 42, 41)]]


#A1 = "D2 D2 A2 A2|=c2 =c2 A3 G2|G2 =F2 F2 F2|E2 E2 D4|n A2 A2 G2 G2|F2 F2 E3 A2|A2 G2 F2 F2|F5 D2 D2|n A2 A2 B2 B2|A4 G2 G2|F2 F4 E2|=C]n"



# returns a list of tuples in the form (Piano Key Number, duration)
# where duration is the length in eight notes (ie 2 would mean a quarter note)
def main(audiofile, tempo, timeSignature, xml, instrument, keyM, small, debug=False):
    x, Fs = sf.read(audiofile)

    # remember to check for multi channel audio files
    if (x.ndim>1):
        x = np.average(x, axis=1)

    if (instrument=="piano"): onsets = findPianoOnsets(x,Fs)
    elif (instrument=="violin"): onsets = findViolinOnsets(x,Fs)
    freqs, amps, spectrum = findFrequencies(onsets,x, Fs)
    for i in range(0,len(freqs)):
        if freqs[i][0]==None: continue
        key = np.rint(12*np.log2(freqs[i]/440)+49)
        temp = freqs[i][np.abs(key-np.mean(key))<=18]
        if len(temp)!=0:
            freqs[i] = temp
    freqs_new = removeHarmonics(freqs, amps, spectrum, Fs)
    if (debug):
        print("Possible Notes")
        for i in range(0, len(freqs)):
            keynotes = np.rint(12*np.log2(freqs[i]/440)+49)
            print(keynotes)
    keynotes = np.rint(12*np.log2(freqs_new/440)+49)
    if (debug):
        print("Selected Notes")
        print(keynotes)
    durations = findDuration(list(zip(*onsets))[0], tempo, Fs)
    if (debug):
        print("Durations")
        print(durations)
    noteDurList = list(zip(keynotes.tolist(), durations.tolist()))
    noteDurList = list(filter(lambda x: x[1]>0, noteDurList))

    start = 0
    end = 0
    foundFirst = False
    foundLast = False
    for i in range(0,len(noteDurList)):
        (pitch,duration) = noteDurList[i]
        if (not foundFirst) and (pitch!= -np.inf):
            foundFirst = True
            start = i
            break
    for i, (pitch, duration) in reversed(list(enumerate(noteDurList))):
        if (not foundLast) and (pitch!= -np.inf):
            foundLast = True
            end = i
            break
    noteDurList = noteDurList[start:end+1]
    #print(convertToString(noteDurList, "4/4"))
    #return noteDurList
    player = convertToString(noteDurList, timeSignature, instrument, keyM)
    xmlNotes = convertToPitches(xml, small, keyM, instrument)
    incorrect = v.iterative_levenshtein(xmlNotes, noteDurList)
    print(incorrect)
    print(identifyIncorrect(incorrect, player))
    return (player, identifyIncorrect(incorrect, player))

if __name__=="__main__":
    audiofile = sys.argv[1]
    timeSignature = sys.argv[2]
    tempo = int(sys.argv[3])
    instrument = sys.argv[4]
    x = main(audiofile, tempo, timeSignature, instrument)
    print(x)

