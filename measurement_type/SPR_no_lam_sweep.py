import communication
import traceback
from numpy import average as np_average

import os, sys
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
    "current",
    "v_max",
    "save_folder",
    "custom_name",
]
_optional_arguments = {
    "rollover_threshold": 0,
    "rollover_min": 0,
    "plot_interval": 20,
    "verbose_printing": 0,
    "keep_plot": False,
    "offset_background": 0,
}

from drivers.dcam_hamamatsu.dcam_live_capturing import dcam_live_capturing
from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_show_single_captured_image
from spr_functions.main_spr import process_image

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

    Results = SPR_no_lam_sweep_main(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return Results, return_dict


def SPR_no_lam_sweep_main(IPV_config: dict, DC_config: dict):
    
    ## Start live capturing stop with q and start measuring
    dcam_live_capturing()
    
    # The main IPV function
    V_max = IPV_config["v_max"]
    intervals = IPV_config["current"]
    verbose = IPV_config["verbose_printing"]
    interval_list = utils.interval_2_points(intervals)

    # Create result dict
    Results = {
        "header": "Current[mA], Optical Power [mW], Voltage [V]",
        "voltage": [],
        "current": [],
        "power": [],
    }
    
    camera_image_list = []
    
    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    # Plot = utils.AnimatedPlot("Current[mA]", "Optical Power [mW]", "IPV")
    Instrument_COM = communication.Communication()

    # Gets isntruments
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)

    with DC_unit_obj(DC_config) as DC_unit:
        try:
            
            # Set instrument to 0 for safety
            DC_unit.set_current(0.0)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)
                    
            prev_end_current = 0
            # The main measurement loop
            for interval in interval_list:
                # Code to ramp current between intervals
                # power_max = 0
                start_current = interval[0]
                utils.ramp_current(DC_unit, prev_end_current, start_current)
                prev_end_current = interval[-1]
                
                data = 0

                for loop_count, set_current in enumerate(interval):
                    DC_unit.set_current(set_current)

                    volt, current = DC_unit.get_voltage_and_current()

                    Results["voltage"].append(volt)
                    Results["current"].append(current)
                    
                    if verbose & 1:
                        print("IPV data", volt, current)
                        
                    image = dcam_show_single_captured_image()
                    
                    process_image(image)
                    # camera_image_list.append(data)
                    
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    Results["camera_images"] = camera_image_list

    return Results
