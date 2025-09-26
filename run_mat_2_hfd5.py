import os
from os import path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from Library import AudioMat
from pyBat import FileOperations

max_workers = 4
audio_output_folder = '/media/dieter/DataLinux/processed_audio'
audio_input_folder = '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_17_Ind03'
parts = path.split(audio_input_folder)

session_folder = path.join(audio_output_folder, parts[-1])
hdf5_folder = path.join(session_folder, 'hdf5')

FileOperations.create_folder(session_folder, remove_first=False)
FileOperations.create_folder(hdf5_folder, remove_first=False)
#%%
# List .mat files and initialize HDF5 writers for each channel
mat_files, _ = AudioMat.list_mat_files(audio_input_folder)
n_files = len(mat_files)
writer = AudioMat.HDF5ChunkWriter(hdf5_folder, n_files)

# Initialize a lock for thread-safe access
writer_lock = Lock()

# Define a function to process each file in parallel
def process_file(index, mat_file):
    print(f"Processing file: {mat_file} ({index + 1}/{n_files})")
    full_mat_file = os.path.join(audio_input_folder, mat_file)
    raw_data = AudioMat.read_mat_file(full_mat_file)
    for channel in range(0, 25):
        with writer_lock:
            writer.add_chunk(channel, raw_data[:, channel])

# Run the processing in parallel
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    for current_index, current_mat_file in enumerate(mat_files):
        executor.submit(process_file, current_index, current_mat_file)
