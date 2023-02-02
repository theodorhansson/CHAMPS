import communication
from utils import argument_checker, animatedPlot
import numpy as np


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
# _optional_arguments = {"p_cutoff": 0}


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
    # Main measurment loop
    print(config)

    i_start = config["measurement"]["i_start"]
    i_end = config["measurement"]["i_end"]
    V_max = config["measurement"]["v_max"]
    N_datapoints = config["measurement"]["datapoints"]

    Results = {"voltage": [], "current": [], "power": []}

    current_list = np.linspace(i_start, i_end, N_datapoints)

    plot = animatedPlot("Voltage[V]", "Optical Power [W]", "IPV")

    with communication.get_DCsupply(DC_config) as DC_unit, communication.get_PowerUnit(
        P_config
    ) as P_unit:
        DC_unit.set_voltage_limit(V_max)
        for set_current in current_list:
            DC_unit.set_current(set_current)
            # Sleep här?
            volt = DC_unit.get_voltage()
            current = DC_unit.get_current()
            power = P_unit.get_power()
            Results["voltage"] = volt
            Results["current"] = current
            Results["power"] = power

            plot.add_point(volt, power)

    return Results
