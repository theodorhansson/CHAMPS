import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pathlib import Path
import numpy as np
from scipy.interpolate import griddata

## Run MPh
import mph

## Constants
PI  = np.pi
MM  = 1e-3
UM  = 1e-6
NM  = 1e-9
MIN = 60
DEG_TO_RAD = PI/180
RAD_TO_DEG = 180/PI

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib import cm
cmap = cm.magma
colors = cmap(np.linspace(0, 1, 10))

colors_bright = colors[1]
colors_med = colors[3]
colors_dark = colors[9]

mpl.rcParams['axes.titlesize']    = 20
mpl.rcParams['axes.labelsize']    = 20
mpl.rcParams['xtick.labelsize']   = 16
mpl.rcParams['ytick.labelsize']   = 16
mpl.rcParams['legend.fontsize']   = 16
mpl.rcParams['lines.markersize']  = 4
mpl.rcParams['axes.spines.top']   = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['grid.alpha']        = 0.3
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.shadow']     = True

#%%

model_filename = 'spr_1d_bsa_pen_depth'
current_folder = Path(__file__)
save_folder_path = Path(current_folder.parents[2], 'comsol_data', model_filename + '_data')

coordinates_filename = Path(save_folder_path, 'coord.txt')
coordinates = np.loadtxt(coordinates_filename)
x = coordinates[0, :]
y = coordinates[1, :]

normE_filename = Path(save_folder_path, 'normE.txt')
normE = np.loadtxt(normE_filename)

Nx = 1000
Ny = 1000
grid_x, grid_y = np.meshgrid(np.linspace(np.min(x), np.max(x), Nx),
                             np.linspace(np.min(y), np.max(y), Ny),
                             indexing='ij')

normE_grid = griddata((x, y), normE, (grid_x, grid_y), method='cubic')

fig, ax = plt.subplots()
plt.imshow(normE_grid.T, extent=[np.min(x), np.max(x), np.min(y), np.max(y)], origin='lower', cmap=cmap)

#%%

y = grid_y[0, :]
E = normE_grid[0, :]

I = np.abs(E)
y = y[0:-1]
I = I[0:-1]
I_norm = I/np.max(I)

y_nm = y/NM

plt.figure(1)
plt.plot(I_norm, y_nm)

#%%

cutout_field_at = 1992
index_cut = np.argmin(np.abs(y_nm - cutout_field_at))

y_nm_start = y_nm[index_cut]

y_nm_cut = y_nm[0:index_cut]
I_norm_cut = I_norm[0:index_cut]

pen_depth_index = np.argmin(np.abs(I_norm_cut - np.exp(-1)))
y_nm_pen_depth = y_nm_cut[pen_depth_index]

pene_depth = np.abs(y_nm_start - y_nm_pen_depth)
print('Calculated pen depth: ' + str(round(pene_depth, 2)) + ' nm')

plt.figure(1)
plt.plot(I_norm_cut, y_nm_cut)
plt.plot(np.array([0, 1]), np.array([y_nm_pen_depth, y_nm_pen_depth]))

plt.xlabel(r'I')
plt.ylabel(r'y')
plt.tight_layout()

