import cv2
import numpy as np


def add_marks_to_video(binary_array, video_path, output_video_path):
    # Open the input video
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Check if the binary array matches the number of frames
    if len(binary_array) != frame_count:
        raise ValueError("The length of the binary array must match the number of frames in the video.")

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Iterate through each frame and the corresponding binary value
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of the video

        # Get the corresponding binary value for this frame
        binary_value = binary_array[frame_idx]

        # Define the circle's position and size (you can modify the position/size as needed)
        circle_position = (15, 15)  # (x, y) coordinates of the circle's center
        circle_radius = 15  # Radius of the circle

        # If binary value is 1, draw a white circle, otherwise draw a black circle
        color = (255, 255, 255) if binary_value == 1 else (0, 0, 0)
        thickness = -1  # Filled circle

        # Draw the circle on the frame
        cv2.circle(frame, circle_position, circle_radius, color, thickness)

        # Write the modified frame to the output video
        out.write(frame)

        # Increment frame index
        frame_idx += 1

    # Release everything if job is finished
    cap.release()
    out.release()