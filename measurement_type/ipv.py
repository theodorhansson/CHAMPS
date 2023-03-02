import communication
import utils
import traceback


_DC_name_key = "dc_unit"
_P_name_key = "p_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "p_unit",
    "current",
    "v_max",
    "save_folder",
]
_optional_arguments = {
    "rollover_threshold": 0,
    "rollover_min": 0,
    "plot_interval": 20,
    "verbose_printing": 0,
}


def init(config: dict):
    # Get config dict and check for optional arguments
    IPV_config = config["measurement"]
    IPV_name = IPV_config["type"]
    # Check and merge optional arguments
    utils.argument_checker(
        IPV_config, _required_arguments, _optional_arguments, source_func="IPV init"
    )
    IPV_config_opt = utils.optional_arguments_merge(IPV_config, _optional_arguments)

    # Used for getting instrument objects and their names
    DC_name = IPV_config[_DC_name_key]
    DC_config = config[DC_name]
    P_name = IPV_config[_P_name_key]
    P_config = config[P_name]

    Results = ipv_main(IPV_config_opt, DC_config, P_config)

    # Get the used config and return it to main
    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config, P_name: P_config}
    return Results, return_dict


def ipv_main(IPV_config: dict, DC_config: dict, P_config: dict):
    # The main IPV function
    V_max = IPV_config["v_max"]
    plot_update_interval = IPV_config["plot_interval"]
    rollover_threshold = IPV_config["rollover_threshold"]
    rollover_min = IPV_config["rollover_min"]
    intervals = IPV_config["current"]
    verbose_printing = IPV_config["verbose_printing"]
    interval_list = utils.interval_2_points(intervals)

    # Create result dict
    Results = {
        "header": "Current[mA], Optical Power [mW], Voltage [V]",
        "voltage": [],
        "current": [],
        "power": [],
    }

    # Send verbose_printing to instruments if not specified
    for instru_dict in [DC_config, P_config]:
        if not instru_dict.has_key("verbose_printing"):
            instru_dict["verbose_printing"] = verbose_printing

    Plot = utils.AnimatedPlot("Current[mA]", "Optical Power [mW]", "IPV")
    Instrument_COM = communication.Communication()

    # Gets isntruments
    P_unit_obj = Instrument_COM.get_PowerUnit(P_config)
    DC_unit_obj = Instrument_COM.get_DCsupply(DC_config)

    with P_unit_obj(P_config) as P_unit, DC_unit_obj(DC_config) as DC_unit:
        try:
            # Set instrument to 0 for safety
            DC_unit.set_current(0.0)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)

            prev_end_current = 0

            # The main measurement loop
            for interval in interval_list:
                # Code to ramp current between intervals
                power_max = 0
                start_current = interval[0]
                utils.ramp_current(DC_unit, prev_end_current, start_current)
                prev_end_current = interval[-1]

                for loop_count, set_current in enumerate(interval):
                    DC_unit.set_current(set_current)

                    volt, current = DC_unit.get_voltage_and_current()
                    power = P_unit.get_power()

                    Results["voltage"].append(volt)
                    Results["current"].append(current)
                    Results["power"].append(power)

                    Plot.add_point(current, power)

                    if verbose_printing & 1:
                        print("IPV data", volt, current, power)

                    # Only plot sometimes
                    if loop_count % plot_update_interval == 0:
                        # approx 0.5s per measurement
                        Plot.update()
                    # Code to handle rollover functionality
                    if power > rollover_min:
                        power_max = max(power, power_max)
                    if power < (rollover_threshold * power_max) and rollover_threshold:
                        break
                Plot.update()

        except KeyboardInterrupt:
            print("Keyboard interrupt detected, stopping.")
        except:
            # print error if error isn't catched
            traceback.print_exc()

    print("IPV measurements done. Keeping plot alive for your convenience.")
    Plot.keep_open()

    return Results
