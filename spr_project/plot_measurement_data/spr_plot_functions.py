#%%
import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve, butter, filtfilt, savgol_filter
# from spr_project.spr_calculations import SPR_ang, ResonantN, ref_idx, ResonantAngle, SPR_loc

from pathlib import Path
from scipy.optimize import curve_fit

def mov_avg(data, window_size):
    # window_size = 1
    window = np.ones(window_size) / window_size
    data = np.convolve(data, window, mode='same')
    return data

def butterworth(data, cut_off):
    sampling_freq=1/5
    cutoff_freq=cut_off
    order=1
    nyquist_freq = 0.5 * sampling_freq
    normalized_cutoff_freq = cutoff_freq/nyquist_freq
    b, a = butter(order, normalized_cutoff_freq, btype='lowpass')
    data = filtfilt(b, a, data)
    return data

def savgol(data, window, order):
    return savgol_filter(data, window, order)

## Vcesls used in measurement
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5']
filename = 'data'

def load_measurement_data(spr_data_folder, files_to_plot, vcsels, time_mask=None, mov_avg_window=6, sav_gol_window=12, sav_gol_order=5):
    parent_path = Path(__file__).resolve().parents[1]
    measurement_path = Path(parent_path, 'spr_measurement_data', spr_data_folder)

    ## Names of measurement segments
    names = np.array(os.listdir(measurement_path))
    names = names[files_to_plot]
    print('Loading data from: ' + str(names))
    
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
            data_path = Path(measurement_path, name, vcsel, filename)

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
        
    return plot_raw, plot_moving_avg, plot_savgol, frame_time

def plot_single_trace(which_trace, plot_raw, plot_moving_avg, plot_savgol, time_scale, ax, offset=0):

    x_raw = plot_raw[vcsels[which_trace]][0, :]
    y_raw = plot_raw[vcsels[which_trace]][1, :]

    x_data_mov_avg = plot_moving_avg[vcsels[which_trace]][0, :]
    y_data_mov_avg = plot_moving_avg[vcsels[which_trace]][1, :]

    x_data_savgol = plot_savgol[vcsels[which_trace]][0, :]
    y_data_savgol = plot_savgol[vcsels[which_trace]][1, :]
            
    ax.plot(x_raw/time_scale, y_raw, 'blue', linewidth=0.8)
    # ax.plot(x_data_mov_avg/time_scale, y_data_mov_avg, 'black')
    # ax.plot(x_data_savgol/time_scale, y_data_savgol, 'red')
    # ax.set_ylabel(r'SPR shift [$\mu$m]')
    
    plt.ylim([np.min(y_raw), np.max(y_raw)])
    
    # ax2 = ax.twinx()
    # ax2.set_ylabel('Refractive Index')
    # ax2.set_ylim(ax.get_ylim())
    # ylabels = [ResonantN(theta_spr=SPR_ang((x + offset)/1000))/100 for x in ax2.get_yticks()]
    # ax2.set_yticklabels(np.round(ylabels,5))
    
    print('Raw Mean: ', np.mean(y_raw), 'Raw Std: ', np.std(y_raw))
    print('Moving average Mean: ', np.mean(y_data_mov_avg), 'Averaged Std: ', np.std(y_data_mov_avg))
    print('Savgol Mean: ', np.mean(y_data_savgol), 'Averaged Std: ', np.std(y_data_savgol))
    
    return y_raw, y_data_mov_avg, y_data_savgol

def plot_all_traces(plot_raw, plot_moving_avg, plot_savgol, vcsels, time_scale, ax):
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