import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import simps
import imageio.v3 as iio
from PIL import Image
from hamamatsu.dcam import copy_frame, dcam, Stream
import logging
import os
import time
import cv2
from scipy.signal import convolve, butter, filtfilt, argrelextrema
import datetime

TIMESTAMP = datetime.datetime.now().strftime("%m%d_%H%M%S")
PI  = np.pi
DEG = PI/180
px_scale = 1.5679 #um/px

def process_image(image):
    ### takes in the raw camera image and returns an integrated spectrum
    ### find maximum value coordinate
    max_coords = np.unravel_index(np.argmax(image), image.shape)
    
    ### crop image
    cropped_image = image[max_coords[0]-100:max_coords[0]+100,:]
    
    ### integrate vertically
    values = np.mean(cropped_image, axis=0)
    coords = np.arange(cropped_image.shape[1])*px_scale    
    
    return coords, values, cropped_image

def find_valley_width_around_local_minima(data, local_minimum, width_threshold=0):
    valley_widths = []

    for peak_index in local_minimum:
        left_index = peak_index
        right_index = peak_index
        
        while left_index > 0 and data[left_index] <= data[left_index - 1]:
            left_index -= 1
        
        while right_index < len(data) - 1 and data[right_index] <= data[right_index + 1]:
            right_index += 1
        
        valley_width = right_index - left_index + 1
        
        if valley_width > width_threshold:
            valley_widths.append(valley_width)
    
    return valley_widths
    
def find_peaks(coords, values, spacing = 15, px_avg = 3):
    ### takes in the integrated spectrum and returns just the peak values
    ### zero the spectrum to the max peak 
    index_max_peak = 0
    zeroed_values = values[index_max_peak:]    
    zeroed_coords = np.arange(zeroed_values.size)*px_scale
    ### zeroed coordinates
    peak_coords = np.arange(0,max(zeroed_coords), spacing)
    ### find peaks at the line coordinates within px_avg number of pixels
    peaks = []
    for peak_x in peak_coords:
        peaks.append(np.max(zeroed_values[abs(zeroed_coords - peak_x) < px_scale*px_avg]) )
    
    ### moving average
    # window_size = 1
    # window = np.ones(window_size) / window_size
    # peaks = np.convolve(peaks, window, mode='same')
    ### butterworth
    sampling_freq=1/15
    cutoff_freq=1/200
    order=2
    nyquist_freq = 0.5 * sampling_freq
    normalized_cutoff_freq = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff_freq, btype='lowpass')
    peaks = filtfilt(b, a, peaks)
    peaks = np.array(peaks)
    
    ## Extract the localminimum
    local_minimum = argrelextrema(peaks, np.less)[0]
    
    ## Omit last value since the last peak is a "false" local minimum
    local_minimum = local_minimum[:-1]
    
    ## Find widths of dips in spectrum
    valley_widths = find_valley_width_around_local_minima(peaks, local_minimum, width_threshold=0)
    
    ## Coordinate of the SPR dip
    SPR_coord = int(local_minimum[np.argmax(valley_widths)])
    
    return peak_coords, peaks, SPR_coord

def isolate_SPR(peak_coords, peak_values, SPR_coord, manual=None):

    new_x = np.arange(peak_coords[SPR_coord]-210, peak_coords[SPR_coord]+210, 15)
    new_y = peak_values[SPR_coord-new_x.size//2:SPR_coord+new_x.size//2]
    # print(SPR_coord)
    return new_x, new_y
   
def find_centroid(x,y):

    area = simps(y,x)
    x_centroid = simps(x * y, x) / area
    y_centroid = simps(y * y, x) / (2 * area)
    
    # print(f'Found curve center at: x={x_centroid} y={y_centroid}')
    return x_centroid, y_centroid

def init_figure():
    fig = plt.figure(figsize=(10,5))
    ax0 = fig.add_subplot(231); ax0.set_title('Captured Image')
    ax1 = fig.add_subplot(232); ax1.set_title('Raw Data')
    ax2 = fig.add_subplot(234); ax2.set_title('Peak Data')
    ax3 = fig.add_subplot(235); ax3.set_title('SPR Dip')
    ax4 = fig.add_subplot(133); ax4.set_title('SPR Dip Tracking')
    plt.tight_layout()
    return fig

def analyze_image(im, fig=None):    
    x, y, crp_img = process_image(image = im)
    peak_x, peak_y, SPR_coord = find_peaks(x, y)
    sprx, spry = isolate_SPR(peak_x, peak_y, SPR_coord, manual = None)
    x_c, y_cspry = find_centroid(sprx, np.max(spry)-spry)
    if fig is not None:
        for ax in fig.axes:
            ax.clear()
        fig.axes[0].imshow(crp_img)
        fig.axes[1].plot(x,y,linewidth=0.5)
        fig.axes[2].plot(peak_x,peak_y, marker='o',markersize=3)
        fig.axes[3].plot(sprx,spry, marker='o', markersize=3); fig.axes[3].axvline(x_c, color='r')
    return x_c