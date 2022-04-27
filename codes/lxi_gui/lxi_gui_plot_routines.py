from pathlib import Path
from shutil import which
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns

# Set the font style to Times New Roman
font = {'family': 'serif', 'weight': 'normal', 'size': 10}
plt.rc('font', **font)
plt.rc('text', usetex=False)


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
        norm = mpl.colors.LogNorm()

    tick_label_size = 18
    axis_label_size = 25

    x_range = [x_min, x_max]
    y_range = [y_min, y_max]

    # Remove rows with duplicate indices
    df = df[~df.index.duplicated(keep='first')]

    hst = plt.hist2d(df.x_val, df.y_val, bins=bins, range=[x_range, y_range], cmin=cmin,
                     density=density)
    z_counts = np.transpose(hst[0])
    plt.close("all")

    # Make a 2d histogram of the data
    fig = plt.figure(num=None, figsize=(6,7), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0., hspace=3)

    gs = gridspec.GridSpec(8, 4, height_ratios=[1, 1, 1, 1, 1, 1, 1, 1], width_ratios=[1, 1, 1, 1])

    axs1 = plt.subplot(gs[0:5, 0:4])
    #im1 = sns.jointplot(data=df[["x_val", "y_val"]], kind="kde")
    im1 = axs1.imshow(z_counts, cmap='Spectral', norm=norm,
                      extent=[x_range[0], x_range[1], y_range[0], y_range[1]], aspect='auto')

    divider1 = make_axes_locatable(axs1)
    cax1 = divider1.append_axes("top", size="5%", pad=0.02)
    cbar1 = plt.colorbar(im1, cax=cax1, orientation='horizontal', ticks=None, fraction=0.05,
                         pad=0.0)

    cbar1.ax.tick_params(axis='x', which='both', direction='in', labeltop=True, top=True, 
                         labelbottom=False, bottom=False, width=1, length=10, 
                         labelsize=15, labelrotation=0, pad=0)

    cbar1.ax.xaxis.set_label_position('top')

    if density is True:
        cbar1.set_label('Density', fontsize=20)
    else:
        cbar1.set_label(r'$N$', fontsize=15, labelpad=0.0, rotation=0)

    axs1.set_xlabel('x (m)', fontsize=axis_label_size)
    axs1.set_ylabel('y (m)', fontsize=axis_label_size)
    axs1.set_xlim(x_min, x_max)
    axs1.set_ylim(y_min, y_max)
    axs1.tick_params(axis="both", which="major", labelsize=tick_label_size)

    # Save the figure
    save_file_path = "figures/"
    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    plt.savefig(f"{save_file_path}/xy_plot.png", dpi=300, bbox_inches='tight', pad_inches=0.05,
                facecolor='w', edgecolor='w', transparent=False)

    plt.close("all")
    return fig


def plot_indiv_time_series(df=None, key="PinPullerTemp", ms=5, alpha=1):

    tick_label_size = 18
    axis_label_size = 25

    # Plot the data
    fig = plt.figure(num=None, figsize=(4, 2), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
    gs = gridspec.GridSpec(1, 1, width_ratios=[1])

    axs1 = plt.subplot(gs[0])
    axs1.plot(df.index, df[key], '.k', alpha=alpha, ms=ms)
    axs1.set_xlabel('Time (s)', fontsize=axis_label_size)
    #axs1.set_ylabel(f'{key} (K)', fontsize=axis_label_size)
    axs1.tick_params(axis="both", which="major", labelsize=tick_label_size)
    axs1.text(1, 0.95, key, horizontalalignment='right', fontsize=tick_label_size,
              verticalalignment='top', transform=axs1.transAxes)

    # Save the figure
    save_file_path = "figures/"
    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    plt.savefig(f"{save_file_path}/{key}_time_series_plot.png", dpi=300, bbox_inches='tight',
                pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

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

    plt.savefig(f"{save_file_path}/time_series_plot.png", dpi=300, bbox_inches='tight',
                pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

    plt.close("all")
    return fig


# Function for KDE plot using Seaborn for difference cases
def plot_kde(df, key1, key2, data_type=None, fig_save=True):

    pad = 0.02
    labelsize = 28
    ticklabelsize = 20
    clabelsize = 15
    ticklength = 10

    # Remove the rows with duplicated indices
    df = df[~df.index.duplicated(keep='first')]

    fig = plt.figure(num=None, figsize=(3, 4), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0., hspace=3)

    #axs1 = sns.jointplot(x=x_data, y=y_data, kind="kde", cbar=True, thresh=False, fill=True,
    #                     levels=nlevels, log_scale=False, hue_norm=mpl.colors.LogNorm(vmin=1, vmax=5),
    #                     cmap='Blues', xlim=[0.1, 4], ylim=[0.1, 4], height=6, ratio=8, space=0.)

    axs1 = sns.jointplot(x=df[key1], y=df[key2], palette='Spectral',
                         hue_norm=mpl.colors.LogNorm(vmin=1, vmax=100),
                         xlim=[0.1, 4], ylim=[0.1, 4], height=8, ratio=6, space=0.)
    #x0, x1 = axs1.ax_joint.get_xlim()
    #y0, y1 = axs1.ax_joint.get_ylim()
    #lims = [max(x0, y0), min(x1, y1)]
    #axs1.ax_joint.plot(lims, lims, '--r', lw=2) 

    pos_joint_ax = axs1.ax_joint.get_position()
    pos_marg_x_ax = axs1.ax_marg_x.get_position()
    axs1.ax_joint.set_position([pos_joint_ax.x0, pos_joint_ax.y0, pos_marg_x_ax.width,
                                pos_joint_ax.height])
    axs1.fig.axes[-1].set_position([1, pos_joint_ax.y0, .07, pos_joint_ax.height])

    # get the current colorbar ticks
    cbar_ticks = axs1.fig.axes[-1].get_yticks()
    # get the maximum value of the colorbar
    _, cbar_max = axs1.fig.axes[-1].get_ylim()
    # change the labels (not the ticks themselves) to a percentage
    #axs1.fig.axes[-1].set_yticklabels([f'{t / cbar_max * 1:.3f} %' for t in cbar_ticks], size=clabelsize)

    #axs1.fig.axes[-1].set_xlabel('Density', fontsize=clabelsize, labelpad=10)

    axs1.fig.axes[0].tick_params(axis='both', which='major', direction='in', labelbottom=True,
                                 bottom=True, labeltop=False, top=True, labelleft=True, left=True,
                                 labelright=False, right=True, width=1.5, length=ticklength,
                                 labelsize=ticklabelsize, labelrotation=0)

    axs1.fig.axes[0].tick_params(axis='both', which='minor', direction='in', labelbottom=False,
                                 bottom=False, left=False, width=1.5, length=ticklength,
                                 labelsize=ticklabelsize, labelrotation=0)

    axs1.fig.axes[1].tick_params(axis='both', which='both', direction='in', labelbottom=False,
                                 bottom=False, labelleft=False, left=False, width=1.5,
                                 length=ticklength, labelsize=ticklabelsize, labelrotation=0)

    axs1.fig.axes[2].tick_params(axis='both', which='both', direction='in', labelbottom=False,
                                 bottom=False, labelleft=False, left=False, width=1.5,
                                 length=ticklength, labelsize=ticklabelsize, labelrotation=0)

    #axs1.fig.axes[3].tick_params(axis='y', which='major', direction='in', labelbottom=False,
    #                             bottom=False, labelleft=False, left=False, labelright=True,
    #                             right=True, width=1.5, length=ticklength, labelsize=clabelsize,
    #                             labelrotation=0 )

    axs1.fig.axes[0].text(0.1, 0.95, data_type, horizontalalignment='center', fontsize=labelsize,
                          verticalalignment='center', transform=axs1.fig.axes[0].transAxes)

    axs1.set_axis_labels('x', 'y', fontsize=labelsize)
    axs1.ax_joint.set_xlabel(key1, fontsize=labelsize)
    axs1.ax_joint.set_ylabel(key2, fontsize=labelsize)

    if (fig_save):
        fname = f'figures/kde_plot_{key1}_{key2}.png'
        axs1.savefig(fname, format='png', dpi=300, bbox_inches='tight', pad_inches=pad,
                     facecolor='w', edgecolor='w', transparent=False)
    #plt.show()
    plt.close('all')
    return fig
