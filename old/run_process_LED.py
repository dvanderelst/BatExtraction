import time
import os
from Library import ExtractInt
from Library import Video
from Library import Utils
import numpy
from matplotlib import pyplot

led_folder = '/media/dieter/Lillith_Backup/leds/2024-2-2'
pck_file = os.path.join(led_folder, 'output.pck')
results = Utils.load_from_pickle(pck_file)
channel1 = results['ch1']
channel2 = results['ch2']
channel3 = results['ch3']
channel4 = results['ch4']



shift1 = Utils.find_best_alignment(channel1, channel2)
shift2 = Utils.find_best_alignment(channel1, channel3)
shift3 = Utils.find_best_alignment(channel1, channel4)


pyplot.figure()
pyplot.plot(channel1[0:100])
pyplot.plot(channel3[0:100])
pyplot.show()