# Standard python imports
import numpy as np
import matplotlib.pyplot as plt
import time
from pathlib import Path

# Pylablib for andor connection
from pylablib.devices import Andor

# Import CHAMPS module for GPIB connections
import communication

# Import Aurora
from drivers.arduino_giga_serial.aurora import aurora

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
    time_spacing   = measurement_config.get('time_spacing', None)  # optionasl

    camera_number = Andor.get_cameras_number_SDK3()
    if camera_number:
        print('Found camera: ' + str(camera_number))

    start_time = time.time()
    
    ## Intialize connection to SMU --- SMU beeps if successfull
    Instrument_COM = communication.Communication()
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)
    
    ## Start connection to aurora switching
    ## Define which chips is used! -> Find chip maps in drivers/arduino_giga_serial_aurora.py
    vcsel_chip = 'lars'
    laser_switch = aurora(vcsel_chip)
    
    ## Start DC unit with "with" for automatic closure
    with DC_unit_obj(DC_config) as DC_unit:
        
        ## Start output of SMU
        DC_unit.set_current(0.0)
        DC_unit.set_voltage_limit(V_max)
        DC_unit.set_output(True)
        
        
        ## Do whatever you want
        ## Functions for SMU in equipment/keithley2400.py
        ## Fucntions for aurora in drivers/arduino_giga_serial_aurora.py
        
        current = 1
        
        time.sleep(1)
        
        ### DISCO!! ###
        
        for n in range(4):
            for i in range(4):
                laser_switch.turn_off_all_lasers()
                time.sleep(0.1)
                laser_switch.turn_on_all_lasers()
                utils.ramp_current(DC_unit, 0, current)
                time.sleep(0.1)
                
            for i in range(4):
                laser_switch.switch_to_laser(i)
                utils.ramp_current(DC_unit, 0, current)
                time.sleep(0.1)
                
            for i in range(4):
                for j in range(2):
                    laser_switch.switch_to_lasers([j, j+2])
                    utils.ramp_current(DC_unit, 0, current)
                    time.sleep(0.1)
        
    return 0


    
