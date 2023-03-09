[Table of contents](../readme.md)
# Use your own measurements and instruments 
The easiest way here is to take a good look of the IPV measurement protocol. Some extra details are given below.

# Things you need to do
## Main.py
Here you need to implement new logic in the function *identify_measurement_type*. This function returns the **function reference** to the init of measurement code you plan to use.

**Note:** For the rest of Main to work, your measurement needs to return two things:
- The results in a dict
- The config you used, as a dict.

## Communication.py
This file returns the class object that the TOML config requested. To implement new instruments just create a function for the new class or amend the existing. 

## Your_Measurement.py
Here you put all parts of the measurement together. You init objects (as current sources or OSAs), measure whatever you want to etc. 
**Note:** For Main.py to work, your measurement needs to return two things:
- The results in a dict
- The config you used, as a dict.

## Utils.py
This file contains a lot of nice helper functions for you to use. Most importantly, you can check for required arguments and merge optional arguments to fill in the blanks. You can also ramp current, get lists of bias currents, make sure values are in a list of allowed values.  