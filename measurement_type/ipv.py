import communication
from utils import argument_checker, AnimatedPlot
import numpy as np
import traceback
import time


_DC_name_key = "dc_unit"
_P_name_key = "p_unit"
_required_arguments = [
    "type",
    "dc_unit",
    "p_unit",
    "i_start",
    "i_end",
    "v_max",
    "datapoints",
]
_optional_arguments = {"rollover_threshold": 0}


def init(config):
    argument_checker(config["measurement"], _required_arguments)
    # Used for getting instrument objects
    DC_name = config["measurement"][_DC_name_key]
    DC_config = config[DC_name]

    P_name = config["measurement"][_P_name_key]
    P_config = config[P_name]

    print("DC_config", DC_config)

    Results = main(config, DC_config, P_config)
    return Results


def main(config, DC_config, P_config):
    # Main measurement loop
    print(config)

    i_start = config["measurement"]["i_start"]
    i_end = config["measurement"]["i_end"]
    V_max = config["measurement"]["v_max"]
    N_datapoints = config["measurement"]["datapoints"]
    rollover_threshold = optional_config["rollover_threshold"]

    Results = {"voltage": [], "current": [], "power": []}

    current_list = np.linspace(i_start, i_end, N_datapoints)

    plot = AnimatedPlot("Voltage[V]", "Optical Power [W]", "IPV")

    P_unit = communication.get_PowerUnit(P_config)
    DC_unit = communication.get_DCsupply(DC_config)

    P_unit.open()
    DC_unit.open()
    DC_unit.set_current(0.0)
    DC_unit.set_voltage_limit(V_max)
    DC_unit.set_output(True)

    for current in np.linspace(0, current_list[0], 10):
        DC_unit.set_current(current)
        time.sleep(0.05)

    try:
        power_max = 0
        for set_current in current_list:
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
        DC_unit.set_current(0)
        DC_unit.set_output(False)
        P_unit.close()
        DC_unit.close()

    plot.keep_open()

    # TODO: keep plot alive after measurement
    return Results, plot
