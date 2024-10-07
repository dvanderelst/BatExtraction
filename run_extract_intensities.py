from pyBat import PushOver
from Library import FolderManager
from Library import ProcessFolder
from Library import FoldersToProcess
import os.path as path

boxes_only = False

video_folders = FoldersToProcess.base_folders[0:3]
video_folders = ['Mmicrotis_video/2024_03_17_Ind05']
for video_folder in video_folders:
    output_folder = path.split(video_folder)[1]
    folder_manager = FolderManager.FolderManager(video_folder, output_folder)
    ProcessFolder.process_folder(video_folder, folder_manager, boxes_only)
    folder_manager.write_log()
    if not boxes_only: PushOver.send(f'Processing done for {video_folder}')
