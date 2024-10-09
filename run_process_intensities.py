import os
import numpy
from matplotlib import pyplot
from scipy.io import savemat

from Library import FolderManager
from Library import ExtractInt
from Library import Utils
from Library import Settings
from Library import Signal

video_folder = 'Mmicrotis_video/2024_03_17_Ind05'

create_plots = False

thresholds = {}
thresholds[1] = Settings.thresholds1
thresholds[2] = Settings.thresholds2
thresholds[3] = Settings.thresholds3
thresholds[4] = Settings.thresholds4

folder_manager = FolderManager.FolderManager(video_folder, empty_log_folder=False)

led_files = Utils.get_led_files(folder_manager)
int_files = Utils.get_int_files(folder_manager)
vid_files = Utils.get_video_files(folder_manager)

full_output = {}
channel = 1
pyplot.close('all')
output_folder = folder_manager.get_output_folder()
output_file = os.path.join(output_folder, 'processed_intensities.pck')
output_file_mat = os.path.join(output_folder, 'processed_intensities.mat')
for channel_led_files, channel_int_files, channel_vid_files in zip(led_files, int_files, vid_files):
    raw_intensities, fps, indices = ExtractInt.concatenate_intensities(channel_int_files)
    trend = Signal.smooth_with_boxcar(raw_intensities, 50)
    intensities = raw_intensities - trend

    if create_plots:
        pyplot.figure()
        pyplot.subplot(2, 1, 1)
        pyplot.plot(raw_intensities, label='Raw intensities')
        pyplot.plot(trend, label='Trend')
        pyplot.title('Raw intensities, channel %s' % channel)
        pyplot.subplot(2, 1, 2)
        pyplot.plot(intensities, label='Intensities')
        pyplot.title('Intensities, corrected for trend, channel %s' % channel)
        pyplot.legend()
        pyplot.show()

    line = numpy.ones(intensities.size)
    lower = line * thresholds[channel][0]
    upper = line * thresholds[channel][1]
    sd_threshold = line * thresholds[channel][2]

    # Get outliers based on the lower and upper thresholds
    outliers = ((intensities < lower) + (intensities > upper)) > 0
    outliers = Signal.smooth_with_boxcar(outliers, window_size=20)
    outliers = outliers > 0

    # Get time points where the standard deviation is below the threshold
    # This detects sections when the LED is off
    processed = intensities * 1.0
    processed[outliers > 0] = numpy.nan
    running_sd = Signal.running_std(processed, window_size=50)
    led_off = running_sd < sd_threshold

    # Apply the SD threshold to the data
    processed[running_sd < sd_threshold] = numpy.nan
    processed = processed - numpy.nanmean(processed)
    processed = numpy.nan_to_num(processed, 0)

    binary = processed > numpy.nanmean(processed)

    # Use this plot to determine the cut-offs for the outliers
    if create_plots:
        pyplot.figure()
        pyplot.plot(intensities, label='Intensities')
        pyplot.plot(lower, color='red', alpha=0.5, label='Lower cutoff')
        pyplot.plot(upper, color='red', alpha=0.5, label='Upper cutoff')
        pyplot.plot(sd_threshold, color='green', linestyle='--', alpha=0.5, label='SD threshold')
        pyplot.plot(running_sd, color='green', alpha=0.5, label='Running SD')
        pyplot.title(channel)
        pyplot.legend()
        pyplot.show()

        pyplot.figure()
        pyplot.plot(processed, color='orange')
        pyplot.title('Processed, channel %s' % channel)
        pyplot.show()

        pyplot.figure()
        pyplot.plot(binary, color='orange')
        pyplot.title('Binary, channel %s' % channel)
        pyplot.show()

    # Chop the binary signal into sections
    binary_sections = []
    nr_indices = len(indices)
    for i in range(nr_indices):
        begin_index = indices[i]
        end_index = len(binary)
        if i < nr_indices - 1: end_index = indices[i + 1]
        section = binary[begin_index:end_index]
        binary_sections.append(section)

    channel_vid_files_basenames = []
    for vid_file in channel_vid_files:
        base_name = os.path.basename(vid_file)
        channel_vid_files_basenames.append(base_name)


    result = {}
    result['intensities'] = intensities
    result['processed'] = processed
    result['binary'] = binary
    result['binary_sections'] = binary_sections
    result['channel_int_files'] = channel_int_files
    result['channel_vid_files'] = channel_vid_files
    result['channel_vid_files_basenames'] = channel_vid_files_basenames
    result['channel_led_files'] = channel_led_files
    result['indices'] = indices
    result['channel'] = channel
    result['fps'] = int(fps)  # This copies the fps of the last partial trace file in to the results
    full_output[f'channel{channel}'] = result
    channel = channel + 1

# Write some text to add to the full_output dictionary describing each field
full_output['description'] = ('Each channel has the following fields:\n' \
                              '-- intensities: Raw intensities of the LED for all videos\n' \
                             '-- processed: Raw intensities for all videos corrected for slow trends\n' \
                             '-- binary: Processed intensities above the mean (1 = LED is on in frame)\n' \
                             '-- binary_sections: The binary intensities split into sections, one for each video file\n' \
                             '-- channel_int_files: Intensity files (files I write as intermediate results)\n' \
                             '-- channel_vid_files: Video files (the camera video files in the order processed)\n' \
                             '-- channel_vid_files_basenames: Camera video file basenames (same as previous, but just the basenames, for convience)\n' \
                             '-- channel_led_files: LED files (files I write as intermediate results. These are mp4s of the isolated LED)\n' \
                             '-- indices: Indices of the start of each video in the full sequence of intensity data (intensities, processed, binary)\n' \
                             '-- channel: Channel number\n' \
                             '-- fps: Frames per second (of the last video processed. These might not be the same for all video files)')

Utils.save_to_pickle(full_output, output_file)
print(full_output['description'])
savemat(output_file_mat, full_output)
#Test
test = full_output['channel1']['binary_sections'][2]