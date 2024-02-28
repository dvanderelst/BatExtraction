import os
import time
import numpy
import cv2
from tqdm import tqdm
from matplotlib import pyplot
from matplotlib.widgets import RectangleSelector
from Library import Video
from Library import Utils
from Library import Signal


def concatenate_intensities(file_list, processed=True):
    trace_list = []
    file_start_indices = []
    total_length = 0
    fps = None
    for filename in file_list:
        data = load_intensities(filename)
        int_trace = data['processed']
        if not processed: int_trace = data['intensities']
        trace_list.append(int_trace)
        file_start_indices.append(total_length)
        total_length += len(int_trace)
        fps = data['fps']
    concatenated_trace = numpy.concatenate(trace_list)
    return concatenated_trace, fps , file_start_indices


def process_intensities(intensities, fps, window, do_plot=False, plot_file='', show_fig=False):
    trend = Signal.smooth_with_boxcar(intensities, int(fps * window))
    detrended = intensities - trend
    local_sd = Signal.running_std(detrended, int(fps * window))
    sd_threshold = numpy.max(local_sd) / 10
    detrended = detrended - numpy.mean(detrended)
    blank_removed = detrended * 1.0
    blank_removed[local_sd < sd_threshold] = 0
    if len(plot_file) > 0: do_plot = True
    if do_plot:
        threshold_line = numpy.ones(local_sd.shape) * sd_threshold
        fig, axs = pyplot.subplots(4, 1, sharex=True, figsize=(10, 8))  # Adjust figsize as needed
        # Subplot 1
        axs[0].plot(intensities, label='Intensities')
        axs[0].plot(trend, label='Trend')
        axs[0].legend(loc='best')
        # Subplot 2
        axs[1].plot(detrended, label='Detrended')
        axs[1].legend(loc='best')
        # Subplot 2
        axs[2].plot(local_sd, label='Local SD')
        axs[2].plot(threshold_line, label='sd Threshold')
        axs[2].legend(loc='best')
        # Subplot 3
        axs[3].plot(blank_removed, label='Processed')
        axs[3].legend(loc='best')
        if len(plot_file) > 0: fig.savefig(plot_file)
        if show_fig: pyplot.show()
        if not show_fig: pyplot.close()

    return blank_removed


def save_intensities(intensities, processed, fps, filename):
    numpy.savez(filename, intensities=intensities, processed=processed, fps=fps)


def load_intensities(filename):
    data = numpy.load(filename)
    return data


def get_led_video(video, output_folder):
    basename = video.basename
    led_video_file = os.path.join(output_folder, 'LED_' + basename + '.mp4')
    led_file_exists = os.path.isfile(led_video_file)
    box = get_box(video, output_folder)
    led_video = False
    if led_file_exists:
        led_video = Video.Video(led_video_file)
        size = led_video.get_size()
        if size[0] == 0: led_file_exists = False
    if not led_file_exists:
        make_led_video(video, box, led_video_file)
        time.sleep(0.25)
        led_video = Video.Video(led_video_file)
    return led_video


def get_led_intensities(led_video, output_folder, window=1, save_plot=True):
    basename = led_video.basename
    basename = basename.replace('LED_', '')
    led_intensity_file = os.path.join(output_folder, 'INT_' + basename + '.npz')
    led_intensity_plot = os.path.join(output_folder, 'PLT_' + basename + '.png')
    if not save_plot: led_intensity_plot = False
    capture = led_video.capture
    fps, total_number_of_frames = led_video.get_size()
    intensities = []
    for i in tqdm(range(total_number_of_frames)):
        ret, frame = capture.read()
        mean = numpy.mean(frame)
        intensities.append(mean)
    intensities = numpy.array(intensities)
    processed = process_intensities(intensities, fps, window, plot_file=led_intensity_plot)
    save_intensities(intensities, processed, fps, led_intensity_file)
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
    for i in tqdm(range(total_number_of_frames)):
        ret, frame = capture.read()
        if frame is None: frame = previous_frame * 1
        cropped_frame = frame[y1:y2, x1:x2]
        output.write(cropped_frame)
        previous_frame = frame * 1
    output.release()


def get_box(video, output_folder):
    channel = video.channel
    box_file = os.path.join(output_folder, 'box_channel_' + str(channel) + '.pck')
    box_file_exists = os.path.isfile(box_file)
    if box_file_exists:
        box = Utils.load_from_pickle(box_file)
        print(f"Box loaded from: {box_file}")
    else:
        box = draw_box(video)
        Utils.save_to_pickle(box, box_file)
        print(f"Box saved to: {box_file}")
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
        self.toggle_selector = RectangleSelector(self.ax, self.line_select_callback,
                                                 drawtype='box', useblit=True,
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
