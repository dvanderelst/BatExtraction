from pyBat import PushOver
from Library import FolderManager
from Library import ProcessFolder
from Library import FoldersToProcess

boxes_only = False

video_folders = FoldersToProcess.base_folders[0:3]
video_folders = ['Mmicrotis_video/2024_03_17_Ind05']
for video_folder in video_folders:
    folder_manager = FolderManager.FolderManager(video_folder)
    ProcessFolder.process_folder(folder_manager, boxes_only)
    folder_manager.write_log()
    if not boxes_only: PushOver.send(f'Processing done for {video_folder}')
