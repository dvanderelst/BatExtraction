import os
from Library import Settings
from matplotlib import pyplot
from scipy.io.wavfile import write
from matplotlib.widgets import RectangleSelector
import numpy
import cv2


def run(video, temp_video='test.mp4', max_frame=1000000, do_plot=False):
    base_name = os.path.basename(video.full_filename())
    base_name = os.path.splitext(base_name)[0]
    fps, _ = video.get_size()
    fps = int(numpy.round(fps))
    frame = video.get_frame(frame_index=0)
    selector = BoxSelector(frame)
    box = selector.get_selected_box()
    box = numpy.array([box[0][0], box[0][1], box[1][0], box[1][1]])
    box = numpy.round(box)
    video.set_frame_index(0)
    trace = extract_led(video,temp_video , box, max_frame=max_frame)
    trace = numpy.array(trace)
    trace = (trace > numpy.mean(trace)) * 1
    wav_file = os.path.join(Settings.led_folder, base_name + '.wav')
    write_wav(trace, wav_file, fps)
    if do_plot:
        pyplot.figure()
        pyplot.plot(trace)
        pyplot.show()
    return trace

def write_wav(trace, filename, rate):
    trace = trace.astype(numpy.int16) * 32767
    write(filename, rate, trace)

def extract_led(video, output_video_path, bounding_box, max_frame):
    capture = video.capture
    total_number_of_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    x1, y1, x2, y2 = bounding_box
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)
    width = x2 - x1
    height = y2 - y1

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter(output_video_path, fourcc, capture.get(cv2.CAP_PROP_FPS), (int(width), int(height)))

    intensities = []
    previous_frame = None
    for i in range(total_number_of_frames):
        print(i, total_number_of_frames)
        ret, frame = capture.read()
        if frame is None: frame = previous_frame * 1

        cropped_frame = frame[y1:y2, x1:x2]
        grey = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        average_intensity = cv2.mean(grey)[0]
        intensities.append(average_intensity)
        out.write(cropped_frame)
        previous_frame = frame * 1
        if i > max_frame: break
    out.release()
    return intensities


class BoxSelector:
    def __init__(self, image):
        self.image = image
        self.start_point = None
        self.end_point = None
        self.fig, self.ax = pyplot.subplots()
        self.ax.imshow(self.image)
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