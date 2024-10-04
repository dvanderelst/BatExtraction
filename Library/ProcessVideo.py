from os.path import basename

from Library import Video
from Library import ExtractInt
from multiprocessing import Semaphore

def process_worker(semaphore, video_file, channel, admin_helper):
    with semaphore:
        process_video(video_file, channel, admin_helper)

def process_video(video_file, channel, admin_helper):
    base_name = basename(video_file)
    admin_helper.log(0, 'Processing ' + base_name)
    can_read = Video.test_mp4_file(video_file)
    if not can_read:
        admin_helper.log(0, 'Can not read' + base_name)
    if can_read:
        video = Video.Video(video_file)
        led_video = ExtractInt.get_led_video(video, channel, admin_helper)
        admin_helper.processing_progress[channel][base_name][0] = True

        ExtractInt.get_led_intensities(led_video, channel, admin_helper)
        admin_helper.processing_progress[channel][base_name][1] = True

        admin_helper.log(0, 'Finished' + base_name)

        fps = led_video.get_frame_rate()
        size1 = video.get_size()
        size2 = led_video.get_size()
        properties = str([size1, size2, fps])
        admin_helper.log(0, 'Properties' + base_name + ' ' + properties)
        admin_helper.write_log()
