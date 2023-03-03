[Table of contents](../readme.md)
# Keithley2400
The equipment class that controls the Keithley 2400 SourceMeter.
Items marked with {M} are mandatory, {O} optional.


```toml
.[keithley2400] 
type = "keithley2400"   # The specific type of unit
GPIB_address = 24
```
## keithley2400 {M}
The measurement dict contains all info for your specific device. It must always be present! 
**Note:** you may name it someting else:
``` TOML
DC_unit = "The_best_DC_unit"
...

.[The_best_DC_unit]
#Config
```

## Type: string {M}
Contains the name of the device class. This must match with the identifier set in the script!

## GPIB_address: int {M}
A string of the GPIB address your device has. **NOTE:** GPIB0 is the default bus. We currently don't support other choices here.