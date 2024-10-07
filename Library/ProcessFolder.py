from Library import Video
from Library import Utils
from Library import ExtractInt
from Library import Settings
from Library import ProcessVideo
import multiprocessing

from pyBat import PushOver

def process_videos_in_parallel(channel_files, channel, folder_manager):
    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=4)
    # Prepare arguments to pass to the process_video function
    args = [(video_file, channel, folder_manager) for video_file in channel_files]
    # Use pool.starmap to execute the process_video function in parallel
    pool.starmap(ProcessVideo.process_video, args)
    # Close the pool and wait for all tasks to complete
    pool.close()
    pool.join()

def process_folder(video_folder, folder_manager, boxes_only=False):
    indices_to_remove = Settings.indices_to_remove

    remove1 = []
    remove2 = []
    remove3 = []
    remove4 = []

    if video_folder in indices_to_remove.keys():
        remove1 = indices_to_remove[video_folder][0]
        remove2 = indices_to_remove[video_folder][1]
        remove3 = indices_to_remove[video_folder][2]
        remove4 = indices_to_remove[video_folder][3]

    output_folder = folder_manager.get_output_folder()

    files = Utils.get_video_files(video_folder)
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

    ExtractInt.get_box(first_video_channel0, folder_manager)
    ExtractInt.get_box(first_video_channel1, folder_manager)
    ExtractInt.get_box(first_video_channel2, folder_manager)
    ExtractInt.get_box(first_video_channel3, folder_manager)

    if boxes_only: return

    folder_manager.log(0, 'Processing video files')

    for channel in [1, 2, 3, 4]:
        if channel == 1: channel_files = files[0]
        if channel == 2: channel_files = files[1]
        if channel == 3: channel_files = files[2]
        if channel == 4: channel_files = files[3]
        process_videos_in_parallel(channel_files, channel, folder_manager)

        pushover_msg = f"{video_folder}, Channel {channel} done"
        PushOver.send(pushover_msg)



