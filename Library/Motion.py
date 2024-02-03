import time
import pandas
from Library import ImageAnalysis
from Library import Video
from skimage.measure import regionprops, label

def motion_analysis(video, start_frame=None, end_frame=None, steps=10):
    threshold = 2
    sigma = 3
    time_stamp = Extract.get_time_stamp(video)
    capture = Video.Video(video)
    fps, nr_frames = capture.get_size()
    if start_frame is None: start_frame = 1
    if end_frame is None: end_frame = nr_frames - 1
    all_results = pandas.DataFrame()

    for frame_nr in range(start_frame, end_frame, steps):
        start = time.time()

        frame0 = capture.get_frame(frame_nr - 1)
        frame1 = capture.get_frame()
        frame2 = capture.get_frame()
        frames = [frame0, frame1, frame2]
        delta = Extract.difference(frames, sigma=sigma)
        delta = (delta > threshold) * 1
        regions = regionprops(label(delta))
        regions = Extract.select_regions(regions, min_area=1000)
        table = Extract.regions2table(regions)
        table['frame'] = frame_nr
        all_results = pandas.concat((all_results, table))
        nr_regions = len(regions)
        end = time.time()
        duration = end - start
        print(frame_nr, end_frame , duration, nr_regions)

    results = {}
    results['table'] = all_results
    results['frame'] = frame2
    results['stamp'] = time_stamp
    return all_results, time_stamp

