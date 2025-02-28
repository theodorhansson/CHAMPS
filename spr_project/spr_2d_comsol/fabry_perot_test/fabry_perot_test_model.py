import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pathlib import Path
import numpy as np

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


#%%

client = mph.start()

model_filename = 'fabry_perot_test'
current_folder = Path(__file__)
comsol_model_path = Path(current_folder.parents[2], 'spr_project', 'comsol_models', model_filename + '.mph')
save_folder_path = Path(current_folder.parents[2], 'spr_project', 'comsol_data', model_filename + '_data')

model = client.load(str(comsol_model_path))
print('-------- Loaded model: ' + str(model) + ' --------')

#%%
dataset_names = model.datasets()
chosen_set    = dataset_names[0]

S11 = model.evaluate('ewfd.S11', dataset=chosen_set)
S21 = model.evaluate('ewfd.S21', dataset=chosen_set)

R   = np.abs(S11)**2
T   = np.abs(S21)**2

#%%

(x, y, E) = model.evaluate(['x', 'y', 'ewfd.normE'])

coordinates = np.stack([x, y])
coordinates_filename = Path(save_folder_path, 'coord.txt')
np.savetxt(coordinates_filename, coordinates)

E_field_filename = Path(save_folder_path, 'E_field.txt')
np.savetxt(E_field_filename, E)





