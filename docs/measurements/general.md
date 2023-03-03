[Table of contents](../readme.md)
# General configs
## Save_folder: string {M}
Contains the path to a folder in which the data from your measurements will be saved

## V_max: float {M}
This will set the compliance voltage on the current source to this value

## Current: list(list(float)) {M}
Contains the intervals where you want so measure in the form of (min, step, max). Eg (0.1, 0.1, 0.5) will produce a linspace like (0.1, 0.2, 0.3, 0.4, 0.5). The last point is guaranteed to be in the interval, even if it doesn't fit with the spacing, like for the spec (0.1, 0.15, 0.5), the list is (0.1, 0.25, 0.4, 0.5).

## Verbose_printing: int {O}
Sets the level of verbose printing you want. Note that this is actually a set of binary flags. To use multiple, add their decimal representation.
| **Decimal** | **Binary** | **Level**                                                    |
|-------------|------------|--------------------------------------------------------------|
| 0           | 0000 0000  | Nothing                                                      |
| 1           | 0000 0001  | Some results: Singular data points                           |
| 2           | 0000 0010  | All results: Large matrices                                  |
| 4           | 0000 0100  | Some instrument methods: communication init, enable, disable |
| 8           | 0000 1000  | All instrument methods                                       |
| 16          | 0001 0000  | File access and save                                         |

If you want *both* file access and some instrument methods, you enter 16+4=20 or 0001 0100:

```toml
Verbose_printing = 20
# OR
Verbose_printing = 0b00010100
```