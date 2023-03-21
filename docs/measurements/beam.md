# Beam profile measurements
The Beam routine takes a picture of the beam for a list of biasing currents. To make it work you need to supply most of the following params in the TOML file.

Items marked with {M} are mandatory, {O} optional.
**Note:** The resolution of the camera is approx 1920x1440=2 764 800 pixels. This results in HUGE output files.

```toml
#Std units: mA, V, counts

[measurement]
Type = "beam_profile"
Save_folder = "c:/LABDATA"
DC_unit = "keithley2400"    # Refers to the [] below only
BEAM_unit = "beam"          # Refers to the [] below only
V_max = 5
Current = [[1, 0.1, 5], [5, 0.5, 15]]  # [min, step, max] 

# Optional
verbose_printing = 0
plot_image =  0
keep_plot = 0
hold_console = 1  

[keithley2400]
type = "keithley2400"   # The specific type of unit
GPIB_address = "24"  

[beam]
type = "beamgage"
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

## BEAM_unit: string {M}
Contains a direct reference to the TOML-key for the configuration of your power unit of choice, eg
``` toml
P_unit = "SpecificBeamThingy"
...

.[SpecificBeamThingy]
# Specific config
```

## V_max: float {M}
See [general](general.md). 

## Current: list(list(float)) {M}
See [general](general.md). 

## Verbose_printing: int {O}
See [general](general.md). 

## Plot_image: bool {O}
**Default: False**
Whether to plot the image you got from Beamgage or not.

## Keep_plot: bool {O}
**Default: False**
Whether to plot the image you got from Beamgage or not.

## Hold_console: bool {O}
**Default: True**
Whether to block console awaiting manual configuration in Beamgage or not. 
Every measurement a new instance of Beamgage is created and it's in that window most picture settings are done. This option stops the execution of the measurement until you are done making those changes.