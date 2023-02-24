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
_optional_arguments = {"rollover_threshold": 0, "rollover_min": 0, "plot_interval": 20}


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
    interval_list = utils.interval_2_points(intervals)

    Plot = utils.AnimatedPlot("Current[mA]", "Optical Power [mW]", "IPV")
    Instrument_COM = communication.Communication()

    try:
        # Attempts to get instruments
        P_unit = Instrument_COM.get_PowerUnit(P_config)
        DC_unit = Instrument_COM.get_DCsupply(DC_config)
        Results = {"voltage": [], "current": [], "power": []}

        P_unit.open()
        DC_unit.open()
    except:
        traceback.print_exc()
        print("Something went wrong when getting and opening the resources")
        exit()

    # Set instrument to 0 for safety
    DC_unit.set_current(0.0)
    DC_unit.set_voltage_limit(V_max)
    DC_unit.set_output(True)

    # The main measurement loop
    try:
        prev_end_current = 0

        for interval in interval_list:
            # Code to ramp current between intervals
            power_max = 0
            start_current = interval[0]
            utils.ramp_current(DC_unit, prev_end_current, start_current)
            prev_end_current = interval[-1]

            for count, set_current in enumerate(interval):
                DC_unit.set_current(set_current)

                volt, current = DC_unit.get_voltage_and_current()
                power = P_unit.get_power()

                Results["voltage"].append(volt)
                Results["current"].append(current)
                Results["power"].append(power)
                Plot.add_point(current, power)
                print("IPV data", volt, current, power)

                # Code to handle rollover functionality
                if count % plot_update_interval == 0:  # approx 0.5s per measurement
                    Plot.update()
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
    finally:
        # Safely shut down instrument, even if error is detected
        utils.ramp_current(DC_unit, DC_unit.get_current(), 0)
        DC_unit.set_current(0)
        DC_unit.set_output(False)
        DC_unit.close()
        P_unit.close()

    print("IPV measurements done. Keeping plot alive for your convenience.")
    Plot.keep_open()

    return Results
