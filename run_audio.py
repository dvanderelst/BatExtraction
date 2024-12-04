import time
from os import path

from Library import AudioSignal
from Library import AudioExtract
from Library import AudioMat
from pyBat import FileOperations
from pyBat import SaveLoad

audio_output_folder = '/media/dieter/DataLinux/processed_audio'
audio_input_folder = '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_17_Ind03'
parts = path.split(audio_input_folder)

session_folder = path.join(audio_output_folder, parts[-1])
hdf5_folder = path.join(session_folder, 'hdf5')
segments_folder = path.join(session_folder, 'segments')
spectrograms_folder = path.join(session_folder, 'spectrograms')

FileOperations.create_folder(segments_folder, remove_first=False)
FileOperations.create_folder(spectrograms_folder, remove_first=True)

mat_files, _ = AudioMat.list_mat_files(audio_input_folder)

selected_fields = ['file_idx', 'channel_idx', 'segments', 'indices']
#%%
n_files = len(mat_files)
channel_idx = 15

total_nr_segments = 0
for file_idx in range(120, n_files):
    start = time.time()
    pickle_file = path.join(segments_folder, f'file_{file_idx}_channel_{channel_idx}.pck')
    result = AudioExtract.process_chunk(hdf5_folder, file_idx, channel_idx, plot=True)
    break
    selected_result = {key: result[key] for key in selected_fields}
    SaveLoad.pickle_save(pickle_file, selected_result)
    end = time.time()
    print('Processing time:', end - start)
    segments = result['segments']
    nr_segments = result['nr_segments']
    total_nr_segments += nr_segments
    AudioExtract.plot_segments(result, spectrograms_folder, file_idx, channel_idx)
    print('Total number of segments so far:', total_nr_segments)

