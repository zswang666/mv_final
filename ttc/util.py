import numpy as np

import scipy
from scipy import ndimage

from skimage.util import view_as_blocks

import cv2

def uniform_blur(img, n):
    return ndimage.uniform_filter(img, size=n)

def restrict(f, k=2):
    '''
    Apply block average filter to the image f
    '''
    if k == 1:
        return f
    block_shape = (k, k)

    if f.shape[0] % 2 != 0 or f.shape[1] % 2 != 0:
        f = make_even_size(f)

    view = view_as_blocks(f, block_shape)
    flatten_view = view.reshape(view.shape[0], view.shape[1], -1)
    mean_view = np.mean(flatten_view, axis=2)
    return mean_view

def make_even_size(img):
    '''
    Ensure the image to be of even size
    '''
    height, width = img.shape
    
    if (height % 2):
        height += 1

    if (width % 2):
        width += 1
    
    resized_img = cv2.resize(img, (width, height)) 
    
    return resized_img

def rgb2gray(img):
    return np.mean(img, axis=-1)

def load_video(filename):
    '''
    Load video from the file specified by the filename
    '''
    cap = cv2.VideoCapture(filename)
    while(cap.isOpened()):
        ret, frame = cap.read()        
        if frame is None:
            break
        frame = rgb2gray(frame)      
        yield frame
    cap.release()