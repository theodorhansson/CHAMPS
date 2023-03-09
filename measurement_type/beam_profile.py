import communication
import traceback
import sys

# Dumb code to import utils
try:
    import utils
except:
    import sys, pathlib

    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils


_beam_name_key = "beam_unit"
_DC_name_key = "dc_unit"
_required_arguments = [
    "type",
    "beam_unit",
    "dc_unit",
    "current",
    "v_max",
]
_optional_arguments = {
    "verbose_printing": 0,
    "plot_image": False,
}


def init(full_config: dict):
    beam_config = full_config["measurement"]  # Extract dict

    # Check and merge optional arguments
    utils.argument_checker(
        beam_config,
        _required_arguments,
        _optional_arguments,
        source_func="Beam init",
    )
    spectrum_config_opt = utils.optional_arguments_merge(
        beam_config, _optional_arguments
    )

    # Extract dict and parameter from dict
    beam_name = full_config[_beam_name_key]
    DC_name = beam_config[_DC_name_key]
    DC_config = full_config[DC_name]

    Results = beam_main(beam_config, DC_config)

    return_dict = {
        beam_name: spectrum_config_opt,
        DC_name: DC_config,
    }
    return Results, return_dict


def beam_main(beam_config: dict, DC_config: dict):
    current_intervals = beam_config["current"]
    V_max = beam_config["V_max"]
    verbose = beam_config["verbose_printing"]

    current_interval_list = utils.interval_2_points(current_intervals)
    Results = {"header": "Current [mA], Voltage [V], 'photon' count"}

    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    # Try to fetch the objects
    try:
        Instrument_COM = communication.Communication()
        beam_unit_obj = Instrument_COM.get_Beam(beam_config)  # Uninitiated objects
        DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)
    except:
        traceback.print_exc()
        print("Something went wrong when getting and opening the resources")
        sys.exit()

    # Main measurement loop
    try:
        with beam_unit_obj(beam_config) as beam_unit, DC_unit_obj(DC_config) as DC_unit:
            # Some initial settings for DC_unit
            DC_unit.set_current(0.0)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)

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

                    # Get image data
                    image = beam_unit.get_frame_data()

                    # Save data in dict
                    Results[loop_count] = dict()
                    Results[loop_count]["voltage"] = volt
                    Results[loop_count]["current"] = current
                    Results[loop_count]["current"] = image

                    if verbose & 1 + 2:
                        print("volt", volt)
                        print("current", current)
                    if verbose & 2:
                        print("image\n", image)

                    loop_count += 1

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, stopping.")
    except:
        traceback.print_exc()

    print("Spectrum measurements done.")
    return Results
