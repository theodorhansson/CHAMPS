# Import CHAMPS module for GPIB connections
import communication

# Import hamamatsu python drivers
from drivers.dcam_hamamatsu.dcam_live_capturing import dcam_live_capturing
from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_capture_image

# Import Aurora
from drivers.arduino_giga_serial.aurora import aurora

# Import meta-SPR
from spr_functions.main_spr import process_image, init_figure, analyze_image

# # Python modules
import traceback
import numpy as np
import matplotlib.pyplot as plt
import time
import os, sys
import threading
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
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

    results = SPR_no_lam_sweep_main(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return results, return_dict

def process_image(laser, image, fig, results, measurement_time_start, widest_valley_search):
    results['frame_list'][laser].append(image)
    results['frame_time'][laser].append(time.time() - measurement_time_start)
    results['spr_data'][laser].append(analyze_image(image, widest_valley_search, fig))

def SPR_no_lam_sweep_main(IPV_config: dict, DC_config: dict):
    
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
    
    widest_valley_search = False

    # Create result dict
    results = {"frame_list" : {},
               "frame_time" : {},
               "spr_data"   : {},
               }
    
    for i, biases in enumerate(vcsel_biases):
        results[f"frame_list"][i] = []
        results[f"frame_time"][i] = []
        results[f"spr_data"][i]   = []
        
    # Initialize figure for plotting
    # TODO: MAKE NUMBER OF FIGURES AS MANY AS VCSELS OR MERGE INTO ONE FIGURE ##
    fig1 = init_figure()
    fig2 = init_figure()
    fig3 = init_figure()
    fig_list = [fig1, fig2, fig3]
    
    laser_control = aurora(vcsel_chip)
    lasers_on_chip = np.fromiter(laser_control.chip.keys(), dtype=int)
    # TODO: INCLUDE CHECK THAT BIASES AND NUMBER OF VCSELS ARE THE SAME ##

    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    Instrument_COM = communication.Communication()

    # Gets isntruments
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)

    ## Start live capturing stop with q and start measuring
    if find_det_lines:
        dcam_live_capturing(exposure_time=exposure_time)
    
    with DC_unit_obj(DC_config) as DC_unit:
        try:
            ## Set instrument to 0 for safety
            prev_end_current = 0.0
            DC_unit.set_current(prev_end_current)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)
            
            # Check alignment of SPR line
            laser_control.turn_on_all_lasers()
            utils.ramp_current(DC_unit, prev_end_current, check_bias)
            DC_unit.set_current(check_bias)
            if find_line_biased:
                dcam_live_capturing(exposure_time=exposure_time)
        
            utils.ramp_current(DC_unit, check_bias, 0)
            laser_control.turn_off_all_lasers()
            
            # Start time of measurement
            measurement_time_start = time.time()
            
            # Main measurement loop
            while (time.time() - measurement_time_start) < measurement_time:
                start_time = time.time()
                
                frame_counter = 0
                print(f'Taking Picture No {frame_counter}')
                for i, laser in enumerate(lasers_on_chip):
                    
                    # Active switch for current laser
                    laser_control.switch_to_laser(laser)
                    
                    # Ramp current to set bias
                    utils.ramp_current(DC_unit, 0, vcsel_biases[i])
                    
                    # Grab picture from Hamamatsu
                    image = dcam_capture_image(exposure_time=exposure_time)
                    
                    # Process with meta-SPR library
                    process_image(laser, image, fig, results, measurement_time_start, widest_valley_search)
                    
                    ## Include for threading for process images ## WARNING UNTESTED ##
                    # image_processing_thread = threading.Thread(target=process_image(i, image, fig_list[i], results, measurement_time_start))
                    # image_processing_thread.start()
                    
                    # Update inline plot with measurement status
                    ## TODO: WILL ONLY SHOW FIGURE FROM FIRST VCSEL
                    fig1.axes[4].plot(frame_time, SPR_data, marker='o', linewidth=0.2, markersize=3) 
                    plt.show(False)
                    
                    # Ramp down current
                    utils.ramp_current(DC_unit, vcsel_biases[i], 0)
                    
                    # Turn off switch to lasers
                    laser_control.turn_off_all_lasers()
                    
                # Wait until set time for the measurement
                duration = time.time() - start_time
                time.sleep(measurement_interval - duration if duration < measurement_interval else 0)
                    
                ## CLEAN UP OF STARTED THREADS MIGHT NOT BE NEEDED
                # image_processing_thread.join()
                    
                frame_counter += 1
                    
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    return results
