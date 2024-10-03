from Library import Video
from Library import ExtractInt

def process_video(video_file, channel, admin_helper):
    admin_helper.write('Processing video: ' + video_file)
    can_read = Video.test_mp4_file(video_file)
    if not can_read:
        message = 'Cannot read video file: ' + video_file
        admin_helper.write(message)
    if can_read:
        video = Video.Video(video_file)
        led_video = ExtractInt.get_led_video(video, channel, admin_helper)
        ExtractInt.get_led_intensities(led_video, channel, admin_helper)

        message = 'Finished processing video: ' + video_file
        admin_helper.write(message)

        fps = led_video.get_frame_rate()
        size1 = video.get_size()
        size2 = led_video.get_size()

        log = [size1, size2, fps]
        admin_helper.write(log)