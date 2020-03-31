
import tropycal.tracks as tracks

import datetime as dt
import sys

import matplotlib.pyplot as plt

hurdat_atl = tracks.TrackDataset(basin='north_indian',source='ibtracs',ibtracs_mode="jtwc")

# Let's retrieve an instance of Hurricane Kyarr from 2019:

storm = hurdat_atl.get_storm(('vardah',2016))

###########################################
# This instance of Storm contains several methods that return the storm data back in different data types. The following examples will show # how to retrieve 3 different data types.
# 

print(storm.to_dict())

print(storm.to_xarray())

print(storm.to_dataframe())

ax = storm.plot(return_ax=True)

plt.savefig('vardah.png')
