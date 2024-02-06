import re
import natsort
import os
import shutil
import pickle

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

def get_camera_files(directory=None):
    directory = os.path.abspath(directory)
    files = os.listdir(directory)
    mp4_files = [file for file in files if file.lower().endswith('.mp4')]

    mp4_files_full = []
    for mp4_file in mp4_files:
        mp4_file_full = os.path.join(directory, mp4_file)
        mp4_files_full.append(mp4_file_full)

    ch1 = [filename for filename in mp4_files_full if 'ch1' in filename]
    ch2 = [filename for filename in mp4_files_full if 'ch2' in filename]
    ch3 = [filename for filename in mp4_files_full if 'ch3' in filename]
    ch4 = [filename for filename in mp4_files_full if 'ch4' in filename]

    ch1 = natsort.natsorted(ch1)
    ch2 = natsort.natsorted(ch2)
    ch3 = natsort.natsorted(ch3)
    ch4 = natsort.natsorted(ch4)

    file_names = [ch1, ch2, ch3, ch4]
    return file_names

