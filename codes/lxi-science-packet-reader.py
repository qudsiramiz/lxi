import argparse
import csv
import ctypes
import struct
from typing import NamedTuple

packet_format = '>II4H'
sync = b'\xfe\x6b\x28\x40'
volts_per_count = 0.00006881

# class packet(ctypes.Structure):
#     _fields_ = [
#         ('sync', ctypes.c_uint32),
#         ('time', ctypes.c_uint32),
#         ('channel1', ctypes.c_uint16),
#         ('channel2', ctypes.c_uint16),
#         ('channel3', ctypes.c_uint16),
#         ('channel4', ctypes.c_uint16),
#    ]


class packet(NamedTuple):
    is_commanded: bool
    timestamp: int
    channel1: float
    channel2: float
    channel3: float
    channel4: float

    @classmethod
    def from_bytes(cls, bytes_: bytes) -> 'packet':
        structure = struct.unpack(packet_format, bytes_)
        return cls(
            is_commanded=bool(structure[1] & 0x40000000),  # mask to test for commanded event type
            timestamp=structure[1] & 0x3fffffff,           # mask for getting all timestamp bits
            channel1=structure[2] * volts_per_count,
            channel2=structure[3] * volts_per_count,
            channel3=structure[4] * volts_per_count,
            channel4=structure[5] * volts_per_count,
        )


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('in_path')
    arg_parser.add_argument('out_path')
    args = arg_parser.parse_args()

    with open(args.in_path, 'rb') as file:
        raw = file.read()

    index = 0
    packets = []

    while index < len(raw) - 16:
        if raw[index:index + 4] == sync:
            packets.append(packet.from_bytes(raw[index:index + 16]))
            index += 16
            continue

        index += 1

    with open(args.out_path, 'w', newline='') as file:
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
                'TimeStamp': packet.timestamp,
                'IsCommanded': packet.is_commanded,
                'Channel1': packet.channel1,
                'Channel2': packet.channel2,
                'Channel3': packet.channel3,
                'Channel4': packet.channel4,
            }
            for packet in packets
        )


if __name__ == '__main__':
    main()
