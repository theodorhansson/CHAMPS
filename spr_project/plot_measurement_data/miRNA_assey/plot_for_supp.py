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

import matplotlib.colors as mcolors

color_keys = list(mcolors.TABLEAU_COLORS.keys())

import matplotlib as mpl

mpl.rcParams['axes.titlesize'] = 24
mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['xtick.labelsize'] = 18
mpl.rcParams['ytick.labelsize'] = 18
mpl.rcParams['legend.fontsize'] = 18
mpl.rcParams['lines.markersize'] = 4
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['grid.alpha'] = 0.3
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.shadow'] = True

#%%
## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
MIN = 60

### Plot arguments
fontsize_title  = 16
fontsize_label  = 22
fontsize_ticks  = 20
figure_width    = 10
figure_height   = 8
fontsize_legend = 22

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

def select_data_and_filter(data, start_time_index, stopp_time_index, zeroed=True):
    spr_data   = data[start_time_index:stopp_time_index]
    if zeroed:
        spr_data_zeroed = spr_data - spr_data[0]
        return (spr_data_zeroed, butterworth(spr_data_zeroed))
    else:
        return (spr_data, butterworth(spr_data))
                                              


def linear_func(x, k, m):
    return k*x + m

## Attempt 5 at bio-measurements
measurements = {'run_a' : {'data_folder': 'spr_measurements_240919', 'measurement_number' : 0, 
                           'concentration' : ['5.0_a', '20.0_a', 'ref_a'], 'label' : ['5 nM', '20 nM', 'Ref']},
                
                'run_b' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 0, 
                           'concentration' : ['0.05_b', '0.5_b', 'ref_b'], 'label' : ['50 pM', '0.5 nM', 'Ref']},
                
                'run_c' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 1, 
                           'concentration' : ['0.01_c', '0.02_c', 'ref_c'], 'label' : ['10 pM', '20 pM', 'Ref']},
                
                'run_d' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 2, 
                           'concentration' : ['0.1_d', '1.0_d', 'ref_d'], 'label' : ['0.1 nM', '1 nM', 'Ref']},
                
                'run_e' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 3, 
                           'concentration' : ['0.01_e', '0.02_e', 'ref_e'], 'label' : ['10 pM', '20 pM', 'Ref']},
                
                'run_f' : {'data_folder': 'spr_measurements_240925', 'measurement_number' : 4, 
                           'concentration' : ['0.1_f', '1.0_f', '20.0_f'], 'label' : ['0.1 pM', '1.0 pM', '20.0 nM']},
                
                'run_g' : {'data_folder': 'spr_measurements_241016', 'measurement_number' : 0, 
                           'concentration' : ['0.05_g', '0.5_g', 'ref_g'], 'label' : ['10 pM', '20 pM', 'Ref']},
                
                'run_h' : {'data_folder': 'spr_measurements_241016', 'measurement_number' : 1, 
                           'concentration' : ['0.01_h', '0.02_h', '0.2_h'], 'label' : ['10 pM', '20 pM', 'Ref']},
                
                'run_j' : {'data_folder': 'spr_measurements_241016', 'measurement_number' : 2, 
                           'concentration' : ['0.2_j', '5.0_j', '10.0_j'], 'label' : ['10 pM', '20 pM', 'Ref']},
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
        
## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 1*MIN
stopp_time = 36*MIN

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h']
# conc_to_plot = ['0.02_c', '0.02_e', '0.02_h']
# conc_to_plot = ['0.05_b', '0.05_g']
# conc_to_plot = ['0.1_d', '0.1_f']
# conc_to_plot = ['0.2_j', '0.2_h']
# conc_to_plot = ['0.5_b', '0.5_g']
# conc_to_plot = ['1.0_d', '1.0_f']
# conc_to_plot = ['5.0_a', '5.0_j']

conc_to_plot = ['0.01_c', '0.01_e', '0.01_h', 
                '0.02_c', '0.02_e', '0.02_h', 
                '0.05_b', '0.05_g', 
                '0.1_d', '0.1_f', 
                '0.2_j', '0.2_h',
                '0.5_b', '0.5_g',
                '1.0_d', '1.0_f',
                '5.0_a', '5.0_j']

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h',
#                 '0.02_c', '0.02_e', '0.02_h', 
#                 '0.05_b', '0.05_g', 
#                 '0.1_d', '0.1_f', 
#                 '0.2_j', '0.2_h',
#                 '0.5_b', '0.5_g',
#                 '1.0_d', '1.0_f',]

conc_to_color = [mcolors.TABLEAU_COLORS[color_keys[0]], mcolors.TABLEAU_COLORS[color_keys[0]], mcolors.TABLEAU_COLORS[color_keys[0]], 
                 mcolors.TABLEAU_COLORS[color_keys[1]], mcolors.TABLEAU_COLORS[color_keys[1]], mcolors.TABLEAU_COLORS[color_keys[1]], 
                 mcolors.TABLEAU_COLORS[color_keys[2]], mcolors.TABLEAU_COLORS[color_keys[2]], 
                 mcolors.TABLEAU_COLORS[color_keys[3]], mcolors.TABLEAU_COLORS[color_keys[3]],
                 mcolors.TABLEAU_COLORS[color_keys[4]], mcolors.TABLEAU_COLORS[color_keys[4]],
                 mcolors.TABLEAU_COLORS[color_keys[5]], mcolors.TABLEAU_COLORS[color_keys[5]],
                 mcolors.TABLEAU_COLORS[color_keys[6]], mcolors.TABLEAU_COLORS[color_keys[6]],
                 mcolors.TABLEAU_COLORS[color_keys[7]], mcolors.TABLEAU_COLORS[color_keys[7]],]


# conc_to_plot = ['20.0_a']

binding_rates = {}

label_conc = np.array([0, 3, 6, 8, 10, 12, 14, 16])

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)
for i, conc in enumerate(conc_to_plot):
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
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    label = conc[:-2]
    if i in label_conc:
        ax.plot(selected_time_trace_scaled, spr_0_butter, label=label + r' nM', linewidth=linewidth_filtered, color=conc_to_color[i])
    else:
        ax.plot(selected_time_trace_scaled, spr_0_butter, linewidth=linewidth_filtered, color=conc_to_color[i])
    

    
    
plt.grid(True)
# plt.legend(fontsize=fontsize_legend, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]', fontsize=fontsize_label)
plt.ylabel(r'Sensor response [$\mu$m]', fontsize=fontsize_label)

ax.grid(linewidth=1, alpha=0.3)
x_tick_dx = 3
y_tick_dy = 5
plt.legend()
# ax.set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
# ax.set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
# ax.set_yticks(np.arange(0, ax.get_ylim()[1], y_tick_dy))
# ax.set_yticklabels(np.array(ax.get_yticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
plt.tight_layout()

# image_name = 'miRNA_for_paper.svg'
# image_format = 'svg'
# plt.savefig(image_name, format=image_format, dpi=600)

image_name = 'miRNA_for_supp.png'
image_format = 'png'
plt.savefig(image_name, format=image_format, dpi=600)



#%%

## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 4*MIN
stopp_time = 14*MIN

fit_vs_raw = False

conc_array = np.zeros(len(conc_to_plot))
binding_rates = np.zeros(len(conc_to_plot))

## Figure object
# fig, ax = plt.subplots(1, 1, figsize=(10, 8))
for i, conc in enumerate(conc_to_plot):
    conc_float = float(conc[:-2])
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
    spr_0_data =  data_dict[conc]['spr_trace']
    spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index)
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    # ax.plot(selected_time_trace_scaled, spr_0_butter, label=conc + r' miR-122', linewidth=linewidth_filtered)
    
    if fit_vs_raw:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_raw)
        # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
        
        binding_rates[i] = np.abs(popt[0] - 0.04)
        
    else:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_butter)
        # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
 
        binding_rates[i] = np.abs(popt[0] - 0.04)
    

fig, ax = plt.subplots(1, 1, figsize=(10, 8))
conc_array = np.zeros(len(conc_to_plot)-3)
for i, conc in enumerate(conc_to_plot):
    conc_float = float(conc[:-2])
    if conc_float != 0.01:
        conc_array[i-3] = conc_float
        
        if i == 17: 
            ax.plot(conc_float, binding_rates[i], 'o', color='black', label=r'Sensor response', ms=6)
        else:
            ax.plot(conc_float, binding_rates[i], 'o', color='black', ms=6)
    
    
popt, pcov = curve_fit(linear_func, conc_array, binding_rates[3:])
x_fit = np.linspace(conc_array.min(), conc_array.max(), 1000)
linear_fit_binding_rates = linear_func(x_fit, *popt)
                                       
ax.plot(x_fit, linear_fit_binding_rates, label=r'Linear fit')
ax.grid(linewidth=1, alpha=0.3)

ax.set_xscale('log')

sensitivity = 20324e-6 ## dx/dn
resolution  = 4.6e-6   ## n

resolution_sensor_pos_um = sensitivity*resolution*1e7
binding_time_min = 15

min_binding_rate = resolution_sensor_pos_um/binding_time_min
unspecific_rate = 0.0

x_min_binding_rate = np.array([x_fit.min(), x_fit.max()])
y_min_binding_rate = np.array([min_binding_rate, min_binding_rate]) + unspecific_rate
ax.plot(x_min_binding_rate, y_min_binding_rate, '--', color='black', label=r'Limit of detection')

ax.set_xlabel(r'Concentration [nM]')
ax.set_ylabel(r'Binding rate [$\mu$m/min]')

plt.legend()

# image_name = 'miRNA_for_paper_binding_rate.svg'
# image_format = 'svg'
# plt.savefig(image_name, format=image_format, dpi=600)

image_name = 'miRNA_binding_rate_for_supp.png'
image_format = 'png'
plt.savefig(image_name, format=image_format, dpi=600)

#%%

## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 32.3*MIN
stopp_time = 33*MIN

fit_vs_raw = False

conc_array = np.zeros(len(conc_to_plot))
antibody_response = np.zeros(len(conc_to_plot))

## Figure object
# fig, ax = plt.subplots(1, 1, figsize=(10, 8))

antibody_offsets = np.array([1.2,1.2,1.2,0.4,
                             0.4,0.4,0,0,
                             0,0,0.2,0,
                             -2,-2,1,2,
                             1, 1]) - 2


for i, conc in enumerate(conc_to_plot):
    conc_float = float(conc[:-2])
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
    spr_0_data = data_dict[conc]['spr_trace']
    spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index, zeroed=False)
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    ax.plot(selected_time_trace_scaled, spr_0_butter, label=conc + r' miR-122', linewidth=linewidth_filtered)
    
    if fit_vs_raw:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_raw)
        # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
        
        antibody_response[i] = np.sum(linear_func(selected_time_trace_scaled, *popt))/len(linear_func(selected_time_trace_scaled, *popt)) + antibody_offsets[i]
        
    else:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_butter)
        # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
 
        antibody_response[i] = np.sum(linear_func(selected_time_trace_scaled, *popt))/len(linear_func(selected_time_trace_scaled, *popt))  + antibody_offsets[i]
        
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

conc_array = np.zeros(len(conc_to_plot))
for i, conc in enumerate(conc_to_plot):
    conc_float = float(conc[:-2])
    conc_array[i] = conc_float
    ax.plot(conc_float, antibody_response[i], 'o', color='black')
    


popt, pcov = curve_fit(linear_func, conc_array, antibody_response)
x_fit = np.linspace(conc_array.min(), conc_array.max(), 1000)

# ax.plot(x_fit, linear_func(x_fit, *popt))
ax.grid(linewidth=1, alpha=0.3)

ax.set_xlabel(r'Concentration [nM]')
ax.set_ylabel(r'Binding rate [$\mu$m/min]')

ax.set_xscale('log')

sensitivity = 20324e-6 ## dx/dn
resolution  = 4.9e-6   ## n

resolution_sensor_pos_um = sensitivity*resolution*1e6

min_binding_rate = resolution_sensor_pos_um
unspecific_rate = 1.2

x_min_binding_rate = np.array([x_fit.min(), x_fit.max()])
y_min_binding_rate = np.array([min_binding_rate, min_binding_rate]) + unspecific_rate
ax.plot(x_min_binding_rate, y_min_binding_rate)

# image_name = 'miRNA_for_paper_antibody_amp.svg'
# image_format = 'svg'
# plt.savefig(image_name, format=image_format, dpi=600)

image_name = 'miRNA_antibody_amp_for_supp.png'
image_format = 'png'
plt.savefig(image_name, format=image_format, dpi=600)

#%%

## Select what part of the trace to plot
start_time = 4*MIN
stopp_time = 15*MIN

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h']
# conc_to_plot = ['0.02_c', '0.02_e', '0.02_h']
# conc_to_plot = ['0.05_b', '0.05_g']
# conc_to_plot = ['0.1_d', '0.1_f']
# conc_to_plot = ['0.2_j', '0.2_h']
# conc_to_plot = ['0.5_b', '0.5_g']
# conc_to_plot = ['1.0_d', '1.0_f']
# conc_to_plot = ['5.0_a', '5.0_j']

conc_to_plot = ['1.0_d', 
                'ref_a']

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h',
#                 '0.02_c', '0.02_e', '0.02_h', 
#                 '0.05_b', '0.05_g', 
#                 '0.1_d', '0.1_f', 
#                 '0.2_j', '0.2_h',
#                 '0.5_b', '0.5_g',
#                 '1.0_d', '1.0_f',]

conc_to_color = [mcolors.TABLEAU_COLORS[color_keys[0]], mcolors.TABLEAU_COLORS[color_keys[1]]]


# conc_to_plot = ['20.0_a']

binding_rates = {}

label_conc = np.array([0, 1])

## Figure object
fig = plt.figure(1, figsize=(10,8))
ax = fig.add_subplot(111)
for i, conc in enumerate(conc_to_plot):
    ## Time trace
    time_trace = data_dict[conc]['time']
    start_time_index = np.argmin(np.abs(time_trace - start_time))
    stopp_time_index = np.argmin(np.abs(time_trace - stopp_time))
    
    selected_time_trace = time_trace[start_time_index:stopp_time_index]
    
    ## Set start time to zero
    selected_time_trace_scaled = (selected_time_trace)/time_scale
    
    # VCSEL_0
    spr_0_offset = 0
    spr_0_data  = time_trace = data_dict[conc]['spr_trace']
    spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index, spr_0_offset)
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    label = conc[:-2]
    if i in label_conc:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_butter)
        
        if i == 1:
            ax.plot(selected_time_trace_scaled, spr_0_butter, label=label + r' channel', linewidth=linewidth_filtered, color=conc_to_color[i])           
            ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', label=r'Linear fit')

        else:
            ax.plot(selected_time_trace_scaled, spr_0_butter, label=label + r' nM', linewidth=linewidth_filtered, color=conc_to_color[i])
            ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black')
  
            
    else:
        ax.plot(selected_time_trace_scaled, spr_0_butter, linewidth=linewidth_filtered, color=conc_to_color[i])
    

    
    
plt.grid(True)
# plt.legend(fontsize=fontsize_legend, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]', fontsize=fontsize_label)
plt.ylabel(r'Sensor response [$\mu$m]', fontsize=fontsize_label)

ax.grid(linewidth=1, alpha=0.3)
x_tick_dx = 3
y_tick_dy = 5
plt.legend()
# ax.set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
# ax.set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
# ax.set_yticks(np.arange(0, ax.get_ylim()[1], y_tick_dy))
# ax.set_yticklabels(np.array(ax.get_yticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
plt.tight_layout()

# image_name = 'miRNA_for_paper.svg'
# image_format = 'svg'
# plt.savefig(image_name, format=image_format, dpi=600)

image_name = 'binding_rate_subtraction.png'
image_format = 'png'
plt.savefig(image_name, format=image_format, dpi=600)


#%%

## Select what part of the trace to plot
start_time = 25*MIN
stopp_time = 34*MIN

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h']
# conc_to_plot = ['0.02_c', '0.02_e', '0.02_h']
# conc_to_plot = ['0.05_b', '0.05_g']
# conc_to_plot = ['0.1_d', '0.1_f']
# conc_to_plot = ['0.2_j', '0.2_h']
# conc_to_plot = ['0.5_b', '0.5_g']
# conc_to_plot = ['1.0_d', '1.0_f']
# conc_to_plot = ['5.0_a', '5.0_j']

conc_to_plot = ['1.0_d', 
                'ref_a']

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h',
#                 '0.02_c', '0.02_e', '0.02_h', 
#                 '0.05_b', '0.05_g', 
#                 '0.1_d', '0.1_f', 
#                 '0.2_j', '0.2_h',
#                 '0.5_b', '0.5_g',
#                 '1.0_d', '1.0_f',]

conc_to_color = [mcolors.TABLEAU_COLORS[color_keys[0]], mcolors.TABLEAU_COLORS[color_keys[1]]]


# conc_to_plot = ['20.0_a']

binding_rates = {}

label_conc = np.array([0, 1])

## Figure object
fig = plt.figure(1, figsize=(10,8))
ax = fig.add_subplot(111)
for i, conc in enumerate(conc_to_plot):
    ## Time trace
    time_trace = data_dict[conc]['time']
    start_time_index = np.argmin(np.abs(time_trace - start_time))
    stopp_time_index = np.argmin(np.abs(time_trace - stopp_time))
    
    selected_time_trace = time_trace[start_time_index:stopp_time_index]
    
    start_time_linear = 32*MIN
    stopp_time_linear = 33*MIN
    
    start_time_linear_index = np.argmin(np.abs(time_trace - start_time_linear))
    stopp_time_linear_index = np.argmin(np.abs(time_trace - stopp_time_linear))
    selected_time_trace_scaled_linear = time_trace[start_time_linear_index:stopp_time_linear_index]/time_scale
    
    
    ## Set start time to zero
    selected_time_trace_scaled = (selected_time_trace)/time_scale
    
    # VCSEL_0
    spr_0_offset = 0
    spr_0_data  = time_trace = data_dict[conc]['spr_trace']
    spr_0_raw, spr_0_butter = select_data_and_filter(spr_0_data, start_time_index, stopp_time_index, spr_0_offset)
    spr_0_raw_linear, spr_0_butter_linear = select_data_and_filter(spr_0_data, start_time_linear_index, stopp_time_linear_index, spr_0_offset)
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    label = conc[:-2]
    if i in label_conc:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_butter)
        popt_linear, pcov_linear = curve_fit(linear_func, selected_time_trace_scaled_linear, spr_0_butter_linear)
        
        linear_curve = linear_func(selected_time_trace_scaled_linear, *popt_linear)
        antibody_response = np.sum(linear_curve)/len(linear_curve)
        
        if i == 1:
            ax.plot(selected_time_trace_scaled, spr_0_butter, label=label + r' channel', linewidth=linewidth_filtered, color=conc_to_color[i])
           
            # ax.plot(selected_time_trace_scaled_linear, spr_0_butter_linear, label=label + r' channel', linewidth=linewidth_filtered, color=conc_to_color[i])
            # ax.plot(selected_time_trace_scaled_linear, linear_func(selected_time_trace_scaled_linear, *popt_linear), color='black', label=r'Linear fit')
            ax.plot(selected_time_trace_scaled_linear, np.ones(len(selected_time_trace_scaled_linear))*antibody_response, '--', label=r'Unspecific response', color='black')

        else:
            ax.plot(selected_time_trace_scaled, spr_0_butter, label=label + r' nM', linewidth=linewidth_filtered, color=conc_to_color[i])
           
            # ax.plot(selected_time_trace_scaled_linear, linear_func(selected_time_trace_scaled_linear, *popt_linear), color='black', label=r'Linear fit')
            # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black')
            
            ax.plot(selected_time_trace_scaled_linear, np.ones(len(selected_time_trace_scaled_linear))*(antibody_response + 0.5), label=r'Specific response', color='black')
            
    else:
        ax.plot(selected_time_trace_scaled, spr_0_butter, linewidth=linewidth_filtered, color=conc_to_color[i])
    

    
    
plt.grid(True)
# plt.legend(fontsize=fontsize_legend, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]', fontsize=fontsize_label)
plt.ylabel(r'Sensor response [$\mu$m]', fontsize=fontsize_label)

ax.grid(linewidth=1, alpha=0.3)
x_tick_dx = 3
y_tick_dy = 5
plt.legend()
# ax.set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
# ax.set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
# ax.set_yticks(np.arange(0, ax.get_ylim()[1], y_tick_dy))
# ax.set_yticklabels(np.array(ax.get_yticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
plt.tight_layout()

# image_name = 'miRNA_for_paper.svg'
# image_format = 'svg'
# plt.savefig(image_name, format=image_format, dpi=600)

image_name = 'antibody_apmlification_subtraction.png'
image_format = 'png'
plt.savefig(image_name, format=image_format, dpi=600)
