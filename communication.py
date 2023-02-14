from equipment import *
from utils import argument_checker

_required_arguments = ["type"]


def get_DCsupply(config_dict):
    argument_checker(
        config_dict,
        _required_arguments,
        warn_extra=False,
        source_func="communication, DC-supply",
    )

    # For DC power supplies
    DC_type = config_dict["type"]
    match DC_type:
        case "keithley2400":
            return keithley.keithley(config_dict)

        case "powercube":
            return powercube.powercube(config_dict)

        case _:
            # TODO Change this
            raise Exception(f"No DC-unit of type {DC_type} found.")


def get_PowerUnit(config_dict):
    argument_checker(
        config_dict,
        _required_arguments,
        warn_extra=False,
        source_func="communication, powerunit",
    )
    # For measuring power
    Power_type = config_dict["type"]

    match Power_type:
        case "int_sphere":
            return sphere.INT_sphere(config_dict)

        case _:
            # TODO Change this
            raise Exception(f"No Power unit of type {Power_type} found.")


def get_OSA():
    pass


def get_Beam():
    pass
