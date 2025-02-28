#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
    
import matplotlib.pyplot as plt
import numpy as np

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces

#%% Water noise new camera code

## Load all data
spr_data_folder = 'spr_measurements_231217'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4','VCSEL_5']


files_to_plot = np.array([4], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

mov_avg_window=6
sav_gol_window=12
sav_gol_order=5

which_trace = 0
time_scale  = 60
y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

# plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')