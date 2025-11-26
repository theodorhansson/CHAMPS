#%%

import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from scipy.signal import butter, filtfilt, freqz
from pathlib import Path

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, mov_avg, savgol
from spr_project.spr_calculations.spr_sensing import bulk_sensitivity

## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
MIN = 60
import matplotlib as mpl

from matplotlib import cm
cmap = cm.magma
colors = cmap(np.linspace(0, 1, 10))

colors_bright = colors[1]
colors_med = colors[3]
colors_dark = colors[9]

## Butterworth filter to filter out the pump noise
def butterworth(data, plot_filter_transfer=False):
    
    ## Pump noise has a strong peak at roughly 0.2 Hz
    cutoff_freq = 0.05
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
        
        return (data, w, h)
        
    return data


glass_thickness = 1.4*MM
n_water = 1.33
n_glass = 1.51
S_bulk = bulk_sensitivity(n_water, n_glass, glass_thickness)
S_bulk_um = S_bulk/UM
S_bulk_um_meas = 20324

## Water noise new camera code
marker_size = 1
marker_type = '-x'
marker_color  = 'black'
linewidth_raw = 0.4

### --------------------- Pump noise data --------------------- ###
## Load all data
measurement_type = 'spr_ch' 
measurement = '20251125_00.53_karola_top_single_over_night_water'
vcsels = ['VCSEL_0']
spr_data_folder = Path(measurement_type, measurement)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, vcsels,
                                                                           mov_avg_window=mov_avg_window,
                                                                           sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
mov_avg_window = 50
sav_gol_window = 50
sav_gol_order  = 5

time_scale  = 60

what_trace = 0

time_trace = plot_raw[vcsels[what_trace]][0, :]/time_scale
spr_data   = plot_raw[vcsels[what_trace]][1, :]

spr_data_mean = np.sum(spr_data)/len(spr_data)
spr_data_butter = butterworth(spr_data)

spr_data_butter_mean = np.sum(spr_data_butter)/len(spr_data_butter)

std_array = np.arange(0, 1000, 1)
spr_data_std  = np.std(spr_data[std_array], ddof=1)
spr_data_butter_std  = np.std(spr_data_butter[std_array], ddof=1)
delta_n_pump_on = spr_data_std/S_bulk_um_meas
delta_n_pump_on_butter = spr_data_butter_std/S_bulk_um_meas
print()
print(f'------ Delta n with pump on: {np.round(delta_n_pump_on, 7)} ------')
print()

print()
print(f'------ Delta n with filtering: {np.round(delta_n_pump_on_butter, 7)} ------')
print()


spr_data = spr_data - spr_data_mean
spr_data_butter = spr_data_butter - spr_data_butter_mean


fig = plt.figure(figsize=(10,8))
ax1 = fig.add_subplot(111)
ax1.plot(time_trace, spr_data, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
ax1.grid(linewidth=1, alpha=0.3)

ax1.plot(time_trace, spr_data_butter, marker_type, color='red', ms=marker_size, linewidth=linewidth_raw)
ax1.grid(linewidth=1, alpha=0.3)


#%%


### --------------------- FFT for pump noise --------------------- ###
ax2 = fig.add_subplot(222)
delta_t = (time_trace[1] - time_trace[0])*time_scale
N       = len(time_trace)

f_fft = fftshift(fftfreq(N, d=delta_t))
f_fft = f_fft[N//2:-1]

spr_data_fft = fftshift(fft(spr_data))
spr_data_fft = spr_data_fft[N//2:-1]
spr_data_fft = 2*np.abs(spr_data_fft)**2
spr_data_fft = spr_data_fft/np.sum(spr_data_fft)*delta_t

# ax2.plot(f_fft, spr_data_fft, 'red')
ax2.plot(f_fft, 10*np.log10(spr_data_fft), 'red')
ax2.grid(linewidth=1, alpha=0.3)