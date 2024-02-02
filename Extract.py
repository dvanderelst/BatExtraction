import cv2
from skimage.color import rgb2gray
from skimage.filters import gaussian
import numpy
from matplotlib import pyplot
import math
import pandas

def excerpt(vidcap, output_path, start_frame, end_frame):
    # Get the frames per second (fps), width, and height of the video
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create VideoWriter object to save the frames as an MP4 video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Set the start and end frame positions
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    end_frame = min(end_frame, vidcap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)

    # Read and write frames to the output video
    for frame_number in range(start_frame, int(end_frame) + 1):
        ret, frame = vidcap.read()
        if ret:
            out.write(frame)
        else:
            print(f"Error reading frame {frame_number}")
            break
    out.release()


def regions2table(regions):
    df = pandas.DataFrame([{'Label': region.label,
                        'Area': region.area,
                        'BoundingBox': region.bbox,
                        'x': region.centroid[0],
                        'y': region.centroid[1],
                            } for region in regions])
    return df


def plot_regions(image, regions):
    fig, ax = pyplot.subplots()
    ax.imshow(image, cmap=pyplot.cm.gray)

    for props in regions:
        y0, x0 = props.centroid
        ax.plot(x0, y0, '.g', markersize=15)

        minr, minc, maxr, maxc = props.bbox
        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        ax.plot(bx, by, '-b', linewidth=2.5)
    pyplot.show()

def difference(images, sigma=5):
    image0 = images[0]
    image1 = images[1]
    image2 = images[2]

    image0 = gaussian(image0, sigma=sigma)
    image1 = gaussian(image1, sigma=sigma)
    image2 = gaussian(image2, sigma=sigma)

    delta1 = numpy.abs(image0 - image1)
    delta2 = numpy.abs(image0 - image2)
    delta = delta1 + delta2
    return delta

def get_video(video):
    vidcap = cv2.VideoCapture(video)
    return vidcap

def get_parameters(vidcap):
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_number_of_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    return fps, total_number_of_frames

def extract_frames(vidcap, frame_nr):
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_nr-1)
    _, image0 = vidcap.read()
    _, image1 = vidcap.read()
    _, image2 = vidcap.read()

    if image0 is None or image1 is None or image2 is None:
        print('Could not extract frame for frame nr: ' + str(frame_nr))
        return False

    image0 = rgb2gray(image0)
    image1 = rgb2gray(image1)
    image2 = rgb2gray(image2)

    return  image0, image1, image2


def select_regions(region, min_area):
    filtered_props = [prop for prop in region if min_area <= prop.area]
    return filtered_props


def filter_non_contained_bounding_boxes(regions):
    # List to store selected region properties
    selected_regions = []

    # Function to check if one bounding box is not partially or fully contained within another
    def is_not_contained(box1, box2):
        return (box1[0] > box2[2] or box1[2] < box2[0] or
                box1[1] > box2[3] or box1[3] < box2[1])

    # Set to store indices of region properties to be excluded
    exclude_indices = set()

    # Check for containment and mark the regions to be excluded
    for i, region in enumerate(regions):
        current_bbox = region.bbox

        for j, other_region in enumerate(regions):
            if i != j and not is_not_contained(current_bbox, other_region.bbox):
                # If there is an overlap, mark the region with the smaller bounding box for exclusion
                if region.area < other_region.area:
                    exclude_indices.add(i)
                else:
                    exclude_indices.add(j)

    # Create a list of selected region properties
    for i, region in enumerate(regions):
        if i not in exclude_indices:
            selected_regions.append(region)

    return selected_regions

# # Function to check if one bounding box is completely contained within another
# def is_contained(box1, box2):
#     return box2[0] <= box1[0] and box2[1] <= box1[1] and box2[2] >= box1[2] and box2[3] >= box1[3]
#
#
# def filter_bounding_boxes(props):
#     # List to store selected region properties
#     selected_props = []
#
#     # Function to check if one bounding box is completely contained within another
#     def is_contained(box1, box2):
#         return box2[0] <= box1[0] and box2[1] <= box1[1] and box2[2] >= box1[2] and box2[3] >= box1[3]
#
#     # Set to store indices of region properties to be excluded
#     exclude_indices = set()
#
#     # Check for containment and mark the regions to be excluded
#     for i, prop in enumerate(props):
#         current_bbox = prop.bbox
#
#         for j, other_prop in enumerate(props):
#             if i != j:  # Skip comparing with itself
#                 other_bbox = other_prop.bbox
#
#                 if is_contained(current_bbox, other_bbox):
#                     exclude_indices.add(i)
#
#     # Create a list of selected region properties
#     for i, prop in enumerate(props):
#         if i not in exclude_indices:
#             selected_props.append(prop)
#
#     return selected_props
