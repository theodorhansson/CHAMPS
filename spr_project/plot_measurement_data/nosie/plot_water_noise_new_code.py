#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, fftshift, fftfreq

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, mov_avg, savgol

PI = np.pi

#%% Water noise new camera code

## Load all data
spr_data_folder = 'spr_measurements_231219'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4','VCSEL_5']


files_to_plot = np.array([1], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

mov_avg_window = 50
sav_gol_window = 50
sav_gol_order  = 5

time_scale  = 60

what_trace = 0
time_trace = plot_raw[vcsels[what_trace]][0, :]/time_scale
spr_data   = plot_raw[vcsels[what_trace]][1, :]

spr_data_mean = np.sum(spr_data)/len(spr_data)

spr_data = spr_data - spr_data_mean
spr_data_mov_avg = mov_avg(spr_data, mov_avg_window)
spr_data_savgol = savgol(spr_data, sav_gol_window, sav_gol_order)

plt.figure(1)
plt.plot(time_trace, spr_data, linewidth=0.8)
plt.plot(time_trace, spr_data_savgol, 'black', linewidth=1)
plt.plot(time_trace, spr_data_mov_avg, 'red', linewidth=1)

ax.grid(linewidth=1, alpha=0.3)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR noise [$\mu$m]')
plt.title(r'Noise with water')

#%%

delta_t = (time_trace[10] - time_trace[9])*time_scale
N       = len(time_trace)

f_fft = fftshift(fftfreq(N, d=delta_t))
f_fft = f_fft[N//2:-1]

spr_data_fft = fftshift(fft(spr_data))
spr_data_fft = spr_data_fft[N//2:-1]
spr_data_fft = np.abs(spr_data_fft)**2
spr_data_fft = spr_data_fft/np.max(spr_data_fft)

plt.figure(1)
plt.plot(f_fft, spr_data_fft)


#%%

delta_t = 0.01
t = np.arange(0, 100*PI, delta_t)
N = len(t)
y =  np.sin(t*2*PI*20)*np.sin(t*2*PI*10)

f_fft = fftshift(fftfreq(N, d=delta_t))
f_fft = f_fft[N//2:-1]
y_fft = fftshift(fft(y))
y_fft = y_fft[N//2:-1]
y_fft = np.abs(y_fft)**2
y_fft = y_fft/np.max(y_fft)


plt.plot(f_fft,y_fft)
