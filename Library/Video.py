from Library import Utils
from tqdm import tqdm
import cv2
import numpy
import re


def get_filename_indices(intensity_data, start_index, samples):
    indices_array = numpy.array(intensity_data['indices'])
    filenames = intensity_data['cam_files']
    indices_needed = range(start_index, start_index + samples)

    requested_filenames = []
    requested_indices = []
    for index_needed in indices_needed:
        intermediate = numpy.argwhere(indices_array <= index_needed)
        file_index = numpy.max(intermediate)
        index_in_file = index_needed - indices_array[file_index]
        selected_filename = filenames[file_index]
        requested_filenames.append(selected_filename)
        requested_indices.append(index_in_file)
    return requested_filenames, requested_indices


def requested2video(requested_filenames, requested_indices, output_filename):
    cap = cv2.VideoCapture(requested_filenames[0])
    ret, frame = cap.read()
    output_height, output_width, _ = frame.shape
    output_fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, output_fps, (output_width, output_height))
    total_frames = len(requested_indices)

    with tqdm(total=total_frames, desc='Processing Frames') as pbar:
        for video_filename, frame_number in zip(requested_filenames, requested_indices):
            cap = cv2.VideoCapture(video_filename)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            out.write(frame)
            pbar.update(1)
            cap.release()
    out.release()


def test_mp4_file(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        cap.release()
        return False
    cap.release()
    return True
    # successful_frames = 0
    # while True:
    #     ret, frame = cap.read()
    #     if ret: successful_frames += 1
    # cap.release()
    # return successful_frames


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

    def get_frame_rate(self):
        fps, _ = self.get_size()
        return fps

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
