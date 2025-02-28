#%%
import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
import matplotlib.pyplot as plt
import numpy as np

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, butterworth

from scipy.optimize import curve_fit


#%%
## Load all data
spr_data_folder = 'spr_measurements_231219'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5']


files_to_plot = np.array([2], dtype=int)

mov_avg_window = 6
sav_gol_window = 15
sav_gol_order  = 5
plot_raw, plot_moving_avg, plot_savgol, frame_time = load_measurement_data(spr_data_folder, files_to_plot, vcsels,
                                                               mov_avg_window=mov_avg_window,
                                                               sav_gol_window=sav_gol_window, sav_gol_order=sav_gol_order)



## Figure object
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

time_trace_1 = plot_raw[vcsels[0]][0,:]
time_trace_3 = plot_raw[vcsels[2]][0,:]
time_trace_6 = plot_raw[vcsels[5]][0,:]

raw_vcsel_1 = plot_raw[vcsels[0]][1,:] - plot_raw[vcsels[0]][1, 0]
raw_vcsel_3 = plot_raw[vcsels[2]][1,:] - plot_raw[vcsels[2]][1, 0]
raw_vcsel_6 = plot_raw[vcsels[5]][1,:] - plot_raw[vcsels[5]][1, 0]

cut_off = 1/50
# butter_vcsel_1 = butterworth(raw_vcsel_1, cut_off)
# butter_vcsel_3 = butterworth(raw_vcsel_3, cut_off)
# butter_vcsel_6 = butterworth(raw_vcsel_6, cut_off)

remove_step_1_start = 1100
remove_step_1_stopp = 2960

remove_step_3_start = 1210
remove_step_3_stopp = 3100

remove_step_6_start = 1100
remove_step_6_stopp = 2960

time_trace_1 = np.concat((time_trace_1[:remove_step_1_start], time_trace_1[remove_step_1_stopp:] - time_trace_1[remove_step_1_stopp] + time_trace_1[remove_step_1_start]))
time_trace_3 = np.concat((time_trace_3[:remove_step_3_start], time_trace_3[remove_step_3_stopp:] - time_trace_3[remove_step_3_stopp] + time_trace_3[remove_step_3_start]))
time_trace_6 = np.concat((time_trace_6[:remove_step_6_start], time_trace_6[remove_step_6_stopp:] - time_trace_6[remove_step_1_start]))


raw_vcsel_1 = np.concat((raw_vcsel_1[:remove_step_1_start], raw_vcsel_1[remove_step_1_stopp:]))
butter_vcsel_1 = butterworth(raw_vcsel_1, cut_off)
raw_vcsel_3 = np.concat((raw_vcsel_3[:remove_step_3_start], raw_vcsel_3[remove_step_3_stopp:]))
butter_vcsel_3 = butterworth(raw_vcsel_3, cut_off)
raw_vcsel_6 = np.concat((raw_vcsel_6[:remove_step_6_start], raw_vcsel_6[remove_step_6_stopp:]))
butter_vcsel_6 = butterworth(raw_vcsel_6, cut_off)


## Plot filtered data
linewidth_filtered = 1.4
plt.plot(time_trace_1, raw_vcsel_1, 'x', color='black', label=r'Channel 1', linewidth=linewidth_filtered)
plt.plot(time_trace_1, butter_vcsel_1, color='blue', label=r'Channel 1', linewidth=linewidth_filtered)
# plt.plot(time_trace_3, butter_vcsel_3, color='green', label=r'Channel 3', linewidth=linewidth_filtered)
# plt.plot(time_trace_6, butter_vcsel_6, color='aqua', label=r'Channel 3', linewidth=linewidth_filtered)



#%%

step_value_channel_1 = step_values[0]
step_value_channel_2 = step_values[1]
step_value_channel_3 = step_values[2]

# step_value_channel_1 = np.delete(step_value_channel_1, np.array([0, -1]))
# step_value_channel_2 = np.delete(step_value_channel_2, np.array([0, 1]))
# step_value_channel_3 = np.delete(step_value_channel_3, np.array([-1, -2]))

step_value_channel_1_1 = step_value_channel_1[0:6]
step_value_channel_2_1 = step_value_channel_2[0:6]
step_value_channel_3_1 = step_value_channel_3[0:6]

step_value_channel_1_2 = np.flip(step_value_channel_1[6:])
step_value_channel_2_2 = np.flip(step_value_channel_2[6:])
step_value_channel_3_2 = np.flip(step_value_channel_3[6:])


concentrations = np.array([0, 0.01, 0.02, 0.03, 0.04, 0.05])
ref_index      = ref_idx(concentrations) - ref_idx(0.0)

plt.figure(1)
plt.scatter(ref_index, step_value_channel_1_1, s=40, facecolors='none', edgecolors='black')
plt.scatter(ref_index, step_value_channel_2_1, s=40, facecolors='none', edgecolors='black')
plt.scatter(ref_index, step_value_channel_3_1, s=40, facecolors='none', edgecolors='black')

plt.scatter(ref_index, step_value_channel_1_2, s=40, facecolors='none', edgecolors='black')
plt.scatter(ref_index, step_value_channel_2_2, s=40, facecolors='none', edgecolors='black')
plt.scatter(ref_index, step_value_channel_3_2, s=40, facecolors='none', edgecolors='black')

ref_index_tot = np.concatenate((ref_index, ref_index, ref_index, ref_index, ref_index, ref_index))
steps = np.concatenate((step_value_channel_1_1, step_value_channel_2_1, step_value_channel_3_1, step_value_channel_1_2, step_value_channel_2_2, step_value_channel_3_2))

def linear_fit(x, a, b):
    y = a*x + b
    return y

x = np.linspace(0, ref_index[-1])
alpha = curve_fit(linear_fit, xdata = ref_index_tot, ydata = steps)[0]
plt.plot(x, linear_fit(x, alpha[0], alpha[1]), color='r')

plt.grid(linewidth=1, alpha=0.3)
plt.xlabel(r'$\Delta$n')
plt.ylabel(r'Sensor response [$\mu$m]')

image_name = 'pick_out_response.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)



