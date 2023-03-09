import pythonnet
import os, sys, clr
import utils

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {
    "dll_path": "C:\\Program Files\\Spiricon\\BeamGage Professional\\",
    "verbose_printing": 0,
}

_dlls = [
    "Spiricon.Automation.dll",
    "Spiricon.BeamGage.Automation.dll",
    "Spiricon.Interfaces.ConsoleService.dll",
    "Spiricon.TreePattern.dll",
]


class BeamCamera:
    def __init__(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="Beam camera init",
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)

        dll_path = config_dict["dll_path"]
        if dll_path[-1] != "\\":
            dll_path += "\\"

        for dll in _dlls:
            clr.AddReference(dll_path + dll)
        import Spiricon.Automation

    _bg = new AutomatedBeamGage("ClientOne", true);