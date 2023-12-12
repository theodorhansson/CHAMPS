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
x_pixel  = 2048
y_pixel  = 2048
x_axis_um_4x = np.arange(0, x_pixel*px_scale, px_scale)
y_axis_um_4x = np.arange(0, y_pixel*px_scale, px_scale)
extent_raw_4x = np.array([0, x_pixel*px_scale, 0, y_pixel*px_scale])

def process_image(cropped_image, reference_spectrum, use_reference_spectrum):
    if use_reference_spectrum:
        image = cropped_image
        values = np.mean(cropped_image, axis=0)
        coords = np.arange(cropped_image.shape[1])*px_scale 
    else:
        image = cropped_image
        values = np.mean(cropped_image, axis=0)
        coords = np.arange(cropped_image.shape[1])*px_scale  
    return coords, values, image

# def find_valley_width_around_local_minima(data, local_minimum, width_threshold=0):
#     valley_widths = []
#     valley_average = []

#     for peak_index in local_minimum:
#         left_index = peak_index
#         right_index = peak_index
        
#         while left_index > 0 and data[left_index] <= data[left_index - 1]:
#             left_index -= 1
        
#         while right_index < len(data) - 1 and data[right_index] <= data[right_index + 1]:
#             right_index += 1
        
#         valley_width = right_index - left_index + 1
        
#         if valley_width > width_threshold:
#             valley_widths.append(valley_width)
#             valley_average.append(np.sum(data[peak_index-left_index:peak_index+right_index])/valley_width)
    
#     return (valley_widths, valley_average)
    
def find_peaks(coords, values, reference_spectrum, use_reference_spectrum, spacing=15, px_avg = 3, smoothing=True):
    ### takes in the integrated spectrum and returns just the peak values
    ### zero the spectrum to the max peak    
    # zeroed_values = values[np.argmax(values[coords<750]):]      
    # zeroed_values = values[argrelextrema(values, np.greater)[0][5]:]
    zeroed_values = values[14:]
    if use_reference_spectrum:
        zeroed_ref_values = reference_spectrum[7:]
    
    
    ### find x number of largest peaks and select the one with the lowest index
    ### TODO: Not sure if this works correctly yet but might be better in the
    ### long run
    # largest_indices = np.argsort(values)[-3:]
    # zeroed_values = values[largest_indices.min():]
    zeroed_coords = np.arange(zeroed_values.size)*px_scale
    ### zeroed coordinates
    peak_coords = np.arange(0, max(zeroed_coords),spacing)
    ### find peaks at the line coordinates within px_avg number of pixels
    peaks = []
    ref_peaks = []
    for peak_x in peak_coords:
        peaks.append(np.max(zeroed_values[abs(zeroed_coords - peak_x) < px_scale*px_avg]))
        if use_reference_spectrum:
            ref_peaks.append(np.max(zeroed_ref_values[abs(zeroed_coords - peak_x) < px_scale*px_avg]))
    
   ### DEBUGGING START
    # plt.show()
    # fig = plt.figure()
    # fig.plot(zeroed_coords[:200], zeroed_values[:200], linewidth=0.5)
    # fig.scatter(peak_coords[:25], peaks[:25], marker='x', color='r')
    # plt.show()
    ### DEBUGGING END
    ### smoothing
    if smoothing:
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
        if use_reference_spectrum:
            ref_peaks = filtfilt(b, a, ref_peaks)
        
    if use_reference_spectrum:
        return peak_coords, (np.array(peaks) - np.array(ref_peaks)/2)/np.array(peaks)
    else:
        return peak_coords, np.array(peaks)

def isolate_SPR(peak_coords, peak_values, manual=None):
    ### takes in the peak spectrum and isolates the SPR dip only
    if manual:
        SPR_x = np.argmin(abs(peak_coords - manual))
    else:
        SPR_x = np.argmin(peak_values[:2150//15]) # provided SPR is the minimum...
        # TODO: this sets the upper limit of measurement, extra important to fix!
    
    # if SPR_x == 0:
    #     SPR_x = 140
        
    new_x = np.arange(peak_coords[SPR_x]-150, peak_coords[SPR_x]+150, 15)
    if np.any(new_x<0): return 0, 0
    # new_y = np.zeros_like(new_x)
    new_y = peak_values[SPR_x-new_x.size//2:SPR_x+new_x.size//2]
    return new_x, new_y
   
def find_centroid(x,y):
    try:
        area = simps(y,x)
        x_centroid = simps(x * y, x) / area
        y_centroid = simps(y * y, x) / (2 * area)
        
    except:
        x_centroid = 1000
        y_centroid = 3000
        print(f'Failed to find SPR Dip!')
    return x_centroid, y_centroid

class alignment_figure():
    def __init__(self, integrate_over_um):
        self.integrate_over_pixel = int(integrate_over_um/px_scale)
        
        fig = plt.figure(figsize=(10,7))
        ax0 = fig.add_subplot(211)
        ax1 = fig.add_subplot(223)
        ax2 = fig.add_subplot(224)
        self.ax_array = [ax0, ax1, ax2]
        
        plt.suptitle('SPR alignment')
        
        fig.axes[0].set_title(r'Raw image')
        fig.axes[0].set_xlabel(r'x [um]')
        fig.axes[0].set_ylabel(r'y [um]')
        
        fig.axes[1].set_title(r'Find max spectrum')
        fig.axes[1].set_xlabel(r'y [um]')
        fig.axes[1].set_ylabel(r'Intensity [counts]')
        
        fig.axes[2].set_title(r'Find max spectrum')
        fig.axes[2].set_xlabel(r'y [um]')
        fig.axes[2].set_ylabel(r'Intensity [counts]')
        
        plt.tight_layout()
        
        self.fig = fig
        
    def update_alignment_image(self, image):
        
        self.ax_array[0].imshow(image, extent=extent_raw_4x, origin='lower')

        y_cross = np.sum(image, axis=1)
        y_max_index = np.argmax(y_cross)
        self.ax_array[1].plot(y_cross, y_axis_um_4x)
        self.ax_array[1].plot(y_cross[y_max_index], x_axis_um_4x[y_max_index],  'x', color='black')

        self.ax_array[0].plot(np.array([0, np.max(x_axis_um_4x)]), np.array([y_axis_um_4x[y_max_index], y_axis_um_4x[y_max_index]]), color='red', linewidth=0.5)
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um_4x)]), np.array([y_axis_um_4x[y_max_index+self.integrate_over_pixel], y_axis_um_4x[y_max_index+self.integrate_over_pixel]]), color='red', linewidth=0.3)
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um_4x)]), np.array([y_axis_um_4x[y_max_index-self.integrate_over_pixel], y_axis_um_4x[y_max_index-self.integrate_over_pixel]]), '--', color='red', linewidth=0.3)
       
        
        spr_spectrum = np.sum(image[y_max_index-self.integrate_over_pixel:y_max_index+self.integrate_over_pixel, :], axis=0)
        self.ax_array[2].plot(x_axis_um_4x, spr_spectrum/np.max(spr_spectrum))
        
        return y_max_index, spr_spectrum
        
        
        

class SPR_figure():
    def __init__(self, integrate_over_um):
        self.integrate_over_pixel = int(integrate_over_um/px_scale)
        
        # Initiate figure object
        fig = plt.figure(figsize=(10,7))
        ax0 = fig.add_subplot(231)
        ax1 = fig.add_subplot(232)
        ax2 = fig.add_subplot(234)
        ax3 = fig.add_subplot(235)
        ax4 = fig.add_subplot(133)
        self.ax_array = [ax0, ax1, ax2, ax3, ax4]
        
        # Title for entire plot
        plt.suptitle('SPR measurements')
        
        # Set x-axis for plots with um
        for i, ax in enumerate(fig.axes):
            if not i == 0 and not i == 4:
                ax.grid(True)
                ax.set_xlabel(r'x [$\mu$m]')
                
        # Raw image
        fig.axes[0].set_title(r'Raw image')
        fig.axes[0].set_xlabel(r'x [px]')
        fig.axes[0].set_ylabel(r'y [px]')
        
        # Integrate spectrum
        fig.axes[1].set_title(r'Integrate spectrum')
        fig.axes[1].set_ylabel(r'Intensity [Counts]')
        
        # Filtered peaks
        fig.axes[2].set_title(r'Filtered peaks')
        fig.axes[2].set_ylabel(r'Intensity [Counts]')
        
        # SPR dip
        fig.axes[3].set_title(r'SPR dip')
        fig.axes[3].set_ylabel(r'Intensity [Counts]')
        
        # SPR trace
        fig.axes[4].set_title(r'SPR trace')
        fig.axes[4].set_xlabel(r'Time [s]')
        fig.axes[4].set_ylabel(r'x [$\mu$m]')
        fig.axes[4].grid(True)
        fig.axes[4].legend(loc='lower left')
        
        plt.tight_layout()
        
        self.fig = fig
        
    def analyze_image(self, im, y_max_index, frame_counter, line, config, reference_spectrum, use_reference_spectrum, laser=True): 
        cropped_im = im[int(y_max_index-self.integrate_over_pixel):int(y_max_index+self.integrate_over_pixel), :]

        
        x, y, crp_img = process_image(cropped_im, reference_spectrum, use_reference_spectrum)
        peak_x, peak_y = find_peaks(x, y, reference_spectrum, use_reference_spectrum)
        sprx, spry = isolate_SPR(peak_x, peak_y, manual = None)
        x_c, y_cspry = find_centroid(sprx, np.max(spry)-spry)
        
        #TODO: put this on a separate thread from pictures and processing
        if frame_counter%10 == 0:
            if frame_counter == 0 and line == 0 and laser:
                self.im_raw_data = self.ax_array[0].imshow(cropped_im)
                self.line_integrated_spectrum, = self.ax_array[1].plot(x, y, linewidth=0.5)
                self.ax_array[1].set_ylim([np.min(y), np.max(y)])
                self.filtered_peaks, = self.ax_array[2].plot(peak_x, peak_y, color='black',marker='o',markersize=3)
                self.ax_array[2].set_ylim([np.min(peak_y), np.max(peak_y)])
                self.spr_dip, = self.ax_array[3].plot(sprx, spry, 'r', marker='o',markersize=3)
                self.ax_array[3].set_xlim([np.min(sprx), np.max(sprx)])
                self.ax_array[3].set_ylim([np.min(spry), np.max(spry)])
                plt.show(False)
            
            else:
                #TODO: This is slowing down over time and takes way too much time
                # in general
                plot_start = time.time()
                # self.im_raw_data.set_data(im)
                self.line_integrated_spectrum.set_data(x, y)
                self.ax_array[1].set_ylim([np.min(y), np.max(y)])
                self.filtered_peaks.set_data(peak_x, peak_y)
                self.ax_array[2].set_ylim([np.min(peak_y), np.max(peak_y)])
                self.spr_dip.set_data(sprx, spry)
                self.ax_array[3].set_xlim([np.min(sprx), np.max(sprx)])
                self.ax_array[3].set_ylim([np.min(spry), np.max(spry)])
                plt.show(False)
                print(f'Plotting took: {time.time()-plot_start}')

        return x_c