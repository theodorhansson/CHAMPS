#%%

import matplotlib.pyplot as plt
import numpy as np

time_start   = 15*60
time_stopp   = 20*60 -  time_start
time_glycerol  = 5*60

full_time = time_start + 10*time_glycerol + time_stopp
time_trace = np.arange(0, full_time, 1)

level = 148/5
level_offest = np.array([0.2, -1.1, -1.6, 0.4, -1.2, -0.1, -1, 2, 0, -1, -2])
# level_offest = np.array([-0.5, 1.2, -0.5, 1.5, -0.2, 1, 3, -1, 1.5, 1, 0])
# level_offest = np.array([-0.6, 0.1, -1.2, 0.1, 0.6, 0.6, -0-5, 0.1, 2, -1.1, -2.6])


def sigmoid(a, b, const, x):
    return const/(1 + np.exp(-a*x + b))


noise_level = 0.07

final_trace = np.zeros(time_start)

## First step
trace_glycerol = np.zeros(time_glycerol)
glycerol_offset = 1*level + level_offest[0]
a = 0.09
b = 0
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Second step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = 1*level + level_offest[1]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 1*level + level_offest[0] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Third step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = 1*level + level_offest[2]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 2*level + level_offest[0] + level_offest[1] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Fourth step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = 1*level + level_offest[3]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 3*level + level_offest[0] + level_offest[1] + level_offest[2] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Fifth step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = 1*level + level_offest[4]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 4*level + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Sixth step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = -1*level + level_offest[5]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 5*level + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + level_offest[4] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Seventh step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = -1*level + level_offest[6]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 4*level + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + level_offest[4] + level_offest[5] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Eigth step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = -1*level + level_offest[7]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 3*level + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + level_offest[4] + level_offest[5] + level_offest[6] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Ninth step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = -1*level + level_offest[8]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 2*level + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + level_offest[4] + level_offest[5] + level_offest[6] + level_offest[7] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

## Tenth step
trace_glycerol = np.ones(time_glycerol)
glycerol_offset = -1*level + level_offest[8]
for i in range(time_glycerol):
    sig_var = i - time_glycerol/2
    trace_glycerol[i] = 1*level + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + level_offest[4] + level_offest[5] + level_offest[6] + level_offest[7] + level_offest[8] + sigmoid(a, b, glycerol_offset, sig_var) + np.random.normal(0, 2*noise_level)

final_trace = np.concat((final_trace, trace_glycerol))

trace_stopp = np.zeros(time_stopp) + level_offest[0] + level_offest[1] + level_offest[2] + level_offest[3] + level_offest[4] + level_offest[5] + level_offest[6] + level_offest[7] + 2*level_offest[8] 
final_trace = np.concat((final_trace, trace_stopp))

pump_freq = 0.19

pump_noise = np.sin(2*np.pi*pump_freq*time_trace + (np.random.random() - 0.5)*2*np.pi)*0.1
final_trace = final_trace + pump_noise

for i in range(len(final_trace)):
    random_number = np.random.random()
    if random_number > 0.8:
        final_trace[i] = final_trace[i] + (0.5 - np.random.random())*noise_level*10
    
    if random_number > 0.95:
        rand = (0.5 - np.random.random())*noise_level*10
        
        for j in range(30):
            final_trace[i - j] = final_trace[i - j] + rand*(i - 10)/i


plt.plot(time_trace/60, final_trace, '-x', color='black', ms=0.4)


#%%
#%#%%
measurement_folder = 'spr_measurements_250207'

from pathlib import Path
import os
file_path = Path(__file__).parent
save_folder_path = Path(file_path, 'spr_project', 'spr_measurement_data', measurement_folder)
if not os.path.exists(str(save_folder_path)):
   os.makedirs(str(save_folder_path))
   
exact_measurement = '20250207_15.17.10_five_glycerol_steps_cassandra'
exact_measurement_path = Path(save_folder_path, exact_measurement)
if not os.path.exists(str(exact_measurement_path)):
    os.makedirs(str(exact_measurement_path))
   
channels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2']

for i in channels:
    vcsel_path = Path(exact_measurement_path, i)
    if not os.path.exists(str(vcsel_path)):
        os.makedirs(str(vcsel_path))
       
       #%%
trace = 'VCSEL_2'
trace_path = Path(exact_measurement_path, trace)

measurement_trace = np.vstack((time_trace.T, final_trace.T)).T

np.savetxt(str(trace_path) + '//data.txt', measurement_trace, delimiter=',')
    


