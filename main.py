import tomllib
import sys
import numpy as np
import time
import tomli_w

default_conf_path = "config.toml"


def main(config_path):
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    config_lower = dict_2_lower(config)  # sanitize the config dict

    meas_name = config_lower["measurement"]["type"]

    measurement_init = identify_measurement_type(meas_name)
    result_dict, used_config = measurement_init(config_lower)  # Begin the measurement!

    resultarr = []
    result_headers = []
    for key in result_dict.keys():
        result_headers.append(key)
        resultarr.append(result_dict[key])  # One data type per row

    resultarr = np.array(resultarr)
    resultarr = np.transpose(resultarr)  # One data type per column

    save_folder = config_lower["measurement"]["save_folder"]
    if save_folder[-1:] != "/":
        save_folder = save_folder + "/"  # make sure it ends with /

    timestamp = time.strftime(rf"%Y%m%d-%H%M%S")
    save_file = save_folder + meas_name + "-" + timestamp

    np.savetxt(save_file + ".txt", resultarr, header=" ".join(result_headers))

    # Save the config
    with open(save_file + ".toml", "wb") as f:
        tomli_w.dump(used_config, f)


def identify_measurement_type(measurement: str):
    # Matches measurement name with correct module
    match measurement:
        case "ipv":
            import measurement_type.ipv

            return measurement_type.ipv.init
        case _:
            raise Exception("Measurement type not found")  # TODO Change this


def dict_2_lower(indict: dict) -> dict:
    # Recursive dict to lower function
    out_dict = dict()
    for key in indict:
        value = indict[key]
        out_key = key.lower() if type(key) == str else key

        if type(value) == dict:
            temp = dict_2_lower(value)
            out_dict[out_key] = temp

        else:
            out_value = value.lower() if type(value) == str else value
            out_dict[out_key] = out_value
    return out_dict


if __name__ == "__main__":
    if len(sys.argv) == 1:
        config_path = default_conf_path
    else:
        # for optional system path
        config_path = sys.argv[1]

    main(config_path)
