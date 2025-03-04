#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import re

from scipy.optimize import curve_fit
from scipy.signal import butter, filtfilt, freqz
from scipy.interpolate import splrep, BSpline, splev

from spr_project.plot_measurement_data.spr_plot_functions import load_measurement_data, plot_single_trace, plot_all_traces, savgol
from spr_project.spr_calculations.spr_sensing import bulk_sensitivity

## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
MIN = 60
import matplotlib as mpl

from matplotlib import cm
cmap = cm.magma
colors = cmap(np.linspace(0, 1, 10))

colors_bright = colors[1]
colors_med = colors[3]
colors_dark = colors[9]

mpl.rcParams['axes.titlesize'] = 24 
mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['xtick.labelsize'] = 18
mpl.rcParams['ytick.labelsize'] = 18
mpl.rcParams['legend.fontsize'] = 18
mpl.rcParams['lines.markersize'] = 4
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['grid.alpha'] = 0.3
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.shadow'] = True

#%%

def theta_spr(eps_metal, n_glass, n_analyte):
    sin_theta_spr = (1/n_glass)*np.sqrt((np.abs(eps_metal)*n_analyte**2)/(np.abs(eps_metal) - n_analyte**2))
    theta_spr = np.arcsin(sin_theta_spr)
    return theta_spr

def x_spr_detector(theta_spr, glass_thickness):
    return 2*glass_thickness*np.tan(theta_spr)

def bulk_sensitivity(refractive_index, n_glass, glass_thickness):
    n_water = 1.33
    n_highest_possible = 1.45
    refractive_index_array = np.arange(n_water, n_highest_possible, 0.000001)

    resonant_angles = theta_spr(eps_Au, n_glass, refractive_index_array) 
    
    detector_positions = x_spr_detector(resonant_angles, glass_thickness) - x_spr_detector(resonant_angles[0], glass_thickness)
    dpos_dref          = np.gradient(detector_positions, refractive_index_array) 
    
    return dpos_dref[np.where(abs(refractive_index_array - n_water) < 0.0000005)][0]

eps_Au = -40.650+ 1j*2.2254

# n = np.sqrt((np.abs(eps_Au) + np.real(eps_Au))/2)
# k = np.sqrt((np.abs(eps_Au) - np.real(eps_Au))/2)

# print(n, k)

lam0    = 984e-9
n_glass = 1.51
glass_thickness = 1.4*MM
refractive_index = np.arange(1.33, 1.450, 0.000001)

resonant_angles = theta_spr(eps_Au, n_glass, refractive_index) 

detector_positions = x_spr_detector(resonant_angles, glass_thickness) - x_spr_detector(resonant_angles[0], glass_thickness)
dpos_dref          = np.gradient(detector_positions, refractive_index)   


current_folder = Path(__file__)
comsol_data = Path(current_folder.parents[1], 'comsol_data', 'spr_1d_comsol', 'SPR_angle_n_dc_135_n_bsa_142.txt')

in_rad = []
h_bsa = []
R = []

with open(str(comsol_data), 'r') as file:
    for i, line in enumerate(file):
        if i > 4:
            line_array = line.split()
            in_rad.append(float(line_array[0]))
            h_bsa.append(float(line_array[1]))
            R.append(float(line_array[3]))

water_spr_rad = 1.121095417373438

unique_in_rad = np.unique(in_rad)
unique_in_deg = unique_in_rad*180/PI - 66.7
# unique_in_deg = unique_in_rad
unique_h_bsa  = np.unique(h_bsa)
R_matrix = np.zeros(shape=(len(unique_h_bsa), len(unique_in_rad)))

for j in range(len(unique_in_rad)):
    for i in range(len(unique_h_bsa)):
        R_matrix[i, j] = R[j*len(unique_h_bsa) + i]

unique_in_deg = unique_in_deg
R_matrix = R_matrix.T
extent = np.array([unique_h_bsa.min(), unique_h_bsa.max(), unique_in_deg.min(), unique_in_deg.max()])
# plt.imshow(R_matrix, origin='lower', aspect='auto', cmap=cmap, interpolation='spline36', extent=extent)
plt.imshow(R_matrix, origin='lower', aspect='auto', cmap=cmap, extent=extent)

plt.ylabel(r'Sensor response [$^\circ$]')
plt.xlabel(r'$h_{BSA}$ [nm]')

plt.xlim([0, 35])

plt.tight_layout()

# plt.savefig('exp_surface_sensing.png', format='png', dpi=600)

#%%


minimums = np.zeros(len(unique_h_bsa))
for i in np.array([0, 10, 20, 40, 50]):
# for i in np.array([0, 2]):
    # minimums[i] = unique_in_deg[np.argmin(R_matrix[i, :])]
    plt.plot(unique_in_deg, R_matrix[:, i], label=r'$h_{BSA}$ ' + str(round(unique_h_bsa[i] - 1)) + ' nm')


# for i in np.array([0, 2]):
#     minimums[i] = unique_in_deg[np.argmin(R_matrix[:, i])]
#     plt.plot(unique_in_deg - 61, R_matrix[:, i], label=r'$h_{BSA}$ ' + str(round(unique_h_bsa[i] - 1)) + ' nm')

# plt.xlim([63, 70])


xnew = np.linspace(unique_h_bsa.min(), unique_h_bsa.max(), 100) 
tck = splrep(unique_h_bsa, minimums, s=0)
spline = BSpline(*tck)(xnew)

diff = np.diff(spline)

# plt.plot(unique_h_bsa, minimums)
# plt.plot(xnew[:-1], diff)

plt.ylabel(r'Reflectance')
plt.xlabel(r'SPR shift [$^\circ$]')
plt.legend()
plt.grid(linewidth=1, alpha=0.3)
plt.tight_layout()

plt.savefig('resonance_shift_paper.svg', format='svg', dpi=600)
# plt.savefig('resonance_shift_BSA_thesis.svg', format='svg', dpi=600)


#%%

def exp_func(x, a, b, c):
    return a*np.exp(b*x) + c

minimums = np.zeros(len(unique_h_bsa))
for i in range(len(minimums)):
    minimums[i] = unique_sensor_response[np.argmin(R_matrix[:, i])]
    
popt, pcov = curve_fit(exp_func, unique_h_bsa, minimums, p0=[1, 0.2, 100])
xnew = np.linspace(unique_h_bsa.min(), unique_h_bsa.max(), 1000) 

fitted_func = exp_func(xnew, *popt)

plt.plot(unique_h_bsa, minimums, 'x', color='black',label=r'Reflectance minimum')
plt.plot(xnew, exp_func(xnew, *popt), 'r', label=r'Exponential fit')

plt.xlabel(r'$h_{BSA}$ [nm]')
plt.ylabel(r'Sensor response [$\mu$m]')
plt.legend()
plt.grid(linewidth=1, alpha=0.3)
plt.tight_layout()

plt.savefig('exponetial_growth_with_BSA_height.png', format='png', dpi=600)

#%%

diff_x_new = xnew[:-1]
diff_sens = np.diff(fitted_func)
plt.plot(diff_x_new, diff_sens, 'black', label=r'$\frac{dx}{dh_{BSA}}$')

plt.xlabel(r'$h_{BSA}$ [nm]')
plt.ylabel(r'Sensor response increase [$\mu$m/$h_{BSA}$]')
plt.legend()
plt.grid(linewidth=1, alpha=0.3)
plt.tight_layout()




#%%

save_R = np.savetxt('sim_SPR', R_matrix[:, 4])