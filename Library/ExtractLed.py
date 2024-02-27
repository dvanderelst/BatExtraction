import os
import time
import numpy
import cv2
from tqdm import tqdm
from matplotlib import pyplot
import plotly.graph_objs as go
from matplotlib.widgets import RectangleSelector
from Library import Video
from Library import Utils
from plotly.subplots import make_subplots
import wave

def post_process_trace(trace, do_plot=False, window=250, led_video=False, output_folder=False):
    smoothed_trace = Utils.smooth_with_boxcar(trace, window)
    difference = trace - smoothed_trace

    # Get outliers
    overall_std = numpy.std(difference)
    upper = numpy.ones(difference.shape) * overall_std * 3
    #lower = numpy.ones(difference.shape) * overall_std * 3 * -1

    #outliers = ((difference < lower) + (difference > upper)) > 0
    outliers = (difference > upper) > 0
    outliers = Utils.smooth_with_boxcar(outliers, window)
    outliers = (outliers > 0) * 1.0

    running_std = Utils.running_std(difference, window)
    running_std[outliers > 0] = numpy.mean(running_std)
    std_running_std = numpy.std(running_std)
    constants = (running_std <= std_running_std) * 1.0

    final = difference + 0.5 #1.0 * (difference > 0)
    final[outliers > 0] = numpy.nan
    final[constants > 0] = numpy.nan
    final = numpy.nan_to_num(final, nan=0.5)

    if do_plot:
        fig, axs = pyplot.subplots(4, 1, sharex=True, figsize=(10, 8))  # Adjust figsize as needed

        # Subplot 1
        axs[0].plot(trace, label='Trace')
        axs[0].plot(smoothed_trace, label='Smoothed Trace')
        axs[0].legend(loc='best')

        # Subplot 2
        axs[1].plot(difference, label='Difference')
        axs[1].plot(upper, label='Upper Threshold')
        #axs[1].plot(lower, label='Lower Threshold')
        axs[1].plot(running_std, label='Running STD')
        axs[1].legend(loc='best')

        # Subplot 3
        axs[2].plot(outliers, label='Outlier mask')
        axs[2].plot(constants, label='Variation mask')
        axs[2].legend(loc='best')

        # Subplot 4
        axs[3].plot(final, label='Label')
        axs[3].legend(loc='best')

        # Save as HTML
        base_name = led_video.basename
        base_name = base_name.replace('LED_', 'PST_')
        output = os.path.join(output_folder, base_name + '.html')
        if led_video: save_html_plot(axs, output)
        pyplot.show()

    return final


def save_html_plot(axs, output):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True)
    for i, ax in enumerate(axs):
        lines = ax.get_lines()
        for line in lines:
            fig.add_trace(go.Scatter(x=line.get_xdata(), y=line.get_ydata(), name=f'Subplot {i + 1}'), row=i + 1, col=1)
    fig.update_layout(height=800, width=800, title_text="Subplots")
    fig.write_html(output)


def concatenate_traces(file_list):
    trace_list = []
    file_start_indices = []
    total_length = 0
    fps = None

    # Iterate through each filename in the list
    for filename in file_list:
        # Load the .npz file
        data = numpy.load(filename)
        # Extract the 'trace' field from the loaded data
        trace = data['trace']
        # Append the 'trace' array to the list
        trace_list.append(trace)
        # Store the starting index of the current file
        file_start_indices.append(total_length)
        # Increment the total length
        total_length += len(trace)
        fps = data['fps']

    # Concatenate all 'trace' arrays into one long array
    concatenated_trace = numpy.concatenate(trace_list)
    return concatenated_trace, fps , file_start_indices


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
        extract_led_video(video, box, led_video_file)
        time.sleep(0.25)
        led_video = Video.Video(led_video_file)
    return led_video


def get_led_trace(led_video, output_folder):
    basename = led_video.basename
    basename = basename.replace('LED_', '')
    led_trace_file = os.path.join(output_folder, 'TRC_' + basename + '.npz')
    capture = led_video.capture
    fps, total_number_of_frames = led_video.get_size()
    intensities = []
    for i in tqdm(range(total_number_of_frames)):
        ret, frame = capture.read()
        mean = numpy.mean(frame)
        intensities.append(mean)
    intensities = numpy.array(intensities)
    Utils.save_trace(intensities, fps, led_trace_file)
    return intensities


def extract_led_video(video, bounding_box, output_file):
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
