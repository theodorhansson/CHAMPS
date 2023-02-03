from equipment import *


def get_DCsupply(config_dict):
    # For DC power supplies
    DC_type = config_dict["type"]
    match DC_type:
        case "keithley":
            return keithley.keithley(config_dict)

        case "powercube":
            return powercube.powercube(config_dict)

        case _:
            raise Exception("Instrument not found")  # TODO Change this


def get_PowerUnit(config_dict):
    # For measuring power
    Power_type = config_dict["type"]

    match Power_type:
        case "int_sphere":
            return sphere.INT_sphere(config_dict)

        case _:
            raise Exception("Instrument not found")  # TODO Change this


def get_OSA():
    pass


def get_Beam():
    pass
