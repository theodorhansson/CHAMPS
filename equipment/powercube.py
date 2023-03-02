import serial
import utils

_required_arguments = ["port", "type"]
_optional_arguments = {"verbose_printing": 0}


class powercube:
    def __init__(self, config_dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="powercube",
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)
        self.verbose = config_dict["verbose_printing"]

        self.port = str(config_dict["port"])
        print(
            "Now this stuff is seriously untested. Please reconsider using this file."
        )

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()

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
