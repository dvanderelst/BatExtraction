import os
import numpy
import cv2
from tqdm import tqdm
from matplotlib import pyplot
from scipy.io.wavfile import write
from matplotlib.widgets import RectangleSelector
from Library import Video


def extract_led_multiple(ch_files, box, video_folder, max_frame, temp_video=False):
    traces = []
    counter = 0
    for ch_file in ch_files:
        print('File', counter + 1, 'of', len(ch_files))
        if counter > 0: temp_video = False
        video = Video.Video(video_folder, ch_file)
        trace = extract_led(video, box, max_frame=max_frame, temp_video=temp_video)
        counter += 1
        traces.append(trace)
    traces = numpy.concatenate(traces)
    return traces


def extract_led(video, bounding_box, max_frame, temp_video=False):
    print(video.full_filename())
    capture = video.capture
    fps, total_number_of_frames = video.get_size()
    fps = int(numpy.round(fps))

    x1, y1, x2, y2 = bounding_box
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)
    width = x2 - x1
    height = y2 - y1

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    size = (int(width), int(height))
    if temp_video: out = cv2.VideoWriter(temp_video, fourcc, fps, size)

    intensities = []
    previous_frame = None
    for i in tqdm(range(total_number_of_frames)):
        ret, frame = capture.read()
        if frame is None: frame = previous_frame * 1
        cropped_frame = frame[y1:y2, x1:x2]
        grey = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        average_intensity = cv2.mean(grey)[0]
        intensities.append(average_intensity)
        if temp_video: out.write(cropped_frame)
        previous_frame = frame * 1
        if i == max_frame: break

    if temp_video: out.release()
    trace = numpy.array(intensities)
    trace = (trace > numpy.mean(trace)) * 1

    return trace


def get_box(video, title=None):
    frame = video.get_frame(frame_index=0)
    selector = BoxSelector(frame, title)
    box = selector.get_selected_box()
    box = numpy.array([box[0][0], box[0][1], box[1][0], box[1][1]])
    box = numpy.round(box)
    return box


def write_wav(trace, filename, rate):
    trace = trace.astype(numpy.int16) * 32767
    write(filename, rate, trace)


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
