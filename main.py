import tomllib
import sys
import numpy as np
import time
import tomli_w
import utils
import json

default_conf_path = "config.toml"


def main(config_path):
    # Open the config file
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    config_lower = utils.dict_2_lower(config)  # sanitize the config dict
    meas_name = config_lower["measurement"]["type"]

    # Code for printing
    if "verbose_printing" in config_lower["measurement"].keys():
        verbose = config_lower["measurement"]["verbose_printing"]
    else:
        verbose = 0
    print(f"Reading config {config_path} from disk") if verbose & 16 else None

    # Get the measurement object
    measurement_init = identify_measurement_type(meas_name)
    # Begin the measurement!
    result_dict, used_config = measurement_init(config_lower)

    # Logic on where to save file
    save_folder = config_lower["measurement"]["save_folder"]
    if save_folder[-1:] != "/":
        save_folder = save_folder + "/"  # make sure it ends with /

    timestamp = time.strftime(rf"%Y%m%d-%H%M%S")  # get the current time in nice format
    save_file = save_folder + meas_name + "-" + timestamp

    # Save the data as json
    data_save_name = save_file + ".json"
    with open(data_save_name, "w") as export_file:
        json.dump(result_dict, export_file)
    print(f"Saving data file {data_save_name} to disk.") if verbose & 16 else None

    # Save the config
    config_save_name = save_file + ".toml"
    with open(config_save_name + ".toml", "wb") as f:
        tomli_w.dump(used_config, f)
    print(f"Saving config file {config_save_name} to disk.") if verbose & 16 else None


def identify_measurement_type(measurement: str):
    # Matches measurement name with correct module
    match measurement:
        case "ipv":
            import measurement_type.ipv

            return measurement_type.ipv.init

        case "spectrum":
            import measurement_type.spectrum

            return measurement_type.spectrum.init

        case _:
            # TODO Change this
            raise Exception(f"No measurement of type {measurement} found.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        config_path = default_conf_path
    else:
        # for optional system path
        config_path = sys.argv[1]

    main(config_path)
