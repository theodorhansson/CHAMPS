import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from scipy.integrate import simpson 
from scipy.interpolate import CubicSpline
import time

from scipy.signal import butter, filtfilt
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
    
def find_peaks(coords, values, reference_spectrum, use_reference_spectrum, spacing=15, px_avg = 3, smoothing=True):

    zeroed_values = values[120:]
    if use_reference_spectrum:
        zeroed_ref_values = reference_spectrum[7:]
    
    ### find x number of largest peaks and select the one with the lowest index
    ### TODO: Not sure if this works correctly yet but might be better in the
    ### long run
    # largest_indices = np.argsort(values)[-3:]
    # zeroed_values = values[largest_indices.min():]
    zeroed_coords = np.arange(zeroed_values.size)*px_scale
    ### zeroed coordinates
    peak_coords = np.arange(0, max(zeroed_coords), spacing)
    ### find peaks at the line coordinates within px_avg number of pixels
    peaks = []
    ref_peaks = []
    for peak_x in peak_coords:
        peaks.append(np.max(zeroed_values[abs(zeroed_coords - peak_x) < px_scale*px_avg]))
        if use_reference_spectrum:
            ref_peaks.append(np.max(zeroed_ref_values[abs(zeroed_coords - peak_x) < px_scale*px_avg]))
    
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
    right_shift = 3
        
    if manual:
        SPR_x = np.argmin(abs(peak_coords - manual))
    else:
        SPR_x = np.argmin(peak_values[right_shift:1300//15]) # provided SPR is the minimum...
        
    new_x = np.arange(peak_coords[SPR_x+right_shift] - 150, peak_coords[SPR_x+right_shift] + 150, 15)
    
    if np.any(new_x < 0): 
        return 0, 0, 0
    
    new_y = peak_values[SPR_x-new_x.size//2+right_shift:SPR_x+new_x.size//2+right_shift]
    return new_x, new_y, peak_coords[SPR_x + right_shift]
   
def find_centroid(x,y):
    spline_values = 0
    try:
        # area = simpson(y,x)
        # x_centroid = simpson(x * y, x) / area
        # y_centroid = simpson(y * y, x) / (2 * area)
        x_fit = np.linspace(np.min(x), np.max(x), 10000)
        spline = CubicSpline(x, y)
        # print(spline(x_fit))
        # spline_values = spline(x_fit)
        
        x_centroid = x_fit[np.argmax(spline(x_fit))]
        # print(x_centroid)
        y_centroid = 0
        # 
        
        
    except:
        x_centroid = 1000
        y_centroid = 3000
        print('Failed to find SPR Dip!')
        
    return x_centroid, y_centroid

class alignment_figure():
    def __init__(self, integrate_over_um):
        self.integrate_over_pixel = int(integrate_over_um/px_scale)
        
        fig = plt.figure(figsize=(10,7), num=1, clear=True)
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
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
            
        return y_max_index, spr_spectrum
        
        
        

class SPR_figure():
    def __init__(self, integrate_over_um):
        self.integrate_over_pixel = int(integrate_over_um/px_scale)
        
        # Initiate figure object
        # fig = plt.figure(figsize=(10,7))
        plt.ion()
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
        sprx, spry, SPR_x = isolate_SPR(peak_x, peak_y, manual = None)
        x_c, y_cspry = find_centroid(sprx, np.max(spry)-spry)
        
        if frame_counter%100 == 0:    
            plot_start = time.time()
            if frame_counter == 0 and line == 0 and laser:
                ## First cropped image
                self.im_raw_data = self.ax_array[0].imshow(cropped_im)

                ## Integrated detected spectrum
                self.line_integrated_spectrum, = self.ax_array[1].plot(x, y, linewidth=0.5)
                self.ax_array[1].set_ylim([np.min(y), np.max(y)])
                
                ## Filtered spectrum
                self.filtered_spectrum, = self.ax_array[2].plot(peak_x, peak_y, color='black',marker='o',markersize=3)
                self.ax_array[2].set_ylim([np.min(peak_y), np.max(peak_y)])
                # self.spr_dip, = self.ax_array[2].plot(sprx, spry, 'r', marker='o',markersize=3)
                
                self.dip_spectrum, = self.ax_array[3].plot(sprx, spry, 'r', marker='o',markersize=3)
                # self.ax_array[3].plot(np.array([x_c, x_c]), np.array([np.min(spry), np.max(spry)]), 'r', marker='o',markersize=3)


                time.sleep(0.1)

            else:
                self.line_integrated_spectrum.set_data(x, y)
                self.ax_array[1].set_ylim([np.min(y), np.max(y)])
                
                self.filtered_spectrum.set_data(peak_x, peak_y)
                self.ax_array[2].set_ylim([np.min(peak_y), np.max(peak_y)])
                
                self.dip_spectrum.set_data(sprx, spry)
                self.ax_array[3].set_xlim([np.min(sprx), np.max(sprx)])
                self.ax_array[3].set_ylim([np.min(spry), np.max(spry)])

                # self.dip_spectrum.set_data(sprx, spry)
   
                time.sleep(0.1)
                print(f'Plotting took: {time.time()-plot_start}')
                
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
                
        return x_c
    
    def update_spr_trace(self, lasers_on_chip, results, COLORS, frame_counter, start_trace, clear_trace):
        # Update spr trace
        if clear_trace:
            self.fig.axes[4].clear()
            self.fig.axes[4].set_title(r'SPR trace')
            self.fig.axes[4].set_xlabel(r'Time [s]')
            self.fig.axes[4].set_ylabel(r'x [$\mu$m]')
            self.fig.axes[4].grid(True)
            self.fig.axes[4].legend(loc='lower left')
            
        for channels in lasers_on_chip:
            frame_time = results['frame_time'][channels][start_trace:]
            spr_trace  = results['spr_data'][channels][start_trace:]
            self.fig.axes[4].plot(frame_time, spr_trace, 
                                  marker='o', linewidth=0.2, markersize=3, 
                                  color=COLORS[channels], label=f'Laser {channels}') 
            
        
            if frame_counter==0: 
                self.fig.axes[4].legend(loc='lower left')
                
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
    
    
