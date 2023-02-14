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
_P_name_key = "p_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "p_unit",
    "current",
    "v_max",
]
_optional_arguments = {"rollover_threshold": 0}


def init(config: dict):
    # Get config dict and check for optional arguments
    IPV_config = config["measurement"]
    IPV_name = IPV_config["type"]
    # Check and merge optional arguments
    argument_checker(IPV_config, _required_arguments, _optional_arguments)
    IPV_config_opt = optional_arguments_merge(IPV_config, _optional_arguments)

    # Used for getting instrument objects
    DC_name = IPV_config[_DC_name_key]
    DC_config = config[DC_name]
    P_name = IPV_config[_P_name_key]
    P_config = config[P_name]

    Results = ipv_main(IPV_config_opt, DC_config, P_config)

    return_dict = {IPV_name: IPV_config_opt, DC_name: DC_config, P_name: P_config}
    return Results, return_dict


def ipv_main(IPV_config: dict, DC_config: dict, P_config: dict):
    # Main measurement loop

    V_max = IPV_config["v_max"]
    rollover_threshold = IPV_config["rollover_threshold"]
    intervals = IPV_config["current"]
    interval_list = interval_2_points(intervals)

    plot = AnimatedPlot("Current[A]", "Optical Power [W]", "IPV")

    try:
        P_unit = communication.get_PowerUnit(P_config)
        DC_unit = communication.get_DCsupply(DC_config)
        Results = {"voltage": [], "current": [], "power": []}

        P_unit.open()
        DC_unit.open()
    except:
        print("Something went wrong when getting and opening the resources")
        exit()

    DC_unit.set_current(0.0)
    DC_unit.set_voltage_limit(V_max)
    DC_unit.set_output(True)

    try:
        power_max = 0
        prev_end_current = 0

        for interval in interval_list:
            start_current = interval[0]
            ramp_current(DC_unit, prev_end_current, start_current)
            prev_end_current = interval[-1]

            for set_current in interval:
                DC_unit.set_current(set_current)

                volt = DC_unit.get_voltage()
                current = DC_unit.get_current()
                power = P_unit.get_power()

                Results["voltage"].append(volt)
                Results["current"].append(current)
                Results["power"].append(power)
                plot.add_point(current, power)
                print("IPV data", volt, current, power)

                if power > power_max:
                    power_max = power
                if power < (rollover_threshold * power_max) and rollover_threshold:
                    break

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
        P_unit.close()

    plot.keep_open()

    return Results
