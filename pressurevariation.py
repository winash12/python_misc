import pandas as pd
import numpy as np
import sys
from  scipy import signal
import matplotlib.pyplot as plt



data = pd.read_csv('ICHENN39_NOV2021.csv',parse_dates=[['Date','Time']])

times = pd.to_datetime(data['Date_Time'],unit='ms')
print(times)

minutes = times.view(np.int64)/6E10
print(minutes)

print(minutes.shape)


df1 = (data[['Pressure_hPa']])
print(df1)


fig,ax = plt.subplots()
ax.plot(times.ravel(),df1.to_numpy().ravel())
plt.xlabel('Time')
plt.ylabel('Atmospheric Pressure hPa')
plt.show()

sys.exit()
df2 = (data[['Precip_Rate_mm']])



freq = np.linspace(0, np.pi/300.0,8928//2)

xx = df1.to_numpy().ravel()

xx_detrended = signal.detrend(xx,type='constant')
xx_detrended = signal.detrend(xx,type='constant')

periodogram = signal.lombscargle(minutes,xx_detrended,freq[1:])
print(periodogram.shape)


fig,ax = plt.subplots()

print(periodogram)
ax.plot(freq[1:],np.sqrt(4*periodogram))
plt.xlabel('Frequency(rad/second)')
plt.ylabel('Periodogram')
#plt.show()
plt.savefig('b.png')


