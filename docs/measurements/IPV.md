[Table of contents](../readme.md)
# IPV measurements
The IPV routine measures Optical Power and Voltage for a list of biasing currents. To make it work you need to supply most of the following params in the TOML file:

Items marked with {M} are mandatory, {O} optional.


```toml
#Std units: mA, V, mW, nm
[measurement]
Type = "ipv"
Save_folder = "c:/LABDATA"
DC_unit = "keithley2400"    # Refers to the [] below only
P_unit = "INT_sphere"
V_max = 5
Current = [[1, 0.1, 5], [5, 0.5, 15]]  # mA [min, step, max]

# Optional arguments
Rollover_threshold = 0  # Stops measurement when power < rollover_threshold * maxpower
Rollover_min = 0        # Doesn't do rollover check on power values lower than this
Offset_background = 10  # Number of times to measure background and offset
Plot_interval = 20      # Update plot every nth measurement
Keep_plot = 0           # To keep plot after measurement is done
Verbose_printing = 0    # Flag for printing
```
## measurement {M}
The measurement dict contains all info for your specific measurement. It must always be present!

## Type: string {M}
Contains the name of the measurement types. In this case wa want a IPV measurement.

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

## P_unit: string {M}
Contains a direct reference to the TOML-key for the configuration of your power unit of choice, eg
``` toml
P_unit = "INT_sphere"
...

.[INT_sphere]
# Specific config
```

## V_max: float {M}
See [general](general.md). 

## Current: list(list(float)) {M}
See [general](general.md). 

## Rollover_threshold: float {O}
**Default: 0 (disabled)**
This specifies a percentage of the maximum measured power where the measurement will auto stop. Eg 0.8 indicates that the measurement stops when the measured value is **less** than 80% of the currently recorded maximum for this measurement. 

## Rollover_min: float {O}
**Default: 0 (disabled)**
This specifies a minimum power (in mW) that are ignored by the rollover functionality. All recorded values lower than this are ignored when looking for the maximum. Using this is preferred when low input values are noisy, eq for the measurement (0, 0, 0.01, *0.05*, 0.1, 0.2, 0.3, ...) where the small dip to 0.05 stops the measurement, even though it's just noise and you want to continue.

## Offset_background: int {O}
**Default: 0 (disabled)**
Specifies the amount of times (if any) you measure the background optical power before turning on the LED. If you do this, the average of the results will be subtracted from all subsequent measurements yielding only the optical power generated from the device under test (DUT). 

## Plot_interval: int {O}
**Default: 20**
This specifies how often the plot should be updated. Due to slow rendering a larger interval will make the measurements go faster since less time is spent redrawing the plot.

## Keep_plot: bool | int {O}
**Default: False**
Decides whether the IPV plot shall be kept alive after measurement is done or not. Usually it's enough to only see it during the measurements.

## Verbose_printing: int {O}
See [general](general.md). 