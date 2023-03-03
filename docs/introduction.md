[Table of contents](readme.md)
# Introduction
CHAMPS aims to provide a simple and modular experience for lab measurements. This is accomplished through a [TOML config file](https://toml.io) and easy writing of your own instrument wrappers and new measurement routines. 

# Getting started
First you need to get all the dependencies. Install this by running
``` python
pip install requirements.txt -r
```
Please not that this requires at least Python 3.11. Then the easiest way to get started is by using the default config files, eg for [IPV](../IPVconfig.toml) or [Spectrum](../OSAconf.toml) measurements. Specify the params you want to use in the file and then run 
```python
python main.py your_config.toml
```
from the terminal. 

When done, close the figure and look for your saved data!

# Further reading
Take a look at the configs for different measurement types or the instruments themselves. If you're brave you might even want to develop your own routines!