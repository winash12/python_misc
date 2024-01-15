from datetime import datetime



from siphon.simplewebservice.wyoming import WyomingUpperAir
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units

import sys

####################################################
# Create a datetime object for the sounding and string of the station identifier.
date = datetime(2020, 3, 15, 0)
station = '42101'

####################################################
# Make the request (a pandas dataframe is returned).
df = WyomingUpperAir.request_data(date, station)

####################################################
# Inspect data columns in the dataframe.
print(df.columns)

####################################################
# Pull out a specific column of data.
print(df['pressure'])

####################################################
# Units are stored in a dictionary with the variable name as the key in the `units` attribute
# of the dataframe.
print(df.units)

####################################################
print(df.units['pressure'])

####################################################
# Units can then be attached to the values from the dataframe.
pressure = df['pressure'].values * units(df.units['pressure'])
temperature = df['temperature'].values * units(df.units['temperature'])
wind_speed = df['speed'].values * units.knots
print(temperature)

dewpoint = df['dewpoint'].values * units(df.units['dewpoint'])
print(dewpoint)

u_wind = df['u_wind'].values * units(df.units['u_wind'])
print(u_wind)
v_wind = df['v_wind'].values * units(df.units['v_wind'])
heights = df['height'].values * units(df.units['height'])
print(mpcalc.wind_direction(u_wind,v_wind))
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(1,1,1)
h= Hodograph(ax,component_range=60.)
h.plot(u_wind,v_wind,linewidth=5)
h.add_grid(increment=10)
#h.add_grid(increment=20,color='tab:orange',linestyle='-')
h.plot_colormapped(u_wind, v_wind, wind_speed)  # Plot a line colored by wind speed
plt.savefig('hodograph.png')
plt.show()
sys.exit()

#lcl_pressure, lcl_temperature = mpcalc.lcl(pressure[0], temperature[0], dewpoint[0])

#print(lcl_pressure, lcl_temperature)

# Calculate the parcel profile.
parcel_prof = mpcalc.parcel_profile(pressure, temperature[0], dewpoint[0]).to('degC')
