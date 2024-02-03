import cv2
import numpy

def gaussian(image, sigma):
    blurred_image = cv2.GaussianBlur(image, (0, 0), sigma, sigma)
    return blurred_image


def difference(images, sigma=5):
    image0 = images[0] * 1.0
    image1 = images[1] * 1.0
    image2 = images[2] * 1.0

    image0 = gaussian(image0, sigma)
    image1 = gaussian(image1, sigma)
    image2 = gaussian(image2, sigma)

    delta1 = numpy.abs(image0 - image1)
    delta2 = numpy.abs(image0 - image2)
    delta = delta1 + delta2
    return delta

