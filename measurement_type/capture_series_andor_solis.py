# Import CHAMPS module for GPIB connections
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
    """
    Capture a series of images with hardware-controlled timing (grab),
    then save them sequentially.
    """
    # Load parameters
    V_max          = measurement_config['v_max']
    verbose        = measurement_config['verbose']
    exposure_time  = measurement_config['exposure_time'] * 1e-3   # ms → s
    num_images     = measurement_config.get('num_images', 5)
    time_spacing   = measurement_config.get('time_spacing', None)  # optional

    camera_number = Andor.get_cameras_number_SDK3()
    if camera_number:
        print('Found camera: ' + str(camera_number))

    start_time = time.time()

    with Andor.AndorSDK3Camera(idx=0) as camera:
        camera.set_exposure(exposure_time)
        camera.set_roi(0, 2048, 0, 2028, hbin=2, vbin=2)

        if verbose:
            print(f"Starting acquisition of {num_images} images...")

        if time_spacing is not None and time_spacing > exposure_time:
            try:
                camera.set_attribute_value("CycleTime", time_spacing)
            except Exception as e:
                print(f"Warning: Time spacing is too small, using exposure time instead. ({e})")

        # Grab all frames at once (hardware-timed)
        images = camera.grab(nframes=num_images, frame_timeout=5.0)

        if verbose:
            print(f"Grabbed {len(images)} images in {time.time() - start_time:.2f} s")

    # Save AFTER acquisition
    for i, img in enumerate(images, start=1):
        save_measurements(img, meas_output_dir_path, i)

    if verbose:
        print(f"Finished saving {len(images)} images")

    return 0


def save_measurements(image, meas_output_dir_path, idx):
    """
    Save image as binary .npy file (much faster than .txt).
    """
    output_dir = Path(meas_output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"image_{idx}.npy"
    np.save(file_path, image)  # fast binary save

    return file_path

    
