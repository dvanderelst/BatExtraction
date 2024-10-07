from Library import Video
from Library import Settings
from Library import Utils
from Library import MatchAudio
import os

write_video = True
audio_folder = Settings.audio_folder
drive = Settings.input_drive
audio_folder = os.path.join(drive, audio_folder)

selected_runs = [9, 10, 19]
selected_runs = None
mat_files = Utils.get_mat_files(audio_folder, runs=selected_runs)
quality = []
for selected_file in mat_files:
    output = MatchAudio.match_audio(selected_file, write_video=write_video)
    result_folder = output['result_folder']
    camera_fps = output['camera_fps']
    distinctiveness_log = output['distinctiveness_log']
    quality = quality + distinctiveness_log
    Video.create_combined_video(result_folder, camera_fps)