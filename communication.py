from equipment import *


def get_DCsupply(config_dict):
    DC_type = config_dict["type"]
    match DC_type:
        case "keithly":
            return keithley.keithley(config_dict)

        case "powercube":
            return powercube.powercube(config_dict)

        case _:
            pass  # TODO error handling


def get_Sphere():
    pass


def get_OSA():
    pass


def get_Beam():
    pass
