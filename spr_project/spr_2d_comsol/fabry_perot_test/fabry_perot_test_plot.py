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


#%%

model_filename = 'fabry_perot_test'
current_folder = Path(__file__)
save_folder_path = Path(current_folder.parents[2], 'spr_project', 'comsol_data', model_filename + '_data')

coordinates_filename = Path(save_folder_path, 'coord.txt')
coordinates = np.loadtxt(coordinates_filename)
x = coordinates[0, :]
y = coordinates[1, :]

# X, Y = np.meshgrid(x, y)

E_field_filename = Path(save_folder_path, 'E_field.txt')
E_field = np.loadtxt(E_field_filename)

Nx = 1000
Ny = 1000
grid_x, grid_y = np.meshgrid(np.linspace(np.min(x), np.max(x), Nx),
                             np.linspace(np.min(y), np.max(y), Ny),
                             indexing='ij')

grid_z0 = griddata((x, y), E_field, (grid_x, grid_y), method='cubic')

fig, ax = plt.subplots()
plt.imshow(grid_z0.T, origin='lower', cmap=cmap)

#%%

y_cs = grid_y[0, :]
grid_z0 = grid_z0[0, :]

plt.plot(grid_z0, y_cs)

