from Library import Video
from Library import ExtractLed

video = Video.Video('N883A6_ch4_main_20240131213003_20240131213503.mp4')
trace = ExtractLed.run(video, do_plot=True)


