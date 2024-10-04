import os
import time

import numpy
import cv2
from tqdm import tqdm
from matplotlib import pyplot
from matplotlib.widgets import RectangleSelector
from datetime import datetime, timedelta
from Library import Video
from Library import Utils


def get_filename_for_index(intensity_index, intensity_data):
    filenames = intensity_data['cam_files']
    indices = intensity_data['indices']
    fps = intensity_data['fps']
    for i, idx in enumerate(indices):
        if intensity_index >= idx and (i == len(indices) - 1 or intensity_index < indices[i+1]):
            filename = filenames[i]
            delta_time = (intensity_index - indices[i]) / fps
            delta_time = timedelta(seconds=delta_time)
            return filename, delta_time
    return None, None


def concatenate_intensities(file_list, processed=True):
    trace_list = []
    file_start_indices = []
    total_length = 0
    fps = None
    for filename in file_list:
        data = load_intensities(filename)
        intensities = data['intensities']
        trace_list.append(intensities)
        file_start_indices.append(total_length)
        total_length += len(intensities)
        fps = data['fps']
    concatenated_trace = numpy.concatenate(trace_list)
    return concatenated_trace, fps, file_start_indices


def save_intensities(intensities, fps, filename):
    numpy.savez(filename, intensities=intensities, fps=fps)


def load_intensities(filename):
    data = numpy.load(filename)
    return data


def get_led_video(video, channel, admin_helper):
    basename = video.basename
    output_folder = admin_helper.get_output_folder()
    led_output_folder = admin_helper.get_folder(channel, 'led')
    led_output_file = os.path.join(led_output_folder, 'LED_' + basename + '.mp4')
    led_file_exists = os.path.isfile(led_output_file)
    box = get_box(video, admin_helper)
    base_name_led_output_file = os.path.basename(led_output_file)
    led_video = False
    if led_file_exists:
        message = f"LED video exists: {base_name_led_output_file}"
        admin_helper.log(0, message)
        led_video = Video.Video(led_output_file)
        size = led_video.get_size()
        if size[0] == 0: led_file_exists = False
    if not led_file_exists:
        message = f"Creating LED video: {base_name_led_output_file}"
        admin_helper.log(0, message)
        make_led_video(video, box, led_output_file)
        time.sleep(0.25)
        led_video = Video.Video(led_output_file)
    return led_video


def get_led_intensities(led_video, channel, admin_helper):
    base_name_led_output_file = os.path.basename(led_video.filename)
    message = f"Getting intensities for: {base_name_led_output_file}"
    admin_helper.log(0, message)
    basename = led_video.basename
    basename = basename.replace('LED_', '')
    int_output_folder = admin_helper.get_folder(channel, 'int')
    int_output_file = os.path.join(int_output_folder, 'INT_' + basename + '.npz')
    capture = led_video.capture
    fps, total_number_of_frames = led_video.get_size()
    intensities = []
    #for i in tqdm(range(total_number_of_frames)):
    for i in range(total_number_of_frames):
        if i%100 == 0: print('int', led_video.basename, i, '/', total_number_of_frames)
        ret, frame = capture.read()
        mean = numpy.mean(frame)
        intensities.append(mean)
    intensities = numpy.array(intensities)
    save_intensities(intensities, fps, int_output_file)
    return intensities


def make_led_video(video, bounding_box, output_file):
    capture = video.capture
    fps, total_number_of_frames = video.get_size()
    x1, y1, x2, y2 = bounding_box
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)
    width = x2 - x1
    height = y2 - y1

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    size = (int(width), int(height))
    output = cv2.VideoWriter(output_file, fourcc, fps, size)
    previous_frame = None
    #for i in tqdm(range(total_number_of_frames)):
    for i in range(total_number_of_frames):
        if i%100 == 0: print('led', video.basename, i, '/', total_number_of_frames)
        ret, frame = capture.read()
        if frame is None: frame = previous_frame * 1
        cropped_frame = frame[y1:y2, x1:x2]
        output.write(cropped_frame)
        previous_frame = frame * 1
    output.release()


def get_box(video, admin_helper):
    output_folder = admin_helper.get_output_folder()
    channel = video.channel
    box_file = os.path.join(output_folder, 'box_channel_' + str(channel) + '.pck')
    box_file_exists = os.path.isfile(box_file)
    if box_file_exists:
        box = Utils.load_from_pickle(box_file)
        message = f"Box loaded from: {box_file}"
        admin_helper.log(0, message)
    else:
        box = draw_box(video)
        Utils.save_to_pickle(box, box_file)
        message = f"Box saved to: {box_file}"
        admin_helper.log(0, message)
    return box


def draw_box(video, title=None):
    frame = video.get_frame(frame_index=0)
    selector = BoxSelector(frame, title)
    box = selector.get_selected_box()
    box = numpy.array([box[0][0], box[0][1], box[1][0], box[1][1]])
    box = numpy.round(box)
    return box


class BoxSelector:
    def __init__(self, image, title):
        self.image = image
        self.title = title
        self.start_point = None
        self.end_point = None
        self.fig, self.ax = pyplot.subplots()
        self.ax.imshow(self.image)
        self.ax.set_title(self.title)
        self.toggle_selector = RectangleSelector(self.ax, self.line_select_callback, useblit=True,
                                                 button=[1], minspanx=5, minspany=5,
                                                 spancoords='pixels', interactive=True)
        self.fig.canvas.mpl_connect('key_press_event', self.key_press_callback)
        pyplot.show(block=True)

    def line_select_callback(self, eclick, erelease):
        self.start_point = (min(eclick.xdata, erelease.xdata), min(eclick.ydata, erelease.ydata))
        self.end_point = (max(eclick.xdata, erelease.xdata), max(eclick.ydata, erelease.ydata))

    def key_press_callback(self, event):
        if event.key in ['Q', 'q'] and self.toggle_selector.active:
            self.toggle_selector.set_active(False)
            pyplot.close()

    def get_selected_box(self):
        return self.start_point, self.end_point
