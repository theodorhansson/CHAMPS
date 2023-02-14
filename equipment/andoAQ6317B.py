import pyvisa
from utils import argument_checker

_required_arguments = ["gpib_address", "type"]


# NOTE: GPIB1 is used for controlling unit, GPIB2 is used for contrilling other units.
### Read manual page 384 ###


class SpectrumAnalyzer:
    def __init__(self, config_dict: dict):
        self.address = str(config_dict["gpib_address"])
        self.interface_ID = "GPIB0"

    def open(self):
        # Define where instrument is
        conn_str = self.interface_ID + "::" + self.address
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(conn_str)

    def close(self):
        # Exit instrument
        self.instrument.close()

    def set_avg(self):
        pass

    def get_avg(self):
        pass

    def set_center_wavelength_nm(self, center_wl: float):
        # Sets the center wavelength in nm
        GPIB_write = ":CTRWL" + str(round(center_wl, 2))
        self.instrument.write(GPIB_write)

    def get_center_wavelength_nm(self):
        GPIB_write = ":CTRWL?"
        center_wl = self.instrument.write(GPIB_write)
        return center_wl

    def set_level_scale(self):
        pass

    def get_level_scale(self):
        pass

    def get_linear_resolutuin(self):
        pass

    def set_linear_resolutuin(self):
        pass

    def set_num_sample(self):
        pass

    def get_num_sample(self):
        pass

    def set_ref_level(self):
        pass

    def get_ref_level(self):
        pass

    def set_sensitivity(self):
        pass

    def get_sensitivity(self):
        pass

    def set_wavelength_span(self):
        pass

    def get_wavelength_span(self):
        pass

    def get_wavelength(self):
        pass

    def get_spectrum_data(self):
        pass

    def set_single_span(self):
        pass

    def get_connected_visa_devices(self):
        devices = pyvisa.ResourceManager()


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
