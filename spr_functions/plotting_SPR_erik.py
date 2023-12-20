#%%
import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve, butter, filtfilt, savgol_filter
from spr_functions.spr_calculations import SPR_ang, ResonantN, ref_idx, ResonantAngle, SPR_loc

from pathlib import Path

def mov_avg(data, window_size):
    # window_size = 1
    window = np.ones(window_size) / window_size
    data = np.convolve(data, window, mode='same')
    return data

def butterworth(data):
    sampling_freq=1/5
    cutoff_freq=1/100
    order=1
    nyquist_freq = 0.5 * sampling_freq
    normalized_cutoff_freq = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff_freq, btype='lowpass')
    data = filtfilt(b, a, data)
    return data

def savgol(data, window, order):
    return savgol_filter(data, window, order)

## Vcesls used in measurement
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']
filename = 'data'

def load_measurement_data(spr_data_folder, files_to_plot, time_mask=None, mov_avg_window=6, sav_gol_window=12, sav_gol_order=5):
    parent_path = Path(__file__).resolve().parents[1]
    measurement_path = Path(parent_path, spr_data_folder)

    ## Names of measurement segments
    names = np.array(os.listdir(measurement_path))
    names = names[files_to_plot]
    
    ## Dict for plotting data
    plot_raw = {}
    plot_moving_avg = {}
    plot_savgol = {}


    ## Concatenate measurement segements
    for vcsel in vcsels:
        frame_time = np.array([])
        spr_data = np.array([])
        
        start_time_segment = 0
        reference_level = 0
        for i, name in enumerate(names):
            data_path = Path(parent_path, spr_data_folder, name, vcsel, filename)

            data = np.genfromtxt(str(data_path) + '.txt', delimiter=',')
       
            current_frame_time = data[:, 0] + start_time_segment
            start_time_segment = current_frame_time[-1]
            
            # if reference_level == 0:
                # reference_level = data[0, 1]
            current_spr_data = data[:, 1]
            # - reference_level
            # else:
                # current_spr_data = data[:, 1] - reference_level
                
                
            frame_time = np.concatenate((frame_time, current_frame_time))
            spr_data   = np.concatenate((spr_data, current_spr_data))
        
        if time_mask != None:
            for mask in time_mask:
                frame_time = frame_time[int(mask[0]):int(mask[1])]
                spr_data = spr_data[int(mask[0]):int(mask[1])]
                
        plot_raw[vcsel] = np.vstack((frame_time, spr_data))
        plot_moving_avg[vcsel] = np.vstack((frame_time, mov_avg(np.hstack(spr_data), mov_avg_window)))
        plot_savgol[vcsel] = np.vstack((frame_time, savgol(np.hstack(spr_data), sav_gol_window, sav_gol_order)))
        
    return plot_raw, plot_moving_avg, plot_savgol

def plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax):

    x_raw = plot_raw[vcsels[which_trace]][0, :]
    y_raw = plot_raw[vcsels[which_trace]][1, :]

    x_data_mov_avg = plot_moving_avg[vcsels[which_trace]][0, :]
    y_data_mov_avg = plot_moving_avg[vcsels[which_trace]][1, :]

    x_data_savgol = plot_savgol[vcsels[which_trace]][0, :]
    y_data_savgol = plot_savgol[vcsels[which_trace]][1, :]
            
    ax.plot(x_raw/time_scale, y_raw, 'blue', linewidth=0.8)
    # ax.plot(x_data_mov_avg/time_scale, y_data_mov_avg, 'black')
    # ax.plot(x_data_savgol/time_scale, y_data_savgol, 'red')
    
    print('Raw Mean: ', np.mean(y_raw), 'Raw Std: ', np.std(y_raw))
    print('Moving average Mean: ', np.mean(y_data_mov_avg), 'Averaged Std: ', np.std(y_data_mov_avg))
    print('Savgol Mean: ', np.mean(y_data_savgol), 'Averaged Std: ', np.std(y_data_savgol))
    
    return y_raw, y_data_mov_avg, y_data_savgol

def plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax):
    colors  = ['red', 'lightcoral', 'green', 'lightgreen', 'blue', 'lightblue']
    marking = ['', '--', '', '--', '', '--']
    
    for i, vcsel in enumerate(vcsels):
        x_raw = plot_raw[vcsels[i]][0, :]
        y_raw = plot_raw[vcsels[i]][1, :]

        x_data_mov_avg = plot_moving_avg[vcsels[i]][0, :]
        y_data_mov_avg = plot_moving_avg[vcsels[i]][1, :]

        x_data_savgol = plot_savgol[vcsels[i]][0, :]
        y_data_savgol = plot_savgol[vcsels[i]][1, :]
        
        
        ax.plot(x_raw/time_scale, y_raw, marking[i], color=colors[i])
        # ax.plot(x_data_mov_avg/time_scale, y_data_mov_avg, 'black')
        # ax.plot(x_data_savgol/time_scale, y_data_savgol, 'black')

#%% BSA DS attempt 3

## Load all data
spr_data_folder = 'spr_measurements_231212'
parent_path = Path(__file__).resolve().parents[1]
measurement_path = Path(parent_path, spr_data_folder)

## Names of measurement segments
names = os.listdir(measurement_path)

## Remove reference spectrum
names.pop(0)

## Dict for plotting data
plot_data = {}

## Concatenate measurement segements
for vcsel in vcsels:
    frame_time = np.array([])
    spr_data = np.array([])
    
    start_time_segment = 0
    reference_level = 0
    for i, name in enumerate(names):
        data_path = Path(parent_path, spr_data_folder, name, vcsel, filename)
        if i == 0:
            data = np.genfromtxt(str(data_path) + '.txt', delimiter=' ')
        else:
            data = np.genfromtxt(str(data_path) + '.txt', delimiter=',')
   
        current_frame_time = data[:, 0] + start_time_segment
        start_time_segment = current_frame_time[-1]
        
        if reference_level == 0:
            reference_level = data[0, 1]
            current_spr_data = data[:, 1] - reference_level
        else:
            current_spr_data = data[:, 1] - reference_level
            
            
        frame_time = np.concatenate((frame_time, current_frame_time))
        spr_data   = np.concatenate((spr_data, current_spr_data))
    
    plot_data[vcsel] = np.vstack((frame_time, spr_data))
        

## Figure object
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

colors  = ['red', 'lightcoral', 'green', 'lightgreen', 'blue', 'lightblue']
marking = ['', '--', '', '--', '', '--']

# which_trace = 5
# x_data = plot_data[vcsels[which_trace]][0, :]/60
# y_data = plot_data[vcsels[which_trace]][1, :]

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5

# y_data_movavg = mov_avg(np.hstack(y_data), mov_avg_window)
# y_data_savgol = savgol(np.hstack(y_data), sav_gol_window, sav_gol_order)
        
# ax.plot(x_data, y_data)

for i, vcsel in enumerate(vcsels):
    if i == 0 or i == 2 or i == 4:
        ax.plot(plot_data[vcsel][0, :]/60, plot_data[vcsel][1, :], marking[i], color=colors[i])

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'BSA-DS cake')

sav_gol_window = 12
sav_gol_order = 2

# ax.scatter(x_data, y_data, label='Raw Data', alpha=0.7, s=1, facecolor='none', edgecolor='b' )
# ax.scatter(x_data, y_data_movavg, s=1, label=f'Moving Average n={mov_avg_window}', color='r')
# ax.plot(x_data, merged_data_y_savgol, linewidth=1.5,label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

#%%





#%% Water noise new camera code

## Load all data
spr_data_folder = 'spr_measurements_231217'

files_to_plot = np.array([4], dtype=int)

sav_gol_window = 120
plot_raw, plot_moving_avg, plot_savgol = load_measurement_data(spr_data_folder, files_to_plot,
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


#%% NaOH steps

## Load all data
spr_data_folder = 'spr_measurements_231217'

files_to_plot = np.array([5], dtype=int)

time_mask = [(0,1750)]
mov_avg_window = 6
sav_gol_window = 10
sav_gol_order = 5
plot_raw, plot_moving_avg, plot_savgol = load_measurement_data(spr_data_folder, files_to_plot, time_mask,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

which_trace = 0
time_scale  = 60
y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')

#%% Water noise 2

## Load all data
spr_data_folder = 'spr_measurements_231219'

files_to_plot = np.array([1], dtype=int)

# time_mask = [(0,1750)]
mov_avg_window = 6
sav_gol_window = 10
sav_gol_order = 5
plot_raw, plot_moving_avg, plot_savgol = load_measurement_data(spr_data_folder, files_to_plot,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

which_trace = 0
# time_scale  = 60
y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')

#%% 10 Glycerol steps

## Load all data
spr_data_folder = 'spr_measurements_231219'

files_to_plot = np.array([3], dtype=int)

time_mask = [(100,-1)]
mov_avg_window = 6
sav_gol_window = 100
sav_gol_order = 5
plot_raw, plot_moving_avg, plot_savgol = load_measurement_data(spr_data_folder, files_to_plot, time_mask=time_mask,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

which_trace = 0
time_scale  = 60
y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# which_trace = 2
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# which_trace = 3
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

# plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'10 glycerol steps')

#%% 10 Glycerol steps

## Load all data
spr_data_folder = 'spr_measurements_231220'

files_to_plot = np.array([2], dtype=int)

time_mask = [(100,-500)]
mov_avg_window = 6
sav_gol_window = 100
sav_gol_order = 5
plot_raw, plot_moving_avg, plot_savgol = load_measurement_data(spr_data_folder, files_to_plot, time_mask=time_mask,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

which_trace = 0
time_scale  = 60
y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# which_trace = 1
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# which_trace = 2
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

# plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'miRNA')


#%% 10 Glycerol steps

## Load all data
spr_data_folder = 'spr_measurements_231027'

files_to_plot = np.array([2,3,4,5], dtype=int)

time_mask = [(0,1200)]
mov_avg_window = 6
sav_gol_window = 100
sav_gol_order = 5
plot_raw, plot_moving_avg, plot_savgol = load_measurement_data(spr_data_folder, files_to_plot, time_mask=time_mask,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)

## Figure object
fig = plt.figure(1, figsize=(8,5))
ax = fig.add_subplot(111)

which_trace = 0
# time_scale  = 60
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# which_trace = 1
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)
# which_trace = 2
# y_raw, y_data_mov_avg, y_data_savgol = plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, time_scale, ax)

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')
''

