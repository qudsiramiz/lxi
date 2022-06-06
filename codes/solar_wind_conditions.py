import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz

# Set the timezone to UTC for df
# df.index = df.index.tz_localize(pytz.utc)

au = 1.496e8  # 1 AU in kms

df = pd.read_pickle('../data/omni_coho1hr_merged_mag_plasma_19630101_20211201_v03.p')

# For any key in df, if the value is smaller/larger than -/+1e-20,  then set it to NaN
for key in df.keys():
    df[key][(df[key] < -1e20) | (df[key] > 1e20)] = np.nan

# Add particle flux to df
df['particle_flux'] = (df.np * 1e6) * (df.vp_m * 1e3) * ((1.49e11)**2)

# Add dynamic pressure to df
df['dynamic_pressure'] = 1.6726e-6 * 1.15 * df.np * df.vp_m**2

# df_omni = df.resample('4W').median()
df_omni = df.rolling(window='28D', min_periods=100).median()

t_omni = (pd.Series(df_omni.index) -
          pd.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.UTC)).dt.total_seconds()

# try :
#     t_sc_unix = ((df.index - pd.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.UTC)).total_seconds())
#     print('Computing time done')
# except :
#     pass
