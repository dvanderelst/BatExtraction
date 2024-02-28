import os
import pickle
import re
import shutil

import natsort
from scipy.io import loadmat


def read_mat_file(file_path):
    audio = None
    pattern = re.compile(r'data\d{2}')
    data = loadmat(file_path)
    for key, value in data.items():
        if pattern.match(key): audio = value
    result = {}
    result['audio'] = audio
    result['sps'] = data['sampleRate'][0][0]
    # result['raw'] = data
    return result


def list_to_line(lst):
    return ', '.join(map(str, lst)) + '\n'


def split_filename(file_path):
    path, full_filename = os.path.split(file_path)
    basename, extension = os.path.splitext(full_filename)
    return path, basename, extension


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
        if os.path.exists(folder_path) and clear_existing:
            shutil.rmtree(folder_path)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Empty folder created at: {folder_path}")
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
