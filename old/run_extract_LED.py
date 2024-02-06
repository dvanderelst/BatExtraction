import time
import os
from Library import ExtractLed
from Library import Video
from Library import Utils
from matplotlib import pyplot


max_frame = 10000000
video_folder = '/media/dieter/Lillith_Backup/N883A6/2024-2-2'
led_folder = '/media/dieter/Lillith_Backup/leds/2024-2-2'
clear_output = True
channels = [1, 2, 3, 4]

log_file = os.path.join(led_folder, 'log.txt')
pck_file = os.path.join(led_folder, 'output.pck')
files = Utils.get_mp4_files(video_folder)
Utils.create_empty_folder(led_folder, clear_existing=clear_output)

ch1_files = files[0][0:3]
ch2_files = files[1][0:3]
ch3_files = files[2][0:3]
ch4_files = files[3][0:3]

first_ch1 = ch1_files[0]
first_ch2 = ch2_files[0]
first_ch3 = ch3_files[0]
first_ch4 = ch4_files[0]

first_ch1_video = Video.Video(video_folder=video_folder, filename=first_ch1)
first_ch2_video = Video.Video(video_folder=video_folder, filename=first_ch2)
first_ch3_video = Video.Video(video_folder=video_folder, filename=first_ch3)
first_ch4_video = Video.Video(video_folder=video_folder, filename=first_ch4)

box_ch1 = ExtractLed.draw_box(first_ch1_video, title='Channel 1')
box_ch2 = ExtractLed.draw_box(first_ch2_video, title='Channel 2')
box_ch3 = ExtractLed.draw_box(first_ch3_video, title='Channel 3')
box_ch4 = ExtractLed.draw_box(first_ch4_video, title='Channel 4')

## CHANNEL 1
if 1 in channels:
    fl = open(log_file, 'a')
    fl.write(time.asctime() + '\n')
    fl.write(str(ch1_files) + '\n')
    fl.close()
    fps, _ = first_ch1_video.get_size()
    result1 = ExtractLed.extract_led_multiple(ch1_files, box_ch1, video_folder, max_frame)
    result1_file = os.path.join(led_folder, 'ch1.wav')
    ExtractLed.write_wav(result1, result1_file, fps)

## CHANNEL 2
if 2 in channels:
    fl = open(log_file, 'a')
    fl.write(time.asctime() + '\n')
    fl.write(str(ch2_files) + '\n')
    fl.close()
    fps, _ = first_ch2_video.get_size()
    result2 = ExtractLed.extract_led_multiple(ch2_files, box_ch2, video_folder, max_frame)
    result2_file = os.path.join(led_folder, 'ch2.wav')
    ExtractLed.write_wav(result2, result2_file, fps)

## CHANNEL 3
if 3 in channels:
    fl = open(log_file, 'a')
    fl.write(time.asctime() + '\n')
    fl.write(str(ch3_files) + '\n')
    fl.close()
    fps, _ = first_ch3_video.get_size()
    result3 = ExtractLed.extract_led_multiple(ch3_files, box_ch3, video_folder, max_frame)
    result3_file = os.path.join(led_folder, 'ch3.wav')
    ExtractLed.write_wav(result3, result3_file, fps)

## CHANNEL 4
if 4 in channels:
    fl = open(log_file, 'a')
    fl.write(time.asctime() + '\n')
    fl.write(str(ch4_files) + '\n')
    fl.close()
    fps, _ = first_ch4_video.get_size()
    result4 = ExtractLed.extract_led_multiple(ch4_files, box_ch4, video_folder, max_frame)
    result4_file = os.path.join(led_folder, 'ch4.wav')
    ExtractLed.write_wav(result4, result4_file, fps)

pyplot.figure()
pyplot.subplot(2, 2, 1)
if 1 in channels: pyplot.plot(result1)
pyplot.subplot(2, 2, 2)
if 2 in channels: pyplot.plot(result2)
pyplot.subplot(2, 2, 3)
if 3 in channels: pyplot.plot(result3)
pyplot.subplot(2, 2, 4)
if 4 in channels: pyplot.plot(result4)
pyplot.show()

result = {}
result['ch1'] = result1
result['ch2'] = result2
result['ch3'] = result3
result['ch4'] = result4

Utils.save_to_pickle(result, pck_file)



