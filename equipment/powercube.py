import serial
from utils import argument_checker

_required_arguments = ["port", "type"]


class powercube:
    def __init__(self, config_dict):
        argument_checker(config_dict, _required_arguments, source_func="powercube")
        self.port = str(config_dict["port"])
        print(
            "Now this stuff is seriously untested. Please reconsider using this file."
        )

    def get_voltage(self):
        self.serial_port.write(b"VOUT1?")
        ans = self.serial_port.read(1000)
        return float(ans)  # TODO: type?

    def set_voltage_limit(self, volt: float):
        self.serial_port.write(b"VSET1:" + bytes(str(volt), encoding="utf-8"))

    def set_current(self, current: float):
        self.serial_port.write(b"ISET1:" + bytes(str(current), encoding="utf-8"))

    def get_current(self):
        self.serial_port.write(b"IOUT1?")
        ans = self.serial_port.read(1000)
        return float(ans)  # TODO: type?

    def set_output(self, state: bool):
        self.serial_port.write(b"OUT" + bytes(str(int(state)), encoding="utf-8"))

    def open(self):
        self.serial_port = serial.Serial(self.port)

        self.serial_port.baudrate = 9600
        self.serial_port.parity = serial.PARITY_NONE
        self.serial_port.bytesize = 8
        self.serial_port.stopbits = 1

    def close(self):
        self.serial_port.close()
