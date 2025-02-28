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
NM  = 1e-9
MIN = 60
import matplotlib as mpl

from matplotlib import cm
cmap = cm.magma
colors = cmap(np.linspace(0, 1, 10))

colors_bright = colors[1]
colors_med = colors[3]
colors_dark = colors[9]


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


## Measurement variables
glass_thickness = 1.4*MM
n_water = 1.33
n_glass = 1.51
S_bulk = bulk_sensitivity(n_water, n_glass, glass_thickness)
S_bulk_um = S_bulk/UM

lam0   = 984*NM
eps_Au = -40.650 + 1j*2.2254

## Butterworth filter to filter out the pump noise
def butterworth(data, plot_filter_transfer=False):
    
    ## Pump noise has a strong peak at roughly 0.2 Hz
    cutoff_freq = 0.1
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
        plt.title('Lowpass Filter Transfer function')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude [-]')
        plt.grid(linewidth=1, alpha=0.3)
        plt.legend(framealpha=0.3, edgecolor='black', loc='upper right')
        plt.tight_layout()
        
    return data

def select_data_and_filter(data, start_time_index, stopp_time_index, offset):
    spr_data   = data[start_time_index:stopp_time_index]
    spr_data_zeroed = spr_data - spr_data[0] + offset
    return (spr_data_zeroed, butterworth(spr_data_zeroed))


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


spr_data_folder = 'spr_measurements_250207'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']

files_to_plot = np.array([0], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5

plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                                           mov_avg_window=mov_avg_window,
                                                                           sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

time_trace_1 = plot_raw[vcsels[0]][1,:]
time_trace_2 = plot_raw[vcsels[1]][1,:]
time_trace_3 = plot_raw[vcsels[2]][1,:]

butter_1 = butterworth(time_trace_1)
butter_2 = butterworth(time_trace_2)
butter_3 = butterworth(time_trace_3)

water_SPR = theta_spr(eps_Au, n_glass, n_water)
water_SPR_deg = water_SPR*180/PI
water_SPR_pos = x_spr_detector(water_SPR, glass_thickness)
water_SPR_pos_UM = water_SPR_pos*1e6

print('Initial SPR angle in water: ' + str(round(water_SPR_deg, 2)))

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)

butter_1_from_water = butter_1 + water_SPR_pos_UM
butter_2_from_water = butter_2 + water_SPR_pos_UM
butter_3_from_water = butter_3 + water_SPR_pos_UM

# butter_1_theta = np.unravel(np.arctan(butter_1/(2*glass_thickness)))
butter_1_theta = np.arctan(butter_1_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
butter_2_theta = np.arctan(butter_2_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
butter_3_theta = np.arctan(butter_3_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg

ax.plot(frame_time/MIN, butter_1_theta*1e3, label=r'Channel 1', )
ax.plot(frame_time/MIN, butter_2_theta*1e3, label=r'Channel 2', )
ax.plot(frame_time/MIN, butter_3_theta*1e3, label=r'Channel 3', )

# ax.plot(frame_time[::2]/MIN, time_trace_1[::2], 'o', color='black', ms=0.01)
# ax.plot(frame_time[::2]/MIN, time_trace_2[::2], 'o', color='black', ms=0.01)
# ax.plot(frame_time[::2]/MIN, time_trace_3[::2], 'o', color='black', ms=0.01)


levels = np.array([28.4, 2*28.4, 3*28.4, 4*28.4, 5*28.4])
levels_x = np.array([np.min(frame_time/MIN), np.max(frame_time/MIN)])

# for level in levels:
#     levels_y = np.array([level, level])
#     ax.plot(levels_x, levels_y, '--', color='black')

# ax2 = ax.twinx()
# ax2.set_ylabel(r'Refractive index [-]')
    
plt.legend()
plt.grid(True)

plt.savefig('five_steps.svg', format='svg')

#%%

std_array = np.arange(0, 410, 1)
spr_data_std  = np.std(butter_1[std_array], ddof=1)
delta_n_pump_on = spr_data_std/20324
print()
print(f'------ Delta n with pump on: {np.round(delta_n_pump_on, 7)} ------')
print()






