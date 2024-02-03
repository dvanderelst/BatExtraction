import os
import shutil

import cv2
import easygui
import numpy
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.io import imread


def create_folder(folder, remove_first=False, ask=False):
    contents = []
    proceed = True
    full_path = os.path.abspath(folder)
    if os.path.isdir(folder): contents = os.listdir(folder)
    message = 'The folder is not empty. Do you want to delete it?\n' + full_path
    if len(contents) > 0 and remove_first:
        if ask: proceed = easygui.ynbox(message, 'Warning', ('Yes', 'No'))
        if not proceed: return False
        shutil.rmtree(folder)
    if not os.path.isdir(folder): os.makedirs(folder)
    return True


def read_frame(folder, number):
    frame = 'frame_%04d.jpg' % number
    frame = os.path.join(folder, frame)
    image = imread(frame)
    image = rgb2gray(image)
    return image


def difference(image0, image1):
    image0 = gaussian(image0, sigma=3)
    image1 = gaussian(image1, sigma=3)
    delta = numpy.abs(image0 - image1)
    return delta

def extract_frames(video, target, start=None, end=None):
    create_folder(target, remove_first=True, ask=True)
    vidcap = cv2.VideoCapture(video)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_number_of_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(fps, total_number_of_frames)
    if start is None: start = 0
    if end is None: end = total_number_of_frames

    vidcap.set(cv2.CAP_PROP_POS_FRAMES, start)
    number_of_frames_to_process = end - start
    current_frame = start
    for i in range(number_of_frames_to_process + 1):
        frame_name = 'frame_%04d.png' % current_frame
        file_name = os.path.join(target, frame_name)
        print(file_name)

        success, image = vidcap.read()
        cv2.imwrite(file_name, image)
        current_frame = current_frame + 1

