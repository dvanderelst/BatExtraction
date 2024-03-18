import os
import pickle
import re
import shutil
import time
import natsort
from scipy.io import loadmat
from datetime import datetime
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


def print_dict_fields(dictionary, output_file=None):
    max_key_length = max(len(str(key)) for key in dictionary.keys())
    output_lines = []
    for key, value in dictionary.items():
        output_line = f"{key:{max_key_length}}: {value}"
        output_lines.append(output_line)

    for line in output_lines:
        print(line)

    if output_file:
        with open(output_file, 'w') as file:
            for line in output_lines:
                file.write(line + '\n')


def get_audio_time(filename):
    pattern = r'(\d{4}_\d{2}_\d{2})_(\d{2}_\d{2}_\d{2})'
    match = re.search(pattern, filename)
    date_str = match.group(1)
    time_str = match.group(2)
    datetime_str = f"{date_str}_{time_str}"
    return datetime.strptime(datetime_str, '%Y_%m_%d_%H_%M_%S')


def remove_items_by_index(lst, indices_to_remove):
    updated_list = [item for i, item in enumerate(lst) if i not in indices_to_remove]
    removed_items = [lst[i] for i in indices_to_remove]
    return updated_list, removed_items


def purge_cam_files(cam_files, remove1=[], remove2=[], remove3=[], remove4=[]):
    new1, r1 = remove_items_by_index(cam_files[0], remove1)
    new2, r2 = remove_items_by_index(cam_files[1], remove2)
    new3, r3 = remove_items_by_index(cam_files[2], remove3)
    new4, r4 = remove_items_by_index(cam_files[3], remove4)
    new = [new1, new2, new3, new4]
    removed = r1 + r2 + r3 + r4
    return new, removed


def visualize_cam_file_durations(cam_files, output_folder, prefix=''):
    one_minute = timedelta(minutes=1)
    longest = longest_list_length(cam_files)
    min_start_time, max_end_time = get_min_max_times(cam_files)
    channel = 1
    plt.figure(figsize=(20,10))
    for channel_files in cam_files:
        plt.subplot(2, 2, channel)
        for j, file in enumerate(channel_files):
            start, end = get_times_from_file(file)
            plot_times(start, end, y_position=j)
        plt.ylim(-1, longest)
        plt.xlim(min_start_time - one_minute, max_end_time + one_minute)
        plt.title(channel)
        channel = channel + 1
    output_file = os.path.join(output_folder, prefix + 'timing.png')
    plt.savefig(output_file)
    plt.tight_layout()
    plt.show()


def longest_list_length(list_of_lists):
    max_length = 0
    for sublist in list_of_lists:
        length = len(sublist)
        if length > max_length:
            max_length = length
    return max_length


def get_min_max_times(filenames):
    min_start_time = None
    max_end_time = None
    for channel_files in filenames:
        for filename in channel_files:
            start_time, end_time = get_times_from_file(filename)
            if min_start_time is None or start_time < min_start_time:
                min_start_time = start_time
            if max_end_time is None or end_time > max_end_time:
                max_end_time = end_time
    return min_start_time, max_end_time


def get_times_from_file(filename):
    pattern = r'(\d{14})_(\d{14})\.mp4$'
    match = re.search(pattern, filename)
    start_datetime_str = match.group(1)
    end_datetime_str = match.group(2)
    start_datetime = datetime.strptime(start_datetime_str, '%Y%m%d%H%M%S')
    end_datetime = datetime.strptime(end_datetime_str, '%Y%m%d%H%M%S')
    return start_datetime, end_datetime


def plot_times(start_time, end_time, y_position, color='blue'):
    plt.plot([start_time, start_time], [y_position - 0.1, y_position + 0.1], color=color)  # Start time vertical line
    plt.plot([end_time, end_time], [y_position - 0.1, y_position + 0.1], color=color)  # End time vertical line
    plt.plot([start_time, end_time], [y_position, y_position], color=color,
             label='label')  # Horizontal line between start and end


def read_mat_file(file_path):
    start = time.time()
    audio = None
    pattern = re.compile(r'data\d{2}')
    data = loadmat(file_path)
    for key, value in data.items():
        if pattern.match(key):
            audio = value
            break
    result = {}
    result['audio'] = audio
    result['sps'] = data['sampleRate'][0][0]
    end = time.time()
    #print('read mat time:', end - start)
    return result


def list_to_line(lst):
    return ', '.join(map(str, lst)) + '\n'


def split_filename(file_path):
    path, full_filename = os.path.split(file_path)
    basename, extension = os.path.splitext(full_filename)
    return path, basename, extension


def remove_files_containing_substrings(folder_path, substrings):
    # Get list of files in the folder
    files = os.listdir(folder_path)

    # Iterate through files
    for file in files:
        # Check if any of the substrings are found in the file name
        if any(substring in file for substring in substrings):
            file_path = os.path.join(folder_path, file)
            # Remove the file
            os.remove(file_path)
            print(f"Removed file: {file_path}")


def get_basename(file_path):
    path, basename, extension = split_filename(file_path)
    return basename


def get_basenames(file_paths):
    basenames = []
    for file_path in file_paths:
        basename = get_basename(file_path)
        basenames.append(basename)
    return basenames


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
        #print(f"Object loaded from pickle file: {file_path}")
        return obj
    except Exception as e:
        #print(f"Error loading object from pickle file: {e}")
        return None


def create_empty_folder(folder_path, clear_existing=False):
    try:
        if os.path.exists(folder_path) and clear_existing:
            shutil.rmtree(folder_path)
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"Error creating empty folder: {e}")


def get_mat_files(directory):
    mat_files = []
    for file in os.listdir(directory):
        if file.endswith(".mat"):
            mat_files.append(os.path.join(directory, file))
    mat_files = natsort.natsorted(mat_files)
    return mat_files


def get_int_files(directory):
    int_files = []
    files = os.listdir(directory)
    for file in files:
        if file.startswith('INT'): int_files.append(file)

    int_files_full = []
    for int_file in int_files:
        int_file_full = os.path.join(directory, int_file)
        int_files_full.append(int_file_full)

    file_names = split_files_by_channel(int_files_full)
    return file_names


def get_cam_files(directory):
    directory = os.path.abspath(directory)
    files = os.listdir(directory)
    mp4_files = [file for file in files if file.lower().endswith('.mp4')]

    mp4_files_full = []
    for mp4_file in mp4_files:
        mp4_file_full = os.path.join(directory, mp4_file)
        mp4_files_full.append(mp4_file_full)

    file_names = split_files_by_channel(mp4_files_full)
    return file_names


def split_files_by_channel(file_names):
    ch1 = [filename for filename in file_names if '_ch1_' in filename]
    ch2 = [filename for filename in file_names if '_ch2_' in filename]
    ch3 = [filename for filename in file_names if '_ch3_' in filename]
    ch4 = [filename for filename in file_names if '_ch4_' in filename]

    ch1 = natsort.natsorted(ch1)
    ch2 = natsort.natsorted(ch2)
    ch3 = natsort.natsorted(ch3)
    ch4 = natsort.natsorted(ch4)

    file_names = [ch1, ch2, ch3, ch4]
    return file_names
