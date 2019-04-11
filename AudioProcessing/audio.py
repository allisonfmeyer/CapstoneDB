import soundfile as sf
import numpy as np
from scipy import signal
import sys
import math
import matplotlib.pyplot as plt

pianoNoteMap = {42:"D", 44: "E", 46: "F", 47: "G", 49: "A", 50: "_B", 51: "B",
                59: "G", 58: "F", 56:"E"}


def findPianoOnsets(x, Fs, plot=False):
    window_size = round(int((5200/44100)*Fs))

    window = signal.gaussian(window_size, std = window_size/(6))
    edge_detector = np.ediff1d(window)


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

    # Rest Detection
    normalized = np.abs(x)/np.max(np.abs(x))
    threshold = 0.04
    if (plot):
        plt.plot(normalized, ',')
        plt.axhline(threshold, color='r')
        plt.show()

    ma_window = 100
    ma = signal.fftconvolve(normalized, np.ones(ma_window)/ma_window)

    fc = 100 # Cut-off frequency of the filter
    w = fc / (Fs / 2) # Normalize the frequency
    b, a = signal.butter(5, w, 'low')
    output = 2*signal.filtfilt(b, a, normalized)

    if (plot):
        plt.plot(normalized, color='b')
        plt.plot(output, color='k')
        plt.axhline(threshold, color='r')
    indicies = np.where(output<threshold)[0]
    rests = []
    start = indicies[0]
    for i in range(0,len(indicies)-1):
        if indicies[i+1]-indicies[i]>300:
            end = indicies[i]
            rests.append((int(start),int(end)))
            start = indicies[i+1]
    rests.append((int(start), int(indicies[-1])))

    new_rests = []
    first =  rests[0][0]
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
    peaks = list(zip(peaks,[False]*len(peaks)))
    rests = [(L,True) for (L,R) in new_rests]
    onsets = sorted(peaks+rests, key=lambda x: x[0])
    plt.plot(x)
    for onset in onsets:
        plt.axvline(onset[0], color='r')
    plt.show()
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
    peaks, _ = signal.find_peaks(med, height=threshold, distance=100)

    minima = []
    for i in range(0,len(peaks)):
        if i==0:
            z = med[:peaks[i]]
            indicies = np.where(z<threshold)
            minima.append(indicies[0][-1])
        else:
            minima.append(np.argmin(med[peaks[i-1]:peaks[i]])+peaks[i-1])
    peaks = [minima[i]*window_size/2 for i in range(0,len(minima))]
    if (plot):
        plt.plot(x)
        for peak in peaks:
            plt.axvline(peak,color='r')
        plt.show()
    # Add an onset to the end to capture last note
    peaks.append(len(x)-1)
    peaks = np.array(peaks)
    peaks = list(zip(peaks,[False]*len(peaks)))
    return peaks

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

    # remember to check for multi channel audio files
    if (x.ndim>1):
        x = np.average(x, axis=1)

    #onsets = findPianoOnsets(x,Fs)
    onsets = findViolinOnsets(x,Fs)
    freqs, amps, spectrum = findFrequencies(onsets,x, Fs)
    for i in range(0,len(freqs)):
        if freqs[i][0]==None: continue
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
    durations = findDuration(list(zip(*onsets))[0], tempo, Fs)
    if (debug):
        print("Durations")
        print(durations)
    noteDurList = list(zip(keynotes.tolist(), durations.tolist()))
    print(noteDurList)
    return noteDurList
    #return convertToString(noteDurList, timeSignature)

if __name__=="__main__":
    audiofile = sys.argv[1]
    timeSignature = sys.argv[2]
    tempo = int(sys.argv[3])
    x = main(audiofile, tempo, timeSignature)
    for note in x:
        print(note)

