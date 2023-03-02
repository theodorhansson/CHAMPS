# Config files
A config file might look like this:
```toml
.[measurement]
Type = "ipv"
Save_folder = "c:/LABDATA"
DC_unit = "keithley2400"    # Refers to the [] below only
P_unit = "INT_sphere"
V_max = 5
Rollover_threshold = 0  # Stops measurement when power < rollover_threshold * maxpower
Rollover_min = 0        # Doesn't do rollover check on power values lower than this
Current = [[1, 0.1, 5], [5, 0.5, 15]]  # mA [min, step, max]
Plot_interval = 2
```
The parsing is case insensitive, so use whatever CaSe you'd like.
For exact contents of your config file, see the different measurement types ([IPV](measurements/ipv.md), [Spectrum](spectrum.md)).