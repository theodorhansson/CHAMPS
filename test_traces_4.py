#%%

import matplotlib.pyplot as plt
import numpy as np

time_buffer_PBS = 20*60
time_buffer_C6 = 15*60

full_time = time_buffer_PBS

time_trace = np.arange(0, full_time, 1)
noise_level = 0.1
final_trace = np.random.normal(0, noise_level, time_buffer_PBS)
    
for i in range(len(final_trace)):
    random_number = np.random.random()
    if random_number > 0.8:
        final_trace[i] = final_trace[i] + (0.5 - np.random.random())*noise_level*3
        
pump_freq = 0.2
final_trace = final_trace

plt.plot(time_trace/60, final_trace, '-x', color='black', ms=0.4)

#%%
measurement_folder = 'spr_measurements_240922'

from pathlib import Path
import os
file_path = Path(__file__).parent
save_folder_path = Path(file_path, 'spr_project', 'spr_measurement_data', measurement_folder)
if not os.path.exists(str(save_folder_path)):
   os.makedirs(str(save_folder_path))
   
exact_measurement = '20240922_17.01.01_no_pump_noise_C6'
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
    


