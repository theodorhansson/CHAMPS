import tomllib
import sys
import numpy as np
import time
import tomli_w
import utils
import json
import os
import imageio.v3 as iio

default_conf_path = "config.toml"
import numpy as npq
import matplotlib.pyplot as plt
from PIL import Image

def main(config_path):
    # Open the config file
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    config_lower = utils.dict_2_lower(config)  # sanitize the config dict
    meas_name = config_lower["measurement"]["type"]

    # Code for printing
    if "verbose_printing" in config_lower["measurement"].keys():
        verbose = config_lower["measurement"]["verbose_printing"]
    else:
        verbose = 0
    print(f"Reading config {config_path} from disk") if verbose & 16 else None

    # get the current time in nice format
    timestamp = time.strftime(rf"%Y%m%d-%H%M%S")

    # Set file name to current time if undefined
    if "custom_name" not in config_lower["measurement"].keys():
        config_lower["measurement"]["custom_name"] = meas_name
    config_lower["measurement"]["custom_name"] += "-" + timestamp

    file_name = config_lower["measurement"]["custom_name"]

    # Get the measurement object
    measurement_init = identify_measurement_type(meas_name)
    # Begin the measurement!
    result_dict, used_config = measurement_init(config_lower)

    # Logic on where to save file
    save_folder = config_lower["measurement"]["save_folder"]
    if save_folder[-1:] != "/":
        save_folder = save_folder + "/"  # make sure it ends with /

    # Create save folder if it doesn't exist
    if not os.path.isdir(save_folder):
        print("Woops, your folder doesn't exist. Creating one here: ", save_folder)
        os.mkdir(save_folder)
    save_file_name = save_folder + file_name

    # print(config_lower["type"])
    if config_lower["measurement"]["type"] == "missalignment" or config_lower["measurement"]["type"] == "spr_no_lam_sweep":

        SPR_measurement_name = config_lower["measurement"]["spr_measurement_name"]
        
        save_path_current_measurement = os.path.join(save_folder, SPR_measurement_name)
        if not os.path.isdir(save_path_current_measurement):
            os.mkdir(save_path_current_measurement)

        frame_list = result_dict["frame_list"]
        frame_time = result_dict["frame_time"]
        SPR_data = result_dict["SPR_data"]
        fig_object = result_dict["fig_object"]

        print('Saving Images')
        for i, im in enumerate(frame_list):      
            iio.imwrite(os.path.join(save_path_current_measurement, f'{SPR_measurement_name}_image{i}.png'), im)
            
        print(f'Saving Data to {save_folder}')
        xy = np.vstack((frame_time,SPR_data)).T
        np.savetxt(os.path.join(save_path_current_measurement, f'{SPR_measurement_name}_data.txt'), xy, delimiter=',') 
        fig_object.savefig(os.path.join(save_path_current_measurement, f'{SPR_measurement_name}_data.png'))

    else:
        # Save the data as json
        print("Starting saving process. This might take a while for large files.")
        data_save_name = save_file_name + ".json"
        with open(data_save_name, "w") as export_file:
            json.dump(result_dict, export_file)
        print(f"Saving data file {data_save_name} to disk.") if verbose & 16 else None
    
        # Save the config
        config_save_name = save_file_name + ".toml"
        with open(config_save_name, "wb") as f:
            tomli_w.dump(used_config, f)
        print(f"Saving config file {config_save_name} to disk.") if verbose & 16 else None


def identify_measurement_type(measurement: str):
    # Matches measurement name with correct module
    match measurement:
        case "ipv":
            import measurement_type.ipv
            return measurement_type.ipv.init

        case "spectrum":
            import measurement_type.spectrum
            return measurement_type.spectrum.init

        case "ipv_diode":
            import measurement_type.ipv_diode
            return measurement_type.ipv_diode.init

        case "beam_profile":
            import measurement_type.beam_profile
            return measurement_type.beam_profile.init
        
        case "missalignment":
            import measurement_type.missalignment
            return measurement_type.missalignment.init
        
        case "spr_no_lam_sweep":
            import measurement_type.SPR_no_lam_sweep
            return measurement_type.SPR_no_lam_sweep.init
            
        case _:
            # TODO Change this
            raise Exception(f"No measurement of type {measurement} found.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        config_path = default_conf_path
    else:
        # for optional system path
        config_path = sys.argv[1]

    main(config_path)
