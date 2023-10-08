# Import CHAMPS module for GPIB connections
import communication

# Import hamamatsu python drivers
from drivers.dcam_hamamatsu.dcam_live_capturing import dcam_live_capturing
from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_capture_image

# Import meta-SPR
from spr_functions.main_spr import process_image, init_figure, analyze_image

# Python modules
import traceback
from numpy import average as np_average
import matplotlib.pyplot as plt
import time
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
    "check_bias": 1,
    "measurement_time": 1,
    "measurement_inteval": 1,
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

    Results = SPR_no_lam_sweep_main(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return Results, return_dict


def SPR_no_lam_sweep_main(IPV_config: dict, DC_config: dict):
    
    # The main IPV function
    V_max = IPV_config["v_max"]
    check_bias = IPV_config["check_bias"]
    measurement_bias = IPV_config["current"]
    verbose = IPV_config["verbose_printing"]
    measurement_time = IPV_config["measurement_time"]
    measurement_interval = IPV_config["measurement_interval"]
    
    find_det_lines = IPV_config["find_det_lines"]
    find_line_biased = IPV_config["find_line_biased"]
    
    exposure_time = IPV_config["exposure_time"]
    
    
    # interval_list = utils.interval_2_points(intervals)

    # Create result dict
    Results = {
        "header": "Current[mA], Optical Power [mW], Voltage [V]",
        "voltage": [],
        "current": [],
        "power": [],
    }

    frame_list = []
    frame_time = []
    SPR_data = []
    
    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    
    
    # Plot = utils.AnimatedPlot("Current[mA]", "Optical Power [mW]", "IPV")
    Instrument_COM = communication.Communication()

    # Gets isntruments
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)

    ## Start live capturing stop with q and start measuring
    if find_det_lines:
        dcam_live_capturing(exposure_time=exposure_time)
    
    
    
    with DC_unit_obj(DC_config) as DC_unit:
        try:
            
            
            # # Set instrument to 0 for safety
            prev_end_current = 0.0
            DC_unit.set_current(prev_end_current)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)
            
            # Check alignment of SPR line
            utils.ramp_current(DC_unit, prev_end_current, check_bias)
            DC_unit.set_current(check_bias)
            if find_line_biased:
                dcam_live_capturing(exposure_time=exposure_time)
        
            utils.ramp_current(DC_unit, check_bias, 0)
            
            # Initialize figure for plotting
            fig = init_figure()
            
            # Start time of measurement
            measurement_time_start = time.time()
            
            # Main measurement loop
            while (time.time() - measurement_time_start) < measurement_time:
                start_time = time.time()
                
                utils.ramp_current(DC_unit, 0, measurement_bias)
                # Grab picture from Hamamatsu
                image = dcam_capture_image(exposure_time=exposure_time)
                
                frame_list.append(image)
                SPR_data.append(analyze_image(image, fig))
                frame_time.append(time.time() - measurement_time_start)
                
                fig.axes[4].plot(frame_time, SPR_data, marker='o', linewidth=0.2, markersize=3) 

                plt.show(False)
                
                utils.ramp_current(DC_unit, measurement_bias, 0)
                
                duration = time.time() - start_time
                time.sleep(measurement_interval - duration if duration < measurement_interval else 0)
                
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    Results["frame_list"] = frame_list
    Results["frame_time"] = frame_time
    Results["SPR_data"] = SPR_data
    Results["fig_object"] = fig

    return Results
