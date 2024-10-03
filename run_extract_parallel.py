from matplotlib import pyplot
from Library import Video
from Library import Utils
from Library import ExtractInt
from Library import AdminHelper
from Library import Settings
from Library import ProcessVideo
import os

from concurrent.futures import ProcessPoolExecutor, as_completed

# PARAMETERS
drive = Settings.drive
video_folder = Settings.video_folder
output_folder = Settings.output_folder
output_location = Settings.output_location

remove1 = Settings.remove1
remove2 = Settings.remove2
remove3 = Settings.remove3
remove4 = Settings.remove4

# Set paths
camera_folder = os.path.join(drive, video_folder)
output_folder = os.path.join(output_location, output_folder)
admin_helper = AdminHelper.AdminHelper(output_folder)

# Get files and handle preprocessing
files = Utils.get_cam_files(camera_folder)
Utils.visualize_cam_file_durations(files, output_folder)

files, removed_files = Utils.purge_cam_files(files, remove1, remove2, remove3, remove4)
removed_files_basenames = Utils.get_basenames(removed_files)
Utils.remove_files_containing_substrings(output_folder, removed_files_basenames)
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

admin_helper.write('STARTING PROCESSING')

# Function for processing a single video file
def process_single_video(video_file, channel, admin_helper):
    try:
        ProcessVideo.process_video(video_file, channel, admin_helper)
        return f"Processed {video_file} on channel {channel}"
    except Exception as e:
        return f"Failed to process {video_file} on channel {channel}: {e}"

def main(files, admin_helper):
    futures = []

    # Use ProcessPoolExecutor to parallelize the video processing
    with ProcessPoolExecutor() as executor:
        for channel in [1, 2, 3, 4]:
            if channel == 1: channel_files = files[0]
            if channel == 2: channel_files = files[1]
            if channel == 3: channel_files = files[2]
            if channel == 4: channel_files = files[3]

            # Submit each video file for parallel processing
            for video_file in channel_files:
                future = executor.submit(process_single_video, video_file, channel, admin_helper)
                futures.append(future)

        # Collect and process results as they complete
        for future in as_completed(futures):
            result = future.result()
            print(result)
            admin_helper.write(result)

if __name__ == '__main__':
    main(files, admin_helper)

# Ensure all plots are closed
pyplot.close('all')
