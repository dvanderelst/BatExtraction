import os
import numpy
from matplotlib import pyplot
from Library import FolderManager
from Library import Utils
from Library import MarkVideo

video_folder = 'Mmicrotis_video/2024_03_17_Ind05'
folder_manager = FolderManager.FolderManager(video_folder, empty_log_folder=False)

pyplot.close('all')
output_folder = folder_manager.get_output_folder()
output_file = os.path.join(output_folder, 'processed_intensities.pck')
processed_intensities = Utils.load_from_pickle(output_file)

for channel in [1, 2, 3, 4]:
    channel_text = 'channel%s' % channel
    keys = processed_intensities[channel_text].keys()
    channel_led_files = processed_intensities[channel_text]['channel_led_files']
    binary_sections = processed_intensities[channel_text]['binary_sections']
    indices = processed_intensities[channel_text]['indices']
    frame_rate = processed_intensities[channel_text]['fps']
    nr_indices = len(indices)
    for i in range(nr_indices):
        binary_section = binary_sections[i]
        video_file_name = channel_led_files[i]
        new_video_file_name = video_file_name.replace('LED_', 'MRK_')
        print('Processing', video_file_name)
        MarkVideo.add_marks_to_video(binary_section, video_file_name, new_video_file_name)
