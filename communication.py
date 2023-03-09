import equipment
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
                return equipment.keithley2400.keithley2400

            case "powercube":
                return equipment.powercube.powercube

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
                return equipment.ophir_IS6_D_UV.INT_sphere

            case _:
                # TODO Change this
                raise Exception(f"No Power unit of type {Power_type} found.")

    def get_OSA(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            warn_extra=False,
            source_func="communication, OSA",
        )
        # For measuring spectrum
        OSA_type = config_dict["type"]

        match OSA_type:
            case "ando_osa":
                return equipment.andoAQ6317B.SpectrumAnalyzer

            case "anritsu_osa":
                return equipment.anritsuMS9710A.SpectrumAnalyzer

            case _:
                # TODO Change this
                raise Exception(f"No OSA of type {OSA_type} found.")

    def get_Beam(self, config_dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            warn_extra=False,
            source_func="communication beam",
        )

        Beam_type = config_dict["type"]

        match Beam_type:
            case None:
                return equipment.Spiricon_BGP_USB_SP928_OSI.BeamCamera
            case _:
                # TODO Change this
                raise Exception(f"No Beam of type {Beam_type} found.")

    def __getattr__(self, name):
        # Returns do_nothing instrument for undefined methods
        def method(*args, **kwargs):
            try:
                if args[0]["type"] == "do_nothing":
                    return equipment.do_nothing.DoNothing
            except:
                pass
            raise AttributeError(f"Unknown attribute {name} in communication")

        return method

    def __getattribute__(self, name):
        # Returns do_nothing instrument for defined methods
        attr = object.__getattribute__(self, name)

        def method(*args, **kwargs):
            try:
                if args[0]["type"] == "do_nothing":
                    return equipment.do_nothing.DoNothing
            except:
                pass
            result = attr(*args, **kwargs)
            return result

        return method


if __name__ == "__main__":
    pass
