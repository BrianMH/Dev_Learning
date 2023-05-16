#!/usr/bin/env python3

import os
import pickle
import hashlib

import lab
import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


def compare_images(im1, im2):
    assert set(im1.keys()) == {'height', 'width', 'pixels'}, 'Incorrect keys in dictionary'
    assert im1['height'] == im2['height'], 'Heights must match'
    assert im1['width'] == im2['width'], 'Widths must match'
    assert len(im1['pixels']) == im1['height']*im1['width'], 'Incorrect number of pixels'
    assert all(isinstance(i, int) for i in im1['pixels']), 'Pixels must all be integers'
    assert all(0<=i<=255 for i in im1['pixels']), 'Pixels must all be in the range from [0, 255]'
    pix_incorrect = (None, None)
    for ix, (i, j) in enumerate(zip(im1['pixels'], im2['pixels'])):
        if i != j:
            pix_incorrect = (ix, abs(i-j))
    assert pix_incorrect == (None, None), 'Pixels must match.  Incorrect value at location %s (differs from expected by %s)' % pix_incorrect


def verboseExtendWrap(im, row, col):
    ''' Performs extend padding, but with simpler logic for testing smaller images '''
    extendRow, extendCol = row, col
    if row < 0:
        extendRow = 0
    elif row >= im['height']:
        extendRow = im['height'] - 1

    if col < 0:
        extendCol = 0
    elif col >= im['width']:
        extendCol = im['width'] - 1
    
    return lab.get_pixel(im, extendRow, extendCol)


def test_load():
    result = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    compare_images(result, expected)


def test_inverted_1():
    im = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    result = lab.inverted(im)
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
    }
    compare_images(result, expected)

def test_inverted_2():
    im = {'height': 1,
          'width': 4,
          'pixels': [23, 80, 149, 193]}
    result = lab.inverted(im)
    expected = {'height': 1,
                'width': 4,
                'pixels': [255-23, 255-80, 255-149, 255-193]}
    compare_images(result, expected)

@pytest.mark.parametrize("imSize", [1, 3, 7])
@pytest.mark.parametrize("padMethod", ['zero', 'wrap', 'extend'])
def test_padded_get_inbounds(imSize, padMethod):
    im = {'height': imSize,
          'width': imSize,
          'pixels': list(range(imSize*imSize))}
    
    # make sure we can get the normal pixels just fine
    for row in range(im['height']):
        for col in range(im['width']):
            assert lab.get_pixel(im, row, col) == lab.get_pixel_padded(im, row, col, padMethod), "Incorrect pixel wrapping values."

@pytest.mark.parametrize("imSize", [1, 3, 7])
def test_padded_get_zero_outbounds(imSize):
    im = {'height': imSize,
          'width': imSize,
          'pixels': list(range(imSize*imSize))}
    
    # test out of bounds values now
    test_limits = 2
    for row in range(-1 * test_limits * im['height'], test_limits * im['height']):
        for col in range(-1 * test_limits * im['width'], test_limits * im['width']):
            if 0 <= row < im['height'] and 0 <= col < im['width']:
                continue
            assert lab.get_pixel_padded(im, row, col, 'zero') == 0, "Zero padding incorrectly implemented"

@pytest.mark.parametrize("imSize", [1, 3, 7])
def test_padded_get_extend_outbounds(imSize):
    im = {'height': imSize,
          'width': imSize,
          'pixels': list(range(imSize*imSize))}
    
    # test out of bounds values now
    test_limits = 2
    for row in range(-1 * test_limits * im['height'], test_limits * im['height']):
        for col in range(-1 * test_limits * im['width'], test_limits * im['width']):
            if 0 <= row < im['height'] and 0 <= col < im['width']:
                continue
            expectedVal = verboseExtendWrap(im, row, col)
            assert lab.get_pixel_padded(im, row, col, 'extend') == expectedVal, "Extend padding incorrectly implemented"

@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
@pytest.mark.parametrize("kern_size", [3, 5, 7])
@pytest.mark.parametrize("padding", ['zero', 'extend', 'wrap'])
def test_correlation_images_identity(fname, kern_size, padding):
    inpFile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    im = lab.load_greyscale_image(inpFile)
    oim = object_hash(im)

    # create the kernel and then convolve with the image
    identKern = [[0]*kern_size for _ in range(kern_size)]
    identKern[kern_size//2][kern_size//2] = 1
    result = lab.correlate(im, identKern, padding)
    assert object_hash(im) == oim, 'Be careful not to modify the original image!'
    compare_images(result, im)

@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_inverted_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_invert.png' % fname)
    im = lab.load_greyscale_image(inpfile)
    oim = object_hash(im)
    result = lab.inverted(im)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(im) == oim, 'Be careful not to modify the original image!'
    compare_images(result, expected)


@pytest.mark.parametrize("kernsize", [1, 3, 7])
@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_blurred_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_blur_%02d.png' % (fname, kernsize))
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.blurred(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)

@pytest.mark.parametrize("kernsize", [3, 5])
def test_blurred_black_image(kernsize):
    # REPLACE THIS with your 1st test case from section 5.1
    imHeight, imWidth = 6, 5
    inpImg = {'height': imHeight,
              'width' : imWidth,
              'pixels': [0]*imHeight*imWidth}
    oim = object_hash(inpImg)
    result = lab.blurred(inpImg, kernsize)
    assert object_hash(inpImg) == oim, "Be careful not to modify the original image!"
    compare_images(result, inpImg)

@pytest.mark.parametrize("kernsize", [3, 5])
def test_blurred_centered_pixel(kernsize):
    # REPLACE THIS with your 2nd test case from section 5.1
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png')
    inpImg = lab.load_greyscale_image(inpfile)
    oim = object_hash(inpImg)
    result = lab.blurred(inpImg, kernsize)

    # output of a single pixel box blue will always be a box of size
    # (kernsize x kernsize) with the value equivalent to 1/(kernsize**2)
    expected2d = lab.boxBlurKernel(kernsize)
    padRow = (inpImg['height'] - kernsize)//2
    padCol = (inpImg['width'] - kernsize)//2
    expected2d = ([[0]*inpImg['width'] for _ in range(padRow)] +
                  [[0]*padCol + curRow + [0]*padCol for curRow in expected2d]+
                  [[0]*inpImg['width'] for _ in range(padRow)])
    expected = {'height': inpImg['height'],
                'width': inpImg['width'],
                'pixels':[255*elem for curRow in expected2d for elem in curRow]}
    expected = lab.round_and_clip_image(expected)
    compare_images(result, expected)

@pytest.mark.parametrize("kernsize", [1, 3, 9])
@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_sharpened_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_sharp_%02d.png' % (fname, kernsize))
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.sharpened(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)


@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_edges_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_edges.png' % fname)
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.edges(input_img)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)

def test_edges_centered_pixel():
    # REPLACE THIS with your test case from section 6
    assert False


if __name__ == "__main__":
    import sys
    res = pytest.main(["-k", " or ".join(sys.argv[1:]), "-v", __file__])
