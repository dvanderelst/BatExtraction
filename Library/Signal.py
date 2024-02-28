import numpy
from matplotlib import pyplot as plt


def running_std(arr, window_size):
    rolling_mean = numpy.convolve(arr, numpy.ones(window_size) / window_size, mode='valid')
    rolling_sum_squares = numpy.convolve(arr ** 2, numpy.ones(window_size) / window_size, mode='valid')
    rolling_var = rolling_sum_squares - rolling_mean ** 2
    rolling_var = numpy.maximum(rolling_var, 0)
    rolling_std = numpy.sqrt(rolling_var)
    pad_left = (window_size - 1) // 2
    pad_right = window_size - 1 - pad_left
    rolling_std = numpy.pad(rolling_std, (pad_left, pad_right), mode='edge')
    return rolling_std


def smooth_with_boxcar(array, window_size):
    if window_size % 2 == 0: window_size += 1
    reflected_array = numpy.pad(array, window_size // 2, mode='reflect')
    kernel = numpy.ones(window_size) / window_size
    smoothed_array = numpy.convolve(reflected_array, kernel, mode='valid')
    return smoothed_array


def scale(arr):
    scaled_arr = (arr - arr.min()) / (arr.max() - arr.min())
    return scaled_arr


def downsample_signal(signal, original_rate, new_rate):
    downsampling_factor = int(original_rate / new_rate)
    downsampled_signal = signal[::downsampling_factor]
    return downsampled_signal


def upsample_signal(signal, original_rate, new_rate):
    ratio = new_rate / original_rate
    original_time = numpy.arange(len(signal))
    new_time = numpy.arange(0, len(signal), 1 / ratio)
    upsampled_signal = numpy.interp(new_time, original_time, signal)
    return upsampled_signal


def find_best_match(short_signal, long_signal):
    cross_corr = numpy.correlate(long_signal, short_signal, mode='full')
    best_match_index = numpy.argmax(cross_corr)
    start_index = best_match_index - len(short_signal) + 1

    plt.figure()
    plt.plot(long_signal, label='Long Array')
    plt.plot(numpy.arange(start_index, start_index + len(short_signal)), short_signal, label='Short Array Shifted')
    plt.legend()
    plt.show()

    return start_index, cross_corr
