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
from spr_functions.main_spr import SPR_figure

# Python modules
import traceback
import numpy as np
import time
from pathlib import Path
import imageio.v3 as iio
import gc
# import threading
    
COLORS = ['blue','aqua','red','lightcoral','green','lightgreen']

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
    "frame_average_buffer",
    "frame_average",
    
]
_optional_arguments = {
    "rollover_threshold": 0,
    "rollover_min": 0,
    "verbose_printing": 0,
    "keep_plot": False,
    "offset_background": 0,
    "measurement_time": 1,
    "measurement_interval": 1,
    "exposure_time": 0.03,
    "save_raw_images": 0,
    "measurement_subinterval": 0.01
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
    temp_avg_1 = np.zeros(shape=(x_pixel, y_pixel))
    temp_avg_2 = np.zeros(shape=(x_pixel, y_pixel))
    temp_avg_3 = np.zeros(shape=(x_pixel, y_pixel))

    with Stream(camera, frame_average_buffer) as stream:
        camera.start()
        
        for k in range(frame_average):  
            # start_time = time.time()
            for i, frame_buffer in enumerate(stream): 
                fr = copy_frame(frame_buffer).astype(int)

                average_buffer += fr
                
            captured_frames += average_buffer/frame_average_buffer
            time.sleep(measurement_subinterval)  
            
            # stop_time = time.time()
            # print(stop_time - start_time)
                
        camera.stop()                        
                    
    return np.flip(captured_frames/frame_average)

def SPR_process_image(spr_figure, image, results, image_capture_time, measurement_time_start, frame_counter, IPV_config, y_max_index, ref_spectrums, use_reference_spectrum):
                            
    frame_time = image_capture_time - measurement_time_start
    for i in range(len(y_max_index)):
        results['frame_time'][i].append(frame_time)
        results['spr_data'][i].append(spr_figure.analyze_image(image, y_max_index[i], frame_counter, i, IPV_config, ref_spectrums[i], use_reference_spectrum))

def SPR_no_lam_sweep_main(IPV_config: dict, DC_config: dict):
    
    # The main IPV function
    V_max = IPV_config["v_max"]
    verbose = IPV_config["verbose_printing"]
    measurement_time = IPV_config["measurement_time"]
    measurement_interval = IPV_config["measurement_interval"]
    measurement_subinterval = IPV_config["measurement_subinterval"]

    vcsel_chip = IPV_config["vcsel_chip"]
    vcsel_biases = IPV_config["vcsel_biases"]
    laser_indexing = {index: value for index, value in enumerate(vcsel_biases)}
    vcsel_array_bias = IPV_config["vcsel_array_bias"]
    ref_spectrums = {}
    
    exposure_time = IPV_config["exposure_time"]
    frame_average = IPV_config["frame_average"]
    frame_average_buffer = IPV_config["frame_average_buffer"]
    integrate_over_um = 80
    
    use_reference_spectrum = False
    
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
        
    
    laser_control = aurora(vcsel_chip)
    lasers_on_chip = np.fromiter(laser_control.chip.keys(), dtype=int)

    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    Instrument_COM = communication.Communication()

    # Gets isntruments
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)

    # Start live capturing stop with q and start measuring
    # if find_det_lines:
    #     dcam_live_capturing(exposure_time=exposure_time)
    
    # Start time of measurement
    measurement_time_start = time.time()
    measurement_timestamp = time.strftime(rf"%Y%m%d_%H.%M.%S")
    
    parent_path = Path(__file__).resolve().parents[1]
    save_folder_path = Path(parent_path, IPV_config["save_folder"])
    if not os.path.isdir(save_folder_path):
        print("Woops, your folder doesn't exist. Creating one here: ", save_folder_path)
        os.mkdir(save_folder_path)
    hard_coded_reference_measurement = '20231212_11.03.42_y_max_ref'
    
    counter = 0
    for folders in os.listdir(str(Path(parent_path, save_folder_path))):

        if folders == hard_coded_reference_measurement:
            ref_path = Path(save_folder_path, hard_coded_reference_measurement)
            y_max_path = Path(ref_path, 'y_max.txt')
            
            y_max_index = np.loadtxt(y_max_path)
            
        for spectrum_folder in os.listdir(ref_path):
            
            vcsel_path = Path(ref_path, spectrum_folder)
            spectrum_path = Path(vcsel_path, 'ref_spectrum.txt')
            
            if os.path.isdir(str(vcsel_path)):
                ref_spectrums[counter] = np.loadtxt(spectrum_path)
                counter += 1
                # print(counter)
            
    # with DC_unit_obj(DC_config) as DC_unit:
    #     try:
    #         ## Set instrument to 0 for safety
    #         prev_end_current = 0.0
    #         DC_unit.set_current(prev_end_current)
    #         DC_unit.set_voltage_limit(V_max)
    #         DC_unit.set_output(True)
            
    spr_figure = SPR_figure(integrate_over_um)
    results["fig_object"] = spr_figure.fig

            
    # Frame counter
    frame_counter = 0
    
    # Main measurement loop
    while (time.time() - measurement_time_start) < measurement_time:
        with dcam:
            try:
                camera = dcam[0]
                
                with camera:
     
                    camera["exposure_time"] = exposure_time 
                    total_duration = 0
      
                    start_time = time.time()
                    # Active switch for current laser
                    # laser_control.turn_on_all_lasers()
                    
                    # Ramp current to set bias
                    # utils.ramp_current(DC_unit, 0, vcsel_array_bias)
                    
                    print(f'Taking Picture No {frame_counter}')
                    # Grab picture from Hamamatsu
                    image = grab_image(camera, frame_average, measurement_subinterval, frame_average_buffer)
                        # 
                    # threading.Thread(target=thread_function, args=(1,))
                    # Ramp down current
                    # utils.ramp_current(DC_unit, vcsel_array_bias, 0)
                    
                    # Turn off switch to lasers
                    laser_control.turn_off_all_lasers()
                    
                    image_capture_time = time.time()
                        
                    SPR_process_image(spr_figure,\
                                      image, results, \
                                      image_capture_time, \
                                      measurement_time_start, frame_counter, IPV_config,\
                                      y_max_index, ref_spectrums, use_reference_spectrum)
    
                    spr_figure.update_spr_trace(lasers_on_chip, results, COLORS, frame_counter)

                    duration = time.time() - start_time
                    total_duration += duration
                    print(f'Picture grabbing and processing took: {duration:.2f} s')
                    
                    # Wait until set time for the measurement
                    print(f'Will sleep for: {(measurement_interval - total_duration if total_duration < measurement_interval else 0):.2f} s')
                    print('----------------------------------')
                    time.sleep(measurement_interval - total_duration if total_duration < measurement_interval else 0)
                    frame_counter += 1  
                    
                    
                    if (save_data) and (periodic_saving) and ((time.time() - measurement_time_start)>saving_interval*save):
                        saving_results(IPV_config, results, measurement_timestamp)
                        save+=1
                        gc.collect()
                    
                # Clean up of all started threads after each round of pictures
                # image_processing_thread.join()
                    
                    
            except KeyboardInterrupt:
                print("Keyboard interrupt detected, stopping.")
                break
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
    for laser in results['frame_list'].items():
        laser = laser[0]
        
        frame_list = results['frame_list'][laser]
        frame_time = results['frame_time'][laser]
        spr_data   = results['spr_data'][laser]
        
        save_folder_current_VCSEL = Path(save_path_current_measurement,
                                          f'VCSEL_{laser}')
        
        if not os.path.isdir(save_folder_current_VCSEL):
            os.mkdir(save_folder_current_VCSEL)
            
        if IPV_config["save_raw_images"]:
            for i, im in enumerate(frame_list):      
                iio.imwrite(os.path.join(save_folder_current_VCSEL, 
                                          f'{SPR_measurement_name}_image{i}.png'), im)
        
        if not len(frame_time) == len(spr_data):
            if len(frame_time) > len(spr_data):
                frame_time = frame_time[:-1]
            else:
                spr_data = spr_data[:-1]
                
        xy = np.vstack((frame_time, spr_data)).T
        np.savetxt(os.path.join(save_folder_current_VCSEL, 'data.txt'), xy, 
                    delimiter=',') 
        
    fig_object = results['fig_object']
    fig_object.savefig(os.path.join(save_path_current_measurement, 
                                    f'{SPR_measurement_name}_data.png'))
    
