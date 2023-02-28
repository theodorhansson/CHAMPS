import tomllib
import sys
import numpy as np
import time
import tomli_w
import utils

default_conf_path = "config.toml"


def main(config_path):
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    config_lower = utils.dict_2_lower(config)  # sanitize the config dict
    meas_name = config_lower["measurement"]["type"]

    # Get the measurement object
    measurement_init = identify_measurement_type(meas_name)
    # Begin the measurement!
    result_dict, used_config = measurement_init(config_lower)

    # Extract results from dict and put in list(of lists)
    result_matrix, header_string = utils.create_save_list(result_dict)

    # Logic on where to save file
    save_folder = config_lower["measurement"]["save_folder"]
    if save_folder[-1:] != "/":
        save_folder = save_folder + "/"  # make sure it ends with /

    timestamp = time.strftime(rf"%Y%m%d-%H%M%S")  # get the current time in nice format
    save_file = save_folder + meas_name + "-" + timestamp

    # Save the data
    np.savetxt(save_file + ".txt", result_matrix, header=header_string)

    # Save the config
    with open(save_file + ".toml", "wb") as f:
        tomli_w.dump(used_config, f)


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
