"""
6.101 Spring '23 Lab 1: Image Processing
"""

#!/usr/bin/env python3

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col):
    return image["pixels"][row*image["width"] + col]


def get_pixel_padded(image, row, col, padding = 'zero'):
    if 0 <= row < image["height"] and 0 <= col < image["width"]:
        return get_pixel(image, row, col)
    
    match padding:
        case 'zero':
            return 0
        case 'wrap':
            return get_pixel(image, row%image["height"], col%image["width"])
        case 'extend':
            clampRow = ((0 <= row < image["height"])*row) or ((row >= image["height"])*(image["height"]-1)) or ((row < 0)*0)
            clampCol = ((0 <= col < image["width"])*col) or ((col >= image["width"])*(image["width"]-1)) or ((col < 0)*0)
            return get_pixel(image, clampRow, clampCol)


def set_pixel(image, row, col, color):
    image["pixels"][row*image["width"] + col] = color


def apply_per_pixel(image, func):
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0]*len(image["pixels"]),
    }

    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255-color)


# HELPER FUNCTIONS

def boxBlurKernel(kernSize):
    return [[1.0/(kernSize**2)]*kernSize for _ in range(kernSize)]

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    Kernels will be represented as a list of lists in order to be consistent with
        the general 2d nature of image convolution kernels. It also reduces the general
        necessity of functions needed to index the kernel as a 1d list despite being
        2d in nature.
    """
    # edge cases
    if boundary_behavior not in ["zero", "extend", "wrap"]:
        return None
    
    # compute correlation with unknown sized kernel
    outIm = {'height': image['height'],
             'width': image['width'],
             'pixels': [0]*len(image['pixels'])}
    kernHalfWidth = (len(kernel)-1)//2 # kernel ranges from -2, -1, 0, 1, 2 for a 3x3
    
    # determines the beginning of correlation w.r.t. input image coords
    for rowOrigin in range(image['height']):
        for colOrigin in range(image["width"]):
            # calculates the correlation starting from the origins
            outPixelVal = 0
            for kernRow, offsetRow in enumerate(range(-1*kernHalfWidth, kernHalfWidth+1)):
                for kernCol, offsetCol in enumerate(range(-1*kernHalfWidth, kernHalfWidth+1)):
                    outPixelVal += get_pixel_padded(image, 
                                                    rowOrigin + offsetRow, 
                                                    colOrigin + offsetCol, 
                                                    boundary_behavior
                                                    ) * kernel[kernRow][kernCol]

            # and then write to our output image
            set_pixel(outIm, rowOrigin, colOrigin, outPixelVal)
    return outIm


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    # first round all values and then clip
    for pixInd in range(len(image["pixels"])):
        newPixelVal = round(image["pixels"][pixInd])
        if newPixelVal < 0:
            newPixelVal = 0
        elif newPixelVal > 255:
            newPixelVal = 255
        image["pixels"][pixInd] = newPixelVal
    
    return image


# FILTERS

def blurred(image, kernel_size, * , padMethod = 'extend'):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    blurKern = boxBlurKernel(kernel_size)

    # then compute the correlation of the input image with that kernel
    outIm = correlate(image, blurKern, padMethod)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(outIm)

def sharpened(image, kernel_size, * , padMethod = 'extend'):
    """
    Return a new image representing the result of applying a sharpening operation
    (composed of a blur of kernel_size) to the given input image.

    As usual, returns a new image and does not modify the original image.

    Since correlation calculations (effectively convolution) are linear in nature,
    a convolution of form A*K1+A*K2 is equivalent to A*(K1+K2).
    """
    # First we create the kernel from the blur kernel as 2K_i - K_b
    blurKern = boxBlurKernel(kernel_size)
    sharpKern = [[-1*elem for elem in row] for row in blurKern]
    sharpKern[kernel_size//2][kernel_size//2] += 2

    # And then apply it to the image
    outIm = correlate(image, sharpKern, padMethod)

    # And then bound it to proper values
    return round_and_clip_image(outIm)


def edges(image):
    """
    Performs a sobel edge detection over a given input image and returns
    the output on a completely new image.

    More formally, a sobel edge detector is the root of the sum of squares
    produced by the two sobel edge detection kernels in the vertical and
    horizontal orientation.
    """
    # define our kernels
    kRow = [[-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]]
    kCol = [[-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]]
    
    # and now process the final image
    imRSAdder = lambda im1, im2: {'pixels':[math.sqrt(elem1**2+elem2**2) for elem1, elem2 in zip(im1['pixels'], im2['pixels'])],
                                  'height':im1['height'],
                                  'width': im1['width']}
    return round_and_clip_image(imRSAdder(correlate(image, kRow, 'extend'), correlate(image, kCol, 'extend')))
