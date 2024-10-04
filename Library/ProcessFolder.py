import multiprocessing
from multiprocessing import Semaphore
from Library import Video
from Library import Utils
from Library import ExtractInt
from Library import AdminHelper
from Library import Settings
from Library import ProcessVideo
import os

def process_folder(video_folder, output_folder):
    admin_helper = AdminHelper.AdminHelper(video_folder, output_folder)
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

    ExtractInt.get_box(first_video_channel0, admin_helper)
    ExtractInt.get_box(first_video_channel1, admin_helper)
    ExtractInt.get_box(first_video_channel2, admin_helper)
    ExtractInt.get_box(first_video_channel3, admin_helper)

    admin_helper.log(0, 'Processing video files')

    for channel in [1, 2, 3, 4]:
        if channel == 1: channel_files = files[0]
        if channel == 2: channel_files = files[1]
        if channel == 3: channel_files = files[2]
        if channel == 4: channel_files = files[3]

        max_processes = 8
        semaphore = Semaphore(max_processes)
        jobs = []

        for video_file in channel_files:
            process_worker= ProcessVideo.process_worker
            p = multiprocessing.Process(target=process_worker, args=(semaphore, video_file, channel, admin_helper))
            jobs.append(p)
            p.start()

        for job in jobs:
            job.join()

        for video_file in channel_files:
            ProcessVideo.process_video(video_file, channel, admin_helper)



