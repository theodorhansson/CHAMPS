from equipment import *
import utils

_required_arguments = ["type"]


class Communication:
    def __init__(self) -> None:
        pass

    def get_DCsupply(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            warn_extra=False,
            source_func="communication, DC-supply",
        )

        # For DC power supplies
        DC_type = config_dict["type"]
        match DC_type:
            case "keithley2400":
                return keithley2400.keithley2400

            case "powercube":
                return powercube.powercube

            case _:
                # TODO Change this
                raise Exception(f"No DC-unit of type {DC_type} found.")

    def get_PowerUnit(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            warn_extra=False,
            source_func="communication, powerunit",
        )
        # For measuring power
        Power_type = config_dict["type"]

        match Power_type:
            case "ophir_is6_d_uv":
                return ophir_IS6_D_UV.INT_sphere

            case _:
                # TODO Change this
                raise Exception(f"No Power unit of type {Power_type} found.")

    def get_OSA(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            warn_extra=False,
            source_func="communication, powerunit",
        )
        # For measuring spectrum
        OSA_type = config_dict["type"]

        match OSA_type:
            case "ando_osa":
                return andoAQ6317B.SpectrumAnalyzer

            case "anritsu_osa":
                return anritsuMS9710A.SpectrumAnalyzer

            case _:
                # TODO Change this
                raise Exception(f"No OSA of type {OSA_type} found.")

    def get_Beam(self):
        pass


if __name__ == "__main__":
    pass
