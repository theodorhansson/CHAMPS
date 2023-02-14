import pyvisa
from utils import argument_checker

_required_arguments = ["gpib_address", "type"]


class SpectrumAnalyzer:
    def __init__(self, config_dict: dict):
        pass

    def set_avg(self):
        pass

    def get_avg(self):
        pass

    def set_center_wavelength(self):
        pass

    def get_center_wavelength(self):
        pass

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
