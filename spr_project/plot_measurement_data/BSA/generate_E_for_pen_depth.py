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

model_filename = 'spr_1d_bsa_pen_depth'
current_folder = Path(__file__)
comsol_model_path = Path(current_folder.parents[2], 'comsol_models', model_filename + '.mph')
save_folder_path = Path(current_folder.parents[2], 'comsol_data', model_filename + '_data')

model = client.load(str(comsol_model_path))
print('-------- Loaded model: ' + str(model) + ' --------')

#%%
dataset_names = model.datasets()
chosen_set    = dataset_names[0]

(x, y, normE) = model.evaluate(['x', 'y', 'ewfd.normE'], dataset=chosen_set)


#%%

coordinates = np.stack([x, y])
coordinates_filename = Path(save_folder_path, 'coord.txt')
np.savetxt(coordinates_filename, coordinates)

normE_filename = Path(save_folder_path, 'normE.txt')
np.savetxt(normE_filename, normE)


#%%



#%%sim_filename = 'n_1_3.5_s_pol_AOI_15.txt'

# if __name__ == "__main__":
    
#     model_filename = '2d_SPR_benchmark_R_and_T.mph'
#     current_folder = Path(__file__)
#     comsol_model_path = Path(current_folder.parents[2], 'spr_project', 'comsol_models', model_filename)
    
#     def run_comsol():
#         client = mph.start()
        
#         model = client.load(str(comsol_model_path))
#         print(model)
#         # dataset_names = model.datasets()
#         # chosen_set = dataset_names[4]
    
#         # x = np.array(model.evaluate('x', dataset=chosen_set))
#         # y = np.array(model.evaluate('y', dataset=chosen_set))
#         # E_field = np.array(model.evaluate('ewfd.normE', dataset=chosen_set))
        
#         x = 0
#         y = 0 
#         E_field = 0
        
#         return x, y, E_field
    
#     result_queue = multiprocessing.Queue()
    
#     with multiprocessing.Pool(1) as pool:
#         pool.apply_async(run_comsol, (result_queue,))
#         pool.close()
#         pool.join()
        
        
#     x, y, E_field = result_queue.get()
#     print(x)

#     x, y, E_field = pool.apply(run_comsol)


# plt.scatter(x, y, c=np.abs(E_field), cmap="inferno", marker="s")
# plt.colorbar(label="Electric Field Magnitude")
# plt.show()





# #%%sim_filename = 'n_1_3.5_s_pol_AOI_15.txt'

# model_filename = '2d_SPR_benchmark_AOI.mph'
# current_folder = Path(__file__)
# comsol_model_path = Path(current_folder.parents[2], 'spr_project', 'comsol_models', model_filename)

# def run_comsol():
#     client = mph.start()
    
#     model = client.load(str(comsol_model_path))
#     dataset_names = model.datasets()
#     chosen_set = dataset_names[4]

#     x = np.array(model.evaluate('x', dataset=chosen_set))
#     y = np.array(model.evaluate('y', dataset=chosen_set))
#     E_field = np.array(model.evaluate('ewfd.normE', dataset=chosen_set))
    
#     return x, y, E_field

# with multiprocessing.Pool(1) as pool:
#     x, y, E_field = pool.apply(run_comsol)


# plt.scatter(x, y, c=np.abs(E_field), cmap="inferno", marker="s")
# plt.colorbar(label="Electric Field Magnitude")
# plt.show()




#%%
# which_sol = 0
# x_plot = x[which_sol, :]
# y_plot = y[which_sol, :]
# Ex     = dataset[which_sol, :]

# plt.scatter(x_plot, y_plot, c=np.abs(Ex), cmap="inferno", marker="s")
# plt.colorbar(label="Electric Field Magnitude")
# plt.xlabel("x (µm)")
# plt.ylabel("y (µm)")
# plt.title("Electric Field Distribution from COMSOL")
# plt.show()

# result_tags = mphtags(model, 'result');

# result_index = 4;

# ffd = mphplot(model,result_tags{result_index},'createplot','off');

 

# ffdd_water = ffd{1}{1};

# ffdd_clad = ffd{2}{1};

# ffdd_core = ffd{3}{1};

 

# FarField_water_theta(iter,:) = ffdd_water.p*180/pi;

# FarField_water_rho(iter,:) = ffdd_water.d;

 

# FarField_clad_theta(iter,:) = ffdd_clad.p*180/pi;

# FarField_clad_rho(iter,:) = ffdd_clad.d;

 

# FarField_core_theta(iter,:) = ffdd_core.p*180/pi;

# FarField_core_rho(iter,:) = ffdd_core.d;

# model.datasets()

