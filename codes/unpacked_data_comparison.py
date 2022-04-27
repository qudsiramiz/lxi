import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set the font style to Times New Roman
font = {'family': 'serif', 'weight': 'normal', 'size': 10}
plt.rc('font', **font)
plt.rc('text', usetex=True)

read_data = '1'
if read_data:
    df_sc_n = pd.read_csv("../data/raw_data/2022_04_21_1431_LEXI_HK_unit_1_mcp_unit_1_eBox_1987_hk_/2022_04_21_1431_LEXI_unit_1_mcp_unit_1_eBox_1987.csv")
    df_sc_q = pd.read_csv("../data/processed_data/sci/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_qudsi.csv")

    df_sc_n['Channel4'] = df_sc_n['Channel3']
    df_sc_n['Channel3'] = df_sc_n['Channel2']
    df_sc_n['Channel2'] = df_sc_n['Channel1']
    df_sc_n['Channel1'] = df_sc_n['Timestamp']
    df_sc_n['Timestamp'] = df_sc_n.index

    # Choose only datapoints where 'IsCommanded' is False
    #df_sc_q = df_sc_q[df_sc_q['IsCommanded'] == False]

    df_hk_n = pd.read_csv("../data/raw_data/2022_04_21_1431_LEXI_HK_unit_1_mcp_unit_1_eBox_1987_hk_/2022_04_21_1431_LEXI_HK_unit_1_mcp_unit_1_eBox_1987_hk_.csv")
    df_hk_q = pd.read_csv("../data/processed_data/hk/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_qudsi.csv")

    sc_key_list = ['Channel1', 'Channel2', 'Channel3', 'Channel4']
    hk_key_list = ['PinPullerTemp', 'OpticsTemp', 'LEXIbaseTemp', 'HVsupplyTemp',
                   '+5.2V_Imon', '+10V_Imon', '+3.3V_Imon', '+28V_Imon', 'ADC_Ground', 'Cmd_count','Pinpuller_Armed', 'Unused', 'Unused', 'HVmcpAuto', 'HVmcpMan', 'DeltaEvntCount', 'DeltaDroppedCount', 'DeltaLostevntCount']

ms_n = 3
ms_q = 3
alpha_n = 0.5
alpha_q = 0.75

axis_label_size = 20

# plot the data from df_sc_n and df_hk_n to compare
for key in sc_key_list:
    plt.figure(figsize=(6, 6))
    plt.plot(df_sc_n['Timestamp'], df_sc_n[key], 'ro', ms=ms_n, mfc='r', alpha=alpha_n, label=f"GSFC")
    plt.plot(df_sc_q['TimeStamp'], df_sc_q[key], 'bo', ms=ms_q, mfc='none', alpha=alpha_q, label=f"BU")
    plt.legend(loc=1, fontsize=axis_label_size)
    plt.xlim(214502, 217502)
    plt.ylim(-0.1, 4)
    plt.xlabel("TimeStamp", fontsize=axis_label_size)
    plt.ylabel(key, fontsize=axis_label_size)
    plt.title(f"{key} comparison", fontsize=axis_label_size)
    plt.savefig(f"../figures/comparison_figures/compare_sc_n_q_{key}.png", dpi=300, bbox_inches='tight',
                pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)
    plt.close()
    print(f"Figure saved for key {key}")

# Plot data for the HK data
for key in hk_key_list[0:]:
    plt.figure(figsize=(6, 6))
    plt.plot(df_hk_n['Time'], df_hk_n[key], 'ro', ms=ms_n, mfc='r', alpha=alpha_n, label=f"GSFC")
    plt.plot(df_hk_q['TimeStamp'], df_hk_q[key], 'bo', ms=ms_q, mfc='none', alpha=alpha_q, label=f"BU")
    plt.legend(loc='best', fontsize=axis_label_size)
    plt.xlim(990, 51500)
    plt.xlabel("TimeStamp", fontsize=axis_label_size)
    plt.ylabel(key, fontsize=axis_label_size)
    plt.title(f"{key} comparison", fontsize=axis_label_size)
    plt.savefig(f"../figures/comparison_figures/compare_hk_n_q_{key}.png", dpi=300, bbox_inches='tight',
                pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)
    plt.close()
    print(f"Figure saved for key {key}")
