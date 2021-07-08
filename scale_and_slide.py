#%%

import matplotlib.pyplot as plt
import numpy as np
import math

from PIL import Image

#%%

def simple_display_image(img: Image.Image):
    """displays single image in pyplot

    Args:
        img (PIL.Image.Image): image to display
    """

    plt.figure()
    plt.imshow(img)
    plt.show()

#%%

def display_crops(img: Image.Image, crops: list, 
                  window_dimensions: tuple, stride: int):
    """displays gropu of image crops in a nicely formated rectangle

    Args:
        img (PIL.Image.Image): image whose crops are being displayed
        crops (list): list of image crops
        window_dimensions (tuple): dimensions of the cropping window
        stride (int): the stride
    """
    print('BEGIN PYPLOT CROPS DISPLAY')
    rows = 1 + math.ceil((img.height - window_dimensions[1]) / stride)
    columns = 1 + math.ceil((img.width - window_dimensions[0]) / stride)
    figsize = (10 * columns, 10 * rows)

    print('rows: ' + str(rows))
    print('columns: ' + str(columns))

    fig = plt.figure(figsize=figsize)

    for i in range(0, columns * rows):
        fig.add_subplot(rows, columns, i + 1)
        plt.imshow(crops[i])
        plt.axis('off')

    plt.show()

    print('END PYPLOT CROPS DISPLAY \n')

#%%

def get_scaled_images(img: Image.Image, count=3, increment=.5):
    """returns a list of multiple versions of one image, each of a 
    differnt size
    Args:
        img (PIL.Image.Image): image to resize
        count (int): number of images to return (will be length of the 
        array that is returned)
        increment (float): percentage increase from one size to the next
    Returns:
        list of PIL.Image.Image: the resized images
    """
# number of images smaller than img will be determined 
# by math.floor(num/2)
#     ex-odd: math.floor(3/2) = 1  ---  num == 3
#     ex-even: math.floor(4/2) = 2  ---  num == 4
# number of images larger than img will be determined 
# by math.ceiling(num/2) - 1
#     ex-odd: math.ceiling(3/2) - 1 = 1  ---  num == 3
#     ex-even: math.ceiling(4/2) - 1 = 1  ---  num == 4

    print('START IMAGE RESCALING')
    imgs = []

    # add images from smallest to largest
    for i in range(count - 1) :
        resize_amount = increment ** (count - 1 - i)
        new_dims = (
                    int(img.width * resize_amount), 
                    int(img.height * resize_amount)
                    )
        # new_dims = (int(width), int(length))
        imgs.append(img.resize(new_dims))
        print('image size: ', new_dims)

    # apppend the original image before adding larger images
    imgs.append(img)
    
    print('original image size: ', tuple(img.size))
    print('END IMAGE RESCALING \n')

    return imgs

#%%

def sliding_window(image: Image.Image, window_dim: tuple, stride: int):
    """iteratively slides a box across an image, cropping the image
    inside of the bounding box after each iteration. The crops are
    returned inside of an array
    Args:
        image (PIL.Image.Image): the image from which the crops wil be made
        window_dim (tuple): the dimensions of the sliding window, where
                            the 0th index holds the width and 1st slot
                            holds the width
        stride (int): how much to slide the window after 
                               each iteration

    Raises:
        ValueError: if window_dim is larger than image to crop

    Returns:
        list of PIL.Image.Image: the cropped images
    """
    
    if window_dim[0] > image.width or window_dim[1] > image.height:
        raise ValueError('window dimension of ' + str(window_dim) + ' is \
                         larger than image of size: ' + str(image.size))

    print('START WINDOW SLIDING')
    print('cropping im size:' + str(image.size))

    pictures = []

    tally = 0

    for y in range(0, image.height, stride):
        for x in range(0, image.width, stride):
            tally += 1
            # set crop bounds
            left_bound = x
            right_bound = left_bound + window_dim[0]
            upper_bound = y
            lower_bound = upper_bound + window_dim[1]

            # adjust bounds in cases of overflow
            if image.height < lower_bound:
                upper_bound = image.height - window_dim[1]
                lower_bound = image.height

            if image.width < right_bound:
                left_bound = image.width - window_dim[0]
                right_bound = image.width
            
            crop_bounds = [left_bound, upper_bound, right_bound, lower_bound]

            crop = image.crop(crop_bounds)
            pict = [crop, crop_bounds]
            pictures.append(pict)

            if right_bound == image.width:
                break

    print('total sliding crops: ' + str(tally))

    print('END WINDOW SLIDING \n')

    return [im for [im, dims] in pictures]

#%%

def get_image_chunks(img: Image.Image, window_dim: tuple, stride: int, 
                     num_rescales: int, rescale_increment: float):
    """Generates sub-images by resizing the image and running a sliding
    window across each of the resized images
    Args:
        img (PIL.Image.Image): image to process
        window_dim (tuple): dimensions of the sliding window
        stride (int): amount to slide the window after 
                               each iteration
        num_rescales (int): number of rescaled images to make
        rescale_increment (float): fraction by which to increase image 
                                   after each resize
    Returns:
        list: a nested list of lists of PIL.Image.Image of cropped images.
        Each resized image is stored inside of its own list
    """

    # first task - rescale the image into multiple sizes
    scaled_images = get_scaled_images(img=img, count=num_rescales, 
                                      increment=rescale_increment)

    # next - slide a window and crop sub-images from each of the
    # rescaled images
    crops = []
    
    for im in scaled_images:
        crops.append(sliding_window(im, window_dim, stride))
        

    return crops

# %%

# ************************************
# SAMPLE TEST
# ************************************
def test():
    img = Image.open('test.jpg')
    window_dimensions = (75, 100)
    stride = 50
    num_rescales = 3
    rescale_increment = .5

    crops = get_image_chunks(img, window_dimensions, stride,
                            num_rescales, rescale_increment)

    rescaled_images = get_scaled_images(img, num_rescales, rescale_increment)
    simple_display_image(img)

    for i in range(num_rescales):
        display_crops(rescaled_images[i], crops[i], window_dimensions, stride)
    
test()

# %%
