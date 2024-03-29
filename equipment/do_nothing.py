import numpy as np
import time

# This class can be used if you want an instrument, but don't have it connected


class DoNothing:
    def __init__(self, *args, **kwargs):
        for arg in args:
            if type(arg) == dict:
                if "verbose_printing" in arg.keys():
                    self.verbose = arg["verbose_printing"]
                    break
        else:
            self.verbose = 0

        print("__init__() in do_nothing") if self.verbose & 4 + 8 else None

    def __enter__(self, *args, **kwargs):
        print("__enter__() in do_nothing") if self.verbose & 4 + 8 else None
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        exception_traceback,
        *args,
        **kwargs,
    ):

        if self.verbose & 4 + 8:
            if self.verbose & 8:
                print("__exit__() in do_nothing")
                print(f"{exception_type=}, {exception_value=}, {exception_traceback=}")

    def __getattr__(self, name):
        # This method is called if an attribute isn't found. Overloads take precedence.
        # Returns none if unknown method or setter

        def method(*args, **kwargs):
            if self.verbose & 8:
                print(f"{name}() in do_nothing, with {args=}, {kwargs=}")
            # Return something for getters
            if "get" in name:
                time.sleep(0.25)
                return 1
            else:
                return None

        return method

    def get_voltage_and_current(self, *args, **kwargs):
        time.sleep(0.25)
        print("get_voltage_and_current() in do_nothing") if self.verbose & 8 else None
        return 1, 1

    def get_power(self, *args, **kwargs):
        return np.random.rand()

    def get_frame_data(self, *args, **kwargs):
        time.sleep(0.5)
        print("get_frame_data() in do_nothing") if self.verbose & 8 else None
        # Returns large integer random matrix
        length = 100
        bit_depth = 12
        max_val = 2**bit_depth - 1
        image = np.random.randint(0, max_val, size=(length, length))
        image = [[int(element) for element in row] for row in image]
        return image


def test_do_nothing():
    config = {"verbose_printing": 8}
    DN = DoNothing(config)

    with DN as P:
        # print(DN.get_frame_data())
        print(P.get_voltage_and_current())
        print(P.undefined())


if __name__ == "__main__":
    test_do_nothing()
