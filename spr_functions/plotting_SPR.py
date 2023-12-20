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



#%% GLYCEROL MEASUREMENT
names=[
       # '1003_151911_Flushing400',
       # '1003_152419_Flushing400',
       # '1003_152924_Flushing400',
       # '1003_153434_Flushing400',
       # '1003_154102_Flushing400',
       # '1003_154706_Flushing400',
       # '1003_155400_Stepsv2_400',
       # '1003_165424_SmallSteps_400',
       # '1003_172429_Flushing_400',
       # '20231212_00.04.55_test_spectrum'
       ]

fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

end_time = 0
merged_data_x = []
merged_data_y = []
for name in names:
    data = np.genfromtxt(f'data/{name}/{name}_data.txt', delimiter=',')
    merged_data_x.append(data[:,0]+end_time)
    merged_data_y.append(data[:,1])    
    end_time += data[-1,0]

mov_avg_window = 7
sav_gol_window = 12
sav_gol_order = 2

merged_data_x = np.hstack(merged_data_x)
merged_data_y_raw = np.hstack(merged_data_y)
merged_data_y_movavg = mov_avg(np.hstack(merged_data_y), mov_avg_window)
merged_data_y_savgol = savgol(np.hstack(merged_data_y), sav_gol_window, sav_gol_order)

ax.scatter(merged_data_x, merged_data_y_raw, label='Raw Data', alpha=0.15, s=5, facecolor='none', edgecolor='b' )
ax.plot(merged_data_x, merged_data_y_movavg, linewidth=1, label=f'Moving Average n={mov_avg_window}')
# ax.plot(merged_data_x, merged_data_y_savgol, linewidth=1,label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

# finding the levels
# for i in range(18):
#     mask = (merged_data_x > 32*60+310*i) & (merged_data_x < 34*60+310*i)
#     ax.plot(merged_data_x[mask], merged_data_y_raw[mask])
#     print(i, np.mean(merged_data_y_raw[mask]))

# mask = (merged_data_x > 120*60) & (merged_data_x < 129*60)
# ax.plot(merged_data_x[mask], merged_data_y_raw[mask])
# print('Raw Mean: ', np.mean(merged_data_y_raw[mask]), 'Raw Std: ', np.std(merged_data_y_raw[mask]))
# print('Averaged Mean: ', np.mean(merged_data_y_movavg[mask]), 'Averaged Std: ', np.std(merged_data_y_movavg[mask]))
# print('SavGol Mean: ', np.mean(merged_data_y_savgol[mask]), 'SavGol Std: ', np.std(merged_data_y_savgol[mask]))

ax.legend(loc='upper left', fontsize=10)
    
ax.set_xlabel('Time, min')
ax.set_ylabel('SPR Coordinate, um')
ax.set_xlim([0*60,110*60])
ax.set_ylim([360,525])
ax.grid(linewidth=1, alpha=0.3)
ax.set_xticks(np.arange(ax.get_xlim()[0],ax.get_xlim()[1]+300,300))
ax.set_xticklabels(np.array(ax.get_xticks()/60).astype(int), rotation=90)

offset = 3985
ax2 = ax.twinx()
ax2.set_ylabel('Refractive Index')
ax2.set_ylim(ax.get_ylim())
ylabels = [ResonantN(theta_spr=SPR_ang((x+offset)/1000)) for x in ax2.get_yticks()]
ax2.set_yticklabels(np.round(ylabels,5))


concentrations = [0,0.01,0.02,0.03,0.04,0.05]
clrs = ['r','g','b','m','y','k']
for c, clor in zip(concentrations,clrs):
    ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(c)**2))*1000-offset, color=clor,linewidth=0.5,label=f'Glycerol {c*100:.1f}%',linestyle='--')

ax2.legend(fontsize=10)
# fig.savefig('GlycerolExperiment.svg', dpi=300)
plt.show()

#%% BSA EXPERIMENT
names=[
       # '1009_114001_Filling56',
       #  '1009_115601_Flushing120',
       #  '1009_120721_Flushing120',
       #  '1009_133117_Flushing120',
       #  '1009_134124_Flushing120',
       #  '1009_135148_Flushing120',
       #  '1009_140247_NaOH120',
       #  '1009_141250_NaOH120',
       #  '1009_142252_Buffer120',
       #  '1009_143257_Buffer200',
       #  '1009_144316_Buffer200',
       #  '1009_145327_Buffer200_15f',
         # '1009_145933_Buffer400',
        '1009_150440_Buffer400',
       '1009_151040_Buffer400',
       '1009_151720_BSAExperiment400',
       '1009_161738_BSAExperiment400',
       '1009_171035_Flushing400',
       ]

fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)
end_time = 0
merged_data_x = []
merged_data_y = []
for name in names:
    data = np.genfromtxt(f'data/{name}/{name}_data.txt', delimiter=',')
    for i, datapoint in enumerate(data):
        data[i,1] = data[i,1] if data[i,1]>350 else data[i,1]+150
        # data[i,1] = data[i,1] if data[i,1]<420 else None
    
    # ax.plot(data[:,0]+end_time, data[:,1], label=name, marker='o', linewidth=0.3, markersize=2, alpha=0.5)
    # ax.plot(data[:,0]+end_time, mov_avg(data[:,1], 10), label=name+'_avg', linewidth=1)
    
    merged_data_x.append(data[:,0]+end_time)
    merged_data_y.append(data[:,1])
    
    end_time += data[-1,0]


mov_avg_window = 7
sav_gol_window = 12
sav_gol_order = 2

merged_data_x = np.hstack(merged_data_x)
merged_data_y_raw = np.hstack(merged_data_y)
merged_data_y_movavg = mov_avg(np.hstack(merged_data_y), mov_avg_window)
merged_data_y_savgol = savgol(np.hstack(merged_data_y), sav_gol_window, sav_gol_order)

ax.scatter(merged_data_x, merged_data_y_raw, label='Raw Data', alpha=0.15, s=5, facecolor='none', edgecolor='b' )
ax.plot(merged_data_x, merged_data_y_movavg, linewidth=1, label=f'Moving Average n={mov_avg_window}')
# ax.plot(merged_data_x, merged_data_y_savgol, linewidth=1,label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

# finding the levels`
interval = 1365
for i in range(5):
    mask = (merged_data_x > 12*60+interval*i) & (merged_data_x < 15*60+interval*i)
    ax.plot(merged_data_x[mask], merged_data_y_raw[mask])
    print(i, np.mean(merged_data_y_raw[mask]),
          ResonantN(theta_spr=SPR_ang((np.mean(merged_data_y_raw[mask])+3985)/1000)))
# plt.show()
# mask = (merged_data_x > 121*60) & (merged_data_x < 124*60)
# plt.plot(merged_data_x[mask], merged_data_y_raw[mask])
# plt.plot(merged_data_x[mask], merged_data_y_movavg[mask])
# print('Raw Mean: ', np.mean(merged_data_y_raw[mask]), 'Raw Std: ', np.std(merged_data_y_raw[mask]))
# print('Averaged Mean: ', np.mean(merged_data_y_movavg[mask]), 'Averaged Std: ', np.std(merged_data_y_movavg[mask]))
# print('SavGol Mean: ', np.mean(merged_data_y_savgol[mask]), 'SavGol Std: ', np.std(merged_data_y_savgol[mask]))

ax.legend(loc='upper left', fontsize=10)
    
ax.set_xlabel('Time, min')
ax.set_ylabel('SPR Coordinate, um')
ax.set_xlim([0*60,125*60])
ax.set_ylim([360,800])
# ax.set_ylim([362,368])
# ax.set_xlim([120*60,129*60])
ax.grid(linewidth=1, alpha=0.3)
ax.set_xticks(np.arange(ax.get_xlim()[0],ax.get_xlim()[1]+300,300))
ax.set_xticklabels(np.array(ax.get_xticks()/60).astype(int), rotation=90)

offset = 3985
ax2 = ax.twinx()
ax2.set_ylabel('Refractive Index')
ax2.set_ylim(ax.get_ylim())
ylabels = [ResonantN(theta_spr=SPR_ang((x+offset)/1000)) for x in ax2.get_yticks()]
ax2.set_yticklabels(np.round(ylabels,5))

### REJECTING POINTS WITH HIGH ERROR FROM MEAN
# condition = np.abs(merged_data_y_raw-merged_data_y_movavg)/merged_data_y_movavg < 0.005
# clean_data_y_raw = np.where(condition, merged_data_y_raw, None)
# plt.show()
# plt.plot(merged_data_x, clean_data_y_raw)

# concentrations = [0,0.01,0.02,0.03,0.04,0.05]
# clrs = ['r','g','b','m','y','k']

# for c, clor in zip(concentrations,clrs):
#     ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(c)**2))*1000-offset, color=clor,linewidth=0.5,label=f'Glycerol {c*100:.1f}%',linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.008)**2))*1000-offset,color='g',linewidth=0.5,label='1% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.020)**2))*1000-offset,color='b',linewidth=0.5,label='2% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.026)**2))*1000-offset,color='y',linewidth=0.5,label='3% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.035)**2))*1000-offset,color='m',linewidth=0.5,label='4% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.043)**2))*1000-offset,color='k',linewidth=0.5,label='5% Glycerol', linestyle='--')
# # ax2.legend(fontsize=10)
# fig.savefig('BSAExperiment.svg', dpi=300)
plt.show()

#%% Three glycerol pyramids EXPERIMENT

spr_data_folder = 'spr_measurements_231026'
parent_path = Path(__file__).resolve().parents[1]
names=[
       '20231026_15.53.54_100_glycerol_3_channels',
        '20231026_16.22.03_100_glycerol_3_channels',
        '20231026_16.50.08_100_glycerol_3_channels',
        '20231026_17.20.44_100_glycerol_3_channels',
       ]


mov_avg_window = 16
VCSEL = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']
filename = 'data'

fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)
end_time = 0
merged_data_x = []
merged_data_y = []
for name in names:
    for vcs in VCSEL:
        data_path = Path(parent_path, spr_data_folder, name, vcs, filename)
        data = np.genfromtxt(str(data_path) + '.txt', delimiter=',')
        for i, datapoint in enumerate(data):
            data[i,1] = data[i,1] if data[i,1]>350 else data[i,1]+150
            # data[i,1] = data[i,1] if data[i,1]<420 else None
        # ax.plot(data[:,0], mov_avg(data[:,1], 7), linewidth=1, label=f'Moving Average n={mov_avg_window}')
        # ax.plot(data[:,0]+end_time, data[:,1], label=name, marker='o', linewidth=0.3, markersize=2, alpha=0.5)
        # ax.plot(data[:,0]+end_time, mov_avg(data[:,1], 10), label=name+'_avg', linewidth=1)
        # merged_data_x = data[:,0]
        # merged_data_y = data[:,1]
    merged_data_x.append(data[:,0]+end_time)
    merged_data_y.append(data[:,1])
    
    end_time += data[-1,0]

sav_gol_window = 12
sav_gol_order = 2

merged_data_x = np.hstack(merged_data_x)
merged_data_y_raw = np.hstack(merged_data_y)
merged_data_y_movavg = mov_avg(np.hstack(merged_data_y), mov_avg_window)
# merged_data_y_savgol = savgol(np.hstack(merged_data_y), sav_gol_window, sav_gol_order)

# ax.scatter(merged_data_x, merged_data_y_raw, label='Raw Data', alpha=0.7, s=5, facecolor='none', edgecolor='b' )
ax.plot(merged_data_x, merged_data_y_movavg, linewidth=1, label=f'Moving Average n={mov_avg_window}', color='r')
# ax.plot(merged_data_x, merged_data_y_savgol, linewidth=1,label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

# finding the levels`
# interval = 1365
# for i in range(5):
#     mask = (merged_data_x > 12*60+interval*i) & (merged_data_x < 15*60+interval*i)
#     ax.plot(merged_data_x[mask], merged_data_y_raw[mask])
#     print'(i, np.mean(merged_data_y_raw[mask]),
#           ResonantN(theta_spr=SPR_ang((np.mean(merged_data_y_raw[mask])+3985)/1000)))
# plt.show()
# mask = (merged_data_x > 25*60) & (merged_data_x < 20*60)
# plt.plot(merged_data_x[mask], merged_data_y_raw[mask])
# plt.plot(merged_data_x[mask], merged_data_y_movavg[mask])
print('Raw Mean: ', np.mean(merged_data_y_raw[mask]), 'Raw Std: ', np.std(merged_data_y_raw[mask]))
print('Averaged Mean: ', np.mean(merged_data_y_movavg[mask]), 'Averaged Std: ', np.std(merged_data_y_movavg[mask]))
# print('SavGol Mean: ', np.mean(merged_data_y_savgol[mask]), 'SavGol Std: ', np.std(merged_data_y_savgol[mask]))

# ax.legend(loc='upper left', fontsize=10)
    
ax.set_xlabel('Time, min')
ax.set_ylabel('SPR Coordinate, um')
# ax.set_xlim([13*60,16*60])
# ax.set_ylim([530.5,532.5])
# ax.set_ylim([362,368])
# ax.set_xlim([120*60,129*60])
ax.grid(linewidth=1, alpha=0.3)
ax.set_xticks(np.arange(ax.get_xlim()[0],ax.get_xlim()[1]+300,300))
ax.set_xticklabels(np.array(ax.get_xticks()/60).astype(int), rotation=90)

offset = 3820
ax2 = ax.twinx()
ax2.set_ylabel('Refractive Index')
# ax2.set_ylim(ax.get_ylim())
ylabels = [ResonantN(theta_spr=SPR_ang((x+offset)/1000)) for x in ax2.get_yticks()]
ax2.set_yticklabels(np.round(ylabels,5))

### REJECTING POINTS WITH HIGH ERROR FROM MEAN
# condition = np.abs(merged_data_y_raw-merged_data_y_movavg)/merged_data_y_movavg < 0.005
# clean_data_y_raw = np.where(condition, merged_data_y_raw, None)
# plt.show()
# plt.plot(merged_data_x, clean_data_y_raw)

concentrations = [0,0.01,0.02,0.03,0.04,0.05]
clrs = ['r','g','b','m','y','k']

for c, clor in zip(concentrations,clrs):
    ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(c)**2))*1000-offset, color=clor,linewidth=0.5,label=f'Glycerol {c*100:.1f}%',linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.008)**2))*1000-offset,color='g',linewidth=0.5,label='1% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.020)**2))*1000-offset,color='b',linewidth=0.5,label='2% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.026)**2))*1000-offset,color='y',linewidth=0.5,label='3% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.035)**2))*1000-offset,color='m',linewidth=0.5,label='4% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.043)**2))*1000-offset,color='k',linewidth=0.5,label='5% Glycerol', linestyle='--')
# ax2.legend(fontsize=10)
# fig.savefig('BSAExperiment.svg', dpi=300)
plt.show()

#%% Flushing

spr_data_folder = 'spr_measurements_231212'
parent_path = Path(__file__).resolve().parents[1]
names=[
        '20231212_00.43.49_test_spectrum',
        '20231212_01.01.39_test_spectrum',
        # '20231212_00.17.43_test_spectrum',
       ]


mov_avg_window = 16
VCSEL = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5', 'VCSEL_6',]
filename = 'data'

fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)
end_time = 0
merged_data_x = []
merged_data_y = []
for name in names:
    for vcs in VCSEL:
        data_path = Path(parent_path, spr_data_folder, name, vcs, filename)
        data = np.genfromtxt(str(data_path) + '.txt', delimiter=',')
        for i, datapoint in enumerate(data):
            data[i,1] = data[i,1] if data[i,1]>350 else data[i,1]+150
            # data[i,1] = data[i,1] if data[i,1]<420 else None
        ax.plot(data[:,0], mov_avg(data[:,1], 7), linewidth=1, label=f'Moving Average n={mov_avg_window}')
        ax.plot(data[:,0]+end_time, data[:,1], label=name, marker='o', linewidth=0.3, markersize=2, alpha=0.5)
        ax.plot(data[:,0]+end_time, mov_avg(data[:,1], 10), label=name+'_avg', linewidth=1)
        merged_data_x = data[:,0]
        merged_data_y = data[:,1]
    # merged_data_x.append(data[:,0]+end_time)
    # merged_data_y.append(data[:,1])
    
    end_time += data[-1,0]

sav_gol_window = 12
sav_gol_order = 2

merged_data_x = np.hstack(merged_data_x)
merged_data_y_raw = np.hstack(merged_data_y)
merged_data_y_movavg = mov_avg(np.hstack(merged_data_y), mov_avg_window)
# merged_data_y_savgol = savgol(np.hstack(merged_data_y), sav_gol_window, sav_gol_order)

ax.scatter(merged_data_x, merged_data_y_raw, label='Raw Data', alpha=0.7, s=5, facecolor='none', edgecolor='b' )
# ax.plot(merged_data_x, merged_data_y_movavg, linewidth=1, label=f'Moving Average n={mov_avg_window}', color='r')
# ax.plot(merged_data_x, merged_data_y_savgol, linewidth=1,label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

# finding the levels`
# interval = 1365
# for i in range(5):
#     mask = (merged_data_x > 12*60+interval*i) & (merged_data_x < 15*60+interval*i)
#     ax.plot(merged_data_x[mask], merged_data_y_raw[mask])
#     print'(i, np.mean(merged_data_y_raw[mask]),
#           ResonantN(theta_spr=SPR_ang((np.mean(merged_data_y_raw[mask])+3985)/1000)))
# plt.show()
# mask = (merged_data_x > 25*60) & (merged_data_x < 20*60)
# plt.plot(merged_data_x[mask], merged_data_y_raw[mask])
# plt.plot(merged_data_x[mask], merged_data_y_movavg[mask])
print('Raw Mean: ', np.mean(merged_data_y_raw[mask]), 'Raw Std: ', np.std(merged_data_y_raw[mask]))
print('Averaged Mean: ', np.mean(merged_data_y_movavg[mask]), 'Averaged Std: ', np.std(merged_data_y_movavg[mask]))
# print('SavGol Mean: ', np.mean(merged_data_y_savgol[mask]), 'SavGol Std: ', np.std(merged_data_y_savgol[mask]))

# ax.legend(loc='upper left', fontsize=10)
    
ax.set_xlabel('Time, min')
ax.set_ylabel('SPR Coordinate, um')
# ax.set_xlim([13*60,16*60])
# ax.set_ylim([530.5,532.5])
# ax.set_ylim([362,368])
# ax.set_xlim([120*60,129*60])
ax.grid(linewidth=1, alpha=0.3)
ax.set_xticks(np.arange(ax.get_xlim()[0],ax.get_xlim()[1]+300,300))
ax.set_xticklabels(np.array(ax.get_xticks()/60).astype(int), rotation=90)

offset = 3820
ax2 = ax.twinx()
ax2.set_ylabel('Refractive Index')
# ax2.set_ylim(ax.get_ylim())
ylabels = [ResonantN(theta_spr=SPR_ang((x+offset)/1000)) for x in ax2.get_yticks()]
ax2.set_yticklabels(np.round(ylabels,5))

### REJECTING POINTS WITH HIGH ERROR FROM MEAN
# condition = np.abs(merged_data_y_raw-merged_data_y_movavg)/merged_data_y_movavg < 0.005
# clean_data_y_raw = np.where(condition, merged_data_y_raw, None)
# plt.show()
# plt.plot(merged_data_x, clean_data_y_raw)

concentrations = [0,0.01,0.02,0.03,0.04,0.05]
clrs = ['r','g','b','m','y','k']

for c, clor in zip(concentrations,clrs):
    ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(c)**2))*1000-offset, color=clor,linewidth=0.5,label=f'Glycerol {c*100:.1f}%',linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.008)**2))*1000-offset,color='g',linewidth=0.5,label='1% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.020)**2))*1000-offset,color='b',linewidth=0.5,label='2% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.026)**2))*1000-offset,color='y',linewidth=0.5,label='3% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.035)**2))*1000-offset,color='m',linewidth=0.5,label='4% Glycerol', linestyle='--')
# # ax2.axhline(SPR_loc(ResonantAngle(e_analyte=ref_idx(0.043)**2))*1000-offset,color='k',linewidth=0.5,label='5% Glycerol', linestyle='--')
# ax2.legend(fontsize=10)
# fig.savefig('BSAExperiment.svg', dpi=300)
plt.show()

#%% BSA DS attempt 3

## Load all data
spr_data_folder = 'spr_measurements_231212'
parent_path = Path(__file__).resolve().parents[1]
measurement_path = Path(parent_path, spr_data_folder)

## Names of measurement segments
names = os.listdir(measurement_path)

## Remove reference spectrum
names.pop(0)

## Vcesls used in measurement
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5']
filename = 'data'

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
        


# which_trace = 4
# ax.plot(plot_data[vcsels[which_trace]][0, :], plot_data[vcsels[which_trace]][1, :])

# mov_avg_window = 16

## Figure object
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

colors  = ['red', 'lightcoral', 'green', 'lightgreen', 'blue', 'lightblue']
marking = ['', '--', '', '--', '', '--']

which_trace = 5
x_data = plot_data[vcsels[which_trace]][0, :]/60
y_data = plot_data[vcsels[which_trace]][1, :]
        
# ax.plot(x_data, y_data)

# for i, vcsel in enumerate(vcsels):
#     ax.plot(plot_data[vcsel][0, :]/60, plot_data[vcsel][1, :], marking[i], color=colors[i])

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'BSA-DS cake')


sav_gol_window = 12
sav_gol_order = 2

merged_data_y_movavg = mov_avg(np.hstack(y_data), mov_avg_window)
merged_data_y_savgol = savgol(np.hstack(y_data), sav_gol_window, sav_gol_order)

ax.scatter(x_data, y_data, label='Raw Data', alpha=0.7, s=1, facecolor='none', edgecolor='b' )
ax.scatter(x_data, merged_data_y_movavg, s=1, label=f'Moving Average n={mov_avg_window}', color='r')
# ax.plot(x_data, merged_data_y_savgol, linewidth=1.5,label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')


#%% Water

## Load all data
spr_data_folder = 'spr_measurements_231215'
parent_path = Path(__file__).resolve().parents[1]
measurement_path = Path(parent_path, spr_data_folder)

## Names of measurement segments
names = os.listdir(measurement_path)

## Remove reference spectrum
names.pop(0)

## Vcesls used in measurement
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5']
filename = 'data'

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
        


# which_trace = 4
# ax.plot(plot_data[vcsels[which_trace]][0, :], plot_data[vcsels[which_trace]][1, :])

# mov_avg_window = 16

for i, vcsel in enumerate(vcsels):
    frame_time = plot_data[vcsel][0, :]
    spr_data   = plot_data[vcsel][1, :]
    
    for j in range(len(spr_data)):
        if spr_data[j] > 100:
            spr_data[j] = spr_data[j-1]
    
    # ax.plot(plot_data[vcsel][0, :]/60, plot_data[vcsel][1, :], marking[i], color=colors[i])



## Figure object
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

colors  = ['red', 'lightcoral', 'green', 'lightgreen', 'blue', 'lightblue']
marking = ['', '--', '', '--', '', '--']

which_trace = 2
x_data = plot_data[vcsels[which_trace]][0, :]
y_data = plot_data[vcsels[which_trace]][1, :]
        
# ax.plot(x_data, y_data)

# for i, vcsel in enumerate(vcsels):
#     ax.plot(plot_data[vcsel][0, :]/60, plot_data[vcsel][1, :], marking[i], color=colors[i])

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')


mov_avg_window = 6
sav_gol_window = 200
sav_gol_order = 5

merged_data_y_movavg = mov_avg(np.hstack(y_data), mov_avg_window)
merged_data_y_savgol = savgol(np.hstack(y_data), sav_gol_window, sav_gol_order)

ax.scatter(x_data/60, y_data, label='Raw Data', alpha=0.7, s=1, facecolor='none', edgecolor='b' )
# ax.scatter(x_data, merged_data_y_movavg, s=1, label=f'Moving Average n={mov_avg_window}', color='r')
ax.plot(x_data/60, merged_data_y_savgol, 'r', linewidth=1.5, label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

print('Raw Mean: ', np.mean(y_data), 'Raw Std: ', np.std(y_data))
print('Averaged Mean: ', np.mean(merged_data_y_savgol), 'Averaged Std: ', np.std(merged_data_y_savgol))

#%% Water noise new camera code

## Load all data
spr_data_folder = 'spr_measurements_231217'
parent_path = Path(__file__).resolve().parents[1]
measurement_path = Path(parent_path, spr_data_folder)

## Names of measurement segments
names = os.listdir(measurement_path)

## Remove reference spectrum
names.pop(0)
names.pop(0)
names.pop(0)
names.pop(0)
names.pop(1)
print(names)

## Vcesls used in measurement
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5']
filename = 'data'

## Dict for plotting data
plot_data = {}
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
        
        if reference_level == 0:
            reference_level = data[0, 1]
            current_spr_data = data[:, 1] - reference_level
        else:
            current_spr_data = data[:, 1] - reference_level
            
            
        frame_time = np.concatenate((frame_time, current_frame_time))
        spr_data   = np.concatenate((spr_data, current_spr_data))
    
    plot_data[vcsel] = np.vstack((frame_time, spr_data))
    plot_moving_avg[vcsel] = np.vstack((frame_time, mov_avg(np.hstack(spr_data), mov_avg_window)))
    plot_savgol[vcsel] = np.vstack((frame_time, savgol(np.hstack(spr_data), sav_gol_window, sav_gol_order)))
        


# which_trace = 4
# ax.plot(plot_data[vcsels[which_trace]][0, :], plot_data[vcsels[which_trace]][1, :])

# mov_avg_window = 16

mov_avg_window = 6
sav_gol_window = 200
sav_gol_order = 5

## Figure object
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

colors  = ['red', 'lightcoral', 'green', 'lightgreen', 'blue', 'lightblue']
marking = ['', '--', '', '--', '', '--']

which_trace = 0
x_data = plot_data[vcsels[which_trace]][0, :]
y_data = plot_data[vcsels[which_trace]][1, :]

x_data_mov_avg = plot_moving_avg[vcsels[which_trace]][0, :]
y_data_mov_avg = plot_moving_avg[vcsels[which_trace]][1, :]

x_data_savgol = plot_savgol[vcsels[which_trace]][0, :]
y_data_savgol = plot_savgol[vcsels[which_trace]][1, :]
        
ax.plot(x_data/60, y_data)
ax.plot(x_data_mov_avg/60, y_data_mov_avg, 'black')
ax.plot(x_data_savgol/60, y_data_savgol, 'red')

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')

print('Raw Mean: ', np.mean(y_data), 'Raw Std: ', np.std(y_data))
print('Moving average Mean: ', np.mean(y_data_mov_avg), 'Averaged Std: ', np.std(y_data_mov_avg))
print('Savgol Mean: ', np.mean(y_data_savgol), 'Averaged Std: ', np.std(y_data_savgol))



#%% Water noise new

## Load all data
spr_data_folder = 'spr_measurements_231217'
parent_path = Path(__file__).resolve().parents[1]
measurement_path = Path(parent_path, spr_data_folder)

## Names of measurement segments
names = os.listdir(measurement_path)

## Remove reference spectrum
names.pop(0)
names.pop(0)
names.pop(0)
names.pop(0)
names.pop(0)
print(names)

## Vcesls used in measurement
vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4', 'VCSEL_5']
filename = 'data'

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
        


# which_trace = 4
# ax.plot(plot_data[vcsels[which_trace]][0, :], plot_data[vcsels[which_trace]][1, :])

# mov_avg_window = 16

for i, vcsel in enumerate(vcsels):
    frame_time = plot_data[vcsel][0, :]
    spr_data   = plot_data[vcsel][1, :]
    
    for j in range(len(spr_data)):
        if spr_data[j] > 100:
            spr_data[j] = spr_data[j-1]
    
    # ax.plot(plot_data[vcsel][0, :]/60, plot_data[vcsel][1, :], marking[i], color=colors[i])



## Figure object
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)

colors  = ['red', 'lightcoral', 'green', 'lightgreen', 'blue', 'lightblue']
marking = ['', '--', '', '--', '', '--']

which_trace = 1
x_data = plot_data[vcsels[which_trace]][0, :]
y_data = plot_data[vcsels[which_trace]][1, :]
        
# ax.plot(x_data, y_data)

# for i, vcsel in enumerate(vcsels):
#     ax.plot(plot_data[vcsel][0, :]/60, plot_data[vcsel][1, :], marking[i], color=colors[i])

plt.grid(True)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')
plt.title(r'Noise with water')


mov_avg_window = 6
sav_gol_window = 200
sav_gol_order = 5

merged_data_y_movavg = mov_avg(np.hstack(y_data), mov_avg_window)
merged_data_y_savgol = savgol(np.hstack(y_data), sav_gol_window, sav_gol_order)

ax.scatter(x_data/60, y_data, label='Raw Data', alpha=0.7, s=1, facecolor='none', edgecolor='b' )
# ax.scatter(x_data, merged_data_y_movavg, s=1, label=f'Moving Average n={mov_avg_window}', color='r')
ax.plot(x_data/60, merged_data_y_savgol, 'r', linewidth=1.5, label=f'Savitzky-Golay n={sav_gol_window} o={sav_gol_order}')

print('Raw Mean: ', np.mean(y_data), 'Raw Std: ', np.std(y_data))
print('Averaged Mean: ', np.mean(merged_data_y_savgol), 'Averaged Std: ', np.std(merged_data_y_savgol))