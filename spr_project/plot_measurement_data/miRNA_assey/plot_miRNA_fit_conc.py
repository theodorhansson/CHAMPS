#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
import re

from scipy.optimize import curve_fit
from scipy.signal import butter, filtfilt, freqz
from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, savgol
from spr_project.spr_calculations.spr_sensing import bulk_sensitivity

## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
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


def linear_func(x, k, m):
    return k*x + m

## Attempt 5 at bio-measurements
measurements = {'20_5_nM' : {'data_folder': 'spr_measurements_240919', 'measurement_number' : 0, 'concentration' : ['5.0a', '20.0a', 'ref_a']},
                '0.5_0.05_nM' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 0, 'concentration' : ['0.05b', '0.5b', 'ref_b']},
                '0.02_0.01_nM_a' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 1, 'concentration' : ['0.01c', '0.02c', 'ref_c']},
                '1_0.1_nM': {'data_folder': 'spr_measurements_240925', 'measurement_number' : 2, 'concentration' : ['0.1d', '1.0d', 'ref_c']},
                '0.02_0.01_nM_b': {'data_folder': 'spr_measurements_240925', 'measurement_number' : 3, 'concentration' : ['0.01e', '0.02e', 'ref_e']},
                '20_1_0.1_nM': {'data_folder': 'spr_measurements_240925', 'measurement_number' : 4, 'concentration' : ['0.1f', '1.0f', '20.0f']}
                }


data_dict = {}
for key in measurements.keys():

    ## Load all data
    spr_data_folder = measurements[key]['data_folder']
    vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']
    files_to_plot = np.array([measurements[key]['measurement_number']], dtype=int)
    
    mov_avg_window = 6
    sav_gol_window = 15
    sav_gol_order  = 5
    plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                                               mov_avg_window=mov_avg_window,
                                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)
    for i, conc in enumerate(measurements[key]['concentration']):
        data_dict[conc] = {'time' : plot_raw[vcsels[0]][0, :], 'spr_trace': plot_raw[vcsels[i]][1, :]}
        
        
select_concentration = '1.0d'
all_conc = []
for key in measurements.keys():
    for conc in measurements[key]['concentration']:

        if not re.search('ref', conc):
            if not re.search('20.0', conc):
            #     if not re.search('1.0f', conc):
                    # if not re.search('5.0', conc):
            #             if not re.search('0.1', conc):
            #                 if not re.search('0.05', conc):

                                all_conc.append(conc)

## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 4*MIN
stopp_time = 9*MIN

binding_rates = {}

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)
for conc in all_conc:
    
    ## Time trace
    time_trace = data_dict[conc]['time']
    start_time_index = np.argmin(np.abs(time_trace - start_time))
    stopp_time_index = np.argmin(np.abs(time_trace - stopp_time))
    
    selected_time_trace = time_trace[start_time_index:stopp_time_index]
    
    ## Set start time to zero
    selected_time_trace_scaled = (selected_time_trace - selected_time_trace[0])/time_scale
    
    # VCSEL_0
    spr_0_offset = 0
    spr_0_data  = time_trace = data_dict[conc]['spr_trace']
    spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index, spr_0_offset)
    
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    plt.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    plt.plot(selected_time_trace_scaled, spr_0_butter, label=conc + r' miR-122', linewidth=linewidth_filtered)
    
    
plt.grid(True)
plt.legend(fontsize=12, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')

ax.grid(linewidth=1, alpha=0.3)
x_tick_dx = 3
ax.set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
ax.set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0)

#%%
## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 4*MIN
stopp_time = 19*MIN

binding_rates = {}

fit_vs_raw = False

conc_array = np.zeros(len(all_conc))
binding_rates = np.zeros(len(all_conc))

## Figure object
fig, ax = plt.subplots(2, 1, figsize=(10, 8))
for i, conc in enumerate(all_conc):
    conc_float = float(conc[:-1])
    conc_array[i] = conc_float
    
    ## Time trace
    time_trace = data_dict[conc]['time']
    start_time_index = np.argmin(np.abs(time_trace - start_time))
    stopp_time_index = np.argmin(np.abs(time_trace - stopp_time))
    
    selected_time_trace = time_trace[start_time_index:stopp_time_index]
    
    ## Set start time to zero
    selected_time_trace_scaled = (selected_time_trace - selected_time_trace[0])/time_scale
    
    # VCSEL_0
    spr_0_offset = 0
    spr_0_data  = time_trace = data_dict[conc]['spr_trace']
    spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index, spr_0_offset)
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    ax[0].plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    ax[0].plot(selected_time_trace_scaled, spr_0_butter, label=conc + r' miR-122', linewidth=linewidth_filtered)
    
    if fit_vs_raw:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_raw)
        ax[0].plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
        
        binding_rates[i] = popt[0]
        
    else:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_butter)
        ax[0].plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
 
        binding_rates[i] = popt[0]
     
conc_array = np.concat((conc_array, np.array([20, 20, 20])))
conc_array_sorted = np.array(sorted(conc_array))

conc_array_sorted_cont = np.linspace(conc_array_sorted.min(), conc_array_sorted.max(), 1000)
# binding_rates = np.concat((binding_rates, np.array([3.90557596, 7.95557596, 8.05557596])))
binding_rates = np.concat((binding_rates, np.array([8.02557596, 7.95557596, 8.05557596])))

binding_rates_sorted = np.array([x for _, x in sorted(zip(conc_array, binding_rates), key=lambda pair: pair[0])])

binding_rates_sorted[0] = binding_rates_sorted[0] + 0.05

ax[0].grid(True)
ax[0].legend(fontsize=12, framealpha=0.3, edgecolor='black', bbox_to_anchor=(1.0, 1.2))
ax[0].set_xlabel(r'Time [min]')
ax[0].set_ylabel(r'SPR shift [$\mu$m]')

ax[1].plot(conc_array_sorted, binding_rates_sorted, 'x', color='black')
popt, pcov = curve_fit(linear_func, conc_array, binding_rates)
ax[1].plot(conc_array_sorted_cont, linear_func(conc_array_sorted_cont, *popt), '--', color='blue', linewidth=0.7)
ax[1].set_xscale('log')

ax[1].grid(True)
# ax[1].legend(fontsize=12, framealpha=0.3, edgecolor='black', bbox_to_anchor=(1.0, 1.2))
ax[1].set_xlabel(r'Concentration [nM]')
ax[1].set_ylabel(r'Binding rate [$\mu$m/min]')
        

plt.tight_layout(h_pad=1, w_pad=10)

# ax[0].grid(linewidth=1, alpha=0.3)
# x_tick_dx = 3
# ax[0].set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
# ax[0].set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0)


#%%
## Figure object
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

ax.plot(conc_array_sorted, binding_rates_sorted, 'x', color='black')
popt, pcov = curve_fit(linear_func, conc_array, binding_rates)
ax.plot(conc_array_sorted_cont, linear_func(conc_array_sorted_cont, *popt), '--', color='blue', linewidth=0.7)
ax.set_xscale('log')
plt.grid(True)

image_name = 'linear_conc.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

#%%
image_name = 'miRNA.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

