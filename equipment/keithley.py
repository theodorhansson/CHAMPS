import pyvisa
from utils import argument_checker

_required_arguments = ["gpib_address", "type"]


class keithley:
    def __init__(self, config_dict: dict):
        argument_checker(config_dict, _required_arguments)
        self.address = str(config_dict["gpib_address"])
        self.interface = "GPIB0"

    def get_voltage(self):
        ans = self.instrument.query(":READ?")
        ans = ans.split(",")[0]  # First item is voltage
        return float(ans)

    def set_voltage_limit(self, volts: float):
        self.instrument.write(":SENSE:VOLTAGE:DC:PROTECTION " + str(volts))

    def set_current(self, current: float):
        self.instrument.write(":SOURCE:CURRENT " + str(current))

    def get_current(self):
        ans = self.instrument.query(":READ?")
        ans = ans.split(",")[1]  # Second item is current
        return float(ans)

    def set_output(self, state: bool):
        self.instrument.write(":OUTPUT " + str(int(state)))

    def open(self):
        conn_str = self.interface + "::" + self.address  # like GPIB0::24

        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(conn_str)

        self.instrument.write(":SOURCE:FUNCTION CURRENT")
        self.instrument.write(":SOURCE:CURRENT:MODE FIXED")
        self.instrument.write(":SOURCE:CURRENT:RANGE:AUTO 1")

        self.instrument.write(
            ":SENSE:FUNCTION 'VOLT'"
        )  # Sets what the display shall show
        self.instrument.write(":SENSE:VOLT:RANGE:AUTO 1")

    def close(self):
        self.instrument.close()
