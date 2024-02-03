import os
import re
from Library import Settings

def get_mp4_files(directory=None):
    if directory is None: directory = Settings.video_folder
    directory = os.path.abspath(directory)
    files = os.listdir(directory)
    mp4_files = [file for file in files if file.lower().endswith('.mp4')]
    return mp4_files

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
    result = {}
    result['year'] = int(year)
    result['month'] = int(month)
    result['day'] = int(day)
    result['hour'] = int(hour)
    result['minute'] = int(minute)
    result['second'] = int(second)
    return result
