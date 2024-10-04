from matplotlib import pyplot
from Library import Video
from Library import Utils
from Library import ExtractInt
from Library import AdminHelper
from Library import Settings
from Library import ProcessVideo
import os
import time



# PARAMETERS
drive = Settings.drive
video_folder = Settings.video_folder
output_folder = Settings.output_folder
output_location = Settings.output_location


#############

camera_folder = os.path.join(drive, video_folder)

remove1 = Settings.remove1
remove2 = Settings.remove2
remove3 = Settings.remove3
remove4 = Settings.remove4

output_folder = os.path.join(output_location, output_folder)
admin_helper = AdminHelper.AdminHelper(output_folder)

files = Utils.get_video_files(camera_folder)
# Plot the durations of the all video files and save the image
Utils.visualize_cam_file_durations(files, output_folder)
# Remove video files (in case we have files that overlap with others in time)
files, removed_files = Utils.purge_cam_files(files, remove1, remove2, remove3, remove4)
removed_files_basenames = Utils.get_basenames(removed_files)
Utils.remove_files_containing_substrings(output_folder, removed_files_basenames)
# Plot the durations of the remaining files and save the image
Utils.visualize_cam_file_durations(files, output_folder, prefix='removed_')

# Get the boxes for the LED videos
first_video_channel0 = Video.Video(files[0][0])
first_video_channel1 = Video.Video(files[1][0])
first_video_channel2 = Video.Video(files[2][0])
first_video_channel3 = Video.Video(files[3][0])

ExtractInt.get_box(first_video_channel0, admin_helper)
ExtractInt.get_box(first_video_channel1, admin_helper)
ExtractInt.get_box(first_video_channel2, admin_helper)
ExtractInt.get_box(first_video_channel3, admin_helper)

admin_helper.write2logfile('STARTING PROCESSING')


for channel in [1, 2, 3, 4]:
    if channel == 1: channel_files = files[0]
    if channel == 2: channel_files = files[1]
    if channel == 3: channel_files = files[2]
    if channel == 4: channel_files = files[3]
    for video_file in channel_files:
        ProcessVideo.process_video(video_fileA, channel, admin_helper)



