[Table of contents](../readme.md)
# anritsuMS9710A
The equipment class that controls the Anritsu MS9710A Optical Spectrum Analyzer.
Items marked with {M} are mandatory, {O} optional.


```toml
.[anritsu]
type = "anritsu_osa"
GPIB_address = 8
reference_level_dbm = -40
display_level_scale_dbm = 10
```
## anritsu {M}
The measurement dict contains all info for your specific device. It must always be present! 
**Note:** you may name it someting else:
``` TOML
OSA_unit = "That_old_thingy"
...

.[That_old_thingy]
#Config
```

## Type: string {M}
Contains the name of the device class. This must match with the identifier set in the script!

## GPIB_address: int {M}
A string of the GPIB address your device has. **NOTE:** GPIB0 is the default bus. We currently don't support other choices here.

## reference_level_dbm: float {O}
**default: -40**
Sets a reference value in the display. **NOTE:** Currently broken for Anritsu. 

## display_level_scale_dbm: float {O}
**default: 10**
Sets dBm/div in the display.

## Note to Sample_points: int {M}
For this device only certain values are allowed:
	251
	501
	1001
	2001
	5001
**Note:** If you supply another value the system will automatically round up to the closest value, or down if you supplied a too large number

## Note to Linear_Resolution: int {M}
For this device only certain values are allowed:
	1.0
	0.5
	.02
	.01
	0.07
	0.05
**Note:** If you supply another value the system will automatically round down to the closest value, or down if you supplied a too large number