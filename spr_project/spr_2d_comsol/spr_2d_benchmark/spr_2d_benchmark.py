#%%

import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
NM  = 1e-9
MIN = 60
DEG_TO_RAD = PI/180
RAD_TO_DEG = 180/PI
import matplotlib as mpl

from matplotlib import cm
cmap = cm.magma
colors = cmap(np.linspace(0, 1, 10))

colors_bright = colors[1]
colors_med = colors[3]
colors_dark = colors[9]

mpl.rcParams['axes.titlesize'] = 20
mpl.rcParams['axes.labelsize'] = 20
mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16
mpl.rcParams['legend.fontsize'] = 16
mpl.rcParams['lines.markersize'] = 4
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['grid.alpha'] = 0.3
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.shadow'] = True

def R_s(n1, n2, theta):
    return np.abs((n1*np.cos(theta) - n2*np.sqrt(1 - ((n1/n2)*np.sin(theta))**2))/((n1*np.cos(theta) + n2*np.sqrt(1 - ((n1/n2)*np.sin(theta))**2))))**2

def R_p(n1, n2, theta):
    return np.abs((n1*np.sqrt(1 - ((n1/n2)*np.sin(theta))**2) - n2*np.cos(theta))/(n1*np.sqrt(1 - ((n1/n2)*np.sin(theta))**2) + n2*np.cos(theta)))**2

def load_COMSOL_data(save_folder_path, filename, col_data, header):
    
    comsol_data_path = Path(save_folder_path, filename)
    
    data_dict = {}
    for i in range(col_data):
        data_dict['x' + str(i)] = []

    with open(str(comsol_data_path), 'r') as file:
        for i, line in enumerate(file):
            if i > (header - 1):
                line_array = line.split()
                
                for j in range(len(line_array)):
                    data_dict['x' + str(j)].append(float(line_array[j]))
                
                
    for key in data_dict.keys():
        data_dict[key] = np.array(data_dict[key])

    return data_dict

current_folder = Path(__file__)
comsol_data_path = Path(current_folder.parents[2], 'comsol_data', 'spr_2d_comsol_benchmark_data')

#%% Benchmarking s pol with different refractive index at AOI = 15 deg

sim_filename = 'n_1_3.5_s_pol_AOI_15.txt'

col_data = 7
header   = 5
data = load_COMSOL_data(comsol_data_path, sim_filename, col_data, header)

n_sim   = data['x0']
lam0    = data['x1']
Pup     = data['x2']
Pdown   = data['x3']
Pleft   = data['x4']
Pright  = data['x5']
Ptot    = data['x6']

lam0 = 980*NM

P_tot_sim = Pup + Pdown + Pleft + Pright

T_sim = Pdown/P_tot_sim
R_sim = Pup/P_tot_sim

AOI = 15*DEG_TO_RAD
 
n1 = 1
R = R_s(n1, n_sim, AOI)
T = 1 - R

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(n_sim, T_sim, 'b', label=r'$T_{sim}$')
ax[0].plot(n_sim, T, '.', color='black', label=r'$T_{analytical}$')

ax[0].plot(n_sim, R_sim, 'r', label=r'$R_{sim}$')
ax[0].plot(n_sim, R, '.', color='black', label=r'$R_{analytical}$')

ax[0].set_xlabel(r'n')
ax[0].set_ylabel(r'T, R')
ax[0].set_title(r'S-pol $\theta_{in}=15$ deg')

ax[0].legend()

T_error = np.abs(T_sim - T)/T
R_error = np.abs(R_sim - R)/R

ax[1].plot(n_sim[1:-1], np.log10(T_error[1:-1]), 'b', label=r'$e_{T} = \frac{|T_{sim} - T|}{T}$')
ax[1].plot(n_sim[1:-1], np.log10(R_error[1:-1]), 'r', label=r'$e_{R} = \frac{|R_{sim} - R|}{R}$')

ax[1].set_xlabel(r'n')
ax[1].set_ylabel(r'$\log_{10}{(e)}$')
ax[1].set_title(r'Relative error $c_{mesh}= 10$')

ax[1].legend()

plt.tight_layout()


#%% Benchmarking p pol with different refractive index at AOI = 15 deg

sim_filename = 'n_1_3.5_p_pol_AOI_15.txt'

col_data = 7
header   = 5
data = load_COMSOL_data(comsol_data_path, sim_filename, col_data, header)

n_sim   = data['x0']
lam0    = data['x1']
Pup     = data['x2']
Pdown   = data['x3']
Pleft   = data['x4']
Pright  = data['x5']
Ptot    = data['x6']

lam0 = 980*NM

P_tot_sim = Pup + Pdown + Pleft + Pright

T_sim = Pdown/P_tot_sim
R_sim = Pup/P_tot_sim

AOI = 15*DEG_TO_RAD
 
n1 = 1
R = R_p(n1, n_sim, AOI)
T = 1 - R

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(n_sim, T_sim, 'b', label=r'$T_{sim}$')
ax[0].plot(n_sim, T, '.', color='black', label=r'$T_{analytical}$')

ax[0].plot(n_sim, R_sim, 'r', label=r'$R_{sim}$')
ax[0].plot(n_sim, R, '.', color='black', label=r'$R_{analytical}$')

ax[0].set_xlabel(r'n')
ax[0].set_ylabel(r'T, R')
ax[0].set_title(r'P-pol $\theta_{in}=15$ deg')

ax[0].legend()

T_error = np.abs(T_sim - T)/T
R_error = np.abs(R_sim - R)/R

ax[1].plot(n_sim[1:-1], np.log10(T_error[1:-1]), 'b', label=r'$e_{T} = \frac{|T_{sim} - T|}{T}$')
ax[1].plot(n_sim[1:-1], np.log10(R_error[1:-1]), 'r', label=r'$e_{R} = \frac{|R_{sim} - R|}{R}$')

ax[1].set_xlabel(r'n')
ax[1].set_ylabel(r'$\log_{10}{(e)}$')
ax[1].set_title(r'Relative error $c_{mesh}= 10$')

ax[1].legend()

plt.tight_layout()

#%% Benchmarking s pol with different AOI n_s = 2.5

sim_filename = 'AOI_10_80_s_pol_n_2.5.txt'

col_data = 6
header   = 5
data = load_COMSOL_data(comsol_data_path, sim_filename, col_data, header)

theta_rad   = data['x0']
Pup         = data['x1']
Pdown       = data['x2']
Pleft       = data['x3']
Pright      = data['x4']
Ptot        = data['x5']

lam0 = 980*NM

P_tot_sim = Pup + Pdown + Pleft + Pright

T_sim = Pdown/P_tot_sim
R_sim = Pup/P_tot_sim
 
n_glass = 1
n_s     = 2.5
R = R_s(n_glass, n_s, theta_rad)
T = 1 - R

theta_deg = theta_rad*RAD_TO_DEG

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(theta_deg, T_sim, 'b', label=r'$T_{sim}$')
ax[0].plot(theta_deg, T, '.', color='black', label=r'$T_{analytical}$')

ax[0].plot(theta_deg, R_sim, 'r', label=r'$R_{sim}$')
ax[0].plot(theta_deg, R, '.', color='black', label=r'$R_{analytical}$')

ax[0].set_xlabel(r'$\theta_{\text{in}}$ [deg]')
ax[0].set_ylabel(r'T, R')
ax[0].set_title(r'P-pol $n_{s} = 2.5$')

ax[0].legend()

T_error = np.abs(T_sim - T)/T
R_error = np.abs(R_sim - R)/R

ax[1].plot(theta_deg[1:-1], np.log10(T_error[1:-1]), 'b', label=r'$e_{T} = \frac{|T_{sim} - T|}{T}$')
ax[1].plot(theta_deg[1:-1], np.log10(R_error[1:-1]), 'r', label=r'$e_{R} = \frac{|R_{sim} - R|}{R}$')

ax[1].set_xlabel(r'$\theta_{\text{in}}$ [deg]')
ax[1].set_ylabel(r'$\log_{10}{(e)}$')
ax[1].set_title(r'Relative error $c_{mesh}= 10$')

ax[1].legend()

plt.tight_layout()
#%% Benchmarking p pol with different AOI n_s = 2.5

sim_filename = 'AOI_10_80_p_pol_n_2.5.txt'

col_data = 6
header   = 5
data = load_COMSOL_data(comsol_data_path, sim_filename, col_data, header)

theta_rad   = data['x0']
Pup         = data['x1']
Pdown       = data['x2']
Pleft       = data['x3']
Pright      = data['x4']
Ptot        = data['x5']

lam0 = 980*NM

P_tot_sim = Pup + Pdown + Pleft + Pright

T_sim = Pdown/P_tot_sim
R_sim = Pup/P_tot_sim
 
n_glass = 1
n_s     = 2.5
R = R_p(n_glass, n_s, theta_rad)
T = 1 - R

theta_deg = theta_rad*RAD_TO_DEG

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(theta_deg, T_sim, 'b', label=r'$T_{sim}$')
ax[0].plot(theta_deg, T, '.', color='black', label=r'$T_{analytical}$')

ax[0].plot(theta_deg, R_sim, 'r', label=r'$R_{sim}$')
ax[0].plot(theta_deg, R, '.', color='black', label=r'$R_{analytical}$')

ax[0].set_xlabel(r'$\theta_{\text{in}}$ [deg]')
ax[0].set_ylabel(r'T, R')
ax[0].set_title(r'P-pol $n_{s} = 2.5$')

ax[0].legend()

T_error = np.abs(T_sim - T)/T
R_error = np.abs(R_sim - R)/R

ax[1].plot(theta_deg[1:-1], np.log10(T_error[1:-1]), 'b', label=r'$e_{T} = \frac{|T_{sim} - T|}{T}$')
ax[1].plot(theta_deg[1:-1], np.log10(R_error[1:-1]), 'r', label=r'$e_{R} = \frac{|R_{sim} - R|}{R}$')

ax[1].set_xlabel(r'$\theta_{\text{in}}$ [deg]')
ax[1].set_ylabel(r'$\log_{10}{(e)}$')
ax[1].set_title(r'Relative error $c_{mesh}= 10$')

ax[1].legend()

plt.tight_layout()


#%% Benchmarking s pol with different transmittance index at AOI = 25 deg

sim_filename = 'n_glass_1_3.5_s_pol_AOI_25.txt'

col_data = 7
header   = 5
data = load_COMSOL_data(comsol_data_path, sim_filename, col_data, header)

n_glass   = data['x0']
lam0      = data['x1']
Pup       = data['x2']
Pdown     = data['x3']
Pleft     = data['x4']
Pright    = data['x5']
Ptot      = data['x6']

lam0 = 980*NM

P_tot_sim = Pup + Pdown + Pleft - Pright
P_error = np.abs(Ptot - P_tot_sim)/Ptot

T_sim = Pdown/P_tot_sim
R_sim = Pup/P_tot_sim

AOI = 25*DEG_TO_RAD/n_glass ## Division with n_glass is not needed in general. But I forgot to add in COMSOL
 
n2 = 1
R = R_s(n_glass, n2, AOI)
T = 1 - R

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(n_glass, T_sim, 'b', label=r'$T_{sim}$')
ax[0].plot(n_glass, T, '.', color='black', label=r'$T_{analytical}$')

ax[0].plot(n_glass, R_sim, 'r', label=r'$R_{sim}$')
ax[0].plot(n_glass, R, '.', color='black', label=r'$R_{analytical}$')

ax[0].set_xlabel(r'n')
ax[0].set_ylabel(r'T, R')
ax[0].set_title(r'S-pol $\theta_{in}=15$ deg')

ax[0].legend()

T_error = np.abs(T_sim - T)/T
R_error = np.abs(R_sim - R)/R

ax[1].plot(n_glass, np.log10(T_error), 'b', label=r'$e_{T} = \frac{|T_{sim} - T|}{T}$')
ax[1].plot(n_glass, np.log10(R_error), 'r', label=r'$e_{R} = \frac{|R_{sim} - R|}{R}$')

ax[1].set_xlabel(r'n')
ax[1].set_ylabel(r'$\log_{10}{(e)}$')
ax[1].set_title(r'Relative error $c_{mesh}= 10$')

ax[1].legend()

plt.tight_layout()


#%% Benchmarking p pol with different transmittance index at AOI = 15 deg

sim_filename = 'n_glass_1_3.5_p_pol_AOI_25.txt'

col_data = 7
header   = 5
data = load_COMSOL_data(comsol_data_path, sim_filename, col_data, header)

n_glass   = data['x0']
lam0      = data['x1']
Pup       = data['x2']
Pdown     = data['x3']
Pleft     = data['x4']
Pright    = data['x5']
Ptot      = data['x6']

lam0 = 980*NM

P_tot_sim = Pup + Pdown + Pleft - Pright
P_error = np.abs(Ptot - P_tot_sim)/Ptot

T_sim = Pdown/P_tot_sim
R_sim = Pup/P_tot_sim

AOI = 25*DEG_TO_RAD 
 
n2 = 1
R = R_p(n_glass, n2, AOI)
T = 1 - R

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(n_glass, T_sim, 'b', label=r'$T_{sim}$')
ax[0].plot(n_glass, T, '.', color='black', label=r'$T_{analytical}$')

ax[0].plot(n_glass, R_sim, 'r', label=r'$R_{sim}$')
ax[0].plot(n_glass, R, '.', color='black', label=r'$R_{analytical}$')

ax[0].set_xlabel(r'n')
ax[0].set_ylabel(r'T, R')
ax[0].set_title(r'S-pol $\theta_{in}=15$ deg')

ax[0].legend()

T_error = np.abs(T_sim - T)/T
R_error = np.abs(R_sim - R)/R

ax[1].plot(n_glass, np.log10(T_error), 'b', label=r'$e_{T} = \frac{|T_{sim} - T|}{T}$')
ax[1].plot(n_glass, np.log10(R_error), 'r', label=r'$e_{R} = \frac{|R_{sim} - R|}{R}$')

ax[1].set_xlabel(r'n')
ax[1].set_ylabel(r'$\log_{10}{(e)}$')
ax[1].set_title(r'Relative error $c_{mesh}= 10$')

ax[1].legend()

plt.tight_layout()

