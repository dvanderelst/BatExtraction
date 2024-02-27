from Library import Utils
from Library import Signal
from matplotlib import pyplot
import numpy
import os

# PARAMETERS
drive = "/media/dieter/Panama_2024"
#audio_folder = 'Array_Mmicrotis_search_data/2024_02_02_Mmicrotis_search'
#output_folder = 'output'

audio_folder = 'downloaded_data/2024_02_19_New_script_2ndtry_300Hz'
output_folder = 'output2'
channel = 2
############

audio_folder = os.path.join(drive, audio_folder)
output_folder = os.path.join(drive, output_folder)

trace_file = os.path.join(output_folder, f'trace_channel_{channel}.pck')
trace_data = Utils.load_from_pickle(trace_file)
fps = trace_data['fps']
trace = trace_data['trace']
i = 2

mat_files = Utils.get_mat_files(audio_folder)
data = Utils.read_mat_file(mat_files[i])
audio = data['audio']
sps = data['sps']

average = numpy.mean(audio, axis=1)
selected_samples = average > 0
audio = audio[selected_samples, :]

audio_sync_sigal = (audio[:, -1] > 0.5) * 1.0
audio_sync_sigal = Utils.smooth_with_boxcar(audio_sync_sigal, int(sps/fps))
downsampled_sync_signal = Utils.downsample_signal(audio_sync_sigal, sps, fps)
downsampled_sync_signal = Utils.scale(downsampled_sync_signal)
#downsampled_sync_signal  = (downsampled_sync_signal > 0.5) * 1.0

start_index, cross_corr = Signal.find_best_match(downsampled_sync_signal, trace)
print(start_index)

pyplot.figure()
pyplot.subplot(2,1,1)
pyplot.plot(audio_sync_sigal)
pyplot.subplot(2,1,2)
pyplot.plot(downsampled_sync_signal, '.-')
pyplot.show()

pyplot.figure()
pyplot.plot(cross_corr)
pyplot.show()
