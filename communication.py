from equipment import *


def get_DCsupply(config_dict):
    # For DC power supplies
    DC_type = config_dict["type"]
    match DC_type:
        case "keithley":
            return keithley.keithley

        case "powercube":
            return powercube.powercube

        case _:
            pass  # TODO error handling


def get_PowerUnit(config_dict):
    # For measuring power
    Power_type = config_dict["type"]

    match Power_type:
        case "INT_sphere":
            return sphere.INT_sphere(config_dict)

        case _:
            pass  # TODO error handling


def get_OSA():
    pass


def get_Beam():
    pass
