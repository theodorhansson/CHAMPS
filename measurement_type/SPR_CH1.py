#%%
# IMPORTS --------------------------------------------------------------------
import os, sys
import traceback
import numpy as np
import time
from pathlib import Path
import imageio.v3 as iio
import matplotlib.pyplot as plt

from scipy.interpolate import CubicSpline
from scipy.signal import butter, filtfilt

from pylablib.devices import Andor

import communication
from drivers.arduino_giga_serial.aurora import aurora
import general_functions.pretty_printing.verbose_printing as vp

## General constants
rad_to_deg = np.pi/180
deg_to_rad = 180/np.pi

## Plotting constants
x_pixel  = 1024
y_pixel  = 1024
px_scale = 5.596  ## um/px  For 2.5x objective with manual infinity correction
um_scale = 0.1787 ## px/um
x_axis_um = np.arange(0, x_pixel*um_scale, um_scale)
y_axis_um = np.arange(0, y_pixel*um_scale, um_scale)
extent_raw = [x_axis_um.min(), x_axis_um.max(), y_axis_um.min(), y_axis_um.max()]

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']

class alignment_figure():
    def __init__(self, integrate_over_um):
        self.integrate_over_pixel = int(integrate_over_um/px_scale)
        
        fig = plt.figure(figsize=(10, 7), num=0, clear=True)
        ax0 = fig.add_subplot(221)
        ax1 = fig.add_subplot(222)
        ax2 = fig.add_subplot(223)
        self.ax_array = [ax0, ax1, ax2]
        
        plt.suptitle('SPR alignment')
        
        fig.axes[0].set_title(r'Raw image')
        fig.axes[0].set_xlabel(r'x [um]')
        fig.axes[0].set_ylabel(r'y [um]')
        
        fig.axes[1].set_title(r'y-intergrated spectrum')
        fig.axes[1].set_xlabel(r'Intensity [counts]')
        fig.axes[1].set_ylabel(r'y [um]')
        
        fig.axes[2].set_title(r'Reflected spectrum from alignment')
        fig.axes[2].set_xlabel(r'x [um]')
        fig.axes[2].set_ylabel(r'Intensity [counts]')
        
        plt.tight_layout()
        
        self.fig = fig
        
    def update_alignment_image(self, image, color):
        
        ## Plot full image
        self.ax_array[0].imshow(image, extent=extent_raw, origin='lower', cmap='magma')
        
        ## Sum along y-axis
        y_cross = np.sum(image, axis=1)
        ## Pick out maxium value
        y_max_index = np.argmax(y_cross)

        ## Plot in full image where I think the maxium is
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um)]), np.array([y_axis_um[y_max_index], y_axis_um[y_max_index]]), color='red', linewidth=0.5)
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um)]), np.array([y_axis_um[y_max_index+self.integrate_over_pixel], y_axis_um[y_max_index+self.integrate_over_pixel]]), color='red', linewidth=0.3)
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um)]), np.array([y_axis_um[y_max_index-self.integrate_over_pixel], y_axis_um[y_max_index-self.integrate_over_pixel]]), '--', color='red', linewidth=0.3)
               
        ## Plot y-integrated image
        self.ax_array[1].plot(y_cross, y_axis_um, color=color)
        self.ax_array[1].plot(y_cross[y_max_index], x_axis_um[y_max_index],  'x', color='black')

        minimum_index_integration = y_max_index - self.integrate_over_pixel
        maximum_index_integration = y_max_index + self.integrate_over_pixel
        if minimum_index_integration < 0 or maximum_index_integration > y_pixel:
            vp.headline('You, Cassandra, are finding a laser beam to close to the edge of the image. Move stage or integrate less wide.')
        
        ## How does the laser beam actually look
        spr_spectrum = np.sum(image[y_max_index - self.integrate_over_pixel:y_max_index + self.integrate_over_pixel, :], axis=0)
        self.ax_array[2].plot(x_axis_um, spr_spectrum/np.max(spr_spectrum))
        
        ## Update canvas
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
            
        return y_max_index, spr_spectrum
    
def create_peak_spectrum(coords, values, start_cropped_image_from_pixel, stopp_cropped_image_from_pixel):
    
    gold_line_spacing = 15
    pixel_average = 3
    
    ## Remove starting edge of image. Define in config.toml!
    zeroed_values = values[start_cropped_image_from_pixel:stopp_cropped_image_from_pixel]
    zeroed_coords = np.arange(zeroed_values.size)*px_scale
    
    ### Zeroed coordinates
    peak_coords = np.arange(0, max(zeroed_coords), gold_line_spacing)
    
    ### Find peaks at the line coordinates within px_avg number of pixels
    peaks = []
    for peak_x in peak_coords:
        peaks.append(np.max(zeroed_values[abs(zeroed_coords - peak_x) < px_scale*pixel_average]))
    
    ### Butterworth Filtering
    sampling_freq = 1/15
    cutoff_freq   = 1/200
    order         = 2
    nyquist_freq  = 0.5 * sampling_freq
    normalized_cutoff_freq = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff_freq, btype='lowpass')
    peaks = filtfilt(b, a, peaks)
    
    ## Set x-scale to match the choosen from config.toml
    peak_coords = peak_coords + start_cropped_image_from_pixel*px_scale
    
    return peak_coords, np.array(peaks)

def isolate_SPR(peak_coords, peak_values, width_around_SPR_dip_um):
    width_around_SPR_dip_px = int(width_around_SPR_dip_um * um_scale)

    # TODO: stupid hard coded value. Please solve someone.
    start_from = 3
    stopp_at   = 10

    # Not enough points to even apply start/stopp range
    if len(peak_values) <= (start_from + stopp_at):
        return np.array([]), np.array([])

    # Find location of the minimum (assumes SPR is the minimum)
    spr_dip_index = np.argmin(peak_values[start_from:-stopp_at]) + start_from

    # Clamp index to valid range
    spr_dip_index = max(0, min(spr_dip_index, len(peak_coords) - 1))

    # Half window in index space
    half_w = max(1, width_around_SPR_dip_px // 2)

    left  = spr_dip_index - half_w
    right = spr_dip_index + half_w

    # Clamp again to valid range
    left  = max(0, left)
    right = min(len(peak_coords), right)

    # If this still gives an empty slice, bail out
    spr_x = peak_coords[left:right]
    if spr_x.size == 0:
        return np.array([]), np.array([])

    # Now build spr_y with the same size as spr_x
    if spr_dip_index < 2:
        # Near the edge – you already treat this as a special case
        spr_y = np.zeros_like(spr_x, dtype=float)
        print('SPR dip is in the corner of the peak spectrum')
    else:
        center = spr_dip_index
        half_len = spr_x.size // 2

        left_y  = max(0, center - half_len)
        right_y = min(len(peak_values), center + half_len)

        spr_y = peak_values[left_y:right_y]

        # Make sure spr_y is not empty and matches spr_x length
        if spr_y.size == 0:
            return np.array([]), np.array([])
        if spr_y.size != spr_x.size:
            # Trim or pad if you really care about equal length
            min_len = min(spr_x.size, spr_y.size)
            spr_x = spr_x[:min_len]
            spr_y = spr_y[:min_len]

    return spr_x, spr_y

   
def find_SPR_dip(x, y):
    
    ## Create cubicspline
    try:
        x_fit = np.linspace(np.min(x), np.max(x), 10000)
        spline = CubicSpline(x, y)
        x_centroid = x_fit[np.argmax(spline(x_fit))]
        
    except:
        x_centroid = 1000
        print('Failed to find SPR Dip!')
        
    return x_centroid
        
class SPR_figure():
    def __init__(self, integrate_over_um):
        self.integrate_over_pixel = int(integrate_over_um/px_scale)
        
        # Initiate figure object
        plt.ion()
        fig = plt.figure(figsize=(10, 7), num=1, clear=True)
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
        fig.axes[0].set_xlabel(r'x [$\mu$m]')
        fig.axes[0].set_ylabel(r'y [$\mu$m]')
        
        # Integrate spectrum
        fig.axes[1].set_title(r'Integrate spectrum')
        fig.axes[1].set_ylabel(r'Intensity (normalized)')
        
        # Filtered peaks
        fig.axes[2].set_title(r'Filtered peaks')
        fig.axes[2].set_ylabel(r'Intensity (normalized)')
        
        # SPR dip
        fig.axes[3].set_title(r'SPR dip')
        fig.axes[3].set_ylabel(r'Intensity [Counts]')
        
        # SPR trace
        fig.axes[4].set_title(r'SPR trace')
        fig.axes[4].set_xlabel(r'Time [s]')
        fig.axes[4].set_ylabel(r'x [$\mu$m]')
        fig.axes[4].grid(True)
        
        plt.tight_layout()
        
        self.fig = fig
        
    def analyze_image(self, 
                  image, 
                  y_max_index, 
                  frame_counter, 
                  laser, 
                  config, 
                  start_cropped_image_from,
                  stopp_cropped_image_from,
                  start_look_for_dip_from,
                  stopp_look_for_dip_from,
                  width_around_SPR_dip_um, 
                  colors): 
        """
        Analyze one image for a specific laser and update the plots.
    
        image  : 2D numpy array from camera
        laser  : laser index (0,1,2,3,...)
        """
    
        color = colors[laser]
    
        # --- lazy init of per-laser line dicts (in case __init__ wasn't changed) ---
        if not hasattr(self, "line_integrated_spectrum"):
            self.line_integrated_spectrum = {}
            self.filtered_spectrum = {}
            self.dip_spectrum = {}
            self.left_line_peak_spectrum = {}
            self.right_line_peak_spectrum = {}
    
        # --- crop image around this laser's y-position ---
        cropped_image = image[
            int(y_max_index - self.integrate_over_pixel):
            int(y_max_index + self.integrate_over_pixel),
            :
        ]
    
        # Integrate along y and create x-coordinates for cropped image
        x = np.arange(cropped_image.shape[1]) * px_scale
        y = np.mean(cropped_image, axis=0)
    
        # Convert look-for-dip window from um to pixel index in x
        start_look_for_dip_from_pixel = np.argmin(np.abs(x - start_look_for_dip_from))
        stopp_look_for_dip_from_pixel = np.argmin(np.abs(x - stopp_look_for_dip_from))
    
        # Find gold-line peaks
        peak_x, peak_y = create_peak_spectrum(
            x, y,
            start_look_for_dip_from_pixel,
            stopp_look_for_dip_from_pixel
        )
    
        # Locate spectrum around SPR dip
        spr_x, spr_y = isolate_SPR(peak_x, peak_y, width_around_SPR_dip_um)
    
        # If we failed to isolate anything, don't update plots for this laser
        if spr_x.size == 0 or spr_y.size == 0:
            return np.nan
    
        # Find location of SPR dip (invert so dip becomes peak)
        spr_location = find_SPR_dip(spr_x, np.max(spr_y) - spr_y)
    
        # --- raw image plot (shared) ---
        if not hasattr(self, "im_raw_data"):
            # First time: create image
            self.im_raw_data = self.ax_array[0].imshow(
                image, extent=extent_raw, origin='lower'
            )
        else:
            # Update data only
            self.im_raw_data.set_data(image)
    
        # --- create or update line objects for THIS laser only ---
    
        # First time we see this laser: create its lines
        if laser not in self.line_integrated_spectrum:
            # Integrated detected spectrum (normalized)
            y_norm = y / np.max(y)
            self.line_integrated_spectrum[laser], = self.ax_array[1].plot(
                x, y_norm, linewidth=0.5, color=color
            )
            self.ax_array[1].set_xlim([start_cropped_image_from, stopp_cropped_image_from])
            self.ax_array[1].set_ylim([0, 1])
    
            # Filtered peaks (normalized)
            peak_y_norm = peak_y / np.max(peak_y)
            self.filtered_spectrum[laser], = self.ax_array[2].plot(
                peak_x, peak_y_norm, color=color, marker='o', markersize=3
            )
            self.ax_array[2].set_xlim([np.min(peak_x), np.max(peak_x)])
            self.ax_array[2].set_ylim([0, 1])
    
            # Isolated SPR dip (normalized)
            spr_y_norm = spr_y / np.max(spr_y)
            self.dip_spectrum[laser], = self.ax_array[3].plot(
                spr_x, spr_y_norm, color=color, marker='o', markersize=3
            )
            self.ax_array[3].set_ylim([0, 1])
    
            # Window markers for this laser in peak spectrum
            self.left_line_peak_spectrum[laser], = self.ax_array[2].plot(
                [np.min(spr_x), np.min(spr_x)],
                [np.min(peak_y), np.max(peak_y)],
                '--', color='black', linewidth=1
            )
            self.right_line_peak_spectrum[laser], = self.ax_array[2].plot(
                [np.max(spr_x), np.max(spr_x)],
                [np.min(peak_y), np.max(peak_y)],
                '--', color='black', linewidth=1
            )
    
            # Draw vertical lines in the integrated spectrum window only once (global)
            if not hasattr(self, "_dip_window_drawn"):
                self.ax_array[1].plot(
                    [start_look_for_dip_from, start_look_for_dip_from],
                    [0, 1],
                    '--', color='black', linewidth=1
                )
                self.ax_array[1].plot(
                    [stopp_look_for_dip_from, stopp_look_for_dip_from],
                    [0, 1],
                    '--', color='black', linewidth=1
                )
                self._dip_window_drawn = True
    
        else:
            # Update existing lines for THIS laser
            y_norm = y / np.max(y)
            self.line_integrated_spectrum[laser].set_data(x, y_norm)
            self.ax_array[1].set_ylim([0, 1])
    
            peak_y_norm = peak_y / np.max(peak_y)
            self.filtered_spectrum[laser].set_data(peak_x, peak_y_norm)
            self.ax_array[2].set_xlim([np.min(peak_x), np.max(peak_x)])
            self.ax_array[2].set_ylim([0, 1])
    
            spr_y_norm = spr_y / np.max(spr_y)
            self.dip_spectrum[laser].set_data(spr_x, spr_y_norm)
            self.ax_array[3].set_xlim([np.min(spr_x), np.max(spr_x)])
            self.ax_array[3].set_ylim([0, 1])
    
            self.left_line_peak_spectrum[laser].set_data(
                [np.min(spr_x), np.min(spr_x)],
                [np.min(peak_y), np.max(peak_y)]
            )
            self.right_line_peak_spectrum[laser].set_data(
                [np.max(spr_x), np.max(spr_x)],
                [np.min(peak_y), np.max(peak_y)]
            )
    
        # --- redraw ---
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
        return spr_location, y_norm

    
    def update_spr_trace(self, lasers_on_chip, results, color, frame_counter, start_trace, clear_trace):
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
                                  color=color[channels], label=f'Laser {channels}') 
            
        
            if frame_counter == 0: 
                self.fig.axes[4].legend(loc='lower left')
                
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
# ---- Dummy DC class (for running code without DCunit)  ----------------------
class DummyDC:
    def __init__(self, config):
        self.config = config
        self.verbose = config.get('verbose_printing', 0)

    def __enter__(self):
        print("DummyDC: entering context (no hardware connected).")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("DummyDC: exiting context.")
        return False

    def set_current(self, value): pass
    def set_voltage_limit(self, value): pass
    def set_output(self, value): pass

    def get_voltage_and_current(self):
        # return dummy values so alignment doesn't break
        return (0.0, 0.0)

try:
    import utils
except:
    import sys, pathlib

    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils

# DEFINING SOME STUFF  -------------------------------------------------------
_required_arguments = [
    'type',
    'dc_unit',
    'v_max',
    'save_folder',
    'custom_name',
    'spr_measurement_name',
    'vcsel_chip',
    'vcsel_biases',
    'vcsel_array_bias',
    'frame_average_buffer',
    'frame_average',
    
]
_optional_arguments = {
    'rollover_threshold': 0,
    'rollover_min': 0,
    'verbose_printing': 0,
    'keep_plot': False,
    'offset_background': 0,
    'measurement_time': 1,
    'measurement_interval': 1,
    'exposure_time': 0.03,
    'save_raw_images': 0,
    'measurement_subinterval': 0.01
}

# -----------------------------------------------------------------------------

def init(config: dict, meas_output_dir_path: str):
    # Read config and select DC object
    DC_unit_obj = get_DC_unit(config)

    spr_config = config['measurement']
    DC_config = config['dc_unit']
    measurement_type = spr_config['type']
    DC_name = DC_config['type']

    results = SPR_main(spr_config, DC_config, DC_unit_obj, meas_output_dir_path)
    return_dict = {measurement_type: spr_config, DC_name: DC_config}
    return results, return_dict


# Choose which DC unit to use based on config -------------------------------

def get_DC_unit(config):

    dc_cfg = config.get('dc_unit', {})
    dc_type = dc_cfg.get('type', '').lower()

    if dc_type in ('dummy', 'none', 'simulated'):
        if dc_cfg.get('verbose_printing', 0):
            print("Using DummyDC (simulation mode).")
        return DummyDC
    else:
        Instrument_COM = communication.Communication()
        if dc_cfg.get('verbose_printing', 0):
            print(f"Connecting to real DC unit: {dc_type}")
        return Instrument_COM.get_DCsupply(dc_cfg)


# -----------------------------------------------------------------------------

def SPR_main(IPV_config: dict, DC_config: dict, DC_unit_obj,  meas_output_dir_path):
    
    plt.close('all')
    
    ## Definitions from config file:
    ## Compliance voltage
    V_max = IPV_config['v_max']
    ## Verbose?
    verbose = IPV_config['verbose_printing']
    ## Measurement times
    measurement_time = IPV_config['measurement_time']
    measurement_interval = IPV_config['measurement_interval']
    
    ## Which VCSEL chip is used? Define in Aurora
    vcsel_chip = IPV_config['vcsel_chip']
    ## Individual VCSEL biases to use
    vcsel_biases = IPV_config['vcsel_biases']
    
    run_measurement = IPV_config['run_measurement']
    start_cropped_image_from = IPV_config['start_cropped_image_from']
    stopp_cropped_image_from = IPV_config['stopp_cropped_image_from']
    
    start_look_for_dip_from = IPV_config['start_look_for_dip_from']
    stopp_look_for_dip_from = IPV_config['stopp_look_for_dip_from']

    width_around_SPR_dip_um = IPV_config['width_around_spr_dip_um']
    
    ## Exposure time
    exposure_time = IPV_config['exposure_time']
    ## How wide are to integrate over. VCSEL 1/e^2 width should be 90 um wide
    integrate_over_um = IPV_config['integrate_over_um']
    
    ## Save data periodically
    periodic_saving = True
    
    ## Control object from Aurora
    laser_control = aurora(vcsel_chip)
    ## Array from 0 to how many VCSEL are used. Good for loops.
    lasers_on_chip = np.fromiter(laser_control.chip.keys(), dtype=int)
    
    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if 'verbose_printing' not in instru_dict.keys():
            instru_dict['verbose_printing'] = verbose
            
    ## Communication object with measurement instruments
    Instrument_COM = communication.Communication()
    
    # Create result dict. Is this the best way to do it?
    results = {
    'frame_list': {},
    'frame_time': {},
    'spr_data': {},
}

    # Saving integrated y spect
    if IPV_config.get('save_y_spectrum', 0) == 1:
        results['y_spectrum'] = {}
    
    for laser in lasers_on_chip:
        results['frame_list'][laser] = []
        results['frame_time'][laser] = []
        results['spr_data'][laser]   = []
        if IPV_config.get('save_y_spectrum', 0) == 1:
            results['y_spectrum'][laser] = []

        
    ## Which frame are we at?
    global frame_counter ## Global definitions suck!
    frame_counter = 0
    
    # Start time of measurement
    measurement_time_start = time.time()
    measurement_timestamp = time.strftime(rf'%Y%m%d_%H.%M.%S')
            
    ## Doublecheck stuff
    if not len(vcsel_biases) == len(lasers_on_chip):
        print('Not all VCSELs have a bias! Please check your comfig.toml')
        return results
    
    
    with DC_unit_obj(DC_config) as DC_unit, Andor.AndorSDK3Camera(idx=0) as cam:
        try:
            
            cam.set_exposure(exposure_time)
            cam.set_roi(0, 2048, 0, 2048, hbin=2, vbin=2)
            
            ## Set instrument to 0 for safety
            prev_end_current = 0.0
            DC_unit.set_current(prev_end_current)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)
            
            vp.message('Finding new alignment')
            
            ## Arrays for saving the current and voltage during alignment
            alignment_voltage = np.zeros_like(lasers_on_chip, dtype=float)
            alignment_current = np.zeros_like(lasers_on_chip, dtype=float)
            
            ## Create alignment image object
            alignment_figure_obj = alignment_figure(integrate_over_um)
            
            ## List for laser positions
            laser_locations = []
            
            ## Loop over all laser on the chip
            for i, laser in enumerate(lasers_on_chip):
                time_start = time.time()
                laser_control.switch_to_laser(laser)
                utils.ramp_current(DC_unit, 0, vcsel_biases[laser])
                
                ## Grab image
                # image_array = cam.grab(1)
                # image = image_array[0]
                image_array = cam.grab(nframes=10, frame_timeout=1.0, missing_frame='zero', return_info=False, buff_size=None)
    
                image = np.zeros_like(image_array[0])
                for i in image_array:
                    image = image + i
                
                ## Find peak position of laser beam
                color=colors[laser]
                y_max_index, ref_spectrum = alignment_figure_obj.update_alignment_image(image, color)
                laser_locations.append(y_max_index)
                
                ## Get current and voltage during alignment
                output = DC_unit.get_voltage_and_current()
                
                ## Save current and voltage during alignment
                alignment_voltage[laser] = output[0]
                alignment_current[laser] = output[1]
                
                ## Ramp down current
                utils.ramp_current(DC_unit, vcsel_biases[laser], 0)
                
                ## Turn off all lasers
                laser_control.turn_off_all_lasers()
                
                ## Save alignment image
                save_alignment(alignment_figure_obj, alignment_voltage, alignment_current, vcsel_chip, measurement_timestamp, meas_output_dir_path)
            
            if run_measurement:
                vp.message('Running measurement')
                
                ## Start figure for SPR tracking
                spr_figure = SPR_figure(integrate_over_um)
                ## Save figure to results for saving
                results['fig_object'] = spr_figure.fig
                    
                # Ramp current to set bias
                utils.ramp_current(DC_unit, 0, vcsel_biases[0])
                
                start_time = time.time()
                ## MAIN MEASUREMENT LOOP: --------------------------------------
                while (start_time - measurement_time_start) < measurement_time:
                    camera_start = time.time()
                    
                    for laser in lasers_on_chip:
                        laser_control.switch_to_laser(laser)
                        
                        
  
                        ## Grabbing image
                        image_array = cam.grab(nframes=1, frame_timeout=0.5, missing_frame='zero', buff_size=None)

                        image = np.zeros_like(image_array[0])
                        for i in image_array:
                            image = image + i
                            
                        image = image_array[0]
                        
                        # Ramp down current
                        # utils.ramp_current(DC_unit, vcsel_biases[laser], 0)

                        image_capture_time = time.time()
                        frame_time = image_capture_time - measurement_time_start
                        
                        # Analyzing image and adding data to file
                        results['frame_time'][laser].append(frame_time)

                        spr_location, y_norm = spr_figure.analyze_image(
                            image,
                            laser_locations[laser],
                            frame_counter,
                            laser,
                            IPV_config,
                            start_cropped_image_from,
                            stopp_cropped_image_from,
                            start_look_for_dip_from,
                            stopp_look_for_dip_from,
                            width_around_SPR_dip_um,
                            colors
                        )
                        
                        results['spr_data'][laser].append(spr_location)
                        
                        # Save y spectra (if enabled  )
                        if IPV_config.get('save_y_spectrum', 0) == 1:
                            results['y_spectrum'][laser].append(y_norm)

                        
                    spr_figure.update_spr_trace(lasers_on_chip, 
                                                results, 
                                                colors, 
                                                frame_counter, 
                                                0, 
                                                False)
                        
                    ## Wait if the camera was too quick
                    camera_stopp = time.time()
                    if (camera_stopp - camera_start) < measurement_interval:
                        time.sleep(measurement_interval - (camera_stopp - camera_start))
                    frame_counter += 1  
                    
                    time_camera_after_camera = time.time()
                    print('grabbing image took: ' + str(round(time_camera_after_camera - camera_start, 2)))
                    
        except KeyboardInterrupt:
            print('Keyboard interrupt detected, stopping.')
        
        except:
            # print error if error isn't caught
            traceback.print_exc()
            
    
    laser_control.turn_off_all_lasers()
    save_results(IPV_config, results, measurement_timestamp, meas_output_dir_path)
    return results

# ----------------------------------------------------------------------------
def save_results(IPV_config, results, measurement_timestamp, meas_output_dir_path):
    
    print(f'Saving Data to {meas_output_dir_path}')
    
    for laser in results['frame_list'].items():
        laser = laser[0]
        
        frame_list = results['frame_list'][laser]
        frame_time = results['frame_time'][laser]
        spr_data   = results['spr_data'][laser]

            
        if IPV_config['save_raw_images']:
            for i, im in enumerate(frame_list):      
                iio.imwrite(os.path.join(meas_output_dir_path, 
                                          f'image{i}.png'), im)
        
        if len(frame_time) > len(spr_data):
                frame_time = frame_time[:-1]
        elif len(frame_time) < len(spr_data):
                spr_data = spr_data[:-1]
            
        xy = np.vstack((frame_time, spr_data)).T
        np.savetxt(os.path.join(meas_output_dir_path, f'VCSEL_{laser}.txt'), xy, delimiter=',') 
        
        # Save y-integrated spectra only if enabled in config::
        if IPV_config.get('save_y_spectrum', 0) == 1:
            if 'y_spectrum' in results and laser in results['y_spectrum']:
                spectra_list = [s for s in results['y_spectrum'][laser] if s is not None]
        
                if len(spectra_list) > 0:
                    spectra_array = np.vstack(spectra_list)  # 2D array: (n_frames, n_pixels)
                    np.save(
                        os.path.join(meas_output_dir_path, f'VCSEL_{laser}_y_spectrum.npy'),
                        spectra_array
                    )


def save_alignment(alignment_figure_obj, alignment_voltage, alignment_current, vcsel_chip, measurement_timestamp, meas_output_dir_path):
    vp.headline(f'Saving alignment data to {meas_output_dir_path}')

    # Create folder if it doesn't exist
    save_folder_alignment = Path(meas_output_dir_path, 'alignment_vcsel_chip')
    save_folder_alignment.mkdir(parents=True, exist_ok=True)

    # Paths to saved alignment files
    alignment_png = Path(save_folder_alignment, 'alignment_image.png')
    alignment_csv = Path(save_folder_alignment, 'alignment_bias.csv')
    
    # Save figure (use the figure object directly for safety)
    alignment_figure_obj.fig.savefig(alignment_png, format='png', dpi=300)

    # Save alignment data
    alignment_bias = np.vstack((alignment_voltage, alignment_current)).T
    np.savetxt(alignment_csv, alignment_bias, delimiter=',', header='Voltage,Current', comments='')

