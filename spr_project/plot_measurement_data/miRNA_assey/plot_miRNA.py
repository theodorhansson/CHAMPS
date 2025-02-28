#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import matplotlib.pyplot as plt
import numpy as np

from scipy.signal import butter, filtfilt, freqz
from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, savgol
from spr_project.spr_calculations.spr_sensing import bulk_sensitivity

## Constants
PI = np.pi
MM = 1e-3
UM = 1e-6
MIN = 60

### Plot arguments
fontsize_title  = 16
fontsize_label  = 14
fontsize_ticks  = 12
figure_width    = 10
figure_height   = 8
fontsize_legend = 14

## Measurement variables
glass_thickness = 1.4*MM
n_water = 1.33
n_glass = 1.51
S_bulk = bulk_sensitivity(n_water, n_glass, glass_thickness)
S_bulk_um = S_bulk/UM

## Butterworth filter to filter out the pump noise
def butterworth(data, plot_filter_transfer=False):
    
    ## Pump noise has a strong peak at roughly 0.2 Hz
    cutoff_freq = 0.12
    ## Order of butterworth filter
    order = 3
    ## Sampling frequency of signal
    fs = 1
    
    ## Create butterworth low-pass filter
    b, a = butter(order, cutoff_freq, fs=fs, btype='lp', analog=False)
    ## Apply the filter twice
    data = filtfilt(b, a, data)
    
    ## Plot the transfer function of the filter
    if plot_filter_transfer:
        
        plt.figure(0)
        w, h = freqz(b, a, fs=fs, worN=2**12)
        plt.plot(w, np.abs(h), 'b', label=r'Transfer function')
        plt.plot(cutoff_freq, 0.5*np.sqrt(2), 'ko')
        plt.axvline(cutoff_freq, color='k', label=f'$f_c$ = {cutoff_freq} Hz')
        plt.xlim(0, fs/2)
        plt.title('Lowpass Filter Transfer function', fontsize=fontsize_title)
        plt.xlabel('Frequency [Hz]', fontsize=fontsize_label)
        plt.ylabel('Amplitude [-]', fontsize=fontsize_label)
        plt.xticks(fontsize=fontsize_ticks)
        plt.yticks(fontsize=fontsize_ticks)
        plt.grid(linewidth=1, alpha=0.3)
        plt.legend(fontsize=fontsize_legend, framealpha=0.3, edgecolor='black', loc='upper right')
        plt.tight_layout()
        
    return data

def select_data_and_filter(data, start_time_index, stopp_time_index, offset):
    spr_data   = data[start_time_index:stopp_time_index]
    spr_data_zeroed = spr_data - spr_data[0] + offset
    return (spr_data_zeroed, butterworth(spr_data_zeroed))

## Attempt 5 at bio-measurements
measurements = {'20_5_nM' : {'data_folder': 'spr_measurements_240919', 'measurement_number' : 0},
                '0.5_0.05_nM' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 0},
                '0.2_0.01_nM_a' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 1},
                '1_0.1_nM': {'data_folder': 'spr_measurements_240925', 'measurement_number' : 2},
                '0.2_0.01_nM_b': {'data_folder': 'spr_measurements_240925', 'measurement_number' : 3},
                '20_1_0.1_nM': {'data_folder': 'spr_measurements_240925', 'measurement_number' : 4},
                '0.01_0.02_nM_c': {'data_folder': 'spr_measurements_241016', 'measurement_number' : 0}}

select_measurement = '20_1_0.1_nM'

## Load all data
spr_data_folder = measurements[select_measurement]['data_folder']
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']
files_to_plot = np.array([measurements[select_measurement]['measurement_number']], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                                           mov_avg_window=mov_avg_window,
                                                                           sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 4*MIN
stopp_time = 60*MIN

## Time trace
time_trace = plot_raw[vcsels[0]][0, :]
start_time_index = np.argmin(np.abs(time_trace - start_time))
stopp_time_index = np.argmin(np.abs(time_trace - stopp_time))

selected_time_trace = time_trace[start_time_index:stopp_time_index]

## Set start time to zero
selected_time_trace_scaled = (selected_time_trace - selected_time_trace[0])/time_scale

# VCSEL_0
spr_0_offset = 0
spr_0_data  = plot_raw[vcsels[0]][1, :]
spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index, spr_0_offset)

# VCSEL_1
spr_1_offset = 0
spr_1_data  = plot_raw[vcsels[1]][1, :]
spr_1_raw, spr_1_butter = select_data_and_filter(spr_1_data, start_time_index, stopp_time_index, spr_1_offset)

# VCSEL_3
spr_2_offset = 0
spr_2_data  = plot_raw[vcsels[2]][1, :]
spr_2_raw, spr_2_butter = select_data_and_filter(spr_2_data, start_time_index, stopp_time_index, spr_2_offset)


## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

## Plot raw data
marker_size = 0.1
marker_type = '-x'
marker_color  = 'black'
linewidth_raw = 0.1
plt.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.plot(selected_time_trace_scaled, spr_1_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.plot(selected_time_trace_scaled, spr_2_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)

## Plot filtered data
linewidth_filtered = 0.8
plt.plot(selected_time_trace_scaled, spr_0_butter, color='blue', label=r'0.1 nM miR-122', linewidth=linewidth_filtered)
plt.plot(selected_time_trace_scaled, spr_1_butter, color='red', label=r'1.0 nM miR-122', linewidth=linewidth_filtered)
plt.plot(selected_time_trace_scaled, spr_2_butter, color='green', label=r'20.0 reference', linewidth=linewidth_filtered)

plt.grid(True)
plt.legend(fontsize=12, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')

ax.grid(linewidth=1, alpha=0.3)
x_tick_dx = 3
ax.set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
ax.set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0)


#%%
image_name = 'miRNA.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

#%%

vcsel_size = 0.8e-2

