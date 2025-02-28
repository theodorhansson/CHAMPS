#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from scipy.signal import butter, filtfilt, freqz

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



mpl.rcParams['axes.titlesize'] = 28
mpl.rcParams['axes.labelsize'] = 28
mpl.rcParams['xtick.labelsize'] = 26
mpl.rcParams['ytick.labelsize'] = 26
mpl.rcParams['legend.fontsize'] = 26
mpl.rcParams['lines.markersize'] = 4
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['grid.alpha'] = 0.3
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.shadow'] = True

mpl.rcParams['font.family'] = 'Helvetica'


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
spr_data_folder = 'spr_measurements_240922'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']

files_to_plot = np.array([0], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
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
print()
print(f'------ Delta n with pump on: {np.round(delta_n_pump_on, 7)} ------')
print()

delta_n_pump_on_butter = spr_data_butter_std/S_bulk_um_meas
print()
print(f'------ Delta n with pump on: {np.round(delta_n_pump_on_butter, 7)} ------')
print()


spr_data = spr_data - spr_data_mean
spr_data_butter = spr_data_butter - spr_data_butter_mean

time_trace = time_trace[0:700]
spr_data = spr_data[0:700]
spr_data_butter = spr_data_butter[0:700]

fig = plt.figure(figsize=(10,8))
ax1 = fig.add_subplot(221)
ax1.plot(time_trace, spr_data, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
ax1.grid(linewidth=1, alpha=0.3)

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

#%%

fig_paper = plt.figure(figsize=(12,8))
ax1_paper = fig_paper.add_subplot(111)

ax1_paper.plot(time_trace, spr_data, color=colors_bright)
ax1_paper.plot(time_trace, spr_data_butter, color='red')

plt.grid(True)

plt.ylim([-1.5, 2.2])

plt.savefig('pump_measurement.svg', format='svg')


#%%
data, w, h = butterworth(spr_data, plot_filter_transfer=True)

fig2_paper = plt.figure(figsize=(12,8))
ax1_paper = fig2_paper.add_subplot(111)
ax1_paper.plot(f_fft, 10*np.log10(spr_data_fft/np.max(spr_data_fft)), 'red')

plt.plot(w, 10*np.log10(np.abs(h)), 'b', label=r'Transfer function')
# plt.plot(cutoff_freq, 0.5*np.sqrt(2), 'ko')
# plt.axvline(cutoff_freq, color='k', label=f'$f_c$ = {cutoff_freq} Hz')

plt.grid(True)
plt.ylim([-60, 5])

plt.savefig('pump_measurement_fft.svg', format='svg')

#%%
### --------------------- Load data with pump off --------------------- ###
## Load all data
spr_data_folder = 'spr_measurements_240922'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']

files_to_plot = np.array([1], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

mov_avg_window = 50
sav_gol_window = 50
sav_gol_order  = 5

time_scale  = 60

what_trace = 0
time_trace = plot_raw[vcsels[what_trace]][0, :]/time_scale
spr_data   = plot_raw[vcsels[what_trace]][1, :]

spr_data_mean = np.sum(spr_data)/len(spr_data)
spr_data_std  = np.std(spr_data[std_array], ddof=1)
delta_n_pump_off = spr_data_std/S_bulk_um
print()
print(f'------ Delta n with pump off: {np.round(delta_n_pump_off, 8)} ------')
print()

spr_data = spr_data - spr_data_mean
time_trace = time_trace[0:1000]
spr_data = spr_data[0:1000]

fig = plt.figure(figsize=(10,6))
ax3 = fig.add_subplot(121)

ax3.plot(time_trace, spr_data, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
ax3.grid(linewidth=1, alpha=0.3)

### --------------------- FFT without pump --------------------- ###
delta_t = (time_trace[1] - time_trace[0])*time_scale
N       = len(time_trace)

f_fft = fftshift(fftfreq(N, d=delta_t))
f_fft = f_fft[N//2:-1]

spr_data_fft = fftshift(fft(spr_data))
spr_data_fft = spr_data_fft[N//2:-1]
spr_data_fft = 2*np.abs(spr_data_fft)**2
spr_data_fft = spr_data_fft/np.sum(spr_data_fft)*delta_t

ax4 = fig.add_subplot(122)

# ax4.plot(f_fft, spr_data_fft)
ax4.plot(f_fft, 10*np.log10(spr_data_fft/np.max(spr_data_fft)), 'red')

ax4.grid(linewidth=1, alpha=0.3)

ax1.set_ylim([-1.5, 1.5])
ax3.set_ylim([-1, 1])

# ax2.set_xlim([0, 0.08])
# ax4.set_xlim([0, 0.08])

ax1.set_title(r'Spr trace with pump on')
ax2.set_title(r'Spectrum with pump on')
ax3.set_title(r'Spr trace with pump off')
ax4.set_title(r'Spectrum with pump off')

ax1.set_xlabel(r'Time [min]')
ax2.set_xlabel(r'Frequency [Hz]')
ax3.set_xlabel(r'Time [min]')
ax4.set_xlabel(r'Frequency [Hz]')

ax1.set_ylabel(r'Spr coordinate [$\mu$m]')
ax2.set_ylabel(r'Normalized amplitude [-]')
ax3.set_ylabel(r'Spr coordinate [$\mu$m]')
ax4.set_ylabel(r'Normalized amplitude [-]')

# plt.tight_layout(pad=2, w_pad=5, h_pad=2) 

#%%

fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(f_fft, 10*np.log10(spr_data_fft/np.max(spr_data_fft)), 'red')
ax.set_ylim([-35, 2])

ax.set_title(r'Spectrum with pump off')
ax.set_xlabel(r'Frequency [Hz]')
ax.set_ylabel(r'Normalized amplitude [-]')
ax.grid(linewidth=1, alpha=0.3)
plt.tight_layout()

plt.savefig('spectrum_pump_off.png', format='png', dpi=600)



#%%

fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(time_trace, spr_data, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
ax.grid(linewidth=1, alpha=0.3)
ax.set_ylim([-1.0, 1.0])

ax.set_title(r'Spr trace with pump off')
ax.set_xlabel(r'Time [min]')
ax.set_ylabel(r'Sensor response [$\mu$m]')
ax.grid(linewidth=1, alpha=0.3)
plt.tight_layout()

plt.savefig('time_trace_pump_off.png', format='png', dpi=600)





#%%

plt.figure(1)
plt.plot(time_trace, spr_data+0.10, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.grid(linewidth=1, alpha=0.3)
plt.xlabel(r'Time [min]')
plt.ylabel(r'Spr coordinate [$\mu$m]')

image_name = 'pick_out_response.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

