#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, fftshift, fftfreq

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


glass_thickness = 1.4*MM
n_water = 1.33
n_glass = 1.51
S_bulk = bulk_sensitivity(n_water, n_glass, glass_thickness)
S_bulk_um = S_bulk/UM


## Water noise new camera code
marker_size = 1
marker_type = '-x'
marker_color  = 'black'
linewidth_raw = 0.4

### --------------------- Pump noise data --------------------- ###
## Load all data
spr_data_folder = 'spr_measurements_240222'
vcsels = ['VCSEL_1']

files_to_plot = np.array([1], dtype=int)

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

std_array = np.arange(400, 600, 1)
spr_data_std  = np.std(spr_data[std_array], ddof=1)
delta_n_pump_on = spr_data_std/S_bulk_um
print()
print(f'------ Delta n with pump on: {np.round(delta_n_pump_on, 7)} ------')
print()


spr_data = spr_data - spr_data_mean
time_trace = time_trace[0:700]
spr_data = spr_data[0:700]

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
spr_data_fft = np.abs(spr_data_fft)**2
spr_data_fft = spr_data_fft/np.max(spr_data_fft)

# ax2.plot(f_fft, spr_data_fft, 'red')
ax2.plot(f_fft, 10*np.log10(spr_data_fft), 'red')
ax2.grid(linewidth=1, alpha=0.3)

#%%

fig_paper = plt.figure(figsize=(12,8))
ax1_paper = fig_paper.add_subplot(111)

ax1_paper.plot(time_trace, spr_data, color=colors_bright)

plt.grid(True)

plt.savefig('pump_measurement.svg', format='svg')


#%%
fig2_paper = plt.figure(figsize=(12,8))
ax1_paper = fig2_paper.add_subplot(111)
ax1_paper.plot(f_fft, 10*np.log10(spr_data_fft), 'red')

plt.grid(True)

plt.savefig('pump_measurement_fft.svg', format='svg')


#%%

### --------------------- Load data with pump off --------------------- ###
## Load all data
spr_data_folder = 'spr_measurements_240222'
vcsels = ['VCSEL_1']

files_to_plot = np.array([2], dtype=int)

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
print(f'------ Delta n with pump on: {np.round(delta_n_pump_off, 8)} ------')
print()


spr_data = spr_data - spr_data_mean
time_trace = time_trace[200:900]
spr_data = spr_data[200:900]

ax3 = fig.add_subplot(223)

ax3.plot(time_trace, spr_data, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
ax3.grid(linewidth=1, alpha=0.3)



### --------------------- FFT without pump --------------------- ###
delta_t = (time_trace[1] - time_trace[0])*time_scale
N       = len(time_trace)

f_fft = fftshift(fftfreq(N, d=delta_t))
f_fft = f_fft[N//2:-1]

spr_data_fft = fftshift(fft(spr_data))
spr_data_fft = spr_data_fft[N//2:-1]
spr_data_fft = np.abs(spr_data_fft)**2
spr_data_fft = spr_data_fft/np.max(spr_data_fft)

ax4 = fig.add_subplot(224)

# ax4.plot(f_fft, spr_data_fft)
ax4.plot(f_fft, 10*np.log10(spr_data_fft), 'red')

ax4.grid(linewidth=1, alpha=0.3)

ax1.set_ylim([-0.6, 0.8])
ax3.set_ylim([-0.6, 0.8])

ax2.set_xlim([0, 0.08])
ax4.set_xlim([0, 0.08])

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

plt.tight_layout()



#%%

plt.figure(1)
plt.plot(time_trace, spr_data+0.10, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.grid(linewidth=1, alpha=0.3)
plt.xlabel(r'Time [min]')
plt.ylabel(r'Spr coordinate [$\mu$m]')

image_name = 'pick_out_response.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

#%%

delta_t = 0.01
t = np.arange(0, 100*PI, delta_t)
N = len(t)
y =  np.sin(t*2*PI*25)

f_fft = fftshift(fftfreq(N, d=delta_t))
f_fft = f_fft[N//2:-1]
y_fft = fftshift(fft(y))
y_fft = y_fft[N//2:-1]
y_fft = np.abs(y_fft)**2
y_fft = y_fft/np.max(y_fft)


plt.plot(f_fft,y_fft)
