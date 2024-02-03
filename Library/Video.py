from Library import Settings
import os
import cv2

class Video:
    def __init__(self, filename):
        self.folder = Settings.video_folder
        self.filename = filename
        self.frame_index = 0
        self.capture = cv2.VideoCapture(self.full_filename())

    def full_filename(self):
        return os.path.join(self.folder, self.filename)

    def get_size(self):
        capture = self.capture
        fps = capture.get(cv2.CAP_PROP_FPS)
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



