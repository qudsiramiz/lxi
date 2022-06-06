from itertools import cycle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz
import datetime

# Set the timezone to UTC for df
# df.index = df.index.tz_localize(pytz.utc)

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

au = 1.496e8  # 1 AU in kms

data_read = ''
if data_read:
    df = pd.read_pickle('../../../test_folder/omni_coho1hr_merged_mag_plasma_19630101_20211201_v03.p')

    # For any key in df, if the value is smaller/larger than -/+1e-20,  then set it to NaN
    for key in df.keys():
        df[key][(df[key] < -1e20) | (df[key] > 1e20)] = np.nan

    # Add particle flux to df
    df['particle_flux'] = (df.np * 1e6) * (df.vp_m * 1e3) * ((1.49e11)**2)

    # Add dynamic pressure to df
    df['dynamic_pressure'] = 1.6726e-6 * 1.15 * df.np * df.vp_m**2

    # df_omni = df.resample('4W').median()
    df_omni = df.rolling(window='28D', min_periods=100).median()
    t_omni = (pd.Series(df_omni.index) - datetime.datetime(
              1970, 1, 1, 0, 0, 0, 0, pytz.UTC)).dt.total_seconds()

    # Read the solar cycle list
    df_sc = pd.read_csv('../data/solar_cycle_list.csv')

    year_list = []
    month_list = []
    for i in range(len(df_sc)):
        try:
            year_list.append(df_sc.Maximum[i].split('-')[0])
            month_list.append(df_sc.Maximum[i].split('-')[1])
        except:
            pass

    # Get the datetime based on the year_list and month_list
    dt_list = []
    for i in range(len(year_list)):
        dt_list.append(datetime.datetime(
            int(year_list[i]), int(month_list[i]), 1, 0, 0, 0, 0, pytz.UTC))

    # Compute the time 1 year prior to the solar cycle maximum and the time 1 year after the solar cycle
    # maximum and add it to the solar cycle list
    df_sc['t_1yr_prior'] = np.array(dt_list) - pd.to_timedelta(365, unit='d')
    df_sc['Max_time'] = np.array(dt_list)
    df_sc['t_1yr_after'] = np.array(dt_list) + pd.to_timedelta(365, unit='d')

    # Slect the data from omni df corresponding to 1 year before each solar cycle maximum and 1 year
    # after each solar cycle maximum
    df_sc_prior_list = []
    df_sc_after_list = []
    for i in range(len(df_sc)):
        df_sc_prior_list.append(df_omni[(df_omni.index >= df_sc.iloc[i].t_1yr_prior) &
                               (df_omni.index <= df_sc.iloc[i].Max_time)])
        df_sc_after_list.append(df_omni[(df_omni.index <= df_sc.iloc[i].t_1yr_after) &
                               (df_omni.index >= df_sc.iloc[i].Max_time)])

# Define bins for the histogram logarithmically spaced

# Make a histogram of each key for each solar cycle (prior and after)
key_list = ['np', 'vp_m', 'dynamic_pressure', 'Tp', 'bn']
unit_list_dict = {'np': '(cm$^-3$)', 'vp_m': '(km/s)',
                  'dynamic_pressure': '(nPa)', 'Tp': '(K)', 'bn': '(nT)'}

plt.close("all")

nbins=50

for key in key_list[:]:

    fig = plt.figure(figsize=(10, 5))
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.0, hspace=0.0)

    if key == 'bn':
        bins_prior = nbins
        bins_after = nbins
        x_scale = "linear"
    else:
        bins_prior = np.logspace(np.nanmin(np.log10(df_sc_prior_list[i][key])),
                                 np.nanmax(np.log10(df_sc_prior_list[i][key])), nbins)
        bins_after = np.logspace(np.nanmin(np.log10(df_sc_after_list[i][key])),
                                 np.nanmax(np.log10(df_sc_after_list[i][key])), nbins)
        x_scale = "log"

    axs1 = fig.add_subplot(1, 2, 1)
    for i in range(19, 24):
        axs1.hist(df_sc_prior_list[i][key], bins=bins_prior, label=df_sc.Maximum[i], alpha=0.5)
    axs1.set_xlabel(f'{key} {unit_list_dict[key]}')
    axs1.set_ylabel('Count')
    axs1.set_xscale(x_scale)
    axs1.set_title(f'Histogram of {key} before solar maxima')
    axs1.legend()

    axs2 = fig.add_subplot(1, 2, 2)
    for i in range(19, 24):
        axs2.hist(df_sc_after_list[i][key], bins=bins_after, label=df_sc.Maximum[i], alpha=0.5)
    axs2.set_xlabel(f'{key} {unit_list_dict[key]}')
    axs2.set_ylabel('Count')
    axs2.set_xscale(x_scale)
    axs2.set_title(f'Histogram of {key} after solar maxima')
    axs2.legend()

    plt.savefig(f'../figures/hist_{key}_solar_cycle_prior_after.pdf', bbox_inches='tight',
                pad_inches=0.05, dpi=250)
    print(f"Figure saved for {key}")

