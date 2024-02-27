import time
import numpy
from Library import ExtractLed
from Library import Video
from Library import Utils
import os
from Library import Misc
from matplotlib import pyplot

# PARAMETERS
drive = "/media/dieter/Panama_2024"
video_folder = 'downloaded_data/2024-2-19'
output_folder = 'output2'
delete_output = False
window = 25
#############

camera_folder = os.path.join(drive, video_folder)
output_folder = os.path.join(drive, output_folder)
Utils.create_empty_folder(output_folder, clear_existing=delete_output)
log_file_name = os.path.join(output_folder, 'log.txt')
log_file = open(log_file_name, 'w')
log_file.write(time.asctime()+'\n')
log_file.close()

files = Utils.get_cam_files(camera_folder)
unreadable_files = []
counter = 0
for ch_files in files:
    log_file = open(log_file_name, 'a')
    log_file.write(time.asctime() + '\n')
    log_file.close()
    for file_name in ch_files:
        print('*' * 50)
        print(file_name)
        can_read = Video.test_mp4_file(file_name)
        if not can_read:
            unreadable_files.append(file_name)
        if can_read:
            video = Video.Video(file_name)
            led_video = ExtractLed.get_led_video(video, output_folder)
            trace = ExtractLed.get_led_trace(led_video, output_folder)
            post_processed = ExtractLed.post_process_trace(trace, window=window, do_plot=True, led_video=led_video, output_folder=output_folder)
            Misc.add_markers_to_video(led_video, post_processed, output_folder)
            min_trace = numpy.min(trace)
            mean_trace = numpy.mean(trace)
            max_trace = numpy.max(trace)

            formatted_floats = [f'{x:.3f}' for x in [min_trace, mean_trace, max_trace]]
            formatted_floats = ', '.join(formatted_floats)

            size1 = video.get_size()
            size2 = led_video.get_size()

            line = Utils.list_to_line([file_name, size1, size2, formatted_floats])
            log_file = open(log_file_name, 'a')
            log_file.write(line)
            log_file.close()

            time.sleep(0.1)
            counter = counter + 1

            pyplot.close('all')

log_file = open(log_file_name, 'a')
if len(unreadable_files) > 0:
    log_file.write('Unreadable:\n')
    for x in unreadable_files: log_file.write(x + '\n')
log_file.close()
