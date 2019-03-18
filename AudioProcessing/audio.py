import soundfile as sf
import numpy as np
from scipy import signal
import sys
import matplotlib.pyplot as plt

def findOnsets(x, Fs, plot=False):
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
    return peaks

def findFrequencies(onsets, x, Fs, plot=False):
    x = x/np.max(x)
    max_frequencies = 5

    # Add an onset to the end to capture last note
    onsets = np.append(onsets, len(x)-1)
    frequencies = np.zeros((len(onsets)-1,max_frequencies))

    for i in range(0, len(onsets)-1):
        start = int(onsets[i])
        end = int(onsets[i+1])
        fft = np.fft.fft(x[start:end], 8*(end-start))
        spectrum = np.abs(fft[:len(fft)//2+1])
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
        for j in range(0,min(len(d), max_frequencies)):
            frequencies[i][j] = Fs*sorted_d[j][0]/(2*len(spectrum))
    return frequencies

def main(audiofile):
    x, Fs = sf.read(audiofile)
    onsets = findOnsets(x,Fs)
    freqs = findFrequencies(onsets,x, Fs)
    MIDInotes = np.rint(12*np.log2(freqs/440)+49)
    print(MIDInotes)

if __name__=="__main__":
    audiofile = sys.argv[1]
    main(audiofile)
