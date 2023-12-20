import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    
# Import CHAMPS module for GPIB connections
import communication

# # Import hamamatsu python drivers
# from drivers.dcam_hamamatsu.dcam_live_capturing import dcam_live_capturing
# # from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_capture_image
# from drivers.dcam_hamamatsu.dcam_capture_several_images import dcam_capture_average_image

from hamamatsu.dcam import copy_frame, dcam, Stream
# Import Aurora
from drivers.arduino_giga_serial.aurora import aurora

# Import meta-SPR
from spr_functions.main_spr import SPR_figure, alignment_figure

# Python modules
import traceback
import numpy as np
import matplotlib.pyplot as plt
import time
import threading
from scipy.signal import find_peaks
from pathlib import Path
import imageio.v3 as iio
    
COLORS = ['r','g','b','y','cyan','magenta','aqua']
    
x_pixel  = 2048
y_pixel  = 2048

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
    "vcsel_array_bias",
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

    results = SPR_no_lam_sweep_main(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return results, return_dict

def grab_image(camera, frame_average, measurement_subinterval, frame_average_buffer):
    average_buffer  = np.zeros(shape=(x_pixel, y_pixel))
    captured_frames = np.zeros(shape=(x_pixel, y_pixel))


    with Stream(camera, frame_average_buffer) as stream:
        camera.start()
        
        for k in range(frame_average):  
            for i, frame_buffer in enumerate(stream): 
                fr = copy_frame(frame_buffer).astype(int)
                average_buffer += fr
                
            captured_frames += average_buffer/frame_average_buffer
            time.sleep(measurement_subinterval)  
            
        camera.stop()                        
    return np.flip(captured_frames/frame_average)

def find_laser_lines(image, manual=[]):
    if len(manual) >= 1:
        peaks = manual
    else:
        image_shape = image.shape
        integrate_over = 100
        integrate_y = np.sum(image[:, image_shape[0]//2-integrate_over:image_shape[0]//2+integrate_over], axis=1)
        peaks, _ = find_peaks(integrate_y, distance=50, width=10, threshold=500)
        print('Found lasers with coordinates' + str(peaks))
    
    return peaks

def SPR_process_image(laser, spr_figure, line, image, results, image_capture_time, measurement_time_start, frame_counter, IPV_config):
    # results['frame_list'][laser].append(image)
    results['frame_time'][laser].append(image_capture_time - measurement_time_start)
    #TODO: There is an enormous memory leak somewhere, the measurement slows down
    # it is somewhere in the plotting logic
    results['spr_data'][laser].append(spr_figure.analyze_image(image, frame_counter, line, IPV_config))

def SPR_no_lam_sweep_main(IPV_config: dict, DC_config: dict):
    
    # The main IPV function
    V_max = IPV_config["v_max"]
    check_bias = IPV_config["check_bias"]
    verbose = IPV_config["verbose_printing"]
    measurement_time = IPV_config["measurement_time"]
    measurement_interval = IPV_config["measurement_interval"]
    measurement_subinterval = IPV_config["measurement_subinterval"]
    
    vcsel_chip = IPV_config["vcsel_chip"]
    vcsel_biases = IPV_config["vcsel_biases"]
    laser_indexing = {index: value for index, value in enumerate(vcsel_biases)}
    ref_spectrums = {}
    vcsel_array_bias = IPV_config["vcsel_array_bias"]
    
    exposure_time = IPV_config["exposure_time"]
    frame_average = IPV_config["frame_average"]
    frame_average_buffer = IPV_config["frame_average_buffer"]
    integrate_over_um = 80
    
    periodic_saving = True
    save_data = True
    saving_interval = 300
    save = 1

    # Create result dict
    results = {"frame_list" : {},
               "frame_time" : {},
               "spr_data"   : {},
               }
    
    for i, biases in enumerate(vcsel_biases):
        results["frame_list"][i] = []
        results["frame_time"][i] = []
        results["spr_data"][i]   = []
        
    # Initialize figure for plotting
    # TODO: MAKE NUMBER OF FIGURES AS MANY AS VCSELS OR MERGE INTO ONE FIGURE ##
    a_figure   = alignment_figure(integrate_over_um)
    
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

    # Start time of measurement
    measurement_time_start = time.time()
    measurement_timestamp = time.strftime(rf"%Y%m%d_%H.%M.%S")
    
    with DC_unit_obj(DC_config) as DC_unit:
        try:
            ## Set instrument to 0 for safety
            prev_end_current = 0.0
            DC_unit.set_current(prev_end_current)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)
            
            ## Check alignment of SPR line
            for laser in laser_indexing.keys():
                laser_control.switch_to_laser(laser)
                utils.ramp_current(DC_unit, 0, laser_indexing[laser])

                with dcam:
                    camera = dcam[0]
                    
                    with camera:
                        camera["exposure_time"] = exposure_time 
                        
                        image = grab_image(camera, frame_average, measurement_subinterval, frame_average_buffer)
                        y_max_index, ref_spectrum = a_figure.update_alignment_image(image)
                        ref_spectrums[laser] = {'ref_spectrum' : ref_spectrum,
                                                'y_max_index'  : y_max_index,
                                                'raw_image'    : image}
                        # plt.show(False)
                
                utils.ramp_current(DC_unit, laser_indexing[laser], 0)
                
            # time.sleep(3)
            laser_control.turn_off_all_lasers()
            
                    
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    saving_results(IPV_config, ref_spectrums, a_figure, measurement_timestamp)
    return results

def saving_results(IPV_config, ref_spectrums, a_figure, measurement_timestamp):
            
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
    
    all_y_max = []
    for ref in ref_spectrums.keys():

        save_folder_current_VCSEL = Path(save_path_current_measurement, f'VCSEL_{ref}')
        
        if not os.path.isdir(save_folder_current_VCSEL):
            os.mkdir(save_folder_current_VCSEL)

        # iio.imwrite(os.path.join(save_folder_current_VCSEL, f'{SPR_measurement_name}_image{ref}.png'), ref_spectrums[ref]["raw_image"])

        np.savetxt(os.path.join(save_folder_current_VCSEL, 'ref_spectrum.txt'), ref_spectrums[ref]["ref_spectrum"], delimiter=',') 
        all_y_max.append(ref_spectrums[ref]["y_max_index"])
    
    
    np.savetxt(os.path.join(save_path_current_measurement, 'y_max.txt'), np.array(all_y_max))

    a_figure.fig.savefig(os.path.join(save_path_current_measurement, 
                                    f'{SPR_measurement_name}_data.png'))
    
