import communication
from utils import argument_checker, AnimatedPlot, interval_2_points
import numpy as np
import traceback
import time
from utils import *


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


def init(config):
    optional_config = argument_checker(
        config["measurement"], _required_arguments, _optional_arguments
    )
    # Used for getting instrument objects
    DC_name = config["measurement"][_DC_name_key]
    DC_config = config[DC_name]

    P_name = config["measurement"][_P_name_key]
    P_config = config[P_name]

    print("DC_config", DC_config)

    Results = ipv_main(config, DC_config, P_config, optional_config)
    return Results


def ipv_main(config, DC_config, P_config, optional_config=_optional_arguments):
    # Main measurement loop
    print(config)

    V_max = config["measurement"]["v_max"]
    rollover_threshold = optional_config["rollover_threshold"]
    intervals = config["measurement"]["current"]
    interval_list = interval_2_points(intervals)

    plot = AnimatedPlot("Voltage[V]", "Optical Power [W]", "IPV")

    P_unit = communication.get_PowerUnit(P_config)
    DC_unit = communication.get_DCsupply(DC_config)
    Results = {"voltage": [], "current": [], "power": []}

    P_unit.open()
    DC_unit.open()
    DC_unit.set_current(0.0)
    DC_unit.set_voltage_limit(V_max)
    DC_unit.set_output(True)

    try:
        power_max = 0
        prev_end_current = 0

        for interval in interval_list:
            start_current = interval[0]
            prev_end_current = interval[-1]
            ramp_current(DC_unit, prev_end_current, start_current)

            for set_current in interval:
                DC_unit.set_current(set_current)

                volt = DC_unit.get_voltage()
                current = DC_unit.get_current()
                power = P_unit.get_power()

                Results["voltage"].append(volt)
                Results["current"].append(current)
                Results["power"].append(power)
                plot.add_point(volt, power)
                print("IPV data", volt, current, power)

                if power > power_max:
                    power_max = power
                if power < (rollover_threshold * power_max) and rollover_threshold:
                    break

    except Exception:
        traceback.print_exc()
    finally:
        ramp_current(DC_unit, DC_unit.get_current(), 0)
        DC_unit.set_current(0)
        DC_unit.set_output(False)
        P_unit.close()
        DC_unit.close()

    plot.keep_open()

    # TODO: keep plot alive after measurement
    return Results, plot
