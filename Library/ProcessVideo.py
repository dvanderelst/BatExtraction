from os.path import basename
from Library import Video
from Library import ExtractInt



def process_video(video_file, channel, folder_manager):
    base_name = basename(video_file)
    folder_manager.log(0, 'Processing ' + base_name)
    can_read = Video.test_mp4_file(video_file)
    if not can_read:
        folder_manager.log(0, 'Can not read' + base_name)
    if can_read:
        video = Video.Video(video_file)
        led_video = ExtractInt.get_led_video(video, channel, folder_manager)
        folder_manager.log(0, ' LED video done: ' + base_name)
        #folder_manager.update_progress_file(video_file, 'True\nFalse')

        ExtractInt.get_led_intensities(led_video, channel, folder_manager)
        folder_manager.log(0, ' Intensity extraction done: ' + base_name)
        #folder_manager.update_progress_file(video_file, 'True\nTrue')

        folder_manager.log(0, 'Finished' + base_name)

        fps = led_video.get_frame_rate()
        size1 = video.get_size()
        size2 = led_video.get_size()
        properties = str([size1, size2, fps])
        folder_manager.log(0, 'Properties' + base_name + ' ' + properties)

