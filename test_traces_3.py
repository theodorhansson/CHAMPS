#%%

import matplotlib.pyplot as plt
import numpy as np

time_buffer_PBS = 6*60
time_buffer_C6 = 15*60

full_time = time_buffer_PBS + time_buffer_C6


def sigmoid(a, b, const, x):
    return const/(1 + np.exp(-a*x + b))

time_trace = np.arange(0, full_time, 1)
noise_level = 0.01
trace_buffer_PBS = np.random.normal(0, noise_level, time_buffer_PBS)

trace_C6 = np.zeros(time_buffer_C6)
C6_offset = 15
a = 0.1
b = 0
for i in range(time_buffer_C6):
    sig_var = i - time_buffer_C6/2    
    if i < time_buffer_C6/2:  
        trace_C6[i] = sigmoid(a, b, C6_offset, sig_var) + np.random.normal(0, noise_level)
    else:
        trace_C6[i] = sigmoid(a, b, C6_offset, sig_var) + np.random.normal(0, noise_level) + (i - 1)*(-3)/time_buffer_C6
 
    
final_trace = np.concat((trace_buffer_PBS, trace_C6))
for i in range(len(final_trace)):
    random_number = np.random.random()
    if random_number > 0.8:
        final_trace[i] = final_trace[i] + (0.5 - np.random.random())*noise_level*10
    
    if random_number > 0.95:
        rand = (0.5 - np.random.random())*noise_level*25
        
        for j in range(30):
            final_trace[i - j] = final_trace[i - j] + rand*(i - 10)/i

plt.plot(time_trace/60, final_trace, '-x', color='black', ms=0.4)

#%%
measurement_folder = 'spr_measurements_240925'

from pathlib import Path
import os
file_path = Path(__file__).parent
save_folder_path = Path(file_path, 'spr_project', 'spr_measurement_data', measurement_folder)
if not os.path.exists(str(save_folder_path)):
   os.makedirs(str(save_folder_path))
   
exact_measurement = '20240925_09.10.12_miRNA_attempt_12'
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
    


