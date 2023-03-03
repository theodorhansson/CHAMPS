# General configs
## Save_folder: string {M}
Contains the path to a folder in which the data from your measurements will be saved

## V_max: float {M}
This will set the compliance voltage on the current source to this value

## Current: list(list(float)) {M}
Contains the intervals where you want so measure in the form of (min, step, max). Eg (0.1, 0.1, 0.5) will produce a linspace like (0.1, 0.2, 0.3, 0.4, 0.5). The last point is guaranteed to be in the interval, even if it doesn't fit with the spacing, like for the spec (0.1, 0.15, 0.5), the list is (0.1, 0.25, 0.4, 0.5).