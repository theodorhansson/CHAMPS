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

colors = ['tab:blue', 'tab:red', 'tab:green', 'black']

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
        
    def update_alignment_image(self, image):
        
        ## Plot full image
        self.ax_array[0].imshow(image, extent=extent_raw, origin='lower', cmap='magma')
        
        ## Sum along y-axis
        y_cross = np.sum(image, axis=1)
        ## Pick out maxium value
        y_max_index = np.argmax(y_cross)

        ## Plot in full image where I think the maxium is
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um)]), np.array([y_axis_um[y_max_index], y_axis_um[y_max_index]]), color='red', linewidth=0.5)
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um)]), np.array([y_axis_um[min(y_max_index+self.integrate_over_pixel, y_pixel-1)], y_axis_um[min(y_max_index+self.integrate_over_pixel, y_pixel-1)]]), color='red', linewidth=0.3)
        self.ax_array[0].plot(np.array([0, np.max(x_axis_um)]), np.array([y_axis_um[max(y_max_index-self.integrate_over_pixel, 0)], y_axis_um[max(y_max_index-self.integrate_over_pixel, 0)]]), '--', color='red', linewidth=0.3)
               
        ## Plot y-integrated image
        self.ax_array[1].plot(y_cross, y_axis_um)
        self.ax_array[1].plot(y_cross[y_max_index], x_axis_um[y_max_index],  'x', color='black')

        minimum_index_integration = y_max_index - self.integrate_over_pixel
        maximum_index_integration = y_max_index + self.integrate_over_pixel
        if minimum_index_integration < 0 or maximum_index_integration > y_pixel:
            vp.headline('You, Cassandra, are finding a laser beam to close to the edge of the image. Move stage or integrate less wide.')
        
        ## How does the laser beam actually look
        min_row = max(minimum_index_integration, 0)
        max_row = min(maximum_index_integration, image.shape[0])
        if max_row <= min_row:
            spr_spectrum = np.zeros(image.shape[1])
        else:
            spr_spectrum = np.sum(image[min_row:max_row, :], axis=0)

        if np.max(spr_spectrum) > 0:
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
    if zeroed_values.size == 0:
        print("create_peak_spectrum: empty zeroed_values, returning empty arrays.")
        return np.array([]), np.array([])
    zeroed_coords = np.arange(zeroed_values.size)*px_scale
    
    ### Zeroed coordinates
    if zeroed_coords.size == 0:
        print("create_peak_spectrum: zeroed_coords empty, returning empty arrays.")
        return np.array([]), np.array([])
    peak_coords = np.arange(0, max(zeroed_coords), gold_line_spacing)
    if peak_coords.size == 0:
        print("create_peak_spectrum: peak_coords empty, returning empty arrays.")
        return np.array([]), np.array([])
    
    ### Find peaks at the line coordinates within px_avg number of pixels
    peaks = []
    for peak_x in peak_coords:
        mask = np.abs(zeroed_coords - peak_x) < px_scale*pixel_average
        if not np.any(mask):
            peaks.append(0.0)
        else:
            peaks.append(np.max(zeroed_values[mask]))
    
    peaks = np.array(peaks, dtype=float)

    ### Butterworth Filtering – only if enough samples
    if peaks.size > 6:  # filtfilt needs some length; 6 is safe for 2nd order
        sampling_freq = 1/gold_line_spacing
        cutoff_freq   = 1/200
        order         = 2
        nyquist_freq  = 0.5 * sampling_freq
        normalized_cutoff_freq = cutoff_freq / nyquist_freq
        b, a = butter(order, normalized_cutoff_freq, btype='lowpass')
        peaks = filtfilt(b, a, peaks)
    
    ## Set x-scale to match the choosen from config.toml
    peak_coords = peak_coords + start_cropped_image_from_pixel*px_scale
    
    return peak_coords, peaks


def isolate_SPR(peak_coords, peak_values, width_around_SPR_dip_um):
    # convert window from µm to pixels
    width_around_SPR_dip_px = int(width_around_SPR_dip_um * um_scale)

    # SAFETY: make sure the window is at least a few pixels wide
    if width_around_SPR_dip_px < 4:
        width_around_SPR_dip_px = 4

    # TODO: stupid hard coded value. Please solve someone.
    start_from = 3
    stopp_at   = 10

    peak_coords = np.asarray(peak_coords)
    peak_values = np.asarray(peak_values)

    # SAFETY: make sure we actually have enough points to do [start_from:-stopp_at]
    if peak_values.size <= (start_from + stopp_at):
        print("isolate_SPR: peak_values too short, cannot isolate dip.")
        return np.array([]), np.array([])

    # Find location of the minimum (assuming SPR is the minimum)
    spr_dip_index = np.argmin(peak_values[start_from:-stopp_at])
    spr_dip_index = spr_dip_index + start_from

    # Define window around dip and clamp to valid indices
    n = len(peak_coords)
    half_win = width_around_SPR_dip_px // 2
    left  = max(spr_dip_index - half_win, 0)
    right = min(spr_dip_index + half_win, n)

    spr_x = peak_coords[left:right]

    if spr_x.size == 0:
        print("isolate_SPR: empty SPR x-window (check width_around_spr_dip_um and ROI).")
        return np.array([]), np.array([])

    # Values around the SPR dip
    spr_y = peak_values[left:right]

    # Extra guard, though it should match spr_x.size
    if spr_y.size == 0:
        print("isolate_SPR: empty SPR y-window after slicing.")
        return np.array([]), np.array([])

    return spr_x, spr_y

   
def find_SPR_dip(x, y):
    
    ## Create cubicspline
    try:
        x = np.asarray(x)
        y = np.asarray(y)
        if x.size == 0 or y.size == 0:
            return np.nan
        x_fit = np.linspace(np.min(x), np.max(x), 10000)
        spline = CubicSpline(x, y)
        x_centroid = x_fit[np.argmax(spline(x_fit))]
        
    except Exception as e:
        x_centroid = np.nan
        print('Failed to find SPR Dip!', e)
        
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
        
        plt.tight_layout()
        
        self.fig = fig

        # placeholders so .set_data() is always safe
        self.im_raw_data = None
        self.line_integrated_spectrum = None
        self.filtered_spectrum = None
        self.dip_spectrum = None
        self.left_line_peak_spectrum = None
        self.right_line_peak_spectrum = None
        
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
        # Pick color for this channel
        channel_color = colors[int(laser) % len(colors)]
        
        # --- crop around laser ------------------------------------------------
        row_min = max(int(y_max_index - self.integrate_over_pixel), 0)
        row_max = min(int(y_max_index + self.integrate_over_pixel), image.shape[0])
        if row_max <= row_min:
            cropped_image = np.zeros((1, image.shape[1]))
        else:
            cropped_image = image[row_min:row_max, :]

        # --- integrate along y and build x axis ------------------------------
        x = np.arange(cropped_image.shape[1]) * px_scale
        y = np.mean(cropped_image, axis=0)

        # convert ROI limits from µm to pixel indices in x
        start_look_for_dip_from_pixel = np.argmin(np.abs(x - start_look_for_dip_from))
        stopp_look_for_dip_from_pixel = np.argmin(np.abs(x - stopp_look_for_dip_from))
        
        # --- coarse "gold line" spectrum -------------------------------------
        peak_x, peak_y = create_peak_spectrum(
            x, y, 
            start_look_for_dip_from_pixel, 
            stopp_look_for_dip_from_pixel
        )

        # --- isolate SPR region ----------------------------------------------
        spr_x, spr_y = isolate_SPR(peak_x, peak_y, width_around_SPR_dip_um)

        # --- normalize for plotting & for dip finding ------------------------
        # safe normalization (avoid division by 0)
        if peak_y.size > 0 and np.max(peak_y) > 0:
            peak_y_norm = peak_y / np.max(peak_y)
        else:
            peak_y_norm = np.zeros_like(peak_y)

        if spr_y.size > 0 and np.max(spr_y) > 0:
            spr_y_norm = spr_y / np.max(spr_y)
        else:
            spr_y_norm = np.zeros_like(spr_y)

        # find SPR location using normalized curve (same minimum position)
        if spr_x.size == 0 or spr_y_norm.size == 0:
            print(f"SPR analysis warning (laser {laser}): empty SPR window, returning NaN.")
            spr_location = np.nan
        else:
            # we still look for the *dip*, so use (1 - normalized)
            spr_location = find_SPR_dip(spr_x, 1.0 - spr_y_norm)

        # =====================================================================
        # PLOTTING
        # =====================================================================
        if frame_counter == 0:
            # --- ax0: raw image ------------------------------------------------
            self.im_raw_data = self.ax_array[0].imshow(
                image, extent=extent_raw, origin='lower'
            ) 

            # --- ax1: integrated spectrum (unnormalized is fine) --------------
            self.line_integrated_spectrum, = self.ax_array[1].plot(
                x, y, linewidth=0.5, color=channel_color
            )
            self.ax_array[1].set_xlim([start_cropped_image_from, stopp_cropped_image_from])
            if y.size > 0:
                self.ax_array[1].set_ylim([np.min(y), np.max(y)])
            
            # vertical ROI lines in ax1
            if y.size > 0:
                self.ax_array[1].plot(
                    [start_look_for_dip_from, start_look_for_dip_from],
                    [np.min(y), np.max(y)],
                    '--', color='black', linewidth=1
                )
                self.ax_array[1].plot(
                    [stopp_look_for_dip_from, stopp_look_for_dip_from],
                    [np.min(y), np.max(y)],
                    '--', color='black', linewidth=1
                )

            # --- ax2: filtered peaks, NORMALIZED 0–1 -------------------------
            if peak_x.size > 0 and peak_y_norm.size > 0:
                self.filtered_spectrum, = self.ax_array[2].plot(
                    peak_x, peak_y_norm,
                    color=channel_color,
                    marker='o', markersize=3
                )
                self.ax_array[2].set_xlim([np.min(peak_x), np.max(peak_x)])
            else:
                self.filtered_spectrum, = self.ax_array[2].plot(
                    [], [], color=channel_color, marker='o', markersize=3
                )
            # fix y-range to 0–1 so all channels share the same scale
            self.ax_array[2].set_ylim([0, 1])

            # vertical lines bracketing SPR window in ax2 (also 0–1)
            if spr_x.size > 0:
                self.left_line_peak_spectrum, = self.ax_array[2].plot(
                    [np.min(spr_x), np.min(spr_x)],
                    [0, 1],
                    '--', color='black', linewidth=1
                )
                self.right_line_peak_spectrum, = self.ax_array[2].plot(
                    [np.max(spr_x), np.max(spr_x)],
                    [0, 1],
                    '--', color='black', linewidth=1
                )
            else:
                self.left_line_peak_spectrum, = self.ax_array[2].plot([], [], '--', color='black', linewidth=1)
                self.right_line_peak_spectrum, = self.ax_array[2].plot([], [], '--', color='black', linewidth=1)

            # --- ax3: SPR dip, NORMALIZED 0–1 --------------------------------
            if spr_x.size > 0 and spr_y_norm.size > 0:
                self.dip_spectrum, = self.ax_array[3].plot(
                    spr_x, spr_y_norm,
                    color=channel_color,
                    marker='o', markersize=3
                )
                self.ax_array[3].set_xlim([np.min(spr_x), np.max(spr_x)])
            else:
                self.dip_spectrum, = self.ax_array[3].plot(
                    [], [], color=channel_color,
                    marker='o', markersize=3
                )
            self.ax_array[3].set_ylim([0, 1])

        else:
            # --- ax1 updates ---------------------------------------------------
            self.line_integrated_spectrum.set_data(x, y)
            self.line_integrated_spectrum.set_color(channel_color)
            if y.size > 0:
                self.ax_array[1].set_ylim([np.min(y), np.max(y)])

            # --- ax2 updates (normalized 0–1) ---------------------------------
            self.filtered_spectrum.set_data(peak_x, peak_y_norm)
            self.filtered_spectrum.set_color(channel_color)
            if peak_x.size > 0:
                self.ax_array[2].set_xlim([np.min(peak_x), np.max(peak_x)])
            self.ax_array[2].set_ylim([0, 1])

            # vertical lines in ax2 use 0–1 as well
            if spr_x.size > 0:
                self.left_line_peak_spectrum.set_data(
                    [np.min(spr_x), np.min(spr_x)],
                    [0, 1]
                )
                self.right_line_peak_spectrum.set_data(
                    [np.max(spr_x), np.max(spr_x)],
                    [0, 1]
                )
            else:
                self.left_line_peak_spectrum.set_data([], [])
                self.right_line_peak_spectrum.set_data([], [])

            # --- ax3 updates (normalized 0–1) ---------------------------------
            if spr_x.size > 0 and spr_y_norm.size > 0:
                self.dip_spectrum.set_data(spr_x, spr_y_norm)
                self.dip_spectrum.set_color(channel_color)
                self.ax_array[3].set_xlim([np.min(spr_x), np.max(spr_x)])
            else:
                self.dip_spectrum.set_data([], [])
            self.ax_array[3].set_ylim([0, 1])

        # redraw
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
        return spr_location


    
    def update_spr_trace(self, lasers_on_chip, results, colors, frame_counter, start_trace, clear_trace):
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
                                  color=colors[channels], label=f'Laser {channels}') 
            
        
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
    
    plt.clf()
    
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
    results = {'frame_list' : {},
               'frame_time' : {},
               'spr_data'   : {}
               }
    for i in range(len(vcsel_biases)):
        results['frame_list'][i] = []
        results['frame_time'][i] = []
        results['spr_data'][i]   = []
        
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
                image_array = cam.grab(nframes=10, frame_timeout=1.0, missing_frame='zero', return_info=False, buff_size=None)
    
                image = np.zeros_like(image_array[0])
                for i in image_array:
                    image = image + i
                
                ## Find peak position of laser beam
                y_max_index, ref_spectrum = alignment_figure_obj.update_alignment_image(image)
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
                
                ## MAIN MEASUREMENT LOOP: --------------------------------------
                while (time.time() - measurement_time_start) < measurement_time:
                    camera_start = time.time()
                    
                    for laser in lasers_on_chip:
                        laser_control.switch_to_laser(laser)
  
                        ## Grabbing image
                        image_array = cam.grab(nframes=1, frame_timeout=0.5, missing_frame='zero', buff_size=None)
                        image = image_array[0]
                        
                        image_capture_time = time.time()
                        frame_time = image_capture_time - measurement_time_start
                        
                        # Analyzing image and adding data to file
                        results['frame_time'][laser].append(frame_time)
                        results['spr_data'][laser].append(
                            spr_figure.analyze_image(
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
                                colors)
                        )
                        
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
