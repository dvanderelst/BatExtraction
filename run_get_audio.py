from Library import Utils
from Library import Signal
from matplotlib import pyplot
import numpy
import os

# PARAMETERS
drive = "/media/dieter/Panama_2024"
# audio_folder = 'Array_Mmicrotis_search_data/2024_02_02_Mmicrotis_search'
# output_folder = 'output'

audio_folder = '/media/dieter/Panama_2024/downloaded_data/wetransfer_2024_02_19_old_contin_script_25hz-zip_2024-02-20_1716/2024_02_19_Old_contin_script_100Hz'
output_folder = 'output2'
channel = 2
############

audio_folder = os.path.join(drive, audio_folder)
output_folder = os.path.join(drive, output_folder)

trace_file = os.path.join(output_folder, f'trace_channel_{channel}.pck')
intensity_data = Utils.load_from_pickle(trace_file)
fps = intensity_data['fps']
intensities = intensity_data['intensities']
i = 1

mat_files = Utils.get_mat_files(audio_folder)
data = Utils.read_mat_file(mat_files[i])
audio = data['audio']
sps = data['sps']

average = numpy.mean(audio, axis=1)
selected_samples = average > 0
audio = audio[selected_samples, :]

audio_sync_sigal = (audio[:, -1] > 0.5) * 1.0
audio_sync_sigal = Signal.smooth_with_boxcar(audio_sync_sigal, int(sps / fps))

downsampled_sync_signal = Signal.downsample_signal(audio_sync_sigal, sps, fps)
downsampled_sync_signal = Signal.scale(downsampled_sync_signal)

intensities = intensities[10000:]
intensities = Signal.scale(intensities)


start_index, cross_corr = Signal.find_best_match(downsampled_sync_signal, intensities)
print(start_index)

pyplot.figure()
pyplot.subplot(2, 1, 1)
pyplot.plot(audio_sync_sigal)
pyplot.subplot(2, 1, 2)
pyplot.plot(downsampled_sync_signal, '.-')
pyplot.show()

pyplot.figure()
pyplot.plot(cross_corr)
pyplot.show()

samples = len(downsampled_sync_signal)
start = start_index
end = start + samples
segment = intensities[start:end]

pyplot.figure()
pyplot.scatter(segment, downsampled_sync_signal)
pyplot.figure()