import communication


def init(config):
    # Used for getting instrument objects
    print("initing IPV")

    main(config, None, None, None)


def main(config, DC_unit, Voltage_measure, int_sphere):
    required_arguments = []
    optional_arguments = {"p_cutoff": 0}
    # Main measurment loop
    print("IPV success")
