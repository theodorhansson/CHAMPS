#%%
import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces
# from spr_project.spr_calculations import ResonantN, SPR_ang, ResonantAngle, SPR_loc, ref_idx

## Load all data
spr_data_folder = 'spr_measurements_231027'
parent_path = Path(__file__).resolve().parents[1]
measurement_path = Path(parent_path, 'spr_measurement_data', spr_data_folder)

vcsels = ['VCSEL_0']
filename = 'data'

## Names of measurement segments
names = os.listdir(measurement_path)

names.pop(0)
names.pop(0)
names.pop(0)
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
        data_path = Path(measurement_path, name, vcsel, filename)

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

plot_data[vcsels[0]][1,:] = plot_data[vcsels[0]][1,:] - plot_data[vcsels[0]][1, 0]

time_trace = plot_data[vcsels[0]][0,:]
spr_data = plot_data[vcsels[0]][1,:]

for i in range(len(spr_data)):
    if spr_data[i] > 1000:
        spr_data[i] = spr_data[i-1]
        
ax.scatter(time_trace, spr_data, label='Raw Data', alpha=0.3, s=1, facecolor='none', edgecolor='black' )

ax.grid(linewidth=1, alpha=0.3)
ax.set_xticks(np.arange(ax.get_xlim()[0], ax.get_xlim()[1] + 300, 1000))
ax.set_xticklabels(np.array(ax.get_xticks()/60).astype(int), rotation=90)
ax.set_xlabel(r'Time [min]')

ax.set_ylabel(r'Spr shift [$\mu$m]')

x_layers = np.array([frame_time[0], frame_time[-1]])
y_layers = np.array([86, 170, 327, 537, 812])
for i in range(len(y_layers)):
    plt.plot(np.array([x_layers[0], x_layers[1]]), np.array([y_layers[i], y_layers[i]]), '--', color='gray', linewidth=1)




#%%
layer_thickness = np.arange(50, len(y_layers)*50 + 50, 50)

def exp_fit(x, a, b, c):
    return a * np.exp(-b * x) + c

guess = np.array([0, 0, 0])
popt, pcov = curve_fit(exp_fit, layer_thickness, y_layers, guess)

plt.figure(1)
plt.plot(layer_thickness, y_layers, 'x', color='black', label=r'Data points')
plt.plot(layer_thickness, exp_fit(layer_thickness, *popt), 'r-', label='Exponential fit')
plt.grid(True)

print(popt)

plt.xlabel(r'BSA Layer thickness [nm]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Shift as a function of layer thickness')
plt.legend()

        