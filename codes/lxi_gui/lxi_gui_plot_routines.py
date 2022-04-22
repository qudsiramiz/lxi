import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec

def time_series_plot(df=None, ms=1):

    # Plot the data in a 3 by 1 subplot
    fig = plt.figure(num=None, figsize=(4,12), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
    gs = gridspec.GridSpec(3, 1, width_ratios=[1, 1])

    # Plot the counts data
    axs1 = plt.subplot(gs[0, 0])
    axs1.plot(df.index, df['counts'], color='black', marker='.', ms=ms, linestyle='None')
    axs1.set_ylabel('Counts', fontsize=20)
    axs1.set_xlabel('Time', fontsize=20)
    axs1.set_xlim(df.index.min(), df.index.max())

    # Plot the Temperature data and share the x-axis)
    axs2 = plt.subplot(gs[1, 0], sharex=ax1)
    axs2.plot(df.index, df['temp'], color='black', marker='.', ms=ms, linestyle='None')
    axs2.set_ylabel('Temperature (K)', fontsize=20)
    axs2.set_xlabel('Time', fontsize=20)

    # Plot the Voltage data
    axs3 = plt.subplot(gs[2, 0])
    axs3.plot(df.index, df['voltage'], color='black', marker='.', ms=ms, linestyle='None')
    axs3.set_ylabel('Voltage (V)', fontsize=20)
    axs3.set_xlabel('Time', fontsize=20)

    plt.savefig("figures/time_series_plot.png", dpi=300, bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False, frameon=None)

def xy_plot(df=None, ms=1):

    # Plot the location of each observation in the xy plane
    fig = plt.figure(num=None, figsize=(8,8), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
    gs = gridspec.GridSpec(1, 1, width_ratios=[1, 1])

    # Plot the data
    axs1 = plt.subplot(gs[0, 0])
    axs1.plot(df['x_val'], df['y_val'], color='black', marker='.', ms=ms, linestyle='None')
    axs1.set_ylabel('y (m)', fontsize=20)
    axs1.set_xlabel('x (m)', fontsize=20)
    axs1.set_xlim(df['x_val'].min(), df['x_val'].max())
    axs1.set_ylim(df['y_val'].min(), df['y_val'].max())