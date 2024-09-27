from Library import Signal
from Library import ExtractInt
from Library import Utils
from Library import Video
from Library import Settings
from matplotlib import pyplot
import shutil
import numpy
import os


def match_audio(audio_file, write_video=True):
    audio_file_time = Utils.get_audio_time(audio_file)
    audio_file_basename = Utils.get_basename(audio_file)
    print('Audio file basename:', audio_file_basename)

    drive = Settings.drive
    output_folder = Settings.output_folder
    output_folder = os.path.join(drive, output_folder)
    result_folder = Settings.result_folder
    result_folder = os.path.join(drive, result_folder, audio_file_basename)
    video_channels = [1, 2, 3, 4]

    Utils.create_empty_folder(result_folder)

    mat_data = Utils.read_mat_file(audio_file)
    audio_signals = mat_data['audio']
    audio_sps = mat_data['sps']

    average = numpy.mean(audio_signals, axis=1)
    raw_length = len(average)
    selected_samples = average > 0
    audio_signals = audio_signals[selected_samples, :]

    # We use the camera fps from the first channel for all channels.
    # This enables to subsample the sync signal once for all channels.
    intensity_file = os.path.join(output_folder, f'intensity_channel_1.pck')
    intensity_data = Utils.load_from_pickle(intensity_file)
    camera_fps = intensity_data['fps']

    smoothing_window = int(0.5 * (audio_sps / camera_fps))
    audio_sync_sigal = (audio_signals[:, -1] > 0.5) * 1.0
    audio_sync_sigal = Signal.smooth_with_boxcar(audio_sync_sigal, smoothing_window)
    downsampled_sync_signal = Signal.downsample_signal(audio_sync_sigal, audio_sps, camera_fps)
    downsampled_sync_signal = Signal.scale(downsampled_sync_signal)


    shutil.copy(audio_file, result_folder)
    output_lines = []
    distinctiveness_log = []
    for video_channel in video_channels:
        intensity_file = os.path.join(output_folder, f'intensity_channel_{video_channel}.pck')
        intensity_data = Utils.load_from_pickle(intensity_file)

        processed_intensities = intensity_data['processed']
        processed_intensities = Signal.scale(processed_intensities)

        start_index, cross_corr = Signal.find_best_match(downsampled_sync_signal, processed_intensities)
        selected_file, delta_time = ExtractInt.get_filename_for_index(start_index, intensity_data)
        start, end = Utils.get_times_from_file(selected_file)
        error = (start + delta_time) - audio_file_time
        error = error.total_seconds()

        samples = len(downsampled_sync_signal)
        start_sample = start_index
        end_sample = start_index + samples
        segment = processed_intensities[start_sample:end_sample]

        median_cross_correlation = numpy.median(cross_corr)
        max_cross_correlation = numpy.max(cross_corr)
        distinctiveness = max_cross_correlation - median_cross_correlation

        sync_signal_lengths = (raw_length, len(audio_sync_sigal), len(downsampled_sync_signal))

        log_result = {
            'Audio file': audio_file,
            'Audio lengths': str(sync_signal_lengths),
            'Audio sample rate': audio_sps,
            'Start time of audio file': audio_file_time,
            'Channel': video_channel,
            'Video sample rate': camera_fps,
            'Start time of matched video': start,
            'Time since start of matched video': delta_time,
            'Matched start of audio': start + delta_time,
            'Error': error,
            'Start_index in intensity trace': start_index,
            'Distinctiveness': distinctiveness
        }

        output_lines.append(f"Channel{video_channel}")
        output_lines += Utils.print_dict_fields(log_result, output_file=None)
        distinctiveness_log.append(distinctiveness)

        pyplot.figure()
        pyplot.subplot(2, 1, 1)
        pyplot.plot(audio_sync_sigal)
        pyplot.title('audio_sync_sigal')
        pyplot.subplot(2, 1, 2)
        pyplot.plot(downsampled_sync_signal, '.-')
        pyplot.title('downsampled_sync_signal')
        pyplot.show()


        pyplot.figure()
        pyplot.plot(cross_corr)
        pyplot.title(f'cross_corr, Channel {video_channel}')
        cross_correlation_filename = f"cross_ch{video_channel}.png"
        cross_correlation_filename = os.path.join(result_folder, cross_correlation_filename)
        pyplot.savefig(cross_correlation_filename)
        pyplot.show()

        pyplot.figure()
        pyplot.scatter(segment, downsampled_sync_signal, alpha=0.25)
        pyplot.show()

        if write_video:
            requested_filenames, requested_indices = Video.get_filename_indices(intensity_data, start_index, samples)
            result_video_filename = f"video_ch{video_channel}.mkv"
            result_video_filename = os.path.join(result_folder, result_video_filename)
            Video.requested2video(requested_filenames, requested_indices, output_filename=result_video_filename)

        pyplot.close('all')

    result_text_file = 'output.txt'
    result_text_file = os.path.join(result_folder, result_text_file)
    fl = open(result_text_file, 'w')
    for x in output_lines: fl.write(x + '\n')
    fl.close()

    return_results = {}
    return_results['result_folder'] = result_folder
    return_results['camera_fps'] = camera_fps
    return_results['distinctiveness_log'] = distinctiveness_log
    return return_results
