import time
from os import path
from concurrent.futures import ProcessPoolExecutor
from Library import AudioExtract
from Library import AudioMat
from pyBat import FileOperations



# Flag to toggle parallel processing
run_in_parallel = True
channels = range(25)
# Define folders
audio_output_folder = '/media/dieter/DataLinux/processed_audio'
audio_input_folder = '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_17_Ind03'
parts = path.split(audio_input_folder)

session_folder = path.join(audio_output_folder, parts[-1])
hdf5_folder = path.join(session_folder, 'hdf5')
spectrograms_folder = path.join(session_folder, 'spectrograms')

FileOperations.create_folder(spectrograms_folder, remove_first=True)

mat_files, _ = AudioMat.list_mat_files(audio_input_folder)
n_files = len(mat_files)

# Function for processing a single (file_idx, channel_idx) combination
def process_file_channel(args):
    file_idx, channel_idx = args
    start = time.time()
    result = AudioExtract.preprocess_chunk(hdf5_folder, file_idx, channel_idx, plot=False)
    result = AudioExtract.extract_segments(result)
    plot_metadata = {'file_idx': str(file_idx), 'channel_idx': str(channel_idx)}
    AudioExtract.plot_segments(result, spectrograms_folder, file_idx, channel_idx, plain_image=True, metadata=plot_metadata)
    end = time.time()
    print(f"Processed file {file_idx}, channel {channel_idx} in {end - start:.2f} seconds")
    return result['found'], result['lengths']

# Prepare tasks
tasks = [(file_idx, channel_idx) for channel_idx in channels for file_idx in range(n_files)]

# Run tasks
if __name__ == "__main__":
    all_lengths = {}

    if run_in_parallel:
        print("Running in parallel mode...")
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(process_file_channel, tasks))
    else:
        print("Running in sequential mode...")
        results = [process_file_channel(task) for task in tasks]

    # Optional: collect all lengths and found values
    for idx, (found, lengths) in enumerate(results):
        file_idx, channel_idx = tasks[idx]
        all_lengths[(file_idx, channel_idx)] = lengths
