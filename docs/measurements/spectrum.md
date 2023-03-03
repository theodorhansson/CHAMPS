[Table of contents](../readme.md)
# Spectrum measurements
The Spectrum routine measures the spectrum output for a list of biasing currents. To make it work you need to supply most of the following params in the TOML file:

Items marked with {M} are mandatory, {O} optional.


```toml
#Std units: mA, V, mW, nm
[measurement]
Type = "spectrum"
Save_folder = "c:/LABDATA"
DC_unit = "keithley2400"    # Refers to the [] below only
OSA_unit = "anritsu"        # Refers to the [] below only
V_max = 5
Current = [[1, 0.1, 5], [5, 0.5, 15]]  # [min, step, max]

Center_wavelength = 850 #nm
Wavelength_span = 20 #nm
Linear_resolution = 0.1 #nm
sample_points = 501

# Optional
avg_factor = 10
sensitivity = "SHI1"   # Only affects ando
verbose_printing = 0
```
## measurement {M}
The measurement dict contains all info for your specific measurement. It must always be present!

## Type: string {M}
Contains the name of the measurement types. In this case wa want a spectrum measurement.

## Save_folder: string {M}
See [general](general.md). 

## DC_unit: string {M}
Contains a direct reference to the TOML-key for the configuration of your DC unit/current source of choice, eg
``` toml
DC_unit = "keithley2400"
...

.[keithley2400]
# Specific config
```

## OSA_unit: string {M}
Contains a direct reference to the TOML-key for the configuration of your power unit of choice, eg
``` toml
P_unit = "Anritsu_OSA_without_filters"
...

.[Anritsu_OSA_without_filters]
# Specific config
```

## V_max: float {M}
See [general](general.md). 

## Current: list(list(float)) {M}
See [general](general.md). 

## Center_wavelength: float {M}
This specifies the center (in nm) of the scanning window of the Optical Spectrum Analyzer.

## Wavelength_span: float {M}
Sets the width of the scanning window (in nm). A span of 20 nm centered at 850 nm will scan 840 to 860nm

## Linear_resolution: float {M}
This specifies the linear resolution of the grating (in nm). It probably means how precise the grating is moved. For resoultion in data, see  *Sample_points*.
**Note:** Some OSA's only allow specific values. If you supply something incompatible the system will round down to the closest accepted value.

## Sample_points: int {M}
This specifies the number of sample points you'd like to get. 
**Note:** Some OSA's only allow specific values. If you supply something incompatible the system will round up to the closest accepted value.

## avg_factor: float {O}
**default: 5**
This specifies the pointwise averaging amount, ie how many times a point will be measured before moving on to the next.

## Sensitivity: string {O}
**default: SHI1**
Sets the sensitivity of the OSA. For those who don't have a sensitivity you can just use the default as the command wont be sent to the OSA if it doesn't have the setting.

## Verbose_printing: int {O}
See [general](general.md). 