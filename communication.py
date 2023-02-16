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
            return keithley2400.keithley2400(config_dict)

        case "powercube":
            return powercube.powercube(config_dict)

        case _:
            raise Exception("Instrument not found")  # TODO Change this


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
        case "ophir_is6_d_uv":
            return ophir_IS6_D_UV.INT_sphere(config_dict)

        case _:
            raise Exception("Instrument not found")  # TODO Change this


def get_OSA():
    pass


def get_Beam():
    pass
