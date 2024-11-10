import os
import re
from traceback import print_tb

import h5py
from datetime import datetime
from scipy.signal import butter, filtfilt
import numpy as np
import pandas as pd
from natsort import natsorted
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat
import dask.array as da
import h5py
import copy

fs = 400000
lowcut = 30000
highcut = 150000
verbose = 1

def preprocess_mat_file(file_name, input_folder, output_folder):
    # Construct full path for the input file
    selected_file = os.path.join(input_folder, file_name)
    # Extract the base name for saving the output
    base_name = get_basename(file_name)
    output_file = os.path.join(output_folder, f"{base_name}_filtered.npz")
    # Read, process, and save the filtered data
    raw = read_mat_file(selected_file)
    filtered = preprocess_channels(raw, inplace=False)
    # Save the filtered data
    savemat(output_file, {'filtered': filtered}, do_compression=True)
    print(f"Processed and saved {output_file}")
    return raw

def read_mat_file(file_path):
    if verbose > 0: print(f"Reading file: {file_path}")
    data = loadmat(file_path)
    data = {key: value for key, value in data.items() if not key.startswith('__')}
    data = data['data26']
    data = data[:, 0:25]
    return data


def split_filename(file_path):
    path, full_filename = os.path.split(file_path)
    basename, extension = os.path.splitext(full_filename)
    return path, basename, extension

def get_basename(file_path):
    path, basename, extension = split_filename(file_path)
    return basename


def boxcar_smooth(array, window_size):
    # Create the boxcar kernel
    kernel = np.ones(window_size) / window_size
    # Apply the smoothing to each row independently (i.e., smooth along columns)
    smoothed_array = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode='same'), axis=0, arr=array)
    return smoothed_array


def apply_bandpass_filter(data, lowcut, highcut):
    nyquist = 0.5 * fs
    order = 3
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band', output='ba')
    # Apply the filter to the data
    filtered_data = filtfilt(b, a, data, axis=0)  # Use axis=0 for filtering each channel in 2D array
    return filtered_data

def preprocess_channels(data, inplace=True):
    if not inplace:data = copy.copy(data)
    channels = data.shape[1]
    for i in range(channels):
        if verbose > 0: print(f"Preprocessing channel {i + 1}/{channels}, inplace={inplace}")
        shifted = data[:, i] - np.median(data[:, i])
        filtered = apply_bandpass_filter(shifted, lowcut, highcut)
        data[:, i] = filtered
    return data

def get_mat_files(folder_path):
    # Pattern to extract the timestamp from the filename
    pattern = re.compile(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}")
    # Collect all .mat files with their timestamps
    mat_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mat"):
            match = pattern.search(file_name)
            if match:
                timestamp = datetime.strptime(match.group(), "%Y_%m_%d_%H_%M_%S")
                mat_files.append((file_name, timestamp))
    # Sort files by timestamp
    sorted_files_with_timestamps = natsorted(mat_files, key=lambda x: x[1])
    # Extract only filenames from the sorted list
    sorted_files = [file_name for file_name, _ in sorted_files_with_timestamps]
    # Create DataFrame
    df = pd.DataFrame(sorted_files_with_timestamps, columns=['Filename', 'Timestamp'])
    return sorted_files, df


def plot_timestamp_gaps(df):
    # Plotting timestamps with markers
    plt.figure(figsize=(12, 6))
    plt.plot(df['Timestamp'], range(len(df)), marker='o', linestyle='-', markersize=5)
    # Labels and title
    plt.xlabel('Timestamp')
    plt.ylabel('File Index')
    plt.title('Gap Analysis in .mat File Timestamps')
    plt.grid(True)
    plt.tight_layout()
    plt.show()