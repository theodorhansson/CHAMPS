import pyvisa


class keithley:
    def __init__(self, config_dict):
        address = str(config_dict["address"])
        interface = "GPIB0"
        conn_str = interface + "::" + address  # like GPIB0::24

        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(conn_str)
        self.instrument.read_terminationn("\n")
        self.instrument.write_termination("\n")

        self.instrument.write(":SOURCE:CURRENT:MODE:FIXED")
        self.instrument.write(":SOURCE:CURRENT:RANGE:AUTO 1")

        # self.instrument.write("CONFIGURE:VOLTAGE:DC")

    def get_voltage(self):
        ans = self.instrument.query(":READ?")
        return float(ans)

    def set_voltage_limit(self, volts):
        self.instrument.write(":SENSE:VOLTAGE:DC:PROTECTION " + str(volts))

    def set_current(self, current):
        self.instrument.write(":SOURce:CURRent " + str(current))
        pass

    def set_output(self, state):
        self.instrument.write(":OUTPut " + str(int(state)))
        pass
