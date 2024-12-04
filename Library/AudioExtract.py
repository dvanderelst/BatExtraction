import numpy as np
import random
from os import path
from Library import AudioHDF5
from Library import AudioSignal
from matplotlib import pyplot as plt


def process_chunk(hdf5_folder, file_idx, channel_idx, plot=False):
    low_khz = 30
    high_khz = 150
    db_cutoff = -65
    before = 400
    after = 400
    min_length = 400
    max_length = 400 * 5
    print('Getting segments from channel', channel_idx, 'for file idx', file_idx)
    data_chunk = AudioHDF5.read_channel_data(hdf5_folder, channel_idx=channel_idx, chunk_nr=file_idx)
    data_chunk = data_chunk - np.median(data_chunk)
    data_chunk = AudioSignal.bandpass_filter(data_chunk, low_khz * 1000, high_khz * 1000)
    intensity = data_chunk ** 2
    intensity = 10 * np.log10(intensity)
    smoothed_intensity = AudioSignal.boxcar(intensity, 128)
    binary = smoothed_intensity > db_cutoff
    binary = binary[0:-1]
    binary = fill_gaps(binary, 100)
    #segments, indices = extract_segments(data_chunk, binary, before, after, min_length, max_length)
    segments, indices = extract_segments(data_chunk, binary)
    nr_segments = len(segments)
    #print('Channel index', channel_idx, '|', 'file index', file_idx, '-> Found', nr_segments, 'segments')
    print('Found', nr_segments, 'segments')
    result = {}
    result['file_idx'] = file_idx
    result['channel_idx'] = channel_idx
    result['data_chunk'] = data_chunk
    result['channel_idx'] = channel_idx
    result['segments'] = segments
    result['intensity'] = intensity
    result['smoothed_intensity'] = smoothed_intensity
    result['binary'] = binary
    result['nr_segments'] = nr_segments
    result['indices'] = indices

    # Scale binary such that where it's 1, the new value is the max of smoothed_intensity and where it's 0, the new value is the min of smoothed_intensity
    scaled_binary = binary.astype(int)
    scaled_binary = scaled_binary * (np.max(smoothed_intensity) - np.min(smoothed_intensity)) + np.min(smoothed_intensity)

    if plot:
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(data_chunk)
        plt.title('Data chunk')
        plt.subplot(2, 1, 2)
        plt.plot(smoothed_intensity)
        #plt.plot(scaled_binary)


        for i in range(len(indices)):
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            plt.axvspan(indices[i], indices[i] + len(segments[i]), color=color, alpha=0.5)
            print(len(segments[i]))

        plt.title('Intensity and binary')
        plt.show()


    return result


def fill_gaps(signal, n):
    # Identify the start and end of each series of 1's
    ones_indices = np.where(signal == 1)[0]
    if len(ones_indices) < 2:
        return signal  # No gap-filling needed if there's less than two 1's
    # Iterate through indices and fill gaps
    for i in range(len(ones_indices) - 1):
        if ones_indices[i + 1] - ones_indices[i] <= n:
            signal[ones_indices[i]:ones_indices[i + 1] + 1] = 1  # Fill gap with 1's
    return signal


import numpy as np


def extract_segments(signal, binary_signal, min_length=200):
    if len(signal) != len(binary_signal):
        raise ValueError("The signal and binary signal must have the same length.")

    if min_length < 1:
        raise ValueError("Minimum length must be at least 1.")

    segments = []
    start_indices = []
    start_idx = None

    for i, value in enumerate(binary_signal):
        if value == 1 and start_idx is None:
            start_idx = i
        elif value == 0 and start_idx is not None:
            if i - start_idx >= min_length:
                segments.append(signal[start_idx:i])
                start_indices.append(start_idx)
            start_idx = None

    # If the binary signal ends with 1, capture the last segment
    if start_idx is not None and len(signal) - start_idx >= min_length:
        segments.append(signal[start_idx:])
        start_indices.append(start_idx)

    return segments, start_indices


# def extract_segments(data_signal, binary_signal, before=0, after=0, min_length=0, max_length=1000):
#     # Identify where the binary signal changes from 0 to 1 and 1 to 0
#     edges = np.diff(binary_signal, prepend=0, append=0)
#     start_indices = np.where(edges == 1)[0]
#     end_indices = np.where(edges == -1)[0]
#
#     # Adjust start and end indices to include n and m samples, ensuring bounds
#     adjusted_start_indices = np.maximum(start_indices - before, 0)
#     adjusted_end_indices = np.minimum(end_indices + after, len(data_signal))
#
#     # Ensure each segment has at least min_length samples
#     min_length = min_length + before + after
#     for i in range(len(adjusted_start_indices)):
#         segment_length = adjusted_end_indices[i] - adjusted_start_indices[i]
#         if segment_length < min_length:
#             # Extend the end index to meet the minimum length requirement
#             adjusted_end_indices[i] = min(adjusted_start_indices[i] + min_length, len(data_signal))
#
#     # Use adjusted start and end indices to slice data_signal and create segments
#     segments = [data_signal[start:end] for start, end in zip(adjusted_start_indices, adjusted_end_indices)]
#     indices = adjusted_start_indices
#     # Filter out segments that are too long
#     selected_indices = []
#     selected_segments = []
#     for s, i in zip(segments, indices):
#         if len(s) < max_length + 1:
#             selected_indices.append(i)
#             selected_segments.append(s)
#     return selected_segments, selected_indices


def plot_segments(result, output_folder, file_index, channel_index):
    segments = result['segments']
    for array_index, signal in enumerate(segments):
        print(f"Plotting segment {array_index} from file {file_index}, channel {channel_index}")
        frequencies, times, Sxx = AudioSignal.compute_spectrogram(signal)

        dynamic_range = 30
        times_ms = times * 1000
        frequencies_khz = frequencies / 1000
        db = 10 * np.log10(Sxx + 1e-10)
        db = np.maximum(db, db.max() - dynamic_range)
        plt.figure(figsize=(10, 6))
        plt.pcolormesh(times_ms, frequencies_khz, db, shading='gouraud', cmap='viridis')
        plt.colorbar(label='Power (dB)')
        plt.xlabel('Time (ms)')
        plt.ylabel('Frequency (Hz)')
        plt.title(f'Spectrogram - File {file_index}, Channel {channel_index}, Array {array_index}')

        # Save the plot
        filename = path.join(output_folder, f"file_{file_index}_channel_{channel_index}_segment_{array_index}.png")
        plt.savefig(filename)
        plt.close()

    print(f"Spectrograms saved to {output_folder}")
