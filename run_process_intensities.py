import os
import matplotlib
import numpy

from Library import ExtractInt
from Library import Utils
from matplotlib import pyplot
from Library import Signal

matplotlib.use('TkAgg')
thresholds = {}

# PARAMETERS
drive = "/media/dieter/Panama_2024"
video_folder = 'new_data/video'
output_folder = 'output3'

#thresholds[1] = [60, 120, 15]
#thresholds[2] = [90, 130, 7.5]
#thresholds[3] = [95, 115, 4]
#thresholds[4] = [75, 95, 3.5]

thresholds[1] = [-75, 75, 15]
thresholds[2] = [-75, 75, 7.5]
thresholds[3] = [-75, 75, 4]
thresholds[4] = [-75, 75, 3.5]

############

output_folder = os.path.join(drive, output_folder)
camera_folder = os.path.join(drive, video_folder)

int_files_channels = Utils.get_int_files(output_folder)
cam_files_channels = Utils.get_cam_files(camera_folder)
channel = 1

for channel_ints, channel_cams in zip(int_files_channels, cam_files_channels):
    output_file = os.path.join(output_folder, 'intensity_channel_%s.pck' % channel)
    print(output_file)
    intensities, fps, indices = ExtractInt.concatenate_intensities(channel_ints, processed=False)
    trend = Signal.smooth_with_boxcar(intensities, 50)
    intensities = intensities - trend

    line = numpy.ones(intensities.size)
    lower = line * thresholds[channel][0]
    upper = line * thresholds[channel][1]
    sd_threshold = line * thresholds[channel][2]

    outliers = ((intensities < lower) + (intensities > upper)) > 0
    outliers = Signal.smooth_with_boxcar(outliers, window_size=20)
    outliers = outliers > 0

    processed = intensities * 1.0
    processed[outliers > 0] = numpy.nan
    running_sd = Signal.running_std(processed, window_size=50)
    processed[running_sd < sd_threshold] = numpy.nan
    processed = processed - numpy.nanmean(processed)
    processed = numpy.nan_to_num(processed, 0)

    # Use this plot to determine the cut-offs for the outliers
    pyplot.figure(1)
    pyplot.subplot(2, 2, channel)
    pyplot.plot(intensities)
    pyplot.plot(lower, color='red', alpha=0.5)
    pyplot.plot(upper, color='red', alpha=0.5)
    pyplot.title(channel)

    # Use this plot to determine the cut-offs for the SDs
    pyplot.figure(2)
    pyplot.subplot(2, 2, channel)
    pyplot.plot(running_sd)
    pyplot.plot(sd_threshold, color='red', alpha=0.5)
    pyplot.title(channel)

    # Final result
    pyplot.figure(3)
    pyplot.subplot(2, 2, channel)
    pyplot.plot(processed, color='orange')
    pyplot.title(channel)

    # Make and save results
    result = {}
    result['intensities'] = intensities
    result['processed'] = processed
    result['int_files'] = channel_ints
    result['cam_files'] = channel_cams
    result['indices'] = indices
    result['channel'] = channel
    result['fps'] = int(fps)  # This copies the fps of the last partial trace file in to the results
    Utils.save_to_pickle(result, output_file)

    channel = channel + 1

pyplot.show()
