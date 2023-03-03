import communication
import utils
import numpy as np
import traceback
import sys

_DC_name_key = "dc_unit"
_OSA_name_key = "osa_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "osa_unit",
    "current",
    "v_max",
    "save_folder",
    "center_wavelength",
    "linear_resolution",
    "wavelength_span",
    "sample_points",
]
_optional_arguments = {
    "avg_factor": 5,
    "sensitivity": "SHI1",
    "verbose_printing": 0,
}


def init(config: dict):
    # Get config dict and check for optional arguments
    spectrum_config = config["measurement"]
    spectrum_name = spectrum_config["type"]
    # Check and merge optional arguments
    utils.argument_checker(
        spectrum_config,
        _required_arguments,
        _optional_arguments,
        source_func="Spectrum init",
    )
    spectrum_config_opt = utils.optional_arguments_merge(
        spectrum_config, _optional_arguments
    )

    # Used for getting instrument objects
    DC_name = spectrum_config[_DC_name_key]
    DC_config = config[DC_name]
    OSA_name = spectrum_config[_OSA_name_key]
    OSA_config = config[OSA_name]

    Results = spectrum_main(spectrum_config_opt, DC_config, OSA_config)

    return_dict = {
        spectrum_name: spectrum_config_opt,
        DC_name: DC_config,
        OSA_name: OSA_config,
    }
    return Results, return_dict


def spectrum_main(spectrum_config: dict, DC_config: dict, OSA_config: dict):
    V_max = spectrum_config["v_max"]
    current_intervals = spectrum_config["current"]
    verbose = spectrum_config["verbose_printing"]
    current_interval_list = utils.interval_2_points(current_intervals)
    Results = {
        "header": "Current [mA], Voltage [V], Wavelengths [nm], Intensities [dB]"
    }

    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config, OSA_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    # Try to fetch the objects
    try:
        Instrument_COM = communication.Communication()
        OSA_unit_obj = Instrument_COM.get_OSA(OSA_config)
        DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)
    except:
        traceback.print_exc()
        print("Something went wrong when getting and opening the resources")
        sys.exit()

    try:
        with OSA_unit_obj(OSA_config) as OSA_unit, DC_unit_obj(DC_config) as DC_unit:

            # Some initial settings for DC_unit
            DC_unit.set_current(0.0)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)

            # Some initial settings for OSA_unit
            OSA_unit.set_center_wavelength_nm(spectrum_config["center_wavelength"])
            OSA_unit.set_wavelength_span_nm(spectrum_config["wavelength_span"])
            OSA_unit.set_sensitivity(spectrum_config["sensitivity"])
            OSA_unit.set_linear_resolution_nm(spectrum_config["linear_resolution"])
            OSA_unit.set_avg_factor(spectrum_config["avg_factor"])
            OSA_unit.set_sample_points(spectrum_config["sample_points"])

            prev_end_current = 0  # For first ramp up
            loop_count = 0  # The number of

            for interval in current_interval_list:
                # Ramp current between intervals
                start_current = interval[0]
                utils.ramp_current(DC_unit, prev_end_current, start_current)
                prev_end_current = interval[-1]

                for set_current in interval:
                    # Set bias current
                    DC_unit.set_current(set_current)
                    volt = DC_unit.get_voltage()
                    current = DC_unit.get_current()

                    # Start OSA and get data
                    OSA_unit.do_single_scan()
                    spectrum = OSA_unit.get_intensity_data_A_dBm()  # TODO: units? Type?
                    wavelength_axis = OSA_unit.get_wavelength_axis()

                    # Save the data in a dict
                    Results[loop_count] = dict()
                    Results[loop_count]["voltage"] = volt
                    Results[loop_count]["current"] = current
                    Results[loop_count]["intensities"] = spectrum
                    Results[loop_count]["wavelength_axis"] = wavelength_axis
                    loop_count += 1

                    if verbose & 1 + 2:
                        print("volt", volt)
                        print("current", current)
                    if verbose & 2:
                        print("spectrum\n", spectrum)
                        print("wavelength_axis\n", wavelength_axis)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, stopping.")
    except:
        traceback.print_exc()

    print("Spectrum measurements done.")
    return Results
