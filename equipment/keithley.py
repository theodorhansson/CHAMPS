import pyvisa


class keithley:
    def __init__(self, config_dict):
        self.address = str(config_dict["address"])
        self.interface = "GPIB0"

    def get_voltage(self):
        ans = self.instrument.query(":READ?")
        return float(ans)

    def set_voltage_limit(self, volts):
        self.instrument.write(":SENSE:VOLTAGE:DC:PROTECTION " + str(volts))

    def set_current(self, current):
        self.instrument.write(":SOURCE:CURRENT " + str(current))

    def set_output(self, state):
        self.instrument.write(":OUTPUT " + str(int(state)))

    def __enter__(self):
        conn_str = self.interface + "::" + self.address  # like GPIB0::24

        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(conn_str)

        self.instrument.write(":SOURCE:FUNCTION CURRENT")
        self.instrument.write(":SOURCE:CURRENT:MODE FIXED")
        self.instrument.write(":SOURCE:CURRENT:RANGE:AUTO 1")
        self.instrument.write(":SENSE:VOLT:RANGE:AUTO 1")

    def __exit__(self, exception_type, exception_value, exception_trace):
        self.instrument.close()
