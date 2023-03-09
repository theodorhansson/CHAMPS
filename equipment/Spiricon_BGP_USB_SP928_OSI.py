import clr
import utils
import numpy as np

_required_arguments = ["type"]
_optional_arguments = {
    "dll_path": "..\\drivers\\beamgage_drivers\\Beamgage_python_wrapper",
    "verbose_printing": 0,
}


class BeamCamera:
    def __init__(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="Beam camera init",
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)

        self.dll_path = config_dict["dll_path"]
        self.verbose = config_dict["verbose_printing"]

    def open(self):
        clr.AddReference(self.dll_path)
        import Beamgage_python_wrapper

        bg_class = Beamgage_python_wrapper.Beamgage("CHAMPS", True)
        self.bg = bg_class.get_AutomatedBeamGage()

    def __enter__(self):
        print("__enter__() in keithley2400") if self.verbose & 8 else None
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.verbose & 8:
            print("__exit__() in Spiricon camera")
            print(f"{exception_type=}, {exception_value=}, {exception_traceback=}")
        self.close()

    def close(self):
        self.bg.Instance.Shutdown()

    def get_frame_data(self) -> list:
        data_NET = self.bg.ResultsPriorityFrame.DoubleData
        data_list = [x for x in data_NET]

        shape = self.get_frame_shape()
        matrix = np.array(data_NET)
        matrix = np.reshape(matrix, shape)
        return list(matrix)

    def get_frame_shape(self) -> tuple(int, int):
        width = int(self.bg.get_FrameInfoResults().Width)
        height = int(self.bg.get_FrameInfoResults().Height)
        return (height, width)
