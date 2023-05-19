"""
6.101 Spring '23 Lab 2: Image Processing 2
"""

#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image
from prevLab import *   # brings in last week's stuff without the mess here

# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.

    Args:
        filt: A functor to wrap to apply to RGB images.
    """
    def colorApplicableFilter(image):
        # First split the image into three components.
        chSplitImages = [{'height':image['height'],
                                   'width':image['width'],
                                   'pixels':list([elem[chIndex] for elem in image['pixels']])} 
                                   for chIndex in range(len(image['pixels'][0]))]
        
        # Then aply the filter to each of the three "images"
        imOuts = [filt(curIm) for curIm in chSplitImages]

        # And then return the new image formed by these composites as pixel tuples
        return {'height':image['height'],
                'width':image['width'],
                'pixels':list(zip(*[im['pixels'] for im in imOuts]))}

    return colorApplicableFilter
    


def make_blur_filter(kernel_size):
    '''
    We could have bound functions (or allowed them to pass through using *args or **kwargs),
    but for now we can simply wrap our previous blurred function with this function and return
    a function that is only partially bound (w.r.t.) the kernel_size method.
    Or we can implement a simple closure like we do here.
    '''
    def kernelSizeWrapper(image):
        return blurred(image, kernel_size)
    
    return kernelSizeWrapper


def make_sharpen_filter(kernel_size):
    '''
    Like above, we make introduce a closure to partially bind our sharpen function.
    '''
    def kernelSizeWrapper(image):
        return sharpened(image, kernel_size)
    
    return kernelSizeWrapper


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def chainFuncWrapper(image):
        outIm = image
        for imFunc in filters:
            outIm = imFunc(outIm)
        return outIm
    
    return chainFuncWrapper


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols, * , verbose = False):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    newIm = {'height': image['height'],
             'width': image['width'],
             'pixels': image['pixels'].copy()}

    # algorithm repeats for ncols times
    for iterInd in range(ncols):
        # Keep rough track of progress for long operations
        if verbose and iterInd%5 == 0:
            print("\tPerforming seam cut #{}...".format(iterInd+1))

        # make the grayscale image and compute the energy
        energy = compute_energy(greyscale_image_from_color_image(newIm))

        # compute the cummulative energy and find the minimum energy seam
        cummEnergy = cumulative_energy_map(energy)
        minSeamInds = minimum_energy_seam(cummEnergy)

        # And then remove this seam from the original image
        newIm = image_without_seam(newIm, minSeamInds)
    
    return newIm


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    return {'height': image['height'],
            'width': image['width'],
            'pixels': [round(.299*rColor + .587*gColor + .114*bColor) 
                            for rColor, gColor, bColor in image['pixels']]}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    # initialize the map with the proper 2-dimensional size and first row values
    cummEnergyMap = [[0]*energy['width'] for _ in range(energy['height'])]
    
    # and then build up the map row by row
    for rowInd in range(energy['height']):
        for colInd in range(energy['width']):
            # initialize first row
            if rowInd == 0:
                cummEnergyMap[rowInd][colInd] = get_pixel(energy, rowInd, colInd)
            
            # infer from previous row
            cummEnergyMap[rowInd][colInd] = (get_pixel(energy, rowInd, colInd) +
                                             min(getAdjacentEnergies(cummEnergyMap[rowInd-1], colInd)[0]))
    
    return {'height':energy['height'],
            'width': energy['width'],
            'pixels':cummEnergyMap}


def getAdjacentEnergies(aboveRowVals, colInd):
    '''
    Given a column index and the values above the row in question, returns a list
    representing all of the adjacent pixels from the row above (or at least any
    that exist as edges only have 2 adjacent above pixels) along with their column
    indices
    '''
    tReturn = []
    tIndices = []
    for offset in (-1, 0, 1):
        if offset+colInd < 0 or offset+colInd >= len(aboveRowVals):
            continue

        tReturn.append(aboveRowVals[offset+colInd])
        tIndices.append(offset+colInd)
    return tReturn, tIndices


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).

    Note that the cummulative map is a 2-dimensional list at this point!
    """
    # Begin by identifying the lowest energy point in the bottom row
    minIndex = cem['pixels'][-1].index(min(cem['pixels'][-1]))

    # And then slowly traverse upwards
    btList = [(cem['height']-1, minIndex)]
    for rowInd in reversed(range(cem['height']-1)):
        lastCol = btList[-1][1]
        sAdjEnergy = sorted(zip(*getAdjacentEnergies(cem['pixels'][rowInd], lastCol)))
        curMinCol = sAdjEnergy[0][1]
        btList.append((rowInd, curMinCol))

    # finally, convert this back into the 1-d format and return it for use
    twoDToOneD = lambda rowInd, colInd: colInd + rowInd * cem['width']
    return list(reversed([twoDToOneD(*posTuple) for posTuple in btList]))


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.

    Note that since the seam to remove is already in 1-dimensional format, we can
    simply parse through the pixels one by one and pick out what we don't want
    """
    # Create a new template image with one less column (cutting the seam)
    newIm = {'height': image['height'],
             'width': image['width'] - 1,
             'pixels': list()}
    
    skipInd = 0
    for pixInd in range(len(image['pixels'])):
        if skipInd >= len(seam):
            # eliminated all of the seam already so just terminate loop
            newIm['pixels'].extend(image['pixels'][pixInd:])
            break
        elif pixInd == seam[skipInd]:
            # reached a seam element
            skipInd += 1
            continue

        newIm['pixels'].append(image['pixels'][pixInd])
        
    return newIm


def customFeatureDecorator(sigma_s, sigma_r, regDist):
    """
    Since our function has a lot of parameters, we use this function
    to provide closure.
    """
    def argWrapper(image):
        return custom_feature(image, sigma_s, sigma_r, regDist)
    return argWrapper


def custom_feature(image, sigma_s, sigma_r, regDist):
    """
    Implements a custom image-based algorithm of my choosing. In this particular
    case, I will be implementing a non-linear form of image filtering known as
    a bilateral filter. It's a precursor to the slightly more complex non-local
    means filtering method, but it's a pretty interesting filter to create given
    that non-linear filters cannot be as easily implemented using correlation.

    The gist of the bilateral filter is as follows:
        For each pixel in an image, we take the weighted sum of the product of nearby
        pixels in both the literal pixel distance range and the image value range but
        interpreted as values from a Gaussian and scale each of these nearby pixels
        by this product of two gaussians.
        The weighing occurs w.r.t. these two Gaussian products.
    The end result is essentially a Gaussian filter that performs a filtering that is
    a bit more receptive towards preserving edges (as a result of weighing into the
    function the Gaussian distance in pixel values and not just the pixel distance.)

    Note that this is a single channel operation!
    """
    # create a new image to work on
    newIm = {'height': image['height'],
             'width': image['width'],
             'pixels': [0]*len(image['pixels'])}
    
    # a lambda helper to find distances
    pixelDistLam = lambda posP, posQ: math.sqrt((posP[0]-posQ[0])**2 + (posP[1]-posQ[1])**2)
    imDistLam = lambda posP, posQ: get_pixel_padded(image, posP[0], posP[1]) - get_pixel_padded(image, posQ[0], posQ[1])
    
    # define kernel constants for the gaussians of the filter
    kernConst = lambda sigma: -2*math.sqrt(2)*sigma**2
    kern = lambda val, sigma: math.exp(max(val-2*sigma**2, 0)/kernConst(sigma))

    for rowInd in range(image['height']):
        for colInd in range(image['width']):
            Z = 0
            newColor = 0
            
            for rOffset in range(-1*regDist, regDist+1):
                for cOffset in range(-1*regDist, regDist+1):
                    ZTemp = (kern(pixelDistLam((rowInd, colInd), (rowInd+rOffset, colInd+cOffset)), sigma_s) *
                             kern(imDistLam((rowInd, colInd), (rowInd+rOffset, colInd+cOffset)), sigma_r))
                    Z += ZTemp
                    newColor += ZTemp * get_pixel_padded(image, rowInd+rOffset, colInd+cOffset)

            # calculate value now after regional calculation
            newColor /= Z
            set_pixel(newIm, rowInd, colInd, round(newColor))

    return newIm


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # rgb inversion on cat image
    print("Smoke testing RGB adapted inversion...")
    catIm = load_color_image('./test_images/cat.png')
    save_color_image(color_filter_from_greyscale_filter(inverted)(catIm), 
                     './test_results/inverted_rgb_cat.png')

    # rgb blurring on python image
    print("Smoke testing blur filter partial binding...")
    pythonIm = load_color_image('./test_images/python.png')
    save_color_image(color_filter_from_greyscale_filter(make_blur_filter(9))(pythonIm),
                     './test_results/blurred_rgb_python.png')
    
    # rgb sharpening on sparrow image
    print("Smoke testing sharpening filter partial binding...")
    sparrowIm = load_color_image('./test_images/sparrowchick.png')
    save_color_image(color_filter_from_greyscale_filter(make_sharpen_filter(7))(sparrowIm),
                     './test_results/sharpened_rgb_sparrowchick.png')
    
    # test chain function wrapper on frog image
    print("Smoke testing functor chaining wrapper...")
    frogIm = load_color_image('./test_images/frog.png')
    filter1 = color_filter_from_greyscale_filter(edges)
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    filt = filter_cascade([filter1, filter1, filter2, filter1])
    save_color_image(filt(frogIm), './test_results/cascade_frog.png')

    # test a single iteration of the seam cutting algorithm
    print("Smoke testing the seam cut algorithm...")
    patternIm = load_color_image('./test_images/pattern.png')
    greyscaleIm = greyscale_image_from_color_image(patternIm)
    greyEnergy = compute_energy(greyscaleIm)
    cummMap = cumulative_energy_map(greyEnergy)
    print(minimum_energy_seam(cummMap)) # This lines up with the problem statement so it works
                                        # at least on 1 iteration!

    # Now test the algorithm in a multi-pass setting
    print("Now smoke testing a multi-pass situation... (This will take a while!)")
    twoCatsIm = load_color_image('./test_images/twocats.png')
    save_color_image(seam_carving(twoCatsIm, 100, verbose = False), 
                     './test_results/seamcut_twocats.png')
    
    # Finally, smoke test our custom function
    print("Smoke testing the bilateral filer...")
    chessIm = load_color_image('./test_images/chess.png')
    decFunc = customFeatureDecorator(1.0, 100./255, 5)
    save_color_image(color_filter_from_greyscale_filter(decFunc)(chessIm), './test_results/bilateral_chess.png')