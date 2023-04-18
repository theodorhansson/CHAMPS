# Devices, advanced notes

Here are details of how each device works.

## Keithley2400
The Keithley SourceMeter is connected by GPIB. The standard functions are implemented in the class and does nothing special.

## Anritsu MS9710A
This OSA is connected via GPIB. Most things are as expected. A note is that the binary conversion for the read_data-function is a bit advanced (but fast!). It requires some dirty raw reads, but hasn't failed us yet.

## Ophir IS6-D-UV
This integrating sphere uses a local DLL to connect over USB. Most importantly the data is received through a stream, so to make sure it has fresh data it waits a short bit.

## BeamGage
This is actually just a wrapper for the program, but it uses `pythonnet` to speak with a DLL. The DLL is named `Beamgage_python_wrapper.dll` and lives in `/drivers/beamgage_drivers/` . It contains a class, `Beamgage`, that takes two arguments: *window title*(str) and *show window*(bool). The latter simply makes the window invisible if set to false. 

When you create a new instance of the class you may either access its property `bg` or use the function `get_AutomatedBeamGage()` to get a .NET object of `AutomatedBeamGage`-type. This behaves just as the documentation from Spiricon and BeamGage suggests, despite being living inside python.