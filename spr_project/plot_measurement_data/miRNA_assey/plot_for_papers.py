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

#%%
## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
NM  = 1e-9
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

## Parameters
lam0   = 984*NM
eps_Au = -40.650+ 1j*2.2254

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

def theta_spr(eps_metal, n_glass, n_analyte):
    sin_theta_spr = (1/n_glass)*np.sqrt((np.abs(eps_metal)*n_analyte**2)/(np.abs(eps_metal) - n_analyte**2))
    theta_spr = np.arcsin(sin_theta_spr)
    return theta_spr

def n_spr(eps_Au, n_prism, theta_spr):
    param = np.sin(theta_spr*np.pi/180)
    eps_analyte = (np.abs(eps_Au)*n_prism**2*param**2 )/(np.abs(eps_Au) + n_prism**2*param**2)
    return np.sqrt(eps_analyte)

def x_spr_detector(theta_spr, glass_thickness):
    return 2*glass_thickness*np.tan(theta_spr)

def spr_ang(x, glass_thickness):
    return np.arctan(x/(2*glass_thickness))

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
stopp_time = 42*MIN

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h']
# conc_to_plot = ['0.02_c', '0.02_e', '0.02_h']
# conc_to_plot = ['0.05_b', '0.05_g']
# conc_to_plot = ['0.1_d', '0.1_f']
# conc_to_plot = ['0.2_j', '0.2_h']
# conc_to_plot = ['0.5_b', '0.5_g']
# conc_to_plot = ['1.0_d', '1.0_f']
# conc_to_plot = ['5.0_a', '5.0_j']

# conc_to_plot = ['0.01_c', '0.01_e', '0.01_h', 
#                 '0.02_c', '0.02_e', '0.02_h', 
#                 '0.05_b', '0.05_g', 
#                 '0.1_d', '0.1_f', 
#                 '0.2_j', '0.2_h',
#                 '0.5_b', '0.5_g',
#                 '1.0_d', '1.0_f',
#                 '5.0_a', '5.0_j']

conc_to_plot = ['0.01_c', '0.01_e', '0.01_h',
                '0.02_c', '0.02_e', '0.02_h', 
                '0.05_b', '0.05_g', 
                '0.1_d', '0.1_f', 
                '0.2_j', '0.2_h',
                '0.5_b', '0.5_g',
                '1.0_d', '1.0_f',]

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

water_SPR = theta_spr(eps_Au, n_glass, n_water)
water_SPR_deg = water_SPR*180/PI
water_SPR_pos = x_spr_detector(water_SPR, glass_thickness)
water_SPR_pos_UM = water_SPR_pos*1e6

print('Initial SPR angle in water: ' + str(round(water_SPR_deg, 2)))

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
    
    butter_0_from_water = spr_0_butter + water_SPR_pos_UM
    butter_0_theta = np.arctan(butter_0_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    label = conc[:-1]
    ax.plot(selected_time_trace_scaled, butter_0_theta*1e3, label=label + r' nM miRNA', linewidth=linewidth_filtered, color=conc_to_color[i])
    
    
    
plt.grid(True)
# plt.legend(fontsize=fontsize_legend, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]', fontsize=fontsize_label)
plt.ylabel(r'SPR shift [$\mu$m]', fontsize=fontsize_label)

ax.grid(linewidth=1, alpha=0.3)
x_tick_dx = 3
y_tick_dy = 5
# ax.set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
# ax.set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
# ax.set_yticks(np.arange(0, ax.get_ylim()[1], y_tick_dy))
# ax.set_yticklabels(np.array(ax.get_yticks()).astype(int), rotation=0, fontsize=fontsize_ticks)
plt.tight_layout()

image_name = 'miRNA_for_paper.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)


#%%

## Set time scale for plotting
time_scale = MIN

## Select what part of the trace to plot
start_time = 4*MIN
stopp_time = 19*MIN

fit_vs_raw = False
plot_or_not = True

conc_array = np.zeros(len(conc_to_plot))
binding_rates = np.zeros(len(conc_to_plot))
binding_offset = np.zeros(len(conc_to_plot))

## Figure object
if plot_or_not:
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
for i, conc in enumerate(conc_to_plot):
    conc_float = float(conc[:-2])
    conc_array[i] = conc_float
    
    ## Time tracez
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
    
    butter_0_from_water = spr_0_butter + water_SPR_pos_UM
    butter_0_theta = np.arctan(butter_0_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
    
    butter_0_theta = butter_0_theta*1e3
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    ax.plot(selected_time_trace_scaled, butter_0_theta, label=conc + r' miR-122', linewidth=linewidth_filtered)
    
    if fit_vs_raw:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_raw)
        linear_fit = linear_func(selected_time_trace_scaled, *popt)
        ax.plot(selected_time_trace_scaled, linear_fit, color='black', linewidth=0.7)
        
        binding_rates[i] = popt[0] - 0.068
        binding_offset[i] = linear_fit[-1]
        
    else:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, butter_0_theta)
        linear_fit = linear_func(selected_time_trace_scaled, *popt)
        ax.plot(selected_time_trace_scaled, linear_fit, color='black', linewidth=0.7)
 
        binding_rates[i] = popt[0] - 0.068
        binding_offset[i] = linear_fit[-1] 
    

#%%
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
conc_array = np.zeros(len(conc_to_plot) - 6)
for i, conc in enumerate(conc_to_plot):
    conc_float = float(conc[:-2])
    if conc_float != 0.01 and conc_float != 0.02:
        conc_array[i - 6] = conc_float
        if i < 6:
            binding_rates[i] = 0.006
        
        ax.plot(conc_float, binding_offset[i], 'o', color='black')
    
popt, pcov = curve_fit(linear_func, conc_array, binding_rates[6:])
x_fit = np.linspace(conc_array.min(), conc_array.max(), 1000)
linear_fit_binding_rates = linear_func(x_fit, *popt)
# ax.plot(x_fit, linear_fit_binding_rates)                                       

ax.grid(linewidth=1, alpha=0.3)

ax.set_xscale('log')
ax.set_yscale('log')

sensitivity = 20324e-6 ## dx/dn
resolution  = 4.6e-6   ## n

resolution_sensor_pos_um = sensitivity*resolution*1e6
binding_time_min = 15

min_binding_rate = resolution_sensor_pos_um/binding_time_min
unspecific_rate = 0.0

x_min_binding_rate = np.array([x_fit.min(), x_fit.max()])
y_min_binding_rate = np.array([min_binding_rate, min_binding_rate]) + unspecific_rate
# ax.plot(x_min_binding_rate, y_min_binding_rate)

image_name = 'miRNA_for_paper_binding_rate.svg'
image_format = 'svg'
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

# antibody_offsets = np.array([1.3,1.3,1.2,0.4,
#                              0.4,0.4,0,0,
#                              0,0,0.2,0,
#                              -2,-2,1,2,
#                              0, 0]) - 2.2

antibody_offsets = -np.ones(len(conc_to_plot))*2.29

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
    
    
    butter_0_from_water = spr_0_butter + water_SPR_pos_UM
    butter_0_theta = np.arctan(butter_0_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
    
    butter_0_theta = butter_0_theta*1e3
    
    ## Plot raw data
    marker_size = 0.1
    marker_type = '-x'
    marker_color  = 'black'
    linewidth_raw = 0.1
    # ax.plot(selected_time_trace_scaled, spr_0_raw, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
    
    ## Plot filtered data
    linewidth_filtered = 0.8
    ax.plot(selected_time_trace_scaled, butter_0_theta, label=conc + r' miR-122', linewidth=linewidth_filtered)
    
    if fit_vs_raw:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, spr_0_raw)
        # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
        
        antibody_response[i] = np.abs(np.sum(linear_func(selected_time_trace_scaled, *popt))/len(linear_func(selected_time_trace_scaled, *popt)) + antibody_offsets[i])
        
    else:
        popt, pcov = curve_fit(linear_func, selected_time_trace_scaled, butter_0_theta)
        # ax.plot(selected_time_trace_scaled, linear_func(selected_time_trace_scaled, *popt), color='black', linewidth=0.7)
 
        antibody_response[i] = np.abs(np.sum(linear_func(selected_time_trace_scaled, *popt))/len(linear_func(selected_time_trace_scaled, *popt))  + antibody_offsets[i])
        
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

ax.set_xscale('log')
ax.set_yscale('log')

sensitivity = 20324e-6 ## dx/dn
resolution  = 4.9e-6   ## n

resolution_sensor_pos_um = sensitivity*resolution*1e6

min_binding_rate = resolution_sensor_pos_um
unspecific_rate = 1.2

x_min_binding_rate = np.array([x_fit.min(), x_fit.max()])
y_min_binding_rate = np.array([min_binding_rate, min_binding_rate])
# ax.plot(x_min_binding_rate, y_min_binding_rate)
# 

image_name = 'miRNA_for_paper_antibody_amp.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

# conc_array = np.concat((conc_array, np.array([20, 20, 20])))
# conc_array_sorted = np.array(sorted(conc_array))

# conc_array_sorted_cont = np.linspace(conc_array_sorted.min(), conc_array_sorted.max(), 1000)
# # binding_rates = np.concat((binding_rates, np.array([3.90557596, 7.95557596, 8.05557596])))
# binding_rates = np.concat((binding_rates, np.array([8.02557596, 7.95557596, 8.05557596])))

# binding_rates_sorted = np.array([x for _, x in sorted(zip(conc_array, binding_rates), key=lambda pair: pair[0])])

# binding_rates_sorted[0] = binding_rates_sorted[0] + 0.05


# ax[1].plot(np.log10(conc_array_sorted), binding_rates_sorted, 'x', color='black')
# popt, pcov = curve_fit(linear_func, conc_array, binding_rates)
# ax[1].plot(np.log10(conc_array_sorted_cont), linear_func(conc_array_sorted_cont, *popt), '--', color='blue', linewidth=0.7)
 

# # ax[1].grid(True)
# # # ax[1].legend(fontsize=12, framealpha=0.3, edgecolor='black', bbox_to_anchor=(1.0, 1.2))
# # ax[1].set_xlabel(r'Concentration [$\log_{10}$nM]')
# # ax[1].set_ylabel(r'Binding rate [$\mu$m/min]')
        

# plt.tight_layout(h_pad=1, w_pad=10)

# ax[0].grid(linewidth=1, alpha=0.3)
# x_tick_dx = 3
# ax[0].set_xticks(np.arange(selected_time_trace_scaled[0], selected_time_trace_scaled[-1] + x_tick_dx, x_tick_dx))
# ax[0].set_xticklabels(np.array(ax.get_xticks()).astype(int), rotation=0)




#%%
image_name = 'miRNA.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

