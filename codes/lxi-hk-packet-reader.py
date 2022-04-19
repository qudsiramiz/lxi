import csv
import struct
from pathlib import Path
from typing import NamedTuple

import numpy as np

# signed lower case, unsigned upper case
#packet_format_hk =">II2B3H"
packet_format_hk =">II4H"

sync = b'\xfe\x6b\x28\x40'
volts_per_count = 0.00006881

class hk_packet_cls(NamedTuple):
    timestamp: int
    hk_status: int
    hk_value: float
    delta_event_count: int
    delta_drop_event_count: int
    delta_lost_event_count: int

    @classmethod
    def from_bytes(cls, bytes_: bytes) :
        structure = struct.unpack(packet_format_hk, bytes_)
        return cls(
            timestamp=structure[1] & 0x3fffffff,           # mask for getting all timestamp bits
            hk_status=(structure[2] & 0xf000)/(2**12),
            hk_value=structure[2] & 0xfff,
            delta_event_count=structure[3],
            delta_drop_event_count=structure[4],
            delta_lost_event_count=structure[5],
        )

def read_binary_data_hk(
    in_file_path=None,
    in_file_name=None,
    save_file_path="../data/",
    save_file_name="output_hk_v02.csv",
    number_of_decimals=6
    ):
    """
    Reads housekeeping packet of the binary data from a file and saves it to a csv file.

    Parameters
    ----------
    in_file_path : str
        Path to the input file. Default is None.
    in_file_name : str
        Name of the input file. Default is None.
    save_file_path : str
        Path to the output file. Default is "../data/".
    save_file_name : str
        Name of the output file. Default is "output_sci.csv".
    number_of_decimals : int
        Number of decimals to save. Default is 6.

    Raises
    ------
    FileNotFoundError :
        If the input file does not exist.
    TypeError :
        If the name of the input file or input directory is not a string.
    Returns
    -------
        None.
    """
    if in_file_path is None:
        in_file_path = "../data/raw_data/"
    if in_file_name is None:
        in_file_name = "2022_03_03_1030_LEXI_raw_2100_newMCP_copper.txt"

    # Check if the file exists, if does not exist raise an error
    if not Path(in_file_path + in_file_name).is_file():
        raise FileNotFoundError(
            "The file " + in_file_path + in_file_name + " does not exist."
            )
    # Check if the file name and folder name are strings, if not then raise an error
    if not isinstance(in_file_name, str):
        raise TypeError(
            "The file name must be a string."
            )
    if not isinstance(in_file_path, str):
        raise TypeError(
            "The file path must be a string."
            )

    # Check the number of decimals to save
    if not isinstance(number_of_decimals, int):
        raise TypeError(
            "The number of decimals to save must be an integer."
            )

    input_file_name = in_file_path + in_file_name

    with open(input_file_name, 'rb') as file:
        raw = file.read()

    index = 0
    packets = []

    while index < len(raw) - 16:
        if raw[index:index + 4] == sync:
            packets.append(hk_packet_cls.from_bytes(raw[index:index + 16]))
            index += 16
            continue

        index += 1

    TimeStamp = np.full(len(packets), np.nan)
    PinPullerTemp = np.full(len(packets), np.nan)
    OpticsTemp = np.full(len(packets), np.nan)
    LEXIbaseTemp = np.full(len(packets), np.nan)
    HVsupplyTemp = np.full(len(packets), np.nan)
    V_Imon_5_2 = np.full(len(packets), np.nan)
    V_Imon_10 = np.full(len(packets), np.nan)
    V_Imon_3_3 = np.full(len(packets), np.nan)
    AnodeVoltMon = np.full(len(packets), np.nan)
    V_Imon_28 = np.full(len(packets), np.nan)
    ADC_Ground = np.full(len(packets), np.nan)
    Cmd_count = np.full(len(packets), np.nan)
    Pinpuller_Armed = np.full(len(packets), np.nan)
    Unused = np.full(len(packets), np.nan)
    Unused = np.full(len(packets), np.nan)
    HVmcpAuto = np.full(len(packets), np.nan)
    HVmcpMan = np.full(len(packets), np.nan)
    DeltaEvntCount = np.full(len(packets), np.nan)
    DeltaDroppedCount = np.full(len(packets), np.nan)
    DeltaLostevntCount = np.full(len(packets), np.nan)

    for ii,hk_packet in enumerate(packets):
        TimeStamp[ii] = hk_packet.timestamp
        if hk_packet.hk_status==0:
            PinPullerTemp[ii] = (hk_packet.hk_value - 2.73) * 100
        elif hk_packet.hk_status==1:
            OpticsTemp[ii] = (hk_packet.hk_value - 2.73) * 100
        elif hk_packet.hk_status==2:
            LEXIbaseTemp[ii] = (hk_packet.hk_value - 2.73) * 100
        elif hk_packet.hk_status==3:
            HVsupplyTemp[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==4:
            V_Imon_5_2[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==5:
            V_Imon_10[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==6:
            V_Imon_3_3[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==7:
            AnodeVoltMon[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==8:
            V_Imon_28[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==9:
            ADC_Ground[ii] = hk_packet.hk_value * volts_per_count
        elif hk_packet.hk_status==10:
            Cmd_count[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==11:
            Pinpuller_Armed[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==12:
            Unused[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==13:
            Unused[ii] = hk_packet.hk_value
        elif hk_packet.hk_status==14:
            HVmcpAuto[ii] = hk_packet.hk_value * volts_per_count
        elif hk_packet.hk_status==15:
            HVmcpMan[ii] = hk_packet.hk_value * volts_per_count

        DeltaEvntCount[ii] = hk_packet.delta_event_count
        DeltaDroppedCount[ii] = hk_packet.delta_drop_event_count
        DeltaLostevntCount[ii] = hk_packet.delta_lost_event_count

    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    # Name of the output file
    output_file_name = save_file_path + save_file_name
    print(output_file_name)
    with open(output_file_name, 'w', newline='') as file:
        dict_writer = csv.DictWriter(
            file,
            fieldnames=(
                "TimeStamp",
                "PinPullerTemp",
                "OpticsTemp",
                "LEXIbaseTemp",
                "HVsupplyTemp",
                "+5.2V_Imon",
                "+10V_Imon",
                "+3.3V_Imon",
                "AnodeVoltMon",
                "+28V_Imon",
                "ADC_Ground",
                "Cmd_count",
                "Pinpuller_Armed",
                "Unused",
                "Unused",
                "HVmcpAuto",
                "HVmcpMan",
                "DeltaEvntCount",
                "DeltaDroppedCount",
                "DeltaLostevntCount"
            ),
        )
        dict_writer.writeheader()

        dict_writer.writerows(
            {
                "TimeStamp": TimeStamp[ii],
                "PinPullerTemp": PinPullerTemp[ii],
                "OpticsTemp": OpticsTemp[ii],
                "LEXIbaseTemp": LEXIbaseTemp[ii],
                "HVsupplyTemp": HVsupplyTemp[ii],
                "+5.2V_Imon": V_Imon_5_2[ii],
                "+10V_Imon": V_Imon_10[ii],
                "+3.3V_Imon": V_Imon_3_3[ii],
                "AnodeVoltMon": AnodeVoltMon[ii],
                "+28V_Imon": V_Imon_28[ii],
                "ADC_Ground": ADC_Ground[ii],
                "Cmd_count": Cmd_count[ii],
                "Pinpuller_Armed": Pinpuller_Armed[ii],
                "Unused": Unused[ii],
                "Unused": Unused[ii],
                "HVmcpAuto": HVmcpAuto[ii],
                "HVmcpMan": HVmcpMan[ii],
                "DeltaEvntCount": DeltaEvntCount[ii],
                "DeltaDroppedCount": DeltaDroppedCount[ii],
                "DeltaLostevntCount": DeltaLostevntCount[ii],
            }
            for ii in range(len(packets))
        )
    return packets

pkts = read_binary_data_hk()
