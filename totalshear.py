from datetime import datetime



from siphon.simplewebservice.wyoming import WyomingUpperAir
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
import numpy as np
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units

import sys
# Create a datetime object for the sounding and string of the station identifier.
date = datetime(2024, 1, 18, 0)
station = '42809'

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
v_wind = df['v_wind'].values * units(df.units['v_wind'])
heights = df['height'].values * units(df.units['height'])
print(mpcalc.wind_direction(u_wind,v_wind))
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(1,1,1)

zarray=np.array([0,0.5,1,2,3,4,5,6,7,8,9])*units.km
uarray=u_wind*units.knots
varray=v_wind*units.knots

fig = plt.figure(figsize=(8, 8),facecolor='white')
ax = plt.subplot()
h = Hodograph(ax, component_range=50.)

h.add_grid(increment=10)

for i in range(len(zarray)-1):
    plt.arrow(uarray[i].m, varray[i].m,(uarray[1:]-uarray[:-1])[i].m,(varray[1:]-varray[:-1])[i].m,width=0.5,head_width=2,facecolor='r',edgecolor=None,length_includes_head=True)
for i,z in enumerate(zarray):
    plt.scatter(uarray[i],varray[i], s=50, color='k')
plt.savefig('tot_shear_hodo.png')
plt.show()
