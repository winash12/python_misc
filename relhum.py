from cdo import Cdo
from nco import Nco
from netCDF4 import Dataset,num2date
import numpy as np
import sys
cdo = Cdo()
cdo.timmean(input='rhumFile.nc',output='dFile.nc')
nco = Nco()
nco.ncwa(input='dFile.nc',output='eFile.nc',options=['-a', 'bnds'])
nco.ncks(input='eFile.nc',output='fFile.nc',options=['-C','-O','-x','-v','time_bnds'])
fFile = Dataset('fFile.nc','r')
rhum = fFile.variables['rhum'][:]
#print(rhum.shape)
gFile = Dataset('CFile.nc','r')
temp = gFile.variables['air'][:]

z = np.zeros((1, 9,73,144), dtype=rhum.dtype)
c=np.concatenate((rhum,z), axis=1)
print(c[0][10][72][143])
