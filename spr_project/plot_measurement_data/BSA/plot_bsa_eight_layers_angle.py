#%%
import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, butterworth
from spr_project.spr_calculations.spr_sensing import n_spr, theta_spr, x_spr_detector, n_glycerol, pen_depth
# from spr_project.spr_calculations.sensor_setup import plot_sensor_setup

### Defiinitions
PI = np.pi
DEG_TO_RAD = PI/180
RAD_TO_DEG = 180/PI
theta = np.arange(0,90,0.1)*DEG_TO_RAD
MM = 1e-3
UM = 1e-6
NM = 1e-9

### Plot arguments
fontsize_title  = 18
fontsize_label  = 16
fontsize_ticks  = 14
figure_width    = 10
figure_height   = 8
fontsize_legend = 12

## Parameters
lam0   = 984*NM
eps_Au = -40.650+ 1j*2.2254

## Molecular weight of BSA 66.5 kDa
## Molecular weight of DS  5 - 2000 kDa 
## Load all data
spr_data_folder = 'spr_measurements_231212'
parent_path = Path(__file__).resolve().parents[2]
measurement_path = Path(parent_path, 'spr_measurement_data', spr_data_folder)

vcsels = ['VCSEL_0', 'VCSEL_1', 'VCSEL_2', 'VCSEL_3', 'VCSEL_4','VCSEL_5']
filename = 'data'

## Names of measurement segments
names = os.listdir(measurement_path)

## Remove reference spectrum
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
        

def theta_spr(eps_metal, n_glass, n_analyte):
    sin_theta_spr = (1/n_glass)*np.sqrt((np.abs(eps_metal)*n_analyte**2)/(np.abs(eps_metal) - n_analyte**2))
    theta_spr = np.arcsin(sin_theta_spr)
    return theta_spr

def n_spr(eps_Au, n_prism, theta_spr):
    param = np.sin(theta_spr*np.pi/180)
    eps_analyte = (np.abs(eps_Au)*n_prism**2*param**2 )/(np.abs(eps_Au) + n_prism**2*param**2)
    return np.sqrt(eps_analyte)

def x_spr_detector(theta_spr, glass_thickness):
    return 2*glass_thickness*np.tan(theta_spr)

def spr_ang(x, glass_thickness):
    return np.arctan(x/(2*glass_thickness))

## Figure object
fig = plt.figure(figsize=(14,8))
ax1 = fig.add_subplot(221)

n_glass = 1.51
n_water = 1.34
glass_thickness = 1.4*MM
water_SPR = theta_spr(eps_Au, n_glass, n_water)
water_SPR_deg = water_SPR*180/PI
water_SPR_pos = x_spr_detector(water_SPR, glass_thickness)
water_SPR_pos_UM = water_SPR_pos*1e6


start_bubble = 1360
stopp_bubble = 1380
remove = np.arange(start_bubble, stopp_bubble, 1)


time_scale = 60
time_trace_1 = plot_data['VCSEL_0'][0, :]/time_scale
time_trace_2 = plot_data['VCSEL_1'][0, :]/time_scale
time_trace_3 = plot_data['VCSEL_3'][0, :]/time_scale

time_trace_offset_1 = time_trace_1[stopp_bubble] - time_trace_1[start_bubble]
time_trace_offset_2 = time_trace_2[stopp_bubble] - time_trace_2[start_bubble]
time_trace_offset_3 = time_trace_3[stopp_bubble] - time_trace_3[start_bubble]

raw_vcsel_1 = plot_data['VCSEL_0'][1, :]
raw_vcsel_2 = plot_data['VCSEL_1'][1, :]
raw_vcsel_3 = plot_data['VCSEL_3'][1, :]

time_trace_1 = np.delete(time_trace_1, remove)
time_trace_2 = np.delete(time_trace_2, remove)
time_trace_3 = np.delete(time_trace_3, remove)

time_trace_1[start_bubble:-1] = time_trace_1[start_bubble:-1] - time_trace_offset_1
time_trace_2[start_bubble:-1] = time_trace_2[start_bubble:-1] - time_trace_offset_2
time_trace_3[start_bubble:-1] = time_trace_3[start_bubble:-1] - time_trace_offset_3

raw_vcsel_1 = np.delete(raw_vcsel_1, remove) 
raw_vcsel_2 = np.delete(raw_vcsel_2, remove)
raw_vcsel_3 = np.delete(raw_vcsel_3, remove)

cut_off = 1/50
butter_vcsel_1 = butterworth(raw_vcsel_1, cut_off)
butter_vcsel_2 = butterworth(raw_vcsel_2, cut_off)
butter_vcsel_3 = butterworth(raw_vcsel_3, cut_off)

print('Initial SPR angle in water: ' + str(round(water_SPR_deg, 2)))

butter_1_from_water = butter_vcsel_1 + water_SPR_pos_UM
butter_2_from_water = butter_vcsel_2 + water_SPR_pos_UM
butter_3_from_water = butter_vcsel_3 + water_SPR_pos_UM

butter_1_theta = np.arctan(butter_1_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
butter_2_theta = np.arctan(butter_2_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg
butter_3_theta = np.arctan(butter_3_from_water*1e-6/(2*glass_thickness))*180/PI - water_SPR_deg

## Plot raw data
marker_size = 0.1
marker_type = 'x'
marker_color  = 'black'
linewidth_raw = 0.2
# ax1.plot(time_trace_1, raw_vcsel_1, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
# ax1.plot(time_trace_2, raw_vcsel_2, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
# ax1.plot(time_trace_3, raw_vcsel_3, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)

linewidth_filtered = 0.5
ax1.plot(time_trace_1, butter_1_theta, color='blue', label=r'Channel 1', linewidth=linewidth_filtered)
ax1.plot(time_trace_2, butter_2_theta, color='red', label=r'Channel 2', linewidth=linewidth_filtered)
ax1.plot(time_trace_3, butter_3_theta, color='green', label=r'Channel 3', linewidth=linewidth_filtered)

ax1.grid(linewidth=1, alpha=0.3)
ax1.set_xlabel(r'Time [min]')
ax1.set_ylabel(r'Sensor response [$^\circ$]')
ax1.set_title(r'BSA-DS cake')

ax1.legend()


### --------------------- One layer --------------------- ###
one_layer_index = np.arange(1740, 2010, 1)


one_layer_trace_1 = time_trace_1[one_layer_index]
one_layer_trace_2 = time_trace_1[one_layer_index]
one_layer_trace_3 = time_trace_1[one_layer_index]

one_butter_vcsel_1 = butter_1_theta[one_layer_index]
one_butter_vcsel_2 = butter_2_theta[one_layer_index] - 0.025
one_butter_vcsel_3 = butter_3_theta[one_layer_index]


ax3 = fig.add_subplot(223)
linewidth_filtered = 1
ax3.plot(one_layer_trace_1, one_butter_vcsel_1, color='blue', label=r'High miRNA conc.', linewidth=linewidth_filtered)
ax3.plot(one_layer_trace_2, one_butter_vcsel_2, color='red', label=r'Low miRNA conc.', linewidth=linewidth_filtered)
ax3.plot(one_layer_trace_3, one_butter_vcsel_3, color='green', label=r'DNA Reference', linewidth=linewidth_filtered)
ax3.grid(linewidth=1, alpha=0.3)

ax3.set_xlabel(r'Time [min]')
ax3.set_ylabel(r'Sensor response [$^\circ$]')
ax3.set_title(r'Layer 7')

sav_gol_window = 12
sav_gol_order = 2


x_layers = np.array([frame_time[0], frame_time[-1]/60])

time_index_2 = 600
time_index_3 = 820
time_index_4 = 1100
time_index_5 = 1200
time_index_6 = 1400
time_index_7 = 1600
time_index_8 = 1900
time_index_9 = 2100

y_layers = np.array([
                     butter_1_theta[time_index_2], butter_2_theta[time_index_2], butter_3_theta[time_index_2],
                     butter_1_theta[time_index_3], butter_2_theta[time_index_3], butter_3_theta[time_index_3],
                     butter_1_theta[time_index_4], butter_2_theta[time_index_4], butter_3_theta[time_index_4],
                     butter_1_theta[time_index_6], butter_2_theta[time_index_6], butter_3_theta[time_index_6],
                     butter_1_theta[time_index_7], butter_2_theta[time_index_7], butter_3_theta[time_index_7],
                     butter_1_theta[time_index_8], butter_2_theta[time_index_8], butter_3_theta[time_index_8],
                     butter_1_theta[time_index_9], butter_2_theta[time_index_9], butter_3_theta[time_index_9]])


for i in range(len(y_layers)):
    ax1.plot(np.array([x_layers[0], x_layers[1]]), np.array([y_layers[i], y_layers[i]]), '--', color='gray', linewidth=0.5)



y_layers[0]  = y_layers[0]  - butter_1_theta[time_index_2]
y_layers[3]  = y_layers[3]  - butter_1_theta[time_index_2]
y_layers[6]  = y_layers[6]  - butter_1_theta[time_index_2]
y_layers[9]  = y_layers[9]  - butter_1_theta[time_index_2]
y_layers[12] = y_layers[12] - butter_1_theta[time_index_2]
y_layers[15] = y_layers[15] - butter_1_theta[time_index_2]
y_layers[18] = y_layers[18] - butter_1_theta[time_index_2]

y_layers[1]  = y_layers[1]  - butter_2_theta[time_index_2]
y_layers[4]  = y_layers[4]  - butter_2_theta[time_index_2]
y_layers[7]  = y_layers[7]  - butter_2_theta[time_index_2]
y_layers[10] = y_layers[10] - butter_2_theta[time_index_2]
y_layers[13] = y_layers[13] - butter_2_theta[time_index_2]
y_layers[16] = y_layers[16] - butter_2_theta[time_index_2]
y_layers[19] = y_layers[19] - butter_2_theta[time_index_2]

y_layers[2]  = y_layers[2]  - butter_3_theta[time_index_2]
y_layers[5]  = y_layers[5]  - butter_2_theta[time_index_2]
y_layers[8]  = y_layers[8]  - butter_2_theta[time_index_2]
y_layers[11] = y_layers[11] - butter_2_theta[time_index_2]
y_layers[14] = y_layers[14] - butter_2_theta[time_index_2]
y_layers[17] = y_layers[17] - butter_2_theta[time_index_2]
y_layers[20] = y_layers[20] - butter_2_theta[time_index_2]

one_layer_thickness = 50
layer_thickness = np.array([1*one_layer_thickness, 1*one_layer_thickness, 1*one_layer_thickness,
                            2*one_layer_thickness, 2*one_layer_thickness, 2*one_layer_thickness,
                            3*one_layer_thickness, 3*one_layer_thickness, 3*one_layer_thickness,
                            4*one_layer_thickness, 4*one_layer_thickness, 4*one_layer_thickness,
                            5*one_layer_thickness, 5*one_layer_thickness, 5*one_layer_thickness,
                            6*one_layer_thickness, 6*one_layer_thickness, 6*one_layer_thickness,
                            7*one_layer_thickness, 7*one_layer_thickness, 7*one_layer_thickness,])


ax2 = fig.add_subplot(122)
y_layers_thickness = (np.arange(8) + 1)*5
y_one_layers_thickness = 5
y_layers_thickness = np.array([1*y_one_layers_thickness, 1*y_one_layers_thickness, 1*y_one_layers_thickness,
                               2*y_one_layers_thickness, 2*y_one_layers_thickness, 2*y_one_layers_thickness,
                               3*y_one_layers_thickness, 3*y_one_layers_thickness, 3*y_one_layers_thickness,
                               4*y_one_layers_thickness, 4*y_one_layers_thickness, 4*y_one_layers_thickness,
                               5*y_one_layers_thickness, 5*y_one_layers_thickness, 5*y_one_layers_thickness,
                               6*y_one_layers_thickness, 6*y_one_layers_thickness, 6*y_one_layers_thickness,
                               7*y_one_layers_thickness, 7*y_one_layers_thickness, 7*y_one_layers_thickness]) 


ax2.plot(y_layers_thickness, y_layers, 'x', color='black', label=r'Measurement data')
ax2.grid(linewidth=1, alpha=0.3)

ax2.set_xlabel(r'BSA Layer thickness [nm]')
ax2.set_ylabel(r'Sensor response [$^\circ$]')
ax2.set_title(r'Shift as a function of layer thickness')
ax2.legend()


lam0    = 984e-9
n_glass = 1.51
glass_thickness = 1.4*MM
refractive_index = np.arange(1.33, 1.450, 0.000001)

resonant_angles = theta_spr(eps_Au, n_glass, refractive_index) 
resonant_pos    = x_spr_detector(resonant_angles, glass_thickness)

detector_positions = x_spr_detector(resonant_angles, glass_thickness) - x_spr_detector(resonant_angles[0], glass_thickness)
dpos_dref          = np.gradient(detector_positions, refractive_index)   
dpos_dpos          = np.gradient(detector_positions, resonant_pos) 


# Refractive index of proteins
n_BSA = 1.38

# Refractive index of water
n_water = 1.335

# Initial Bulk sensitivity
S = dpos_dref[np.where(np.abs(refractive_index - n_water) < 0.0000005)][0]

# Thickness of a single protein layer
d = 5*NM

# How many layers to calculate for
# m = np.arange(7) + 1
m = np.arange(0, 7, 0.01) + 1

# Initialize shift and effective refractive index arrays
dx = np.zeros_like(m, dtype=float)
neff = np.zeros_like(m, dtype=float)

# SPR Angle for water
spr_water = theta_spr(eps_Au, n_glass, n_water) 

# Intial penetration depth
pen_depth_BSA = pen_depth(lam0, n_glass, n_water, resonant_angles[0])

# For each layer
for i, mm in  enumerate(m):  
    # Calculate the **effective** refractive index within the field
    neff[i] = n_BSA + (n_water - n_BSA)*np.exp(-2*d*mm/pen_depth_BSA)
    
    # Calculate the new SPR angle with this new refractive index
    spr_BSA = theta_spr(eps_Au, n_glass, neff[i])
    
    # Calculate the new penetration depth with the new angle
    pen_depth_BSA = pen_depth(lam0, n_glass, neff[i], spr_BSA)
    pen_depth_BSA = pen_depth_BSA - 70e-9
    
    ## Calculate the new bulk sensitivity for this refractive index
    S = dpos_dref[np.where(np.abs(refractive_index - neff[i]) < 0.0000005)][0]
    
    ## 
    S_surface = S*(1 - np.exp(-2*d*(mm - 1)/pen_depth_BSA))
    # print(1 - np.exp(-2*d*(mm - 1)/pen_depth_BSA))
    
    dx[i] = S*(n_BSA - n_water)*(1 - np.exp(-2*d*(mm - 1)/pen_depth_BSA))*neff[i]


dx = dx 
dx[0] = dx[0] 
dtheta = np.arctan(dx/(2*glass_thickness))*180/PI
dtheta = dtheta

dy_dx = np.gradient(dx, m)    
ax2.plot(m*d/NM, dtheta, label='Fitted analytical sensitivity') 

ax2.legend()
plt.tight_layout()

#%%

first_d_x = m[0:-1]*d/NM
first_d = np.diff(dtheta)


plt.plot(first_d_x, first_d)




# image_name = 'all_BSA.svg'
# image_format = 'svg'
# plt.savefig(image_name, format=image_format, dpi=600)

#%%


std_array = np.arange(0, 50, 1)
spr_data_std  = np.std(butter_vcsel_1[std_array], ddof=1)
delta_n_pump_on = spr_data_std/20348
print()
print(f'------ Delta n with pump on: {np.round(delta_n_pump_on, 7)} ------')
print()


#%%

plt.figure(1)
# plt.plot(y_layers_thickness, y_layers, 'x', color='black', label=r'Measurement data')
plt.scatter(y_layers_thickness, y_layers, s=40, facecolors='none', edgecolors='black')
# ax2.plot(layer_thickness, exp_fit(layer_thickness, *popt), 'r-', label='Exponential fit')
plt.grid(linewidth=1, alpha=0.3)

plt.xlabel(r'BSA Layer thickness [nm]')
plt.ylabel(r'Sensor response [$\mu$m]')
# plt.title(r'Shift as a function of layer thickness')
plt.plot(m*d, dx, label='Fitted analytical sensitivity') 

image_name = 'exponential_fit.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)

#%%

plt.figure(1)
marker_size = 0.1
marker_type = 'x'
marker_color  = 'black'
linewidth_raw = 0.2
# plt.plot(time_trace_1, raw_vcsel_1, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
# plt.plot(time_trace_2, raw_vcsel_2, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
# plt.plot(time_trace_3, raw_vcsel_3, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)

n_water = 1.41
water_SPR = theta_spr(eps_Au, n_glass, n_water)
water_SPR_deg = water_SPR*180/PI
water_SPR_pos = x_spr_detector(water_SPR, glass_thickness)
water_SPR_pos_UM = water_SPR_pos*1e6

print('Initial SPR angle in water: ' + str(round(water_SPR_deg, 2)))

butter_1_from_water = butter_vcsel_1 + water_SPR_pos_UM
butter_2_from_water = butter_vcsel_2 + water_SPR_pos_UM
butter_3_from_water = butter_vcsel_3 + water_SPR_pos_UM

butter_1_theta = np.arctan(butter_1_from_water*1e-6/(2*glass_thickness))*180/PI
butter_2_theta = np.arctan(butter_2_from_water*1e-6/(2*glass_thickness))*180/PI 
butter_3_theta = np.arctan(butter_3_from_water*1e-6/(2*glass_thickness))*180/PI

linewidth_filtered = 0.5
plt.plot(time_trace_1, butter_1_theta, color='blue', label=r'Channel 1', linewidth=linewidth_filtered)
plt.plot(time_trace_2, butter_2_theta, color='red', label=r'Channel 2', linewidth=linewidth_filtered)
plt.plot(time_trace_3, butter_3_theta, color='green', label=r'Channel 3', linewidth=linewidth_filtered)

plt.grid(linewidth=1, alpha=0.3)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [deg]')


#%%

plt.figure(2)

linewidth_filtered = 0.5
plt.plot(time_trace_1, butter_vcsel_1, color='blue', label=r'Channel 1', linewidth=linewidth_filtered)
plt.plot(time_trace_2, butter_vcsel_2, color='red', label=r'Channel 2', linewidth=linewidth_filtered)
plt.plot(time_trace_3, butter_vcsel_3, color='green', label=r'Channel 3', linewidth=linewidth_filtered)

plt.grid(linewidth=1, alpha=0.3)
plt.xlabel(r'Time [min]')
plt.ylabel(r'SPR shift [deg]')


#%%




image_name = 'BSA_eight_layers.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)


#%%

plt.figure(1)

plt.plot(one_layer_trace_1, one_raw_vcsel_1, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.plot(one_layer_trace_2, one_raw_vcsel_2, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)
plt.plot(one_layer_trace_3, one_raw_vcsel_3, marker_type, color=marker_color, ms=marker_size, linewidth=linewidth_raw)

linewidth_filtered = 1
plt.plot(one_layer_trace_1, one_butter_vcsel_1, color='blue', label=r'Channel 1', linewidth=linewidth_filtered)
plt.plot(one_layer_trace_2, one_butter_vcsel_2, color='red', label=r'Channel 2', linewidth=linewidth_filtered)
plt.plot(one_layer_trace_3, one_butter_vcsel_3, color='green', label=r'Channel 3', linewidth=linewidth_filtered)
plt.grid(linewidth=1, alpha=0.3)

plt.xlabel(r'Time [min]')
plt.ylabel(r'Sensor response [$\mu$m]')
# plt.title(r'Layer 7')


plt.legend()
plt.tight_layout()
 
image_name = 'layer_7.svg'
image_format = 'svg'
plt.savefig(image_name, format=image_format, dpi=600)


