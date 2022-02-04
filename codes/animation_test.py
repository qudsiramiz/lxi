# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 10:51:57 2022

@author: ahmad
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
from matplotlib.colors import LinearSegmentedColormap

fig, ax = plt.subplots()
ax.set_xlabel('X Axis', size = 12)
ax.set_ylabel('Y Axis', size = 12)
ax.axis([0,1,0,1])
x_vals = []
y_vals = []
intensity = []
iterations = 100

t_vals = np.linspace(0,1, iterations)

colors = [[0,0,1,0],[0,0,1,0.5],[0,0.2,0.4,1]]
cmap = LinearSegmentedColormap.from_list("", colors)
scatter = ax.scatter(x_vals,y_vals, c=[], cmap=cmap, vmin=0,vmax=1)

def get_new_vals():
    n = np.random.randint(1,5)
    x = np.random.rand(n)
    y = np.random.rand(n)
    return list(x), list(y)

def update(t):
    global x_vals, y_vals, intensity
    # Get intermediate points
    new_xvals, new_yvals = get_new_vals()
    x_vals.extend(new_xvals)
    y_vals.extend(new_yvals)

    # Put new values in your plot
    scatter.set_offsets(np.c_[x_vals,y_vals])

    #calculate new color values
    intensity = np.concatenate((np.array(intensity)*0.96, np.ones(len(new_xvals))))
    scatter.set_array(intensity)

    # Set title
    ax.set_title('Time: %0.3f' %t)

ani = matplotlib.animation.FuncAnimation(fig, update, frames=t_vals,interval=50)

ani.save("../figures/test.gif")
#plt.show()