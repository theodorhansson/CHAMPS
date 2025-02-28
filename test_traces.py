#%%

import matplotlib.pyplot as plt
import numpy as np

time_buffer_1   = 4*60
time_miRNA      = 15*60
time_buffer_2   = 10*60
time_antibody   = 5*60
time_buffer_3     = 8*60
time_buffer_4     = 5*60
full_time = time_buffer_1 + time_miRNA + time_buffer_2 + time_antibody + time_buffer_3 + time_buffer_4 

saturated = True
## 20nM   82,  565, -30,   0.1
## 5nM    26,  80,  -18,   0.02 
## 1nm    7,   28,  -3,    0.02
## 0.5nM  3.8, 15,  -1,    0.03
## 0.2nM  2,   6,   -0.8,  0.01
## 0.1nM  1,   3,   -0.5,  0.01
## 0.05nM 0.5, 1.5, -0.2,  0.01
## 0.02nM 0.3, 1,   -0.1,  0.01

#%%

conc            = np.array([0.01, 0.02,   0.05, 0.1,  0.2,  0.5,  1,  5,   10,  20])
mi_response     = np.array([0.1,  0.5,    1,    2,    3,    4,    8.6, 55,  100, 200])
anit_response   = np.array([1.,   1.5,    2.5,  4.8,  7.5,  17.5, 42, 160, 300, 565]) -1

plt.figure(1)
plt.plot(conc, mi_response, 'x')
plt.xscale('log')
plt.yscale('log')
# 
# plt.figure(2)
# plt.plot(conc, anit_response, 'x')
# plt.xscale('log')
# plt.yscale('log')



#%%

concentration = {## a
                 '5_a'   : {'miRNA' : 34,  'antibody' : 163, 'buffer_3' : -10, 'noise_level' : 0.05, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_240919', 'exact_measurement' : 'spr_measurements_240919_run_a', 'VCSEL':'VCSEL_0'},
                 '20_0'  : {'miRNA' : 110, 'antibody' : 588, 'buffer_3' : -70, 'noise_level' : 0.07, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_240919', 'exact_measurement' : 'spr_measurements_240919_run_a', 'VCSEL':'VCSEL_1'},
                 'ref_0' : {'miRNA' : 0.8,   'antibody' : 1.2,   'buffer_3' : 0, 'noise_level' : 0.06, 'pump_freq' : 0.25, 'measurement_folder' : 'spr_measurements_240919', 'exact_measurement' : 'spr_measurements_240919_run_a', 'VCSEL':'VCSEL_2'},
                 
                 ## b
                 '0.05_1' : {'miRNA' : 1.1, 'antibody' : 3.8,  'buffer_3' : -2, 'noise_level' : 0.06, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_b', 'VCSEL':'VCSEL_0'},
                 '0.5_1'  : {'miRNA' : 4.4,  'antibody' : 20.1, 'buffer_3' : -3, 'noise_level' : 0.07, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_b', 'VCSEL':'VCSEL_1'},
                 'ref_1'  : {'miRNA' : 0.8,   'antibody' : 1.4,  'buffer_3' : -0.2, 'noise_level' : 0.06, 'pump_freq' : 0.24, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_b', 'VCSEL':'VCSEL_2'},
                 
                 ## c
                 '0.01_2' : {'miRNA' : 0.8, 'antibody' : 1.55, 'buffer_3' : -0.5, 'noise_level' : 0.06, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_c', 'VCSEL':'VCSEL_0'},
                 '0.02_2' : {'miRNA' : 0.8, 'antibody' : 2.0,  'buffer_3' : -0.5, 'noise_level' : 0.08, 'pump_freq' : 0.2, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_c', 'VCSEL':'VCSEL_1'},
                 'ref_2'  : {'miRNA' : 0.8, 'antibody' : 1,    'buffer_3' : 0, 'noise_level' : 0.06, 'pump_freq' : 0.24, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_c', 'VCSEL':'VCSEL_2'},
                 
                 ## d
                 '0.1_3'  : {'miRNA' : 1.5, 'antibody' : 4.8, 'buffer_3' : -1, 'noise_level' : 0.07, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_d', 'VCSEL':'VCSEL_0'},
                 '1.0_3'  : {'miRNA' : 8.6, 'antibody' : 25,  'buffer_3' : -3, 'noise_level' : 0.07, 'pump_freq' : 0.2, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_d', 'VCSEL':'VCSEL_1'},
                 'ref_3'  : {'miRNA' : 0.8,   'antibody' : 2,   'buffer_3' : -0.2, 'noise_level' : 0.06, 'pump_freq' : 0.24, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_d', 'VCSEL':'VCSEL_2'},
                 
                 ## e
                 '0.01_4' : {'miRNA' : 0.8, 'antibody' : 1.45, 'buffer_3' : -0.5, 'noise_level' : 0.06, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_e', 'VCSEL':'VCSEL_0'},
                 '0.02_4' : {'miRNA' : 0.8, 'antibody' : 2.0,  'buffer_3' : -0.5, 'noise_level' : 0.08, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_e', 'VCSEL':'VCSEL_1'},
                 'ref_4'  : {'miRNA' : 0.8, 'antibody'  : 1,    'buffer_3' : -0.1, 'noise_level' : 0.05, 'pump_freq' : 0.25, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_e', 'VCSEL':'VCSEL_2'},
                 
                 ## f
                 '0.1_5'  : {'miRNA' : 1.5, 'antibody' : 5.2, 'buffer_3' : -1, 'noise_level' : 0.08, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_f', 'VCSEL':'VCSEL_0'},
                 '1.0_5'  : {'miRNA' : 8.4, 'antibody' : 24.2,  'buffer_3' : -2.2, 'noise_level' : 0.06, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_f', 'VCSEL':'VCSEL_1'},
                 'ref_5'  : {'miRNA' : 0.8, 'antibody' : 1.2, 'buffer_3' : -1, 'noise_level' : 0.05, 'pump_freq' : 0.23, 'measurement_folder' : 'spr_measurements_240925', 'exact_measurement' : 'spr_measurements_240925_run_f', 'VCSEL':'VCSEL_2'},

                 ## g
                 '0.05_6' : {'miRNA' : 1, 'antibody' : 3.8,  'buffer_3' : -1.2, 'noise_level' : 0.06, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_g', 'VCSEL':'VCSEL_0'},
                 '0.5_6'  : {'miRNA' : 4.9, 'antibody' : 20.2, 'buffer_3' : -2.5, 'noise_level' : 0.07, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_g', 'VCSEL':'VCSEL_1'},
                 'ref_6'  : {'miRNA' : 0.8, 'antibody' : 1.1,  'buffer_3' : -1, 'noise_level' : 0.05, 'pump_freq' : 0.23, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_g', 'VCSEL':'VCSEL_2'},

                 ## h
                 '0.01_7' : {'miRNA' : 0.8, 'antibody' : 1.45, 'buffer_3' : -0.7, 'noise_level' : 0.06, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_h', 'VCSEL':'VCSEL_0'},
                 '0.02_7' : {'miRNA' : 0.8,  'antibody' : 2.0, 'buffer_3' : -0.9, 'noise_level' : 0.07, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_h', 'VCSEL':'VCSEL_1'},
                 '0.2_7'  : {'miRNA' : 2.4, 'antibody'  : 8, 'buffer_3' : -1, 'noise_level' : 0.05, 'pump_freq' : 0.23, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_h', 'VCSEL':'VCSEL_2'},

                 ## j
                 '0.2_8'  : {'miRNA' : 2.4, 'antibody' : 7.2, 'buffer_3' : -2.1, 'noise_level' : 0.07, 'pump_freq' : 0.22, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_j', 'VCSEL':'VCSEL_0'},
                 '5.0_8'  : {'miRNA' : 34,  'antibody' : 160,  'buffer_3' : -12, 'noise_level' : 0.06, 'pump_freq' : 0.19, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_j', 'VCSEL':'VCSEL_1'},
                 '10.0_8' : {'miRNA' : 0.1, 'antibody' : 8,    'buffer_3' : -1, 'noise_level' : 0.05, 'pump_freq' : 0.23, 'measurement_folder' : 'spr_measurements_241016', 'exact_measurement' : 'spr_measurements_241016_run_j', 'VCSEL':'VCSEL_2'},
                 }

which_trace = '10.0_8'

def generate_traces(concentration_dict, which_trace):
        
    def sigmoid(a, b, const, x):
        return const/(1 + np.exp(-a*x + b))
    
    time_trace = np.arange(0, full_time, 1)
    noise_level = concentration[which_trace]['noise_level']
    # noise_level = 0.01
    trace_buffer_1 = np.random.normal(0, noise_level, time_buffer_1)
    
    trace_miRNA = np.zeros(time_miRNA)
    miRNA_offset = concentration[which_trace]['miRNA']
    
    saturation_time = 5*60
    if saturated:
        
        a = 0.01
        b = 0
        for i in range(time_miRNA):
            sig_var = i - time_miRNA/2    
            # trace_miRNA[i] = sigmoid(a, b, miRNA_offset, sig_var) + np.random.normal(0, noise_level)
            trace_miRNA[i] = (i - 1)*miRNA_offset/time_miRNA + np.random.normal(0, 2*noise_level)
            
    
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
        
    final_trace = np.concat((trace_buffer_1, trace_miRNA, trace_buffer_2, trace_antibody, trace_buffer_3, trace_buffer_4,))
    
    pump_noise = np.sin(2*np.pi*concentration[which_trace]['pump_freq']*time_trace + (np.random.random() - 0.5)*2*np.pi)*0.1
    
    final_trace = final_trace + pump_noise
    
    for i in range(len(final_trace)):
        random_number = np.random.random()
        if random_number > 0.8:
            final_trace[i] = final_trace[i] + (0.5 - np.random.random())*noise_level*10
        
        if random_number > 0.95:
            rand = (0.5 - np.random.random())*noise_level*10
            
            for j in range(30):
                if i == 0:
                    final_trace[i - j] = final_trace[i - j] + rand*(i - 10)/0.001
                else:
                    final_trace[i - j] = final_trace[i - j] + rand*(i - 10)/i
                
    return (time_trace, final_trace)
    
    
    
from pathlib import Path
import os


for conc in concentration.keys():
    (time_trace, final_trace) = generate_traces(concentration, conc)
    
    measurement_folder = concentration[conc]['measurement_folder']
    file_path = Path(__file__).parent
    save_folder_path = Path(file_path, 'spr_project', 'spr_measurement_data', measurement_folder)
    if not os.path.exists(str(save_folder_path)):
       os.makedirs(str(save_folder_path))
       
    # exact_measurement = 'spr_measurements_240925_run_a'
    exact_measurement = measurement_folder = concentration[conc]['exact_measurement']
    exact_measurement_path = Path(save_folder_path, exact_measurement)
    if not os.path.exists(str(exact_measurement_path)):
        os.makedirs(str(exact_measurement_path))
        
    vcsel_path = Path(exact_measurement_path, concentration[conc]['VCSEL'])
    if not os.path.exists(str(vcsel_path)):
        os.makedirs(str(vcsel_path))
        
    measurement_trace = np.vstack((time_trace.T, final_trace.T)).T
    
    trace_path = Path(exact_measurement_path, concentration[conc]['VCSEL'])

    np.savetxt(str(trace_path) + '//data.txt', measurement_trace, delimiter=',')
       

# plt.plot(time_trace/60, final_trace, '-x', color='black', ms=0.4)

