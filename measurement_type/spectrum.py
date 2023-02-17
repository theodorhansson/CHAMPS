import communication
from utils import (
    argument_checker,
    AnimatedPlot,
    interval_2_points,
    optional_arguments_merge,
    ramp_current,
)
import numpy as np
import traceback

_DC_name_key = "dc_unit"
_OSA_name_key = "osa_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "osa",
    "current",
    "v_max",
    "save_folder",
    "center_wavelength",
    "linear_resoultion",
    "Wavelength_span",
]
_optional_arguments = {
    "sampel_points": 0,
    "avg_factor": 5,
}


def init(config: dict):
    # Get config dict and check for optional arguments
    spectrum_config = config["measurement"]
    spectrum_name = spectrum_config["type"]
    # Check and merge optional arguments
    argument_checker(
        spectrum_config,
        _required_arguments,
        _optional_arguments,
        source_func="Spectrum init",
    )
    spectrum_config_opt = optional_arguments_merge(spectrum_config, _optional_arguments)

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
    current_interval_list = interval_2_points(current_intervals)

    # plot = AnimatedPlot("Current[A]", "Optical Power [W]", "IPV") TODO: keep?
    Instrument_COM = communication.Communication()

    try:
        OSA_unit = Instrument_COM.get_OSA(OSA_config)
        DC_unit = Instrument_COM.get_DCsupply(DC_config)
        Results = {"voltage": [], "current": [], "spectrum": []}

        OSA_unit.open()
        DC_unit.open()
    except:
        traceback.print_exc()
        print("Something went wrong when getting and opening the resources")
        exit()

    DC_unit.set_current(0.0)
    DC_unit.set_voltage_limit(V_max)
    DC_unit.set_output(True)

    OSA_unit.set_center_wavelength_nm(spectrum_config["center_wavelength"])
    OSA_unit.set_wavelength_span_nm(spectrum_config["span"])
    OSA_unit.set_sensitivity(spectrum_config["sensitivity"])
    OSA_unit.set_linear_resolution_nm(spectrum_config["linear_resolution"])
    OSA_unit.set_avg_factor(spectrum_config["avg_factor"])
    OSA_unit.set_sample_points(spectrum_config["sampel_points"])

    try:
        prev_end_current = 0

        for interval in current_interval_list:
            start_current = interval[0]
            ramp_current(DC_unit, prev_end_current, start_current)
            prev_end_current = interval[-1]

            for set_current in interval:
                DC_unit.set_current(set_current)

                volt = DC_unit.get_voltage()
                current = DC_unit.get_current()
                spectrum = OSA_unit.get_wavelength_data_A()  # TODO: units? Type?

                Results["voltage"].append(volt)
                Results["current"].append(current)
                Results["spectrum"].append(spectrum)
                # plot.add_point(current, power)
                # print("IPV data", volt, current, power)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, stopping.")
    except:
        traceback.print_exc()
    finally:
        # Tries to shut down instruments
        ramp_current(DC_unit, DC_unit.get_current(), 0)
        DC_unit.set_current(0)
        DC_unit.set_output(False)
        DC_unit.close()
        OSA_unit.close()

    print("Spectrum measurements done. Keeping plot alive for your convenience.")
    # plot.keep_open()

    return Results
