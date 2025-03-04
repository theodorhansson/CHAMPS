## General python imports needed
import tomllib
import sys
import time
import tomli_w
import utils
import json
import os

## Custom imports
import general_functions.pretty_printing.verbose_printing as vp
import general_functions.files_and_folders.ffp_functions as ffp

## Hard coded config file path
default_conf_path = 'config.toml'

## Main running file for CHAMPS
## Coordinates all measurements
def main(config_path):
    
    ## Find root path for CHAMPS project
    root_path = ffp.generate_CHAMP_paths(__file__)
    
    ## Open the config file
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)
        
    ## Set all strings in config.toml to lower case
    config_lower = utils.dict_2_lower(config)
    
    ## Extract measurement name and print
    meas_name = config_lower['measurement']['type']
    vp.headline('Sucessfully loaded config for ' + meas_name)
    
    ## Check for verbose printing
    verbose = vp.check_flag_for_verbose_printing(config_lower)
        
    ## Current time
    timestamp = time.strftime(rf'%Y%m%d_%H.%M')
    
    ## Create measurement output folder
    output_dir_path = ffp.create_output_folder(root_path)
    
    ## Create folder for current measurement type
    meas_type = config_lower['measurement']['type']
    meas_output_dir_path = ffp.create_measurement_save_folder(output_dir_path, meas_type)
    
    ## Create folder for current measurement
    meas_name = config_lower['measurement']['name']
    meas_name_timestamp = str(meas_name) + '_' + timestamp
    meas_output_dir_path = ffp.create_measurement_save_folder(meas_output_dir_path, meas_name_timestamp)
    
    # Get the measurement object
    measurement_init = identify_measurement_type(meas_type)
    
    # Begin the measurement!
    used_config = measurement_init(config_lower, meas_output_dir_path)


def identify_measurement_type(measurement: str):
    # Matches measurement name with correct module
    match measurement:
        case 'capture_images':
            import measurement_type.capture_images
            return measurement_type.capture_images.init
        
        case 'capture_stokes':
            import measurement_type.capture_stokes
            return measurement_type.capture_stokes.init
        
        case 'ipv':
            import measurement_type.ipv
            return measurement_type.ipv.init
        case 'spectrum':
            import measurement_type.spectrum
            return measurement_type.spectrum.init

        case 'ipv_diode':
            import measurement_type.ipv_diode
            return measurement_type.ipv_diode.init

        case 'beam_profile':
            import measurement_type.beam_profile
            return measurement_type.beam_profile.init
        
        case 'missalignment':
            import measurement_type.missalignment
            return measurement_type.missalignment.init
        
        case 'spr_no_lam_sweep':
            import measurement_type.SPR_no_lam_sweep
            return measurement_type.SPR_no_lam_sweep.init
        
        case 'spr_lam_sweep':
            import measurement_type.SPR_lam_sweep
            return measurement_type.SPR_lam_sweep.init
        
        case 'spr_no_lam_vcsel_sweep':
            import measurement_type.SPR_no_lam_VCSEL_sweep
            return measurement_type.SPR_no_lam_VCSEL_sweep.init
        
        case 'spr_alignment':
            import measurement_type.spr_alignment
            return measurement_type.spr_alignment.init
            
        case _:
            # TODO Change this
            raise Exception(f'No measurement of type {measurement} found.')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        config_path = default_conf_path
    else:
        # for optional system path
        config_path = sys.argv[1]

    main(config_path)
