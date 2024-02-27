import os.path

import cv2
import numpy as np


def add_markers_to_video(led_video, markers_array, output_folder):
    basename = led_video.basename
    basename = basename.replace('LED_', 'MRK_')

    # Open the video
    marker_color = (0, 255, 0)
    marker_radius = 5
    video_path = led_video.filename
    cap = cv2.VideoCapture(video_path)

    # Get the frame count and fps of the video
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video_path = os.path.join(output_folder, basename + '.mp4')
    print(output_video_path)
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Define a function to add marker to the frame
    def add_marker(frame, marker_position):
        if marker_position == 1:
            # Calculate the position of the marker at the bottom right corner
            marker_x = frame_width - marker_radius
            marker_y = frame_height - marker_radius
            # Add a circle marker at the calculated position
            cv2.circle(frame, (marker_x, marker_y), marker_radius, marker_color, -1)

    # Process the video frames
    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        # Get the corresponding marker value from the array
        marker_value = markers_array[i] > 0.75

        # Add marker to the frame based on the marker value
        add_marker(frame, marker_value)

        # Write the frame to the output video file
        out.write(frame)

    # Release the video capture object and close the output video file
    cap.release()
    out.release()

