import os
import re

import cv2
import numpy
from moviepy.editor import VideoFileClip, clips_array
from tqdm import tqdm

from Library import Utils


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
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc = cv2.VideoWriter_fourcc(*'X264')  # Use libx264 codec
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

    #Convert to other codec. Opencv does not support this codec
    #encoded_file_name = Utils.modify_basename(output_filename, suffix='_aac')
    #recode_video(encoded_file_name, encoded_file_name)


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


def recode_video(input_file, output_file):
    try:
        clip = VideoFileClip(input_file)
        clip.write_videofile(output_file, codec='libx264')
        print("Video encoding completed successfully.")
    except Exception as e:
        print("Error:", e)
        print("Video encoding failed.")


def combine_videos(input_paths, output_path, fps):
    file1 = input_paths[0]
    file2 = input_paths[1]
    file3 = input_paths[2]
    file4 = input_paths[3]
    # Load video clips
    clip1 = VideoFileClip(file1).resize(0.5)
    clip2 = VideoFileClip(file2).resize(0.5)
    clip3 = VideoFileClip(file3).resize(0.5)
    clip4 = VideoFileClip(file4).resize(0.5)
    # Stitch clips together in a 2 by 2 array
    final_clip = clips_array([[clip1, clip2], [clip3, clip4]])
    # Write the final clip to a file
    final_clip.write_videofile(output_path, codec='libx264', fps=fps)
    # Close all clips
    clip1.close()
    clip2.close()
    clip3.close()
    clip4.close()

# def recode_video(input_file, output_file):
#     ffmpeg_command = [
#         'ffmpeg',
#         '-i', input_file,
#         '-c:v', 'libx264',
#         output_file
#     ]
#     print(ffmpeg_command)
#     try:
#         result = subprocess.run(ffmpeg_command, check=True)
#         print("FFMPEG Output:", result.stdout.decode('utf-8'))
#         print("FFMPEG Error:", result.stderr.decode('utf-8'))
#         print("Video encoding completed successfully.")
#     except subprocess.CalledProcessError as e:
#         print("Error:", e)
#         print("Video encoding failed.")




# def combine_videos(input_paths, output_path):
#     # Construct ffmpeg command to combine videos
#     cmd = [
#         'ffmpeg',
#         '-i', input_paths[0], '-i', input_paths[1], '-i', input_paths[2], '-i', input_paths[3],
#         '-filter_complex',
#         '[0:v]scale=iw/2:ih/2[v0];[1:v]scale=iw/2:ih/2[v1];[2:v]scale=iw/2:ih/2[v2];[3:v]scale=iw/2:ih/2[v3];[v0][v1]hstack[top];[v2][v3]hstack[bottom];[top][bottom]vstack=inputs=2',
#         '-c:v', 'libx264', '-crf', '23',
#         output_path
#     ]
#
#     # Run ffmpeg command
#     try:
#         subprocess.run(cmd, check=True)
#         print(f"Combined video successfully saved to {output_path}")
#     except subprocess.CalledProcessError as e:
#         print(f"Error combining videos: {e}")



def create_combined_video(directory, fps):
    output = os.path.join(directory, 'combined.mkv')
    Utils.remove_file(output)
    videos = Utils.get_movie_files(directory)
    combine_videos(videos, output, fps)