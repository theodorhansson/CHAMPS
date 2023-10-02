import communication
import traceback
from numpy import average as np_average

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

import logging
from hamamatsu.dcam import copy_frame, dcam, Stream

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


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

    Results = missalignment_main(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return Results, return_dict


def missalignment_main(IPV_config: dict, DC_config: dict):
    # The main IPV function
    V_max = IPV_config["v_max"]
    plot_update_interval = IPV_config["plot_interval"]
    rollover_threshold = IPV_config["rollover_threshold"]
    rollover_min = IPV_config["rollover_min"]
    intervals = IPV_config["current"]
    verbose = IPV_config["verbose_printing"]
    keep_plot = IPV_config["keep_plot"]
    offset_background = IPV_config["offset_background"]
    interval_list = utils.interval_2_points(intervals)

    # Create result dict
    Results = {
        "header": "Current[mA], Optical Power [mW], Voltage [V]",
        "voltage": [],
        "current": [],
        "power": [],
    }
    
    figure_folder = "C:\\Users\\Mindaugas Juodenas\\Documents\\GitHub\\CHAMPS_data"
    figure_number = 0

    figure_list = []
    
    
    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    Plot = utils.AnimatedPlot("Current[mA]", "Optical Power [mW]", "IPV")
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
                power_max = 0
                start_current = interval[0]
                utils.ramp_current(DC_unit, prev_end_current, start_current)
                prev_end_current = interval[-1]

                for loop_count, set_current in enumerate(interval):
                    DC_unit.set_current(set_current)

                    volt, current = DC_unit.get_voltage_and_current()

                    Results["voltage"].append(volt)
                    Results["current"].append(current)

                    Plot.add_point(volt, current)
                    
                    with dcam:
                        camera = dcam[0]
                        with camera:
                            
                            nb_frames = 1
                            camera["exposure_time"] = 0.033
                            
                            x_pixels = camera['image_width'].value
                            y_pixels = camera['image_height'].value
                            
  
                            with Stream(camera, nb_frames) as stream:

                                    camera.start()
                                    
                                    for i, frame_buffer in enumerate(stream):

                                        picture = copy_frame(frame_buffer)
                                        figure_list.append(picture)
                                        
                                        plt.pause(1/30)

                    if verbose & 1:
                        print("IPV data", volt, current)

                    # Only plot sometimes
                    if loop_count % plot_update_interval == 0:
                        # approx 0.5s per measurement
                        Plot.update()
                      

            for i, img in enumerate(figure_list):
                im = Image.fromarray(img)
                im.save(figure_folder + "\\" + str(i) + ".png")
                
                Plot.update()

        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    # To hold plot open when measurement done
    if keep_plot:
        print("IPV measurements done. Keeping plot alive for your convenience.")
        Plot.keep_open()
    else:
        print("IPV measurements done. Vaporizing plot!")

    return Results
