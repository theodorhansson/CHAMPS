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

    def get_voltage(self):
        ans = self.instrument.query("MEASURE:VOLTAGE?")
        return float(ans)

    def set_voltage_limit():
        pass

    def set_current():
        pass

    def set_output(state):
        pass
