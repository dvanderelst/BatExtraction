from Library import ExtractLed
from Library import Utils
import os

# PARAMETERS
drive = "/media/dieter/Panama_2024"
video_folder = 'Video_Mmicrotis_search_data/N883A6/2024-2-2'
output_folder = 'output'
window = 500
############

output_folder = os.path.join(drive, output_folder)
camera_folder = os.path.join(drive, video_folder)

trc_files = Utils.get_trc_files(output_folder)
cam_files = Utils.get_cam_files(camera_folder)

channel = 1

for trc, cam in zip(trc_files, cam_files):
    output_file = os.path.join(output_folder, 'trace_channel_%s.pck' % channel)
    print(output_file)
    trace, fps, indices = ExtractLed.concatenate_traces(trc)
    trace = ExtractLed.post_process_trace(trace, window=window, do_plot=True)

    result = {}
    result['trace'] = trace
    result['trc_files'] = trc
    result['cam_files'] = cam
    result['indices'] = indices
    result['channel'] = channel
    result['fps'] = int(fps) #This copies the fps of the last partial trace file in to the results
    Utils.save_to_pickle(result, output_file)
    channel = channel + 1
