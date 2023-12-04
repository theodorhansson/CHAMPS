#%%
from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter

parent_path = Path(__file__).resolve().parents[1]
measurement = 'camera_ipv_231204'
measurement_path = Path(parent_path, measurement)

IPV_made = os.listdir(measurement_path)
what_IPV = 6
choosen_IPV_path = Path(measurement_path, IPV_made[what_IPV])

print('Loading data for: ' + IPV_made[what_IPV])

Ib = np.loadtxt(Path(choosen_IPV_path, 'Ib_mA.txt'))
Vb = np.loadtxt(Path(choosen_IPV_path, 'Vb.txt'))
Popt = np.loadtxt(Path(choosen_IPV_path, 'Popt.txt'))

I_th_index = 27
Popt_start = Popt[I_th_index + 1]
for i in range(len(Popt)):
    if i < I_th_index:
        Popt[i] = 0
    else:
        Popt[i] = Popt[i] - Popt_start
        


Vb[0] = 0

# smooth_start = 60
# smooth_stopp = -1

# Vb[smooth_start:smooth_stopp] = savgol_filter(Vb[smooth_start:smooth_stopp], 40, 1) # window size 51, polynomial order 3

start = 0
stopp = -2

Ib = Ib[start:stopp]
Vb = Vb[start:stopp]
Popt = Popt[start:stopp]

fig, ax1 = plt.subplots() 
ax1.set_xlabel(r'$I_b$ [mA]') 
ax1.set_ylabel(r'$P_{opt}$ [-]') 
ax1.plot(Ib, Popt, 'black')
ax1.grid(True)

ax2 = ax1.twinx() 
ax2.set_ylabel(r'$V_b$ [V]') 
ax2.plot(Ib, Vb, 'red')


plt.title('IPV glued VCSEL')


