import pyvisa
from utils import argument_checker, optional_arguments_merge

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {"reference_level_dbm": -40, "display_level_scale_dbm": 10}

# Many comments in methods from "MS9710B Optical Spectrum Analyzer Remote Control Operation Manual", ANRITSU 2007
### Read manual page 139, 261 for commands ###

# TODO: Better typecheck?


class SpectrumAnalyzer:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        argument_checker(config_dict, _required_arguments, _optional_arguments)

        config_dict = optional_arguments_merge(config_dict, _optional_arguments)
        self.address = str(config_dict["gpib_address"])
        self.interface_ID = "GPIB0"
        self.conn_str = self.interface_ID + "::" + self.address

        self.reference_level_dBm = config_dict["reference_level_dbm"]
        self.display_level_scale_dBm = config_dict["display_level_scale_dbm"]

        # Use parent resource manager if exists
        if resource_manager != None:
            self.resource_manager = resource_manager
        else:
            self.resource_manager = pyvisa.ResourceManager()

    def open(self):  # TODO: move to __init__?
        # Define instrument with pyvisa
        self.instrument = self.resource_manager.open_resource(self.conn_str)
        self.set_ref_level_dBm(self.reference_level_dBm)
        self.set_level_scale_dBm(self.display_level_scale_dBm)

    def close(self):
        # Exit instrument
        self.instrument.close()

    def set_avg_factor(self, avg_factor: int | str):
        # Sets the number of points for point averaging.
        # Data range 2<= n <= 1000, or "OFF"
        GPIB_write = "AVT " + str(avg_factor)
        self.instrument.write(GPIB_write)

    def get_avg_factor(self):
        GPIB_write = "AVT?"
        avg = self.instrument.query(GPIB_write)
        return avg

    def set_center_wavelength_nm(self, center_wl: float):
        # Sets a center wavelength. The unit is always nm.
        # Input value down to the second decimal place. Data range: 600 <= n <= 1750
        GPIB_write = "CNT " + str(round(center_wl, 2))
        self.instrument.write(GPIB_write)

    def get_center_wavelength_nm(self):
        GPIB_write = "CNT?"
        center_wl = self.instrument.query(GPIB_write)
        return center_wl

    def set_level_scale_dBm(self, level_scale: float):
        # Selects a log scale as a level scale and sets a scale value
        # Data range: 0.1 <= level_scale <= 10.0
        GPIB_write = "LOG " + str(round(level_scale, 1))
        self.instrument.write(GPIB_write)

    def get_level_scale(self) -> str:
        # Returns whether a log or linear scale is set as a level scale.
        GPIB_write = "LVS?"
        scale_type = self.instrument.query(GPIB_write)
        return scale_type

    def set_linear_resolution_nm(self, resolution: float):
        # n indicates measurement resolution. The unit is always nm.
        # input one of the following values: 1.0, 0.5, 0.2, 0.1, 0.07, 0.05
        GPIB_write = "RES " + str(resolution)
        self.instrument.write(GPIB_write)

    def get_linear_resolution_nm(self):
        GPIB_write = "RES?"
        resolution = self.instrument.write(GPIB_write)
        return resolution

    def set_sample_points(self, n_points: int):
        # # Sets the sampling point for measurement. ****: 11 to 20001 (1 step), 0(auto)
        # GPIB_write = ":SMPL" + str(n_points)
        # self.instrument.write(GPIB_write)'
        pass

    def get_sample_points(self):
        # GPIB_write = ":SMPL?"
        # n_points = self.instrument.write(GPIB_write)
        # return n_points
        pass

    def set_ref_level_dBm(self, level: float):
        # Sets the reference level. [in LOG] (Unit: dBm), ***.***: -190.000 to 50.000 (0.1 step)
        GPIB_write = "MKD " + str(level) + " DBM"
        self.instrument.write(GPIB_write)

    def get_ref_level(self):
        GPIB_write = "MKD?"
        n_points = self.instrument.query(GPIB_write)
        return n_points

    def set_sensitivity(self, sensitivity_id: str):
        pass

    def get_sensitivity(self):
        return ""

    def set_wavelength_span_nm(self, span: float):
        # Sets the span. (Unit_ nm), ****.*: 0, 0.5 to 1200.0 (0.1 step)
        GPIB_write = "SPN " + str(round(span, 1))
        self.instrument.write(GPIB_write)

    def get_wavelength_span(self):
        GPIB_write = "SPN?"
        span = self.instrument.query(GPIB_write)
        return span

    def get_wavelength_data_A(self, range: str = ""):
        # Outputs ASCII measurement data equivalent to the number of sampling points from memory A.
        # NOTE: Range option not supported
        GPIB_write = "DMA?"
        wavelength_data = self.instrument.query(GPIB_write)
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
