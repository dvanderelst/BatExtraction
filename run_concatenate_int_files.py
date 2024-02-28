import os
import matplotlib
from Library import ExtractInt
from Library import Utils
from matplotlib import pyplot
matplotlib.use('TkAgg')

# PARAMETERS
drive = "/media/dieter/Panama_2024"
video_folder = 'downloaded_data/2024-2-19'
output_folder = 'output2'
window = 50
############

output_folder = os.path.join(drive, output_folder)
camera_folder = os.path.join(drive, video_folder)

int_files_channels = Utils.get_int_files(output_folder)
cam_files_channels = Utils.get_cam_files(camera_folder)

channel = 1
for channel_ints, channel_cams in zip(int_files_channels, cam_files_channels):
    output_file = os.path.join(output_folder, 'trace_channel_%s.pck' % channel)
    print(output_file)
    intensities, fps, indices = ExtractInt.concatenate_intensities(channel_ints)

    result = {}
    result['intensities'] = intensities
    result['int_files'] = channel_ints
    result['cam_files'] = channel_cams
    result['indices'] = indices
    result['channel'] = channel
    result['fps'] = int(fps) #This copies the fps of the last partial trace file in to the results
    Utils.save_to_pickle(result, output_file)
    channel = channel + 1

    pyplot.figure()
    pyplot.plot(intensities)
    pyplot.show()
