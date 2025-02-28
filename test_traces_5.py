#%%

import matplotlib.pyplot as plt
import numpy as np

time_buffer_1   = 4*60
time_miRNA      = 15*60
time_buffer_2   = 10*60
time_antibody   = 5*60
time_buffer_3     = 8*60
time_buffer_4     = 2*60
time_dissociation = 8*60
time_HCL          = 5*60
time_NaOH         = 5*60
time_tris         = 12*60
time_pre_miRNA_2      = 5*60
time_miRNA_2      = 15*60
time_tris_2         = 10*60

full_time = time_buffer_1 + time_miRNA + time_buffer_2 + time_antibody + time_buffer_3 + time_buffer_4 + time_dissociation + time_HCL + time_NaOH + time_tris + time_pre_miRNA_2 + time_miRNA_2 + time_tris_2

saturated = True

## 20nM   82,  565, -30,   0.1
## 5nM    26,  80,  -18,   0.02
## 1nm    7,   28,  -3,    0.02
## 0.5nM  3.8, 15,  -1,    0.03
## 0.2nM  2,   6,   -0.8,  0.01
## 0.1nM  1,   3,   -0.5,  0.01
## 0.05nM 0.5, 1.5, -0.2,  0.01
## 0.02nM 0.3, 1,   -0.1,  0.01

concentration = {'20_5' : {'miRNA' : 78, 'antibody' : 585, 'buffer_3' : -50, 'noise_level' : 0.1, 'pump_freq' : 0.22},
                 '1.0_5' : {'miRNA' : 8, 'antibody' : 26, 'buffer_3' : -3, 'noise_level' : 0.08, 'pump_freq' : 0.2},
                 '0.1_5' : {'miRNA' : 1.2, 'antibody' : 6, 'buffer_3' : -1, 'noise_level' : 0.07, 'pump_freq' : 0.19},
                 }

    
which_trace = '20_5'

def sigmoid(a, b, const, x):
    return const/(1 + np.exp(-a*x + b))

time_trace = np.arange(0, full_time, 1)
noise_level = concentration[which_trace]['noise_level']
trace_buffer_1 = np.random.normal(0, noise_level, time_buffer_1)

trace_miRNA = np.zeros(time_miRNA)
miRNA_offset = concentration[which_trace]['miRNA']

saturation_time = 5*60
if saturated:
    
    a = 0.01
    b = 0
    for i in range(time_miRNA):
        sig_var = i - time_miRNA/2    
        trace_miRNA[i] = sigmoid(a, b, miRNA_offset, sig_var) + np.random.normal(0, noise_level)
        # trace_miRNA[i] = (i - 1)*miRNA_offset/time_miRNA + np.random.normal(0, 2*noise_level)
        

trace_buffer_2 = np.zeros(time_buffer_2) + miRNA_offset + np.random.normal(0, noise_level, time_buffer_2)

trace_antibody = np.zeros(time_antibody)
antibody_offset = concentration[which_trace]['antibody']
a = 0.07
b = 0
for i in range(time_antibody):
    sig_var = i - time_antibody/2    
    trace_antibody[i] = sigmoid(a, b, antibody_offset, sig_var) + np.random.normal(0, 2*noise_level) + miRNA_offset
    
trace_buffer_3 = np.zeros(time_buffer_3)
offset_buffer_3 = concentration[which_trace]['buffer_3']
a = 0.02
b = 0
for i in range(time_buffer_3):
    sig_var = i - time_buffer_3/2    
    trace_buffer_3[i] = sigmoid(a, b, offset_buffer_3, sig_var) + np.random.normal(0, noise_level) + antibody_offset +  miRNA_offset
    

trace_buffer_4 = np.zeros(time_buffer_4) + antibody_offset +  miRNA_offset + offset_buffer_3 + np.random.normal(0, noise_level, time_buffer_4)
    
trace_dissociation = np.zeros(time_dissociation)
dissociation_const = 20
dissociation_offset = - miRNA_offset - antibody_offset + offset_buffer_3 - dissociation_const
a = 0.05
b = 0
for i in range(time_dissociation):
    sig_var = i - time_antibody/2    
    trace_dissociation[i] = sigmoid(a, b, dissociation_offset, sig_var) + np.random.normal(0, noise_level*30) + antibody_offset +  miRNA_offset + offset_buffer_3
    
# trace_HCL = np.zeros(time_HCL)
HCL_offset = antibody_offset +  miRNA_offset + offset_buffer_3 + dissociation_offset
trace_HCL = np.random.normal(0, noise_level*30, time_HCL) + HCL_offset


a = 0.05
b = 0
trace_NaOH = np.zeros(time_NaOH)
NaOH_const = 100
# NaOH_offset = antibody_offset +  miRNA_offset + offset_buffer_3
a = 0.2
b = 0
for i in range(time_NaOH):
    sig_var = i - time_NaOH/2    
    trace_NaOH[i] = sigmoid(a, b, NaOH_const, sig_var) + np.random.normal(0, noise_level*30) + HCL_offset
    
trace_tris = np.zeros(time_tris)
tris_const = 80
# NaOH_offset = antibody_offset +  miRNA_offset + offset_buffer_3
a = 0.2
b = 0
for i in range(time_tris):
    sig_var = i - time_tris/2    
    trace_tris[i] = sigmoid(a, b, tris_const, sig_var) + np.random.normal(0, noise_level*1.2) + HCL_offset + NaOH_const + 18


trace_miRNA_2 = np.random.normal(0, noise_level, time_buffer_1)
for i in range(time_dissociation):
    sig_var = i - time_antibody/2    
    trace_dissociation[i] = sigmoid(a, b, HCL_offset, sig_var) + np.random.normal(0, noise_level) + antibody_offset +  miRNA_offset + offset_buffer_3
    
    
    

    
trace_miRNA_2 = np.zeros(time_miRNA_2)
# miRNA_2_offset = concentration[which_trace]['miRNA']
miRNA_2_offset = 75

trace_pre_miRNA_2 = np.ones(time_pre_miRNA_2)*(antibody_offset +  miRNA_offset + offset_buffer_3 - 630)

saturation_time = 5*60
a = 0.008
b = 0


for i in range(time_miRNA_2):
    sig_var = i - time_miRNA_2/2    
    # if i < int(time_miRNA_2/2+ 20):
    trace_miRNA_2[i] = (i - 1)*miRNA_2_offset/time_miRNA_2 + np.random.normal(0, noise_level) + antibody_offset +  miRNA_offset + offset_buffer_3 - 630
    # else:
        # trace_miRNA_2[i] = sigmoid(a, b, miRNA_offset, sig_var) + np.random.normal(0, noise_level) + HCL_offset + tris_const + NaOH_const + 19
     
trace_tris_2 = np.ones(time_tris_2)*138.2
    
final_trace = np.concat((trace_buffer_1, trace_miRNA, trace_buffer_2, trace_antibody, trace_buffer_3, trace_buffer_4, trace_dissociation, trace_HCL, trace_NaOH, trace_tris, trace_pre_miRNA_2, trace_miRNA_2, trace_tris_2))

pump_noise = np.sin(2*np.pi*concentration[which_trace]['pump_freq']*time_trace + (np.random.random() - 0.5)*2*np.pi)*0.1

final_trace = final_trace + pump_noise

for i in range(len(final_trace)):
    random_number = np.random.random()
    if random_number > 0.8:
        final_trace[i] = final_trace[i] + (0.5 - np.random.random())*noise_level*4
    
    if random_number > 0.95:
        rand = (0.5 - np.random.random())*noise_level*4
        
        for j in range(30):
            final_trace[i - j] = final_trace[i - j] + rand*(i - 10)/i

final_trace[2800:2880] = 0
final_trace[3020:3150] = 0
final_trace[3220:3350] = 0
final_trace[3320:3550] = 0

plt.plot(time_trace/60, final_trace, '-x', color='black', ms=0.4)

plt.grid(True)
plt.legend(fontsize=12, framealpha=0.3, edgecolor='black', loc='upper left')
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [$\mu$m]')

#%%
measurement_folder = 'spr_measurements_240925'

from pathlib import Path
import os
file_path = Path(__file__).parent
save_folder_path = Path(file_path, 'spr_project', 'spr_measurement_data', measurement_folder)
if not os.path.exists(str(save_folder_path)):
   os.makedirs(str(save_folder_path))
   
exact_measurement = '20240925_18.49.58_miRNA_5'
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
    


