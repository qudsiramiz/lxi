import csv
import struct
from pathlib import Path
from typing import NamedTuple

import numpy as np

packet_format = '>II4H'
sync = b'\xfe\x6b\x28\x40'
volts_per_count = 0.00006881


class sci_packet(NamedTuple):
    is_commanded: bool
    timestamp: int
    channel1: float
    channel2: float
    channel3: float
    channel4: float

    @classmethod
    def from_bytes(cls, bytes_: bytes) :
        structure = struct.unpack(packet_format, bytes_)
        return cls(
            is_commanded=bool(structure[1] & 0x40000000),  # mask to test for commanded event type
            timestamp=structure[1] & 0x3fffffff,           # mask for getting all timestamp bits
            channel1=structure[2] * volts_per_count,
            channel2=structure[3] * volts_per_count,
            channel3=structure[4] * volts_per_count,
            channel4=structure[5] * volts_per_count,
        )

def read_binary_data_sci(
    in_file_path=None,
    in_file_name=None,
    save_file_path="../data/",
    save_file_name="output_sci.csv",
    number_of_decimals=6
    ):
    """
    Reads science packet of the binary data from a file and saves it to a csv file.

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
            packets.append(sci_packet.from_bytes(raw[index:index + 16]))
            index += 16
            continue

        index += 1

    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    # Name of the output file
    output_file_name = save_file_path + save_file_name

    with open(output_file_name, 'w', newline='') as file:
        dict_writer = csv.DictWriter(
            file,
            fieldnames=(
                'TimeStamp',
                'IsCommanded',
                'Channel1',
                'Channel2',
                'Channel3',
                'Channel4',
            ),
        )
        dict_writer.writeheader()
        dict_writer.writerows(
            {
                'TimeStamp': sci_packet.timestamp,
                'IsCommanded': sci_packet.is_commanded,
                'Channel1': np.round(sci_packet.channel1, decimals=number_of_decimals),
                'Channel2': np.round(sci_packet.channel2, decimals=number_of_decimals),
                'Channel3': np.round(sci_packet.channel3, decimals=number_of_decimals),
                'Channel4': np.round(sci_packet.channel4, decimals=number_of_decimals),
            }
            for sci_packet in packets
        )

    return None

def read_binary_data_hk(
    in_file_path=None,
    in_file_name=None,
    save_file_path="../data/",
    save_file_name="output_hk.csv",
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
            packets.append(sci_packet.from_bytes(raw[index:index + 16]))
            index += 16
            continue

        index += 1


    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    # Name of the output file
    output_file_name = save_file_path + save_file_name

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
                'TimeStamp': sci_packet.timestamp,
                'IsCommanded': sci_packet.is_commanded,
                'Channel1': np.round(sci_packet.channel1, decimals=number_of_decimals),
                'Channel2': np.round(sci_packet.channel2, decimals=number_of_decimals),
                'Channel3': np.round(sci_packet.channel3, decimals=number_of_decimals),
                'Channel4': np.round(sci_packet.channel4, decimals=number_of_decimals),
            }
            for sci_packet in packets
        )