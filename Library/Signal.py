import numpy as np
from matplotlib import pyplot as plt
from Library import Utils
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# def find_alignment_index(short_signal, long_signal):
#     long_signal = np.nan_to_num(long_signal)
#     short_signal = np.nan_to_num(short_signal)
#     distance, path = fastdtw(long_signal, short_signal, dist=euclidean)
#     start_index = path[0][1]
#
#     plt.figure()
#     plt.plot(long_signal, label='Long Array')
#     plt.plot(np.arange(start_index, start_index + len(short_signal)), short_signal, label='Short Array Shifted')
#     plt.legend()
#     plt.show()
#
#     return start_index

def find_best_match(short_signal, long_signal):
    long_signal = long_signal - 0.5
    short_signal = short_signal - 0.5

    cross_corr = np.correlate(long_signal, short_signal, mode='full')
    best_match_index = np.argmax(cross_corr)
    start_index = best_match_index - len(short_signal) + 1

    plt.figure()
    plt.plot(long_signal, label='Long Array')
    plt.plot(np.arange(start_index, start_index + len(short_signal)), short_signal, label='Short Array Shifted')
    plt.legend()
    plt.show()


    return start_index, cross_corr