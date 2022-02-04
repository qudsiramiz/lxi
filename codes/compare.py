# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 12:23:26 2022

@author: ahmad
"""

import matplotlib.pyplot as plt
import pandas as pd

df1 = pd.read_pickle('../data/test/1.p')

df5 = pd.read_pickle('../data/test/5.p')

x1 = df1['pvectorlist'][:, 0] * 1e3  # convert to mm
y1 = df1['pvectorlist'][:, 1] * 1e3  # convert to mm
z1 = df1['pvectorlist'][:, 2] * 1e3  # convert to mm

x5 = df5['pvectorlist'][:, 0] * 1e3  # convert to mm
y5 = df5['pvectorlist'][:, 1] * 1e3  # convert to mm
z5 = df5['pvectorlist'][:, 2] * 1e3  # convert to mm

diff_x = x1[::5] - x5[0:10000]

plt.figure()
plt.plot(y1, z1, 'r.', ms=5, alpha=1, label='1')
plt.plot(y5, z5, 'b.', ms=1, alpha=0.5, label='5')
#plt.xlim(9.96, 10.15)
#plt.ylim(29.9, 30.3)
#plt.plot(diff_x, 'r.', ms=1)
plt.show()
