import tomllib
import sys

default_conf_path = "config.toml"


def main(config_path):
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    config_lower = dict_2_lower(config)

    Meas_type = config_lower["measurement"]["type"]

    # Import measurement module
    meas_module = "Measurement_type." + Meas_type
    import_string = "import " + meas_module
    exec(import_string)

    # Run measurement module
    meas_init = meas_module + ".init(config_lower)"
    exec(meas_init)


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
