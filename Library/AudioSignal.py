from scipy.signal import butter, filtfilt
from scipy.signal import spectrogram
from matplotlib import pyplot as plt
from scipy.io.wavfile import write
import numpy as np

def save_to_wav(array, sample_rate, filename):
    if array.dtype not in [np.int16, np.int32, np.float32]:
        # Normalize if it's a float array in the range [-1, 1]
        if np.issubdtype(array.dtype, np.floating):
            array = (array * 32767).astype(np.int16)
        else:
            raise ValueError("Array must be of type int16, int32, or float32")
    write(filename, sample_rate, array)
    print(f"WAV file saved as '{filename}'")

def boxcar(data, window_size):
    padded_data = np.pad(data, (window_size // 2,), mode='reflect')
    boxcar_filter = np.ones(window_size) / window_size
    smoothed_data = np.convolve(padded_data, boxcar_filter, mode='valid')
    return smoothed_data

def bandpass_filter(data, lowcut, highcut):
    fs = 400000  # Sampling frequency
    nyquist = 0.5 * fs
    order = 3
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band', output='ba')
    # Apply the filter to the data
    filtered_data = filtfilt(b, a, data)  # Use axis=0 for filtering each channel in 2D array
    return filtered_data


def compute_spectrogram(signal, nfft=64, noverlap=None, plot=False, cmap='gray'):
    frequencies, times, Sxx = spectrogram(
        signal,
        fs=400000,  # Sampling frequency
        nperseg=nfft,
        noverlap=noverlap if noverlap is not None else nfft - 1,
        scaling='density',  # Power spectral density
        mode='magnitude',  # Returns the amplitude
    )

    # Convert time to milliseconds for plotting
    times_ms = times * 1000
    frequencies_khz = frequencies / 1000

    # Optional plotting
    if plot:
        dynamic_range = 30
        db = 10 * np.log10(Sxx + 1e-10)
        db = np.maximum(db, db.max() - dynamic_range)
        plt.figure(figsize=(10, 6))
        plt.pcolormesh(times_ms, frequencies_khz, db, shading='gouraud', cmap=cmap)
        plt.colorbar(label='Power (dB)')
        plt.xlabel('Time (ms)')
        plt.ylabel('Frequency (kHz)')
        plt.title('Spectrogram')
        plt.show()

    return frequencies_khz, times_ms, Sxx
