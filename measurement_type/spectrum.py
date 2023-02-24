import communication
import utils
import numpy as np
import traceback

_DC_name_key = "dc_unit"
_OSA_name_key = "osa_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "current",
    "v_max",
    "save_folder",
    "center_wavelength",
    "linear_resolution",
    "wavelength_span",
    "sample_points",
]
_optional_arguments = {"avg_factor": 5, "sensitivity": "SHI1"}


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
    current_interval_list = utils.interval_2_points(current_intervals)
    Results = {"voltage": [], "current": [], "intensities": [], "wavelengths": []}

    # plot = AnimatedPlot("Current[A]", "Optical Power [W]", "IPV") TODO: keep?

    try:
        Instrument_COM = communication.Communication()
        OSA_unit_obj = Instrument_COM.get_OSA(OSA_config)
        DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)
    except:
        traceback.print_exc()
        print("Something went wrong when getting and opening the resources")
        exit()

    try:
        with OSA_unit_obj as OSA_unit, DC_unit_obj as DC_unit:

            DC_unit.set_current(0.0)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)

            OSA_unit.set_center_wavelength_nm(spectrum_config["center_wavelength"])
            OSA_unit.set_wavelength_span_nm(spectrum_config["wavelength_span"])
            OSA_unit.set_sensitivity(spectrum_config["sensitivity"])
            OSA_unit.set_linear_resolution_nm(spectrum_config["linear_resolution"])
            OSA_unit.set_avg_factor(spectrum_config["avg_factor"])
            OSA_unit.set_sample_points(spectrum_config["sample_points"])

            prev_end_current = 0

            for interval in current_interval_list:
                start_current = interval[0]
                utils.ramp_current(DC_unit, prev_end_current, start_current)
                prev_end_current = interval[-1]

                for set_current in interval:
                    DC_unit.set_current(set_current)

                    volt = DC_unit.get_voltage()
                    current = DC_unit.get_current()
                    OSA_unit.do_single_scan()
                    spectrum = OSA_unit.get_intensity_data_A_dBm()  # TODO: units? Type?
                    wavelength_axis = OSA_unit.get_wavelength_axis()

                    Results["voltage"].append(volt)
                    Results["current"].append(current)
                    Results["intensities"].append(spectrum)
                    Results["wavelengths"].append(wavelength_axis)
                    # plot.add_point(current, power)
                    # print("IPV data", volt, current, power)
        utils.ramp_current(DC_unit, DC_unit.get_current(), 0)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, stopping.")
    except:
        traceback.print_exc()

    # print("Spectrum measurements done. Keeping plot alive for your convenience.")
    # plot.keep_open()

    return Results
