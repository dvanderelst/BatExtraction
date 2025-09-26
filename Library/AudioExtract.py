import numpy as np
from os import path
from Library import AudioHDF5
from Library import AudioSignal
from Library import AudioUtils
from matplotlib import pyplot as plt
import matplotlib as mpl

from scipy.ndimage import gaussian_filter
from scipy.signal import medfilt2d


mpl.rcParams['agg.path.chunksize'] = 10000
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1

# parameters
fs = 400000
low_khz = 30
high_khz = 150
db_cutoff = -40
max_gap = int(fs / 1000)
verbose = True

nfft = 128
required_length = 1200
plot_range = [-70, -40]

image_width = 400
image_height = 300
image_dpi = 100


def cepstral_smoothing(spectrogram, lifter_size=50):
    # Step 1: Log-transform the spectrogram
    log_spectrogram = np.log1p(spectrogram)  # Use log1p for numerical stability
    # Step 2: Compute the real cepstrum (via rFFT and iFFT along the frequency axis)
    cepstrum = np.fft.irfft(log_spectrogram, axis=0)
    # Step 3: Apply liftering (low-pass filtering in the quefrency domain)
    liftered_cepstrum = np.zeros_like(cepstrum)
    liftered_cepstrum[:lifter_size, :] = cepstrum[:lifter_size, :]  # Retain only low quefrency components
    # Step 4: Transform back to the log-spectral domain
    smoothed_log_spectrogram = np.fft.rfft(liftered_cepstrum, axis=0).real
    # Step 5: Convert back to linear scale and then to dB scale
    smoothed_spectrogram = np.expm1(smoothed_log_spectrogram)  # Reverse log1p
    smoothed_spectrogram_db = 10 * np.log10(smoothed_spectrogram + 1e-10)  # Add a small value to avoid log(0)
    return smoothed_spectrogram_db


def fill_gaps(signal, n):
    ones_indices = np.where(signal == 1)[0]
    if len(ones_indices) < 2: return signal  # No gap-filling needed if there's less than two 1's
    for i in range(len(ones_indices) - 1):
        if ones_indices[i + 1] - ones_indices[i] <= n:
            signal[ones_indices[i]:ones_indices[i + 1] + 1] = 1  # Fill gap with 1's
    return signal


def preprocess_chunk(hdf5_folder, file_idx, channel_idx, plot=False):
    if verbose: print(f'Preprocessing file {file_idx}, channel {channel_idx}')
    data_chunk = AudioHDF5.read_channel_data(hdf5_folder, channel_idx=channel_idx, chunk_nr=file_idx)
    data_chunk = data_chunk - np.median(data_chunk)
    data_chunk = AudioSignal.bandpass_filter(data_chunk, low_khz * 1000, high_khz * 1000)
    intensity = data_chunk ** 2
    intensity = 10 * np.log10(intensity)
    binary = intensity > db_cutoff
    binary_filled = fill_gaps(binary, max_gap)
    scaled_binary = np.interp(binary_filled, (0, 1), (np.min(intensity), np.max(intensity)))
    found = np.sum(binary_filled) > 0

    result = {}
    result['file_idx'] = file_idx
    result['found'] = found
    result['channel_idx'] = channel_idx
    result['data_chunk'] = data_chunk
    result['intensity'] = intensity
    result['binary'] = binary_filled
    result['binary_filled'] = binary_filled

    if plot:
        plt.figure()
        plt.plot(intensity)
        plt.plot(scaled_binary)
        plt.axhline(y=db_cutoff, color='r', linestyle='-')
        plt.ylim(-150, 0)
        plt.show()

    return result


def extract_segments(result):
    if verbose: print(f'Extracting segments for file {result["file_idx"]}, channel {result["channel_idx"]}')
    original_signal = result["data_chunk"]
    binary_signal = result["binary"]
    if len(original_signal) != len(binary_signal):
        raise ValueError("Original signal and binary signal must have the same length.")
    starts = np.where((binary_signal[:-1] == 0) & (binary_signal[1:] == 1))[0] + 1
    ends = np.where((binary_signal[:-1] == 1) & (binary_signal[1:] == 0))[0] + 1
    # If the binary signal starts with 1, add the first index as a start
    if binary_signal[0] == 1: starts = np.insert(starts, 0, 0)
    # If the binary signal ends with 1, add the last index as an end
    if binary_signal[-1] == 1: ends = np.append(ends, len(binary_signal))
    # Adjust for leading and trailing samples
    selected_starts = []
    selected_ends = []
    segments = []
    for start, end in zip(starts, ends):
        length = end - start
        if length <= required_length and length:
            difference = required_length - length
            expand_front = difference // 2
            expand_back = difference - expand_front
            # sample random samples from original_signal
            front_pad = np.random.choice(original_signal, expand_front)
            back_pad = np.random.choice(original_signal, expand_back)
            total = np.concatenate([front_pad, original_signal[start:end], back_pad])
            segments.append(total)

            #new_start = start - expand_front
            #new_end = end + expand_back
            #selected_starts.append(new_start)
            #selected_ends.append(new_end)
    # segments = [original_signal[start:end] for start, end in zip(selected_starts, selected_ends)]
    lengths = [len(segment) for segment in segments]
    # there might be too short segments. We can filter
    new_lengths = []
    new_segments = []
    for segment, length in zip(segments, lengths):
        if length > 0:
            new_lengths.append(length)
            new_segments.append(segment)

    result['lengths'] = new_lengths
    result['segments'] = new_segments
    return result


def plot_segments(result, output_folder, file_index, channel_index, plain_image=False, metadata=None):
    segments = result['segments']
    if metadata is None: metadata = {}
    for array_index, signal in enumerate(segments):
        print(f"Plotting segment {array_index} from file {file_index}, channel {channel_index}")
        # Compute spectrogram
        print('Signal length', len(signal))
        frequencies, times, Sxx = AudioSignal.compute_spectrogram(signal, nfft=nfft)

        db = 10 * np.log10(Sxx + 1e-10)
        db = db - np.max(db)
        db = np.maximum(db, db.max() - 6)
        #db = medfilt2d(db, kernel_size=5)
        # Compute DPI based on desired image size
        figsize = (image_width / image_dpi, image_height / image_dpi)  # Convert pixels to inches
        plt.figure(figsize=figsize, dpi=image_dpi)
        plt.pcolormesh(times, frequencies, db, shading='gouraud', cmap='gray_r')
        # Set caxis limits to the dynamic range
        plt.clim(-6 , 0)

        if not plain_image:
            # Add axes, labels, and titles if not plain_image
            line1 = f'Spectrogram - File {file_index}, Channel {channel_index}, Array {array_index}'
            line2 = f'Number of samples: {len(signal)}'
            plt.colorbar(label='Power (dB)')
            plt.xlabel('Time (ms)')
            plt.ylabel('Frequency (kHz)')
            plt.title(line1 + '\n' + line2)
        else:
            # Remove axes, labels, and colorbars
            plt.axis('off')
        # Save the plot with the desired fixed image size
        spec_filename = path.join(output_folder, f"file_{file_index}_channel_{channel_index}_segment_{array_index}.png")
        wav_filename = path.join(output_folder, f"file_{file_index}_channel_{channel_index}_segment_{array_index}.wav")
        plt.savefig(spec_filename, bbox_inches='tight', pad_inches=0 if plain_image else 0.1, dpi=image_dpi)
        # AudioSignal.save_to_wav(signal, fs, wav_filename)
        metadata['segment_index'] = str(array_index)
        AudioUtils.write_metadata(spec_filename, metadata)
        plt.close()
