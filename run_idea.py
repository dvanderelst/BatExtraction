from Library import Utils
from Library import ExtractLed
from Library import Video
from Library import Utils
import os


camera_folder = '/media/dieter/Lillith_Backup/N883A6/2024-2-2'
output_folder = '/media/dieter/Lillith_Backup/output'
Utils.create_empty_folder(output_folder)

files = Utils.get_camera_files(camera_folder)
ch1_files = files[0]
fl = ch1_files[0]

video = Video.Video(fl)
led_video = ExtractLed.get_led_video(video, output_folder)
trace = ExtractLed.get_led_trace(led_video, output_folder)

# box = ExtractLed.get_box(video, output_folder)
#
# # led_video_output_file = os.path.join(led_video_folder, 'LED_' + video.basename + '.mp4')
# ExtractLed.extract_led_video(video, box, output_folder)