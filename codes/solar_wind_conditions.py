from itertools import cycle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz
import datetime

# Set the timezone to UTC for df
# df.index = df.index.tz_localize(pytz.utc)

au = 1.496e8  # 1 AU in kms

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
solar_cycle_list = pd.read_csv('../data/solar_cycle_list.csv')

# Select data from df corresponding to the time interval of 1963-01-01 to 1964-01-01
df_sc_20 = df[(df.index >= '1963-01-01 00:00:00') & (df.index <= '1964-01-01 00:00:00')]

# Select the data from omni df corresponding to 1 year before the 24th solar cyle maximum 
# and 1 year after the 24th solar cycle maximum
df_sc_20_omni = df_omni[(df_omni.index >= solar_cycle_list.iloc[23].start_time) &
                        (df_omni.index <= solar_cycle_list.iloc[23].end_time)]

# Slect the data from omni df corresponding to 1 year before each solar cycle maximum and 1 year
# after each solar cycle maximum
df_sc_list = []
for i in range(len(solar_cycle_list)):
    df_sc_list.append(df_omni[(df_omni.index >= solar_cycle_list.iloc[i].start_time) &
                              (df_omni.index <= solar_cycle_list.iloc[i].end_time)])

# plot a histogram of np for each solar cycle
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
for i in range(len(solar_cycle_list)):
    ax.hist(df_sc_list[i].np.dropna(), bins=100, label=solar_cycle_list.iloc[i].name)
ax.set_xlabel('$n_p$ [$10^{19}$m$^{-3}$]')
ax.set_ylabel('Frequency')
ax.set_title('Histogram of $n_p$ for each solar cycle')
ax.legend()
plt.savefig('../figures/hist_np_sc.png', dpi=300)
plt.show()

# try :
#     t_sc_unix = ((df.index - pd.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.UTC)).total_seconds())
#     print('Computing time done')
# except :
#     pass
