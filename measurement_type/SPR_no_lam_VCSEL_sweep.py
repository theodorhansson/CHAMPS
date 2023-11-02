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

    results = SPR_no_lam_sweep_main(IPV_config_opt, DC_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}
    return results, return_dict

def grab_image(camera, frame_avg=10):
    captured_frames = []
    with Stream(camera, frame_avg) as stream:
        # logging.info("start acquisition")
        camera.start()                       
        for i, frame_buffer in enumerate(stream): 
            fr = copy_frame(frame_buffer)
            captured_frames.append(fr)                         
            # logging.info(f"acquired frame #%d/%d", i+1, frame_avg)                        
        camera.stop()    
        # logging.info("finished acquisition")   
    mean_frame = np.mean(captured_frames, axis=0).astype(int)
    return mean_frame

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
    spr_figure = SPR_figure()
    results["fig_object"] = spr_figure.fig
    
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

    # Start live capturing stop with q and start measuring
    # if find_det_lines:
    #     dcam_live_capturing(exposure_time=exposure_time)
    
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
            # if find_line_biased:
            #     dcam_live_capturing(exposure_time=exposure_time)
        
            utils.ramp_current(DC_unit, check_bias, 0)
            laser_control.turn_off_all_lasers()
            
            #TODO: What if we put camera into the main measurement while loop?
            with dcam:
                camera = dcam[0]
                
                with camera:
                    # print(camera.info)
                    # print(camera['image_width'].value, camera['image_height'].value)
                    ### set camera exposure time
                    camera["exposure_time"] = exposure_time 
                    
                    
                    laser_control.turn_on_all_lasers()

                    utils.ramp_current(DC_unit, 0, find_laser_lines_bias)
                    image = grab_image(camera, frame_avg=frame_average)

                    utils.ramp_current(DC_unit, find_laser_lines_bias, 0)
                    laser_control.turn_off_all_lasers()
                    
                    laser_lines_index = find_laser_lines(image, manual=manual_lines)
                    print('Found ' + str(len(laser_lines_index)) + ' lasers')
                    
                    # Start time of measurement
                    measurement_time_start = time.time()
                    measurement_timestamp = time.strftime(rf"%Y%m%d_%H.%M.%S")
                    
                    # Frame counter
                    frame_counter = 0
                    
                    # Main measurement loop
                    while (time.time() - measurement_time_start) < measurement_time:
                    
                        total_duration = 0
                        # print(f'Taking Picture No {frame_counter}')
                        # for i, laser in enumerate(lasers_on_chip):
                        start_time = time.time()
                        # Active switch for current laser
                        laser_control.turn_on_all_lasers()
                        
                        # Ramp current to set bias
                        utils.ramp_current(DC_unit, 0, vcsel_biases[0])
                        
                        print(f'Taking Picture No {frame_counter}')
                        # Grab picture from Hamamatsu
                        # image = dcam_capture_average_image(frame_average, exposure_time=exposure_time)
                        image = grab_image(camera, frame_avg=frame_average)
                        
                        # Ramp down current
                        utils.ramp_current(DC_unit, vcsel_biases[0], 0)
                        
                        # Turn off switch to lasers
                        laser_control.turn_off_all_lasers()
                        
                        image_capture_time = time.time()
                        
                        if bias_sweep:
                            for i in range(len(sweep_biases)):
                                DC_unit.set_current(sweep_biases[i])
                                image += grab_image(camera, frame_avg=frame_average)
                                
                            image = image/len(sweep_biases)
                            DC_unit.set_current(vcsel_biases[0])
                            
                 
                        image_width_pixels = 100
                        for i, line_index in enumerate(laser_lines_index):
                            cropped_image = image[line_index-image_width_pixels//2:laser_lines_index[i]+image_width_pixels//2, :]
                            SPR_process_image(i, spr_figure, i, cropped_image, results, image_capture_time, measurement_time_start, frame_counter, IPV_config)
                            # image_processing_thread = threading.Thread(target=SPR_process_image(i, spr_figure, i, cropped_image, results, image_capture_time, measurement_time_start, frame_counter, IPV_config))
                            # image_processing_thread.start()
                        
                        
                        # Update inline plot with measurement status
                        for channels in lasers_on_chip:
                            spr_figure.fig.axes[4].plot(results['frame_time'][channels], results['spr_data'][channels], 
                                                  marker='o', linewidth=0.2, markersize=3, 
                                                  color=COLORS[channels], label=f'Laser {channels}') 
                            
                        
                            if frame_counter==0: 
                                spr_figure.fig.axes[4].legend(loc='upper right')
                            
                        plt.show(False)  
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
                        # Clean up of all started threads after each round of pictures
                        # image_processing_thread.join()
                    
                    
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
    
