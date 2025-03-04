import os
from pathlib import Path

## Generate all project paths
def generate_project_paths(file_name, project_name):
    current_file_path = Path(os.path.realpath(file_name))
    return current_file_path.parent
        
## Generate CHAMP paths
def generate_CHAMP_paths(file_name):
    return generate_project_paths(file_name, 'CHAMP')
        
## Create folders
def create_folder(folder_path):
    if not folder_path.exists():
        os.mkdir(str(folder_path))

def create_output_folder(path):
    output_dir = '_output'
    output_dir_path = Path(path, output_dir)
    create_folder(output_dir_path)
    return output_dir_path
 
def create_measurement_save_folder(output_dir_path, meas_name):
    meas_dir_path = Path(output_dir_path, meas_name)
    create_folder(meas_dir_path)
    return meas_dir_path



    