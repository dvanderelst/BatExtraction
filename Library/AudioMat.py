import re
import os
import h5py
import pandas as pd
from datetime import datetime
from natsort import natsorted
from scipy.io import loadmat

verbose =  1

class HDF5ChunkWriter:
    def __init__(self, output_folder, n_files):
        self.dtype = 'float64'
        self.dataset_name = 'data'
        self.chunk_size = 20 * 400 * 1000
        self.n_files = n_files
        self.total_size = self.n_files * self.chunk_size
        self.current_indices = [0] * 25
        self.file_paths = []
        for channel in range(0, 25):
            current_path = os.path.join(output_folder, f'channel_{channel}.hdf5')
            current_file = h5py.File(current_path, 'w')
            current_file.create_dataset(self.dataset_name, shape=(self.total_size,), dtype=self.dtype)
            current_file.close()
            self.file_paths.append(current_path)

    def add_chunk(self, channel, data):
        current_path = self.file_paths[channel]
        current_index = self.current_indices[channel]
        with h5py.File(current_path, 'a') as hdf5_file:
            dataset = hdf5_file[self.dataset_name]
            end_index = current_index + len(data)
            if end_index > self.total_size: raise ValueError("Data exceeds allocated dataset size.")
            dataset[current_index:end_index] = data
            self.current_indices[channel] = end_index


def read_mat_file(file_path):
    if verbose > 1: print(f"Reading file: {file_path}")
    data = loadmat(file_path)
    data = {key: value for key, value in data.items() if not key.startswith('__')}
    data = data['data26']
    data = data[:, 0:25]
    return data

def list_mat_files(folder_path):
    pattern = re.compile(r"\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}")
    mat_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mat"):
            match = pattern.search(file_name)
            if match:
                timestamp = datetime.strptime(match.group(), "%Y_%m_%d_%H_%M_%S")
                mat_files.append((file_name, timestamp))
    sorted_files_with_timestamps = natsorted(mat_files, key=lambda x: x[1])
    sorted_files = [file_name for file_name, _ in sorted_files_with_timestamps]
    df = pd.DataFrame(sorted_files_with_timestamps, columns=['Filename', 'Timestamp'])
    return sorted_files, df

def check_matlab_version(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(128).decode('utf-8', errors='ignore')
    if 'MATLAB 5.0' in header:
        return 'MATLAB v5 - v7.2 (non-HDF5 format)'
    elif 'MATLAB 7.3' in header:
        return 'MATLAB v7.3 (HDF5 format)'
    else:
        return 'Unknown MATLAB version or unsupported format'