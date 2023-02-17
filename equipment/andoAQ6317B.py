import pyvisa
from utils import argument_checker, optional_arguments_merge

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {"reference_level": -40, "display_level_scale": 10}

# Many comments in methods from "AQ6317B OPTICAL SPECTRUM ANALYZER INSTRUCTION MANUAL", ANDO ELECTRIC 2000
### Read manual page 384 for commands ###

# NOTE: GPIB1 is used for controlling unit, GPIB2 is used for controlling other units.
# TODO: Better typecheck?


class SpectrumAnalyzer:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        argument_checker(config_dict, _required_arguments, _optional_arguments)

        config_dict = optional_arguments_merge(config_dict, _optional_arguments)
        self.address = str(config_dict["gpib_address"])
        self.interface_ID = "GPIB0"
        self.conn_str = self.interface_ID + "::" + self.address

        self.reference_level = config_dict["reference_level"]
        self.display_level_scale = config_dict["display_level_scale"]

        # Use parent resource manager if exists
        if resource_manager != None:
            self.resource_manager = resource_manager
        else:
            self.resource_manager = pyvisa.ResourceManager()

    def open(self):  # TODO: move to __init__?
        # Define instrument with pyvisa
        self.instrument = self.resource_manager.open_resource(self.conn_str)
        self.set_ref_level_dBm(self.reference_level)
        self.set_level_scale(self.display_level_scale)

    def close(self):
        # Exit instrument
        self.instrument.close()

    def set_avg_factor(self, avg_factor: int):
        # Sets the number of averaging times for measurement, ****: 1 to 1000 (1 step)
        GPIB_write = ":AVG" + str(avg_factor)
        self.instrument.write(GPIB_write)

    def get_avg_factor(self):
        GPIB_write = ":AVG?"
        avg = self.instrument.write(GPIB_write)
        return avg

    def set_center_wavelength_nm(self, center_wl: float):
        # Sets the center wavelength (Unit: nm), ****.**: 600.00 to 1750.00 (0.01 step)
        GPIB_write = ":CTRWL" + str(round(center_wl, 2))
        self.instrument.write(GPIB_write)

    def get_center_wavelength_nm(self):
        GPIB_write = ":CTRWL?"
        center_wl = self.instrument.write(GPIB_write)
        return center_wl

    def set_level_scale_dBm(self, scale: float):
        # Sets the scale of the level axis, **.*: 0.1 to 10.0 (0.1 step. Unit: dB/DIV) [or LIN (linear scale) UNINPLEMENTED]
        GPIB_write = ":LSCL" + str(round(scale, 1))
        self.instrument.write(GPIB_write)

    def get_level_scale(self):
        GPIB_write = ":LSCL?"
        avg = self.instrument.write(GPIB_write)
        return avg

    def set_linear_resolution_nm(self, resolution: float):
        # Sets the resolution. (Unit: nm), *.**: 0.01 to 2.0 (1-2-5 steps)
        GPIB_write = ":RESLN" + str(round(resolution, 2))
        self.instrument.write(GPIB_write)

    def get_linear_resolution_nm(self):
        GPIB_write = ":RESLN?"
        resolution = self.instrument.write(GPIB_write)
        return resolution

    def set_sample_points(self, n_points: int):
        # Sets the sampling point for measurement. ****: 11 to 20001 (1 step), 0(auto)
        GPIB_write = ":SMPL" + str(n_points)
        self.instrument.write(GPIB_write)

    def get_sample_points(self):
        GPIB_write = ":SMPL?"
        n_points = self.instrument.write(GPIB_write)
        return n_points

    def set_ref_level_dBm(self, level: float):
        # Sets the reference level. [in LOG] (Unit: dBm), ***.*: -90.0 to 20.0 (0.1 step)
        GPIB_write = ":REFL" + str(level)
        self.instrument.write(GPIB_write)

    def get_ref_level(self):
        GPIB_write = ":REFL?"
        n_points = self.instrument.write(GPIB_write)
        return n_points

    def set_sensitivity(self, sensitivity_id: str):
        # Avaliable sensitivities:
        # SNHD: SENS NORM RANGE HOLD
        # SNAT: SENS NORM RANGE AUTO
        # SMID: SENS MID
        # SHI1: SENS HIGH1
        # SHI2: SENS HIGH2
        # SHI3: SENS HIGH3
        GPIB_write = ":" + sensitivity_id
        self.instrument.write(GPIB_write)

    def get_sensitivity(self):
        GPIB_write = ":SENS?"
        sensitivity = self.instrument.write(GPIB_write)
        return sensitivity

    def set_wavelength_span_nm(self, span: float):
        # Sets the span. (Unit_ nm), ****.*: 0, 0.5 to 1200.0 (0.1 step)
        GPIB_write = ":SPAN" + str(round(span, 1))
        self.instrument.write(GPIB_write)

    def get_wavelength_span(self):
        GPIB_write = ":SPAN?"
        span = self.instrument.write(GPIB_write)
        return span

    def get_wavelength_data_A(self, range: str = ""):
        # Trace A wavelength data **** : 1 to 20001, "R1-R20001" when range ommitted
        GPIB_write = ":WDATA" + range
        wavelength_data = self.instrument.write(GPIB_write)
        return wavelength_data

    def set_single_span(self):
        pass

    def get_connected_visa_devices(self):
        return self.resource_manager.list_resources()


def test_OSA():
    test_config = {"gpib_address": 12, "type": "jiopfjio"}

    OSA = SpectrumAnalyzer(test_config)
    OSA.open()

    print(OSA.get_center_wavelength_nm())
    OSA.set_center_wavelength_nm()
    print(OSA.get_center_wavelength_nm())

    OSA.close()


if __name__ == "__main__":
    test_OSA()
