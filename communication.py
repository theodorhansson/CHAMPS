from equipment import *
import pyvisa
from utils import argument_checker

_required_arguments = ["type"]


class Communication:
    def __init__(self) -> None:
        pass

    def get_DCsupply(self, config_dict: dict):
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
                resource_manager = self.pyvisa_resource_util()
                return keithley.keithley(config_dict, resource_manager)

            case "powercube":
                return powercube.powercube(config_dict)

            case _:
                # TODO Change this
                raise Exception(f"No DC-unit of type {DC_type} found.")

    def get_PowerUnit(self, config_dict: dict):
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

    def get_OSA(self, config_dict: dict):
        argument_checker(
            config_dict,
            _required_arguments,
            warn_extra=False,
            source_func="communication, powerunit",
        )
        # For measuring spectrum
        OSA_type = config_dict["type"]

        match OSA_type:
            case "ando_osa":
                resource_manager = self.pyvisa_resource_util()
                return andoAQ6317B.SpectrumAnalyzer(config_dict, resource_manager)

            case "anritsu_osa":
                resource_manager = self.pyvisa_resource_util()
                return anritsuMS9710A.SpectrumAnalyzer(config_dict, resource_manager)

            case _:
                # TODO Change this
                raise Exception(f"No OSA of type {OSA_type} found.")

    def get_Beam(self):
        pass

    def pyvisa_resource_util(self):
        # Checks if self.resource_manager exists, if not create it.
        if not hasattr(self, "resource_manager"):
            self.resource_manager = pyvisa.ResourceManager()
        return self.resource_manager


def test():
    com = Communication()
    print(com.pyvisa_resource_util())
    print(com.pyvisa_resource_util())
    del com


test()
