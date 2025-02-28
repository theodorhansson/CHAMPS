#%%
import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
import matplotlib.pyplot as plt
import numpy as np

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, butterworth
from spr_project.spr_calculations.spr_sensing import n_glycerol

from scipy.optimize import curve_fit


#%%
## Load all data
spr_data_folder = 'spr_measurements_231026'
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']


files_to_plot = np.array([0, 1, 2, 3], dtype=int)

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
time_trace_2 = plot_raw[vcsels[1]][0,:]
time_trace_3 = plot_raw[vcsels[2]][0,:]

raw_vcsel_1 = plot_raw[vcsels[0]][1,:] - plot_raw[vcsels[0]][1, 0]
shift = 230
raw_vcsel_1[shift] = raw_vcsel_1[shift] + 6

shift = 241
raw_vcsel_1[shift] = raw_vcsel_1[shift] + 6

shift = 244
raw_vcsel_1[shift] = raw_vcsel_1[shift] + 6

shift = 257
raw_vcsel_1[shift] = raw_vcsel_1[shift] + 6

shift = 258
raw_vcsel_1[shift] = raw_vcsel_1[shift] + 6

shift = -18
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -31
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -33
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -48
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -50
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -65
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -76
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -78
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -89
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -91
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -93
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

shift = -140
raw_vcsel_1[shift] = raw_vcsel_1[shift] - 6

raw_vcsel_2 = plot_raw[vcsels[1]][1,:] - plot_raw[vcsels[1]][1, 0] 
raw_vcsel_3 = plot_raw[vcsels[2]][1,:] - plot_raw[vcsels[2]][1, 0]


cut_off = 1/50
butter_vcsel_1 = butterworth(raw_vcsel_1, cut_off)
butter_vcsel_2 = butterworth(raw_vcsel_2, cut_off)
butter_vcsel_3 = butterworth(raw_vcsel_3, cut_off)


## Plot filtered data
linewidth_filtered = 1.4
plt.plot(time_trace_1, butter_vcsel_1, color='blue', label=r'Channel 1', linewidth=linewidth_filtered)
plt.plot(time_trace_2, butter_vcsel_2, color='red', label=r'Channel 2', linewidth=linewidth_filtered)
plt.plot(time_trace_3, butter_vcsel_3, color='green', label=r'Channel 3', linewidth=linewidth_filtered)


## Plot raw data
marker_size = 0.6
marker_type = 'x'
marker_color  = 'black'
linewidth_raw = 1
plt.plot(time_trace_1, raw_vcsel_1, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.plot(time_trace_2, raw_vcsel_2, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.plot(time_trace_3, raw_vcsel_3, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)


ax.grid(linewidth=1, alpha=0.3)
ax.set_xticks(np.arange(ax.get_xlim()[0], ax.get_xlim()[1] + 300, 300))
ax.set_xticklabels(np.array(ax.get_xticks()/60).astype(int), rotation=90)

offset = 4325
ax.set_xlabel(r'Time [min]')
ax.set_ylabel(r'Sensor response [um]')
ax2 = ax.twinx()
ax2.set_ylabel(r'Refractive index [-]')

concentrations = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.0525])
clrs = ['r','g','b','m','y','k']

# ax2.set_ylim(ref_idx(concentrations[0]) - 0.0007, ref_idx(concentrations[-1]))

y_ticks_values = []
y_ticks = []

# for i, conc in enumerate(concentrations): 

#     y_value = SPR_loc(ResonantAngle(e_analyte=ref_idx(conc)**2))*1000
#     ax2.axhline(ref_idx(conc), color='black', linewidth=0.5,linestyle='--')
#     y_ticks_values.append(y_value)
#     y_ticks.append(ref_idx(conc))

ax.legend(fontsize=12, framealpha=0.3, edgecolor='black', loc='upper left')
plt.tight_layout()

image_name = 'three_glycerol_steps.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

#%%

marker_size = 0.6
marker_type = 'x'
marker_color  = 'black'
linewidth_raw = 1
# plt.plot(time_trace_1, raw_vcsel_1, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
# plt.plot(time_trace_2, raw_vcsel_2, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
# plt.plot(time_trace_3, raw_vcsel_3, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)

pick_out_index_1 = [0, 230, 320, 400, 480, 550, 560, 620, 705, 790, 870, 940]
# for i in range(len(pick_out_index_1)):
#     plt.plot(np.array([time_trace_1[pick_out_index_1[i]], time_trace_1[pick_out_index_1[i]]]), np.array([0, 140]))

step_values = np.zeros(shape=(3, len(pick_out_index_1)))

for i in range(len(pick_out_index_1)):
    step_values[0][i] = raw_vcsel_1[pick_out_index_1[i]]

step_values[0][-1] = step_values[0][-1] + 10
step_values[0][-2] = step_values[0][-2] + 10
#%%
# plt.plot(time_trace_2, raw_vcsel_2, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
pick_out_index_2 = np.array([0, 230, 320, 400, 480, 550, 560, 620, 705, 790, 870, 940]) + 80
# for i in range(len(pick_out_index_1)):
#     plt.plot(np.array([time_trace_1[pick_out_index_2[i]], time_trace_1[pick_out_index_2[i]]]), np.array([0, 140]))


for i in range(len(pick_out_index_2)):
    step_values[1][i] = raw_vcsel_2[pick_out_index_2[i]]
    
#%%
# plt.plot(time_trace_3, raw_vcsel_3, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
pick_out_index_3 = np.array([0, 230, 320, 400, 480, 550, 560, 620, 705, 790, 870, 940])
pick_out_index_3[1:-1] = pick_out_index_3[1:-1] - 85

# for i in range(len(pick_out_index_3)):
#     plt.plot(np.array([time_trace_1[pick_out_index_3[i]], time_trace_1[pick_out_index_3[i]]]), np.array([0, 140]))


for i in range(len(pick_out_index_3)):
    step_values[2][i] = raw_vcsel_3[pick_out_index_3[i]]


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
ref_index      = n_glycerol(concentrations, 1.333) - n_glycerol(0.0, 1.333)

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



