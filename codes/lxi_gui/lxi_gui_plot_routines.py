from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Set the font style to Times New Roman
font = {'family': 'serif', 'weight': 'normal', 'size': 10}
plt.rc('font', **font)
plt.rc('text', usetex=True)

def plot_histogram(
    df=None,
    bins=None,
    cmin=5,
    x_min=None,
    x_max=None,
    y_min=None,
    y_max=None,
    density=True,
    norm=None,
    ):

    if x_min is None:
        x_min = np.nanmin(df.x_val)
    if x_max is None:
        x_max = np.nanmax(df.x_val)
    if y_min is None:
        y_min = np.nanmin(df.y_val)
    if y_max is None:
        y_max = np.nanmax(df.y_val)
    if bins is None:
        bins = 50
    if norm == "linear":
        norm = mpl.colors.Normalize()
    elif norm == "log":
        norm = mpl.colors.LogNorm()
    elif norm is None:
        norm = mpl.colors.Normalize()

    x_range = [x_min, x_max]
    y_range = [y_min, y_max]

    hst = plt.hist2d(df.x_val, df.y_val, bins=bins, range=[x_range, y_range], cmin=cmin,
                     density=density)
    z_counts = np.transpose(hst[0])
    plt.close("all")

    # Make a 2d histogram of the data
    fig = plt.figure(num=None, figsize=(6,6), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1])

    axs = plt.subplot(gs[0, 0])
    im = axs.imshow(z_counts, cmap='Spectral', norm=norm,
                    extent=[x_range[0], x_range[1], y_range[0], y_range[1]], aspect='auto')

    divider1 = make_axes_locatable(axs)
    cax = divider1.append_axes("top", size="5%", pad=0.02)
    cbar = plt.colorbar(im, cax=cax, orientation='horizontal', ticks=None, fraction=0.05,
                         pad=0.0)

    cbar.ax.tick_params(axis='x', which='both', direction='in', labeltop=True, top=True, 
                         labelbottom=False, bottom=False, width=1, length=10, 
                         labelsize=15, labelrotation=0, pad=0)

    cbar.ax.xaxis.set_label_position('top')

    if density == True:
        cbar.set_label('Density', fontsize=20)
    else:
        cbar.set_label( r'$N$', fontsize=15, labelpad=0.0, rotation=0)

    axs.set_ylabel('y (m)', fontsize=20)
    axs.set_xlabel('x (m)', fontsize=20)
    axs.set_xlim(x_min, x_max)
    axs.set_ylim(y_min, y_max)

    # Save the figure
    save_file_path = "figures/"
    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    plt.savefig(f"{save_file_path}/xy_plot.png", dpi=300, bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

    plt.close("all")
    return fig

def plot_time_series(df=None, ms=5, alpha=1):

    # TODO: Add alpha and market styyle option to the plot_time_series function
    
    #Index(['TimeStamp', 'HK_id', 'PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp',
    #   'HVsupplyTemp', '+5.2V_Imon', '+10V_Imon', '+3.3V_Imon', 'AnodeVoltMon',
    #   '+28V_Imon', 'ADC_Ground', 'Cmd_count', 'Pinpuller_Armed', 'Unused',
    #   'Unused.1', 'HVmcpAuto', 'HVmcpMan', 'DeltaEvntCount',
    #   'DeltaDroppedCount', 'DeltaLostevntCount'],
    #  dtype='object')

    tick_label_size = 18
    axis_label_size = 25

    # Plot the data
    fig = plt.figure(num=None, figsize=(3,8), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
    gs = gridspec.GridSpec(3, 1, width_ratios=[1])

    # Plot the counts data
    axs1 = plt.subplot(gs[0, 0])
    axs1.plot(df.index, df.OpticsTemp, color='black', marker='.', ms=ms, linestyle='None', alpha=alpha)
    axs1.tick_params(axis='both', which='major', labelsize=tick_label_size)
    axs1.set_ylabel('OpticsTemp (K)', fontsize=axis_label_size)
    axs1.set_xlim(np.nanmin(df.index), np.nanmax(df.index))

    # Plot the Temperature data and share the x-axis)
    axs2 = plt.subplot(gs[1, 0], sharex=axs1)
    axs2.plot(df.index, df.PinPullerTemp, color='black', marker='.', ms=ms, linestyle='None', alpha=alpha)
    axs2.tick_params(axis='both', which='major', labelsize=tick_label_size)
    axs2.set_ylabel('PinPullerTemp', fontsize=axis_label_size)

    # Plot the Voltage data
    axs3 = plt.subplot(gs[2, 0], sharex=axs1)
    axs3.plot(df.index, df.DeltaDroppedCount, color='black', marker='.', ms=ms, linestyle='None', alpha=alpha)
    axs3.tick_params(axis='both', which='major', labelsize=tick_label_size)
    axs3.set_ylabel('DeltaDroppedCount', fontsize=axis_label_size)
    axs3.set_xlabel('Time', fontsize=axis_label_size)

    save_file_path = "figures/"
    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    plt.savefig(f"{save_file_path}/time_series_plot.png", dpi=300, bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

    plt.close("all")
    return fig