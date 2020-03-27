# Copyright (c) 2018 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""
======================
Cross Section Analysis
======================

The MetPy function `metpy.interpolate.cross_section` can obtain a cross-sectional slice through
gridded data.
"""
from netCDF4 import Dataset,num2date

from cdo import Cdo
from nco import Nco
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import sys
import metpy.calc as mpcalc
from metpy.interpolate import cross_section


cdo = Cdo()
cdo.timmean(input='PFile.nc',output='AFile.nc')
nco = Nco()
nco.ncwa(input='AFile.nc',output='BFile.nc',options=['-a', 'bnds'])
nco.ncks(input='BFile.nc',output='CFile.nc',options=['-C','-O','-x','-v','time_bnds'])

cdo.timmean(input='rhumFile.nc',output='dFile.nc')
nco.ncwa(input='dFile.nc',output='eFile.nc',options=['-a', 'bnds'])
nco.ncks(input='eFile.nc',output='fFile.nc',options=['-C','-O','-x','-v','time_bnds'])
fFile = Dataset('fFile.nc','r')

rhum = fFile.variables['rhum'][:]

z = np.zeros((1, 9,73,144), dtype=rhum.dtype)
c=np.concatenate((rhum,z), axis=1)

data = xr.open_dataset('./CFile.nc')
data["rhum"]=(['time','level','lat','lon'],c)
data = data.metpy.parse_cf().squeeze()

print(data)


##############################
# Define start and end points:

start = (5.0, 75.0)
end = (15.0,80.0)

##############################
# Get the cross section, and convert lat/lon to supplementary coordinates:

cross = cross_section(data, start, end).set_coords(('lat', 'lon'))

##############################
# For this example, we will be plotting potential temperature, relative humidity, and
# tangential/normal winds. And so, we need to calculate those, and add them to the dataset:

cross['rhum'].metpy.convert_units('percent')

temperature, pressure,relative_humidity = xr.broadcast(cross['air'],cross['level'],cross['rhum'])



theta = mpcalc.potential_temperature(pressure, temperature)
print(max(theta.flatten()))
print(min(theta.flatten()))

# These calculations return unit arrays, so put those back into DataArrays in our Dataset
cross['Potential_temperature'] = xr.DataArray(theta,
                                              coords=temperature.coords,
                                              dims=temperature.dims,
                                              attrs={'units': theta.units})
cross['rhum'] = xr.DataArray(relative_humidity/100,
                             coords=relative_humidity.coords,
                             dims=relative_humidity.dims,
                             attrs={'units': relative_humidity.units})

cross['uwnd'].metpy.convert_units('knots')
cross['vwnd'].metpy.convert_units('knots')
cross['t_wind'], cross['n_wind'] = mpcalc.cross_section_components(cross['uwnd'],
                                                                   cross['vwnd'])

print(cross)

##############################
# Now, we can make the plot.

# Define the figure object and primary axes
fig = plt.figure(1, figsize=(16., 9.))
ax = plt.axes()

# Plot potential temperature using contour, with some custom labeling

rh_contour = ax.contourf(cross['lon'], cross['level'], cross['rhum'],
                         levels=np.arange(0, 100, 5), cmap='YlGnBu')
rh_colorbar = fig.colorbar(rh_contour)

theta_contour = ax.contour(cross['lon'], cross['level'], cross['Potential_temperature'],
                           levels=np.arange(250, 700, 5), colors='k', linewidths=2)
theta_contour.clabel(theta_contour.levels[1::2], fontsize=8, colors='k', inline=1,
                     inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

# Plot winds using the axes interface directly, with some custom indexing to make the barbs
# less crowded
wind_slc_vert = list(range(0, 17, 1))

wind_slc_horz = slice(5, 100, 5)

ax.barbs(cross['lon'][wind_slc_horz], cross['level'][wind_slc_vert],
         cross['t_wind'][wind_slc_vert, wind_slc_horz],
         cross['n_wind'][wind_slc_vert, wind_slc_horz], color='k')

# Adjust the y-axis to be logarithmic
ax.set_yscale('symlog')
ax.set_yticklabels(np.arange(1000, 50, -100))
ax.set_ylim(cross['level'].max(), cross['level'].min())
ax.set_yticks(np.arange(1000, 50, -100))

# Define the CRS and inset axes
data_crs = data['hgt'].metpy.cartopy_crs
ax_inset = fig.add_axes([0.125, 0.665, 0.25, 0.25], projection=data_crs)

# Plot geopotential height at 500 hPa using xarray's contour wrapper
ax_inset.contour(data['lon'], data['lat'], data['hgt'].sel(level=500.),
                 levels=np.arange(5100, 6000, 60), cmap='inferno')

# Plot the path of the cross section
endpoints = data_crs.transform_points(ccrs.Geodetic(),
                                      *np.vstack([start, end]).transpose()[::-1])
ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
ax_inset.plot(cross['lon'], cross['lat'], c='k', zorder=2)

# Add geographic features
ax_inset.coastlines()
ax_inset.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='k', alpha=0.2, zorder=0)

# Set the titles and axes labels
ax_inset.set_title('')
ax.set_title('NCAR Cross-Section \u2020 {} to {} \u2020 Valid: {}\n'
             'Potential Temperature (K), Tangential/Normal Winds (knots), '
             'Relative Humidity (dimensionless)\n'
             'Inset: Cross-Section Path and 500 hPa Geopotential Height'.format(
                 start, end, cross['time'].dt.strftime('%Y-%m-%d %H:%MZ').item()))
ax.set_ylabel('Pressure (hPa)')
ax.set_xlabel('Longitude (degrees east)')
rh_colorbar.set_label('Relative Humidity (dimensionless)')

plt.savefig('crosssection.png')
plt.show()

##############################
# Note: The x-axis can display any variable that is the same length as the
# plotted variables, including latitude. Additionally, arguments can be provided
# to ``ax.set_xticklabels`` to label lat/lon pairs, similar to the default NCL output.
