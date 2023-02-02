import serial


class powercube:
    def __init__(self, config_dict):
        self.port = str(config_dict["port"])

    def get_voltage(self):
        self.serial_port.write(b"VOUT1?")
        ans = self.serial_port.read(1000)
        return ans

    def set_voltage_limit(self, volt):
        self.serial_port.write(b"VSET1:" + str(volt))

    def set_current(self, current):
        self.serial_port.write(b"ISET1:" + str(current))

    def set_output(self, state):
        self.serial_port.write(b"OUT" + str(int(state)))

    def __enter__(self):
        self.serial_port = serial.Serial(self.port)

        self.serial_port.baudrate = 9600
        self.serial_port.parity = serial.PARITY_NONE
        self.serial_port.bytesize = 8
        self.serial_port.stopbits = 0

    def __exit__(self, exception_type, exception_value, exception_trace):
        self.serial_port.close()