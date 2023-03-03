[Table of contents](../readme.md)
# Ophir IS6-D-UV
The equipment class that controls the Ophir IS6-D-UV integrating sphere.
Items marked with {M} are mandatory, {O} optional.


```toml
.[INT_sphere]
Type = "ophir_IS6_D_UV"
Range = 2
Min_measure_time = 0.2  # How long to wait between new data to arrive from sphere
Wavelength = 5
```
## INT_sphere {M}
The measurement dict contains all info for your specific device. It must always be present! 
**Note:** you may name it someting else:
``` TOML
P_unit = "The_best_P_unit"
...

.[The_best_P_unit]
#Config
```

## Type: string {M}
Contains the name of the device class. This must match with the identifier set in the script!

## Range: int {M}
The identifier of the range of powers you want to use:
	0    auto
	1    1 W
	2    300 mW
	3    30 mW
	4    3 mW
	5    300 uW
	6    30 uW
	7    3 uW

## Wavelength: int {M}
The identifier of the wavelength at which you measure:
	0    940 nm
	1    300 nm
	2    633 nm
	3    543 nm
	4    870 nm
	5    850 nm