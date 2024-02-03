import re
import natsort
import os
import shutil
import pickle
import numpy

def find_best_alignment(signal1, signal2):
    max_len = max(len(signal1), len(signal2))
    signal1_padded = numpy.pad(signal1, (0, max_len - len(signal1)))
    signal2_padded = numpy.pad(signal2, (0, max_len - len(signal2)))
    # Calculate the cross-correlation
    cross_corr = numpy.correlate(signal1_padded, signal2_padded, mode='full')
    # Find the index of the maximum correlation
    shift = numpy.argmax(cross_corr) - (max_len - 1)
    return shift

def save_to_pickle(obj, file_path):
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(obj, file)
        print(f"Object saved to pickle file: {file_path}")
    except Exception as e:
        print(f"Error saving object to pickle file: {e}")

def load_from_pickle(file_path):
    try:
        with open(file_path, 'rb') as file:
            obj = pickle.load(file)
        print(f"Object loaded from pickle file: {file_path}")
        return obj
    except Exception as e:
        print(f"Error loading object from pickle file: {e}")
        return None


def create_empty_folder(folder_path, clear_existing=False):
    try:
        # If the folder exists and clear_existing is True, remove the folder and its contents
        if os.path.exists(folder_path) and clear_existing:
            shutil.rmtree(folder_path)

        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        print(f"Empty folder created at: {folder_path}")
    except Exception as e:
        print(f"Error creating empty folder: {e}")

def get_mp4_files(directory=None):
    directory = os.path.abspath(directory)
    files = os.listdir(directory)
    mp4_files = [file for file in files if file.lower().endswith('.mp4')]

    ch1 = [filename for filename in mp4_files if 'ch1' in filename]
    ch2 = [filename for filename in mp4_files if 'ch2' in filename]
    ch3 = [filename for filename in mp4_files if 'ch3' in filename]
    ch4 = [filename for filename in mp4_files if 'ch4' in filename]

    ch1 = natsort.natsorted(ch1)
    ch2 = natsort.natsorted(ch2)
    ch3 = natsort.natsorted(ch3)
    ch4 = natsort.natsorted(ch4)

    file_names = [ch1, ch2, ch3, ch4]
    return file_names

def get_time_stamp(filename):
    timestamp_pattern = r'\d{14}'
    match = re.search(timestamp_pattern, filename)
    timestamp = match.group()
    year = timestamp[0:4]
    month = timestamp[4:6]
    day = timestamp[6:8]
    hour = timestamp[8:10]
    minute = timestamp[10:12]
    second = timestamp[12:]

    if 'ch1' in filename: channel = 1
    if 'ch2' in filename: channel = 2
    if 'ch3' in filename: channel = 3
    if 'ch4' in filename: channel = 4

    result = {}
    result['year'] = int(year)
    result['month'] = int(month)
    result['day'] = int(day)
    result['hour'] = int(hour)
    result['minute'] = int(minute)
    result['second'] = int(second)
    result['channel'] = int(channel)
    return result
