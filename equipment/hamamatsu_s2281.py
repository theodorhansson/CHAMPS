import pyvisa
import utils
import time

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {"verbose_printing": 0}


class hamamatsu_s2281:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="hamamatsu_s2281",
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)

        self.address = str(config_dict["gpib_address"])
        self.interface = "GPIB0"
        self.verbose = config_dict["verbose_printing"]

        # Use parent resource manager if exists
        if resource_manager != None:
            self.resource_manager = resource_manager
        else:
            self.resource_manager = pyvisa.ResourceManager()

        print("__init__() in hamamatsu_s2281") if self.verbose & 4 + 8 else None

    def __enter__(self):
        print("__enter__() in hamamatsu_s2281") if self.verbose & 8 else None
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        time.sleep(0.1)  # Short wait in case of exception
        self.close()

    def open(self):  # TODO: Rename to open_current?
        # Define where instrument is
        print("enter() in hamamatsu_s2281") if self.verbose & 8 else None
        conn_str = self.interface + "::" + self.address  # like GPIB0::24

        self.instrument = self.resource_manager.open_resource(conn_str)

    def close(self):
        print("close() in hamamatsu_s2281") if self.verbose & 8 else None
        self.instrument.close()

    def get_voltage_for_offset(self) -> float:
        time.sleep(0.2)
        ans = self.instrument.query(":READ?")

        return float(ans)

    def get_power(self, offset_avarage) -> float:
        time.sleep(0.1)
        ans = self.instrument.query(":READ?")

        read_u = -float(ans) + offset_avarage

        I_mA = read_u * (1000 / 50)
        power = I_mA / 0.4525

        # if self.verbose & 8:
        # print(f"get_voltage() in hamamatsu_s2281: value {ans}")
        return power


# if __name__ == "__main__":
#     performance_test()
