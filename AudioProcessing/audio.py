import soundfile as sf
import numpy as np
from scipy import signal
import sys
import matplotlib.pyplot as plt

pianoNoteMap = {42:"D", 44: "E", 46: "F", 47: "G", 49: "A", 50: "_B", 51: "B",
                59: "G", 58: "F", 56:"E"}


def findPianoOnsets(x, Fs, plot=False):
    window_size = round(int((5200/44100)*Fs))

    window = signal.gaussian(window_size, std = window_size/(6))
    edge_detector = np.ediff1d(window)

    '''
    (_, channels) = x.shape
    if (channels>1):
        x = np.average(x, axis=1)
    '''
    filtered = signal.fftconvolve(np.abs(x), edge_detector)
    filtered = filtered/np.max(filtered)
    # Shift signal by half the window size to line up with onset
    filtered = filtered[window_size//2:]
    peaks, _ = signal.find_peaks(filtered, height=0.1, distance=round(window_size*1.5))

    if (plot):
        plt.plot(x)
        for peak in peaks:
            plt.axvline(peak,color='r')
        plt.show()
    '''
    normalized = np.abs(x)/np.max(np.abs(x))
    threshold = 0.04
    if (plot):
        plt.plot(normalized, ',')
        plt.axhline(threshold, color='r')
        plt.show()

    ma_window = 100
    ma = signal.fftconvolve(normalized, np.ones(ma_window)/ma_window)

    plt.plot(normalized)
    plt.plot(ma)
    plt.axhline(threshold, color='r')
    plt.show()
    indicies = np.where(ma<threshold)[0]
    rests = []
    start = indicies[0]
    for i in range(0,len(indicies)-1):
        #print(indicies[i+1]- indicies[i])
        if indicies[i+1]-indicies[i]>300:
            end = indicies[i]
            rests.append((start,end))
            start = indicies[i+1]
    plt.plot(normalized)
    for rest in rests:
        (L,R) = rest
        print(R-L)
        plt.axvline(L,color='r')
        plt.axvline(R,color='g')
    plt.show()
    '''
    return peaks

def findViolinOnsets(x, Fs, plot=False):
    window_size = round(int((5200/44100)*Fs))

    window = signal.gaussian(window_size, std = window_size/(6))
    edge_detector = np.ediff1d(window)

    '''
    (_, channels) = x.shape
    if (channels>1):
        x = np.average(x, axis=1)
    '''
    new_window_size = int(window_size/8)
    plt.plot(np.square(x)/np.max(np.square(x)))
    filtered = signal.fftconvolve(np.square(x)/np.max(np.square(x)), np.ones(new_window_size)/new_window_size) #edge_detector)
    plt.plot(filtered)
    plt.show()
    filtered = filtered/np.max(filtered)
    # Shift signal by half the window size to line up with onset
    filtered = filtered[window_size//2:]
    peaks, _ = signal.find_peaks(filtered, height=0.1, distance=round(window_size*1.5))

    if (plot):
        plt.plot(x)
        for peak in peaks:
            plt.axvline(peak,color='r')
        plt.show()

    # Add an onset to the end to capture last note
    peaks.append(len(x)-1)
    return peaks

# Returns the duration of notes in eighth notes.
# Tempo is bpm for a quarter note
def findDuration(peaks, tempo, Fs):
    times = np.ediff1d(peaks)/Fs
    quarter = 60/tempo
    eighth = quarter/2
    return np.rint(times/eighth)

def findFrequencies(onsets, x, Fs, plot=False):
    x = x/np.max(x)
    max_frequencies = 3

    frequencies = [None for i in range(len(onsets)-1)]
    amplitudes = [None for i in range(len(onsets)-1)]

    for i in range(0, len(onsets)-1):
        start = int(onsets[i])
        end = int(onsets[i+1])

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
    return (frequencies, amplitudes, spectrum)

# Implements two way matching algorithm to find fundamental frequency
def removeHarmonics(freqs,amps, spectrum, Fs, debug=False):
    p=0.5
    q=1.4
    r=0.5

    final_frequencies = np.zeros(len(freqs))
    for i in range(0,len(freqs)):
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

def convertToString(L, timeSignature):
    result = ""
    count = 0
    measureCount = 0
    timeSignature = timeSignature.split("/")
    beats = int(timeSignature[0])
    measure = int(timeSignature[1])
    for (freq, duration) in L:
        num = duration//2
        count += num
        note = pianoNoteMap[int(freq)]
        if(count == beats):
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


# returns a list of tuples in the form (Piano Key Number, duration)
# where duration is the length in eight notes (ie 2 would mean a quarter note)
def main(audiofile, tempo, timeSignature, debug=False):
    x, Fs = sf.read(audiofile)
    onsets = findPianoOnsets(x,Fs)
    freqs, amps, spectrum = findFrequencies(onsets,x, Fs)
    for i in range(0,len(freqs)):
        key = np.rint(12*np.log2(freqs[i]/440)+49)
        freqs[i] = freqs[i][np.abs(key-np.mean(key))<=18]
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
    durations = findDuration(onsets, tempo, Fs)
    if (debug):
        print("Durations")
        print(durations)
    noteDurList = list(zip(keynotes.tolist(), durations.tolist()))
    print(noteDurList)
    return convertToString(noteDurList, timeSignature)

if __name__=="__main__":
    audiofile = sys.argv[1]
    timeSignature = sys.argv[2]
    tempo = 100
    x = main(audiofile, tempo, timeSignature)
    print(x)

