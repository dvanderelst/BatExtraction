from matplotlib import pyplot
from skimage.measure import regionprops, regionprops_table
from skimage.measure import label
import Extract
import pandas



video = 'N883A6_ch1_main_20240129222500_20240129223000.mp4'
video = 'bat_feed_trim.mp4'
vidcap = Extract.get_video(video)
fps, frames = Extract.get_parameters(vidcap)
#%%
start_frame = 25
end_frame = 200

results = pandas.DataFrame()
Extract.excerpt(vidcap,'excerpt.mp4', start_frame, end_frame)
for frame in range(start_frame, end_frame):
    images = Extract.extract_frames(vidcap, frame)
    if images:
        reference = images[0]
        delta = Extract.difference(images)
        delta = delta > 0.02
        regions = regionprops(label(delta))
        regions = Extract.select_regions(regions, min_area=1000)
        regions = Extract.filter_non_contained_bounding_boxes(regions)
        print('frame', frame, len(regions))
        if len(regions) > 0:
            table = Extract.regions2table(regions)
            table['frame'] = frame
            results = pandas.concat((results, table))

#%%
pyplot.figure()
pyplot.imshow(reference)
pyplot.scatter(results.y, results.x, c=results.frame, cmap='jet')
pyplot.show()