from matplotlib import pyplot
from Library import Video
from Library import Utils
from Library import ExtractInt
from Library import Settings
import os
import time
import numpy
import matplotlib
#matplotlib.use('TkAgg')

# PARAMETERS
drive = Settings.drive
video_folder = Settings.video_folder
output_folder = Settings.output_folder

remove1 = Settings.remove1
remove2 = Settings.remove2
remove3 = Settings.remove3
remove4 = Settings.remove4
#############

camera_folder = os.path.join(drive, video_folder)
output_folder = os.path.join(drive, output_folder)
Utils.create_empty_folder(output_folder)
log_file_name = os.path.join(output_folder, 'log.txt')
log_file = open(log_file_name, 'w')
log_file.write(time.asctime() + '\n')
log_file.write(str([remove1, remove2, remove3, remove4]) + '\n')
log_file.close()

files = Utils.get_cam_files(camera_folder)
Utils.visualize_cam_file_durations(files, output_folder)

files, removed_files = Utils.purge_cam_files(files, remove1, remove2, remove3, remove4)
removed_files_basenames = Utils.get_basenames(removed_files)
Utils.remove_files_containing_substrings(output_folder, removed_files_basenames)
Utils.visualize_cam_file_durations(files, output_folder, prefix='removed_')

unreadable_files = []
counter = 0
for ch_files in files:
    log_file = open(log_file_name, 'a')
    log_file.write(time.asctime() + '\n')
    log_file.close()
    processed_file_index = 0
    for file_name in ch_files:
        print('*' * 50)
        print(file_name)
        can_read = Video.test_mp4_file(file_name)
        if not can_read:
            unreadable_files.append(file_name)
        if can_read:
            video = Video.Video(file_name)
            led_video = ExtractInt.get_led_video(video, output_folder)
            fps = led_video.get_frame_rate()
            intensities = ExtractInt.get_led_intensities(led_video, output_folder)

            size1 = video.get_size()
            size2 = led_video.get_size()

            line = Utils.list_to_line([processed_file_index, file_name, size1, size2])
            log_file = open(log_file_name, 'a')
            log_file.write(line)
            log_file.close()
            processed_file_index = processed_file_index + 1

            time.sleep(0.1)
            counter = counter + 1

pyplot.close('all')
log_file = open(log_file_name, 'a')
log_file.write('Unreadable:\n')
for x in unreadable_files: log_file.write(x + '\n')
log_file.close()
