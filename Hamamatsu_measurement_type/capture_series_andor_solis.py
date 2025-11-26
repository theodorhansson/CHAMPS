# Import CHAMPS module for GPIB connections
import communication

import numpy as np
import matplotlib.pyplot as plt
import time
from pathlib import Path

from pylablib.devices import Andor

# Import meta-SPR
# from spr_functions.main_spr import process_image, init_figure, analyze_image

# Python modules
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

_DC_name_key = 'dc_unit'
_required_arguments = [
    'type',
    'dc_unit',
    'v_max',
    'save_folder',
    'measurement_name',
]
_optional_arguments = {
    'verbose_printing': 0,
}

def init(config: dict, meas_output_dir_path: str):
    # Get config dict and check for optional arguments
    measurement_config = config['measurement']
    
    # Check and merge optional arguments
    utils.argument_checker(
        measurement_config, _required_arguments, _optional_arguments, source_func='IPV init'
    )
    measurement_config_opt = utils.optional_arguments_merge(measurement_config, _optional_arguments)

    # Used for getting instrument objects and their names
    DC_name = measurement_config[_DC_name_key]
    DC_config = config[DC_name]

    results = measurement_script(measurement_config, DC_config, meas_output_dir_path)

    # # Get the used config and return it to main
    # return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config}

    Results = {}
    return_dict = {}
    
    return Results, return_dict


def measurement_script(measurement_config: dict, DC_config: dict, meas_output_dir_path):

    
    cam = Andor.AndorSDK3Camera(idx=0)
    
    # open the first camera
    cam.open()
    
    # List all available attributes
    print(cam.get_all_attributes())
    
    # ROI format: (x_start, x_size, y_start, y_size, x_bin, y_bin)
    cam.set_roi(0, 2048, 0, 2048, 1, 1)
    cam.set_attribute_value("PixelEncoding", "Mono16")


    # Query specific attributes
    print("Detector size:", cam.get_detector_size())  # convenience method
    print("ROI:", cam.get_roi())
    print("Pixel encoding:", cam.get_attribute_value("PixelEncoding"))
    print("AOI width:", cam.get_attribute_value("AOIWidth"))
    print("AOI height:", cam.get_attribute_value("AOIHeight"))
    print("AOI stride:", cam.get_attribute_value("AOIStride"))
    print("Image size (bytes):", cam.get_attribute_value("ImageSizeBytes"))
    
    # Close when done
    cam.close()
    

    # The main IPV function
    V_max   = measurement_config['v_max']
    verbose = measurement_config['verbose']
    
    exposure_time = measurement_config['exposure_time']*1e-3
    
    camera_number = Andor.get_cameras_number_SDK3()
    if camera_number:
        print('Found camera: ' + str(camera_number))
    
    # vp.headline('Sucessfully loaded config for ' + meas_name)
    
    start_time = time.time()
    
    with Andor.AndorSDK3Camera(idx=0) as camera:
        camera.set_exposure(exposure_time)
        
        start_up_camera = time.time()
        
        camera.set_roi(0, 2048, 0, 2028, hbin=2, vbin=2)
        # image_list = camera.grab(nframes=6, 
                            # frame_timeout=5., 
                            # missing_frame="skip", 
                            # return_info=False, 
                            # buff_size=None)
                            
        #camera.set_attribute_value("PixelEncoding", "Mono16")
        
        image_taken = time.time()
        
        images = camera.grab(nframes=5, frame_timeout=5) # image series (list)
        #image = camera.snap(timeout=5) # one image
        
        plt.imshow(images[3])
        if verbose:
            print('Comparing start up of camera versus taking images')
            print("Starting up camera: ", start_up_camera - start_time)
            print("Capuring image: ", image_taken - start_up_camera)
            print("Total time: ", image_taken - start_time)

            

    save_measurements(images[3], meas_output_dir_path)
    results = 0
    return results

def save_measurements(image, meas_output_dir_path):
    print(meas_output_dir_path)
    
    filename = 'image1.txt'
    file_path = Path(meas_output_dir_path, filename)
    np.savetxt(file_path, image)
    
    
    
