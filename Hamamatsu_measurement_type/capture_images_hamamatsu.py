import os, sys
if os.path.dirname(os.path.dirname(os.path.realpath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


# Import hamamatsu python drivers
from drivers.dcam_hamamatsu.dcam_live_capturing_ROI import dcam_live_capturing
from drivers.dcam_hamamatsu.dcam_capture_single_image import dcam_capture_image

import general_functions.pretty_printing.verbose_printing as vp
import general_functions.files_and_folders.ffp_functions as ffp

# Python modules
import traceback
import numpy as np
import time
from pathlib import Path
import keyboard


import matplotlib.pyplot as plt
from matplotlib.figure import Figure
    
    
x_pixel = 2048
y_pixel = 2048
# Dumb code to import utils
try:
    import utils
except:
    import sys, pathlib

    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils

_required_arguments = [
    'type',
]
_optional_arguments = {
}


def init(config: dict, meas_output_dir_path: str):
    # Get config dict and check for optional arguments
    config = config['measurement']
    
    meas_type = config['type']
    
    # Check and merge optional arguments
    utils.argument_checker(
        config, _required_arguments, _optional_arguments, source_func=meas_type
    )
    used_config = utils.optional_arguments_merge(config, _optional_arguments)

    ## Run measurement
    results = measurement_main(config, meas_output_dir_path)
    
    return used_config


def measurement_main(config: dict, meas_output_dir_path: str):
    
    exposure_time = config['exposure_time']
    mirror_x = config['mirror_x']
    mirror_y = config['mirror_y']
    transpose = config['transpose']
    
    save_images = config['save_images']
    
    # ROI = [np.array([1000, 1000, 500, 500]), np.array([1500, 1400, 500, 500])]
    
    ROI_config = config['roi']
    ROI = []
    for roi in ROI_config:
        ROI.append(np.array([roi[0], -roi[1], roi[2], roi[3]]))
    
    vp.headline('Opening livestream - press q to quit' )
    dcam_live_capturing(ROI, mirror_x, mirror_y, transpose, exposure_time=exposure_time)
    
    counter = 0
    while True:
        vp.headline('Wating to take image - press c for capturing' )
        key = keyboard.read_key()
        if key == 'c':
            vp.message('Capturing image')
            
            image = dcam_capture_image(mirror_x, mirror_y, transpose, exposure_time=exposure_time)
            
            image_dir_path = ffp.create_measurement_save_folder(meas_output_dir_path, 'image_' + str(counter))
            
            full_image_save_path_txt = Path(image_dir_path, 'full_image_' + str(counter) + '.txt')
            
            np.savetxt(full_image_save_path_txt, image)
            
            roi_counter = 0
            roi_images = []
            for roi in ROI:
                roi_image_save_path_txt = Path(image_dir_path, 'roi_' + str(roi_counter) + '_image_' + str(counter) + '.txt')
                    
                pos_x = roi[0]
                pos_y = roi[1]
                width = roi[2]
                height = roi[3]
                
                roi_image = image[pos_y - height//2:pos_y + height//2, 
                                  pos_x - width//2:pos_x + width//2]
                roi_images.append(roi_image)
                np.savetxt(roi_image_save_path_txt, roi_image)
                roi_counter += 1
                                
            if save_images:
                full_image_save_path_png = Path(image_dir_path, 'full_image_' + str(counter) + '.png')
                figure = Figure()
                ax = figure.add_subplot(1, 1, 1)
                ax.imshow(image)
                figure.savefig(full_image_save_path_png)
                
                for i, roi_image in enumerate(roi_images):
                    roi_image_save_path_png = Path(image_dir_path, 'roi_' + str(i) + '_image_' + str(counter) + '.png')
                    figure = Figure()
                    ax = figure.add_subplot(1, 1, 1)
                    ax.imshow(roi_image)
                    figure.savefig(roi_image_save_path_png)
                    
                
            vp.message('Successfully saved image: ' + str(counter))
            counter += 1
            
        if key == 'q':
            vp.headline('Shutting down')
            break
    
    results = {}
    return results

# def saving_results(IPV_config, results, measurement_timestamp):
            
#     parent_path = Path(__file__).resolve().parents[1]
#     save_folder_path = Path(parent_path, IPV_config['save_folder'])
#     if not os.path.isdir(save_folder_path):
#         print('Woops, your folder doesn't exist. Creating one here: ', save_folder_path)
#         os.mkdir(save_folder_path)
#     SPR_measurement_name = IPV_config['spr_measurement_name']
#     measurement_timestamp = measurement_timestamp + '_' + SPR_measurement_name
#     save_path_current_measurement = os.path.join(save_folder_path, 
#                                                   measurement_timestamp)
#     if not os.path.isdir(save_path_current_measurement):
#         os.mkdir(save_path_current_measurement)
    
#     print('Saving Images')
#     print(f'Saving Data to {save_path_current_measurement}')
#     for laser in results['frame_list'].items():
#         laser = laser[0]
        
#         frame_list = results['frame_list'][laser]
#         frame_time = results['frame_time'][laser]
#         spr_data   = results['spr_data'][laser]
        
#         save_folder_current_VCSEL = Path(save_path_current_measurement,
#                                           f'VCSEL_{laser}')
        
#         if not os.path.isdir(save_folder_current_VCSEL):
#             os.mkdir(save_folder_current_VCSEL)
            
#         if IPV_config['save_raw_images']:
#             for i, im in enumerate(frame_list):      
#                 iio.imwrite(os.path.join(save_folder_current_VCSEL, 
#                                           f'{SPR_measurement_name}_image{i}.png'), im)
        
#         if not len(frame_time) == len(spr_data):
#             if len(frame_time) > len(spr_data):
#                 frame_time = frame_time[:-1]
#             else:
#                 spr_data = spr_data[:-1]
                
#         xy = np.vstack((frame_time, spr_data)).T
#         np.savetxt(os.path.join(save_folder_current_VCSEL, 'data.txt'), xy, 
#                     delimiter=',') 
        
#     fig_object = results['fig_object']
#     fig_object.savefig(os.path.join(save_path_current_measurement, 
#                                     f'{SPR_measurement_name}_data.png'))
    
