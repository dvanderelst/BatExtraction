from matplotlib import pyplot
import pandas

def select_regions(region, min_area):
    filtered_props = [prop for prop in region if min_area <= prop.area]
    return filtered_props


def is_not_contained(box1, box2):
    return (box1[0] > box2[2] or box1[2] < box2[0] or
            box1[1] > box2[3] or box1[3] < box2[1])


def filter_non_contained_bounding_boxes(regions):
    selected_regions = []
    exclude_indices = set()
    for i, region in enumerate(regions):
        current_bbox = region.bbox
        for j, other_region in enumerate(regions):
            if i != j and not is_not_contained(current_bbox, other_region.bbox):
                if region.area < other_region.area:
                    exclude_indices.add(i)
                else:
                    exclude_indices.add(j)
    for i, region in enumerate(regions):
        if i not in exclude_indices:
            selected_regions.append(region)
    return selected_regions


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


def regions2table(regions):
    df = pandas.DataFrame([{'Label': region.label,
                            'Area': region.area,
                            'BoundingBox': region.bbox,
                            'x': region.centroid[0],
                            'y': region.centroid[1],
                            } for region in regions])
    return df
