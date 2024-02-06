from Library import Utils
import cv2
import numpy
import re


class Video:
    def __init__(self, filename):
        path, basename, extension = Utils.split_filename(filename)
        self.path = path
        self.basename = basename
        self.extension = extension
        self.filename = filename
        self.frame_index = 0
        self.properties = parse_filename(filename)
        self.channel = self.properties['channel']
        self.capture = cv2.VideoCapture(filename)


    def get_size(self):
        capture = self.capture
        fps = capture.get(cv2.CAP_PROP_FPS)
        fps = int(numpy.round(fps))
        total_number_of_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        return fps, total_number_of_frames

    def get_frame(self, frame_index=None):
        if frame_index is not None: self.set_frame_index(frame_index)
        _, image = self.capture.read()
        if image is None: return False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.frame_index = self.frame_index + 1
        return image

    def set_frame_index(self, frame_index=0):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        self.frame_index = frame_index


def parse_filename(filename):
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




