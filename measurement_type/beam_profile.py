import communication
import traceback
import sys
import PIL.Image
import numpy as np
from pathlib import Path

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
    "save_folder",
    "custom_name",
]
_optional_arguments = {
    "verbose_printing": 0,
    "plot_image": 0,
    "keep_plot": 0,
    "hold_console": 1,
    "save_to_png": 1,
}


def init(full_config: dict):
    beam_meas_config = full_config["measurement"]  # Extract dict

    # Check and merge optional arguments
    utils.argument_checker(
        beam_meas_config,
        _required_arguments,
        _optional_arguments,
        source_func="Beam init",
    )
    beam_meas_config = utils.optional_arguments_merge(
        beam_meas_config, _optional_arguments
    )

    # Extract name and parameter from dict
    beam_meas_name = beam_meas_config["type"]
    beamgage_name = full_config["measurement"][_beam_name_key]
    beamgage_config = full_config[beamgage_name]
    DC_name = beam_meas_config[_DC_name_key]
    DC_config = full_config[DC_name]

    Results = beam_main(beam_meas_config, DC_config, beamgage_config)

    return_dict = {
        beam_meas_name: beam_meas_config,
        beamgage_name: beamgage_config,
        DC_name: DC_config,
    }
    return Results, return_dict


def beam_main(beam_config: dict, DC_config: dict, beamgage_config: dict):
    current_intervals = beam_config["current"]
    V_max = beam_config["v_max"]
    plot_image = beam_config["plot_image"]
    keep_plot = beam_config["keep_plot"]
    hold_console = beam_config["hold_console"]
    verbose = beam_config["verbose_printing"]
    save_to_png = beam_config["save_to_png"]
    save_folder = beam_config["save_folder"]
    custom_name = beam_config["custom_name"]

    current_interval_list = utils.interval_2_points(current_intervals)
    Results = {"header": "Current [mA], Voltage [V], 'photon' count"}

    for instru_dict in [DC_config]:
        if "verbose_printing" not in instru_dict.keys():
            instru_dict["verbose_printing"] = verbose

    # Try to fetch the objects
    try:
        Instrument_COM = communication.Communication()
        beam_unit_obj = Instrument_COM.get_Beam(beamgage_config)  # Uninitiated objects
        DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)
    except:
        traceback.print_exc()
        print("Something went wrong when getting and opening the resources")
        sys.exit()

    # Main measurement loop
    try:
        with beam_unit_obj(beamgage_config) as beam_unit, DC_unit_obj(
            DC_config
        ) as DC_unit:
            if hold_console:
                input(
                    "Configure settings in other software, press any key to continue: "
                )

            if plot_image:
                Plot = utils.AnimatedPlot(title="Beam profile")

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
                    Results[loop_count]["current"] = current
                    Results[loop_count]["voltage"] = volt

                    if save_to_png:
                        file_name = custom_name + "_" + str(loop_count) + ".png"
                        save_path = str(Path(save_folder, file_name))
                        image = np.array(image)
                        # image = np.left_shift(image, 4) # Image from beamgage is 12 bit. Bitshift for better png
                        image_obj = PIL.Image.fromarray(image)
                        image_obj.save(save_path, format="png", bit_depth=16)
                    else:
                        Results[loop_count]["photon_count"] = image

                    if plot_image:
                        Plot.add_image(image)

                    if verbose & 1:
                        print("volt", volt)
                        print("current", current)
                    if verbose & 2:
                        print("image\n", image)

                    loop_count += 1

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, stopping.")
    except:
        traceback.print_exc()

    # To hold plot open when measurement done
    if keep_plot and plot_image:
        print("Beam measurements done. Keeping plot alive for your convenience.")
        Plot.keep_open()
    else:
        print("Beam measurements done. Vaporizing plot!")

    return Results
