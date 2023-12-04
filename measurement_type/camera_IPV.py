import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
# Import CHAMPS module for GPIB connections
import communication

# Import hamamatsu python drivers
from drivers.dcam_hamamatsu.dcam_live_capturing import dcam_live_capturing
# from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_capture_image
from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_capture_image

# Python modules
import traceback
import numpy as np
import matplotlib.pyplot as plt
import time
import threading
from scipy.signal import find_peaks
from pathlib import Path
import imageio.v3 as iio
    
COLORS = ['r','g','b']
    
# Dumb code to import utils
try:
    import utils
except:
    import sys, pathlib

    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils

_DC_name_key = "dc_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "v_max",
    "save_folder",
    "custom_name",
    "spr_measurement_name",
    "vcsel_chip",
    "vcsel_biases",
    "frame_average",
    
]
_optional_arguments = {
    "rollover_threshold": 0,
    "rollover_min": 0,
    "verbose_printing": 0,
    "keep_plot": False,
    "offset_background": 0,
    "check_bias": 1,
    "measurement_time": 1,
    "measurement_interval": 1,
    "find_det_lines": 1,
    "find_line_biased": 1,
    "exposure_time": 0.03,
    "save_raw_images": 0,
}


def init(config: dict):
    # Get config dict and check for optional arguments
    IPV_config = config["measurement"]
    # Check and merge optional arguments
    utils.argument_checker(
        IPV_config, _required_arguments, _optional_arguments, source_func="IPV init"
    )
    IPV_config_opt = utils.optional_arguments_merge(IPV_config, _optional_arguments)

    # Used for getting instrument objects and their names
    IPV_name = IPV_config["type"]
    DC_name = IPV_config[_DC_name_key]
    DC_config = config[DC_name]

    results = camera_IPV(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return results, return_dict

def camera_IPV(IPV_config: dict, DC_config: dict):
    
    # The main IPV function
    V_max = IPV_config["v_max"]
    check_bias = IPV_config["check_bias"]
    verbose = IPV_config["verbose_printing"]
    measurement_time = IPV_config["measurement_time"]
    measurement_interval = IPV_config["measurement_interval"]
    
    find_det_lines = IPV_config["find_det_lines"]
    find_line_biased = IPV_config["find_line_biased"]
    
    exposure_time = IPV_config["exposure_time"]
    
    vcsel_chip = IPV_config["vcsel_chip"]
    vcsel_biases = IPV_config["vcsel_biases"]
    
    frame_average = IPV_config["frame_average"]
    
    find_laser_lines_bias = 3
    # manual_lines = np.array([0])
    # manual_lines = np.array([698])
    manual_lines = np.array([698, 1174, 1487])
        # 1579
    bias_sweep = False
    sweep_biases = np.array([3.3, 3.6, 3.9])
    
    periodic_saving = True
    save_data = True
    saving_interval = 300
    save = 1
    
    results = {"raw_images" : [],
               "Ib" : [],
               "Vb" : [],
               "Popt": []}
    
    Ib = np.concatenate([np.arange(0, 0.3, 0.01), np.arange(0.3, 10, 0.05)])
    integrate_over = 200
    
    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    Instrument_COM = communication.Communication()

    # Gets isntruments
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)

    # Start live capturing stop with q and start measuring
    if find_det_lines:
        dcam_live_capturing(exposure_time=exposure_time)
    
    measurement_timestamp = time.strftime(rf"%Y%m%d_%H.%M.%S")
            
    with DC_unit_obj(DC_config) as DC_unit:
        try:
            ## Set instrument to 0 for safety
            prev_end_current = 0.0
            DC_unit.set_current(prev_end_current)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)
            
            utils.ramp_current(DC_unit, prev_end_current, check_bias)
            DC_unit.set_current(check_bias)
            if find_line_biased:
                dcam_live_capturing(exposure_time=exposure_time)
        
            utils.ramp_current(DC_unit, check_bias, 0)
            
            for i in range(len(Ib)):
                DC_unit.set_current(Ib[i])
                results["Ib"].append(Ib[i])

                image = dcam_capture_image(exposure_time=exposure_time)
                results["raw_images"].append(image)
                
                max_index = np.unravel_index(np.argmax(image, axis=None), image.shape)
                
                Popt = np.sum(image[max_index[0]-integrate_over:max_index[0]+integrate_over, max_index[1]-integrate_over:max_index[1]+integrate_over])
                results["Popt"].append(Popt)
                
                Vb_current = DC_unit.get_voltage()
                results["Vb"].append(Vb_current)
                
            
                    
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    saving_results(IPV_config, results, measurement_timestamp)
    return results

def saving_results(IPV_config, results, measurement_timestamp):
            
    parent_path = Path(__file__).resolve().parents[1]
    save_folder_path = Path(parent_path, IPV_config["save_folder"])
    if not os.path.isdir(save_folder_path):
        print("Woops, your folder doesn't exist. Creating one here: ", save_folder_path)
        os.mkdir(save_folder_path)
    SPR_measurement_name = IPV_config["spr_measurement_name"]
    measurement_timestamp = measurement_timestamp + '_' + SPR_measurement_name
    save_path_current_measurement = os.path.join(save_folder_path, 
                                                  measurement_timestamp)
    if not os.path.isdir(save_path_current_measurement):
        os.mkdir(save_path_current_measurement)
    
    print('Saving Images')
    print(f'Saving Data to {save_path_current_measurement}')

        
    save_folder_current_VCSEL = Path(save_path_current_measurement)
    
    if not os.path.isdir(save_folder_current_VCSEL):
        os.mkdir(save_folder_current_VCSEL)
    
    Ib = results["Ib"]
    Vb = results["Vb"]
    Popt = results["Popt"]
    np.savetxt(os.path.join(save_folder_current_VCSEL, "Ib_mA.txt"), np.array(Ib))
    np.savetxt(os.path.join(save_folder_current_VCSEL, "Vb.txt"), np.array(Vb))
    np.savetxt(os.path.join(save_folder_current_VCSEL, "Popt.txt"), np.array(Popt))
    for i, image in enumerate(results["raw_images"]):
        iio.imwrite(os.path.join(save_folder_current_VCSEL, f'IMAGE_Ib_{Ib[i]}.png'), image)
        
    
