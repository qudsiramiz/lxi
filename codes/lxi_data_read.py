import re
from ctypes import Structure, c_uint16, c_uint32
from struct import unpack

import numpy as np
import pandas as pd

#xrbr_unpack = '>II4H'
xrbr_unpack = '>II4H'

# t_cut is the limit between a science TLM packet that is not commanded, and one
# that is commanded. 1073741824 in bit form is 01000000000000000000000000000000,
# and the 1 is in the 31st spot, which makes the 1 a commanded event marker in
# the science TLM packet in bit 14 (see above). HK data would have a 1 in the
# 32nd spot, which would make the number larger than this.
t_cut = 1073741824

# Read the binary file

###############################################################################
# X-RAY XRBR (X-Ray Burst) and XRFS (X-Ray Fast)
class xrbr_pkt(Structure):
    _fields_ = [('sync', c_uint32), ('time', c_uint32),
                ('channels', c_uint16 * 4)]

    def __init__(self, unpacked):
        self.sync = unpacked[0]
        self.time = unpacked[1]
        self.channels = unpacked[2:6]

def read_xrbr_sci(filename, varname = []):
    """
    Function to read science data out of XRBR file into numpy array.

    ### Parameters
    * filename : str
        >Name of logfile to read
    * varname : float array-like, optional
        >XRBR sci array to append data into. Default empty.

    ### Returns
    * staging : float array-like
        >Array of XRBR sci data from logfile. Includes data from `varname`,
        if specified.
    """

    f = open(filename, 'rb')
    pkt_list = []
    contents = f.read()
    starts = [m.start() for m in re.finditer(b'\xfe\x6b', contents)]
    stops = starts[1:]
    stops.append(starts[-1]+16)
    for s in starts:
        stuff = unpack(xrbr_unpack, contents[s:s+16])
        data = xrbr_pkt(stuff)
        if (data.time < t_cut):
            pkt_list.append(data)
    f.close()
    npkts = len(pkt_list)
    staging = np.zeros([npkts,5])
    for i in range(npkts):
        pkt = pkt_list[i]
        staging[i,0] = pkt.time
        staging[i,1:5] = pkt.channels[:]
    if (len(varname) != 0):
        xrbr_sci_arr = np.concatenate((varname,staging),axis=0)
    else:
        xrbr_sci_arr = staging
    return xrbr_sci_arr

def read_xrbr_hk(filename, varname = []):
    """
    Function to read housekeeping data out of XRBR file into numpy array.

    ### Parameters
    
    * filename : str
        >Name of logfile to read
    *varname : float array-like, optional
        >XRBR HK array to append data into. Default empty.

    ### Returns
    
    * staging : float array-like
        >Array of XRBR HK data from logfile. Includes data from `varname`,
        if specified.
        
    """
    f = open(filename, 'rb')
    pkt_list = []
    contents = f.read()
    starts = [m.start() for m in re.finditer(b'\xfe\x6b', contents)]
    stops = starts[1:]
    stops.append(starts[-1]+16)
    for idx, s in enumerate(starts):
        stuff = unpack(xrbr_unpack, contents[s:s+16])
        data = xrbr_pkt(stuff)
        # 2147483648
        # This time demarkation is for HK packets from the xray that would have
        # a Telemetry Type of 1 in bit 31 of the 0-31 bit 4 byte Time Tag data
        # (bytes 4-7)
        if (data.time >= 2147483647):
            pkt_list.append(data)
    f.close()
    npkts = len(pkt_list)
    staging = np.zeros([npkts,20])
    for i in range(npkts):
        pkt = pkt_list[i]
        staging[i,0] = pkt.time
        Status = pkt.channels[0]
        StatusBit = "{0:016b}".format(Status)
        if (StatusBit[0] == '1'): #
            MCP_xHV = 1
            if (StatusBit[1] == '1'):
                MCP_xAuto = 1
            else:
                MCP_xAuto = 0
            HVData = int(StatusBit[4:],2)
            TempData = np.nan
        else:
            MCP_xHV = 0
            MCP_xAuto = np.nan
            HVData = np.nan
            TempData = int(StatusBit[4:],2)
        staging[i,1] = MCP_xHV
        staging[i,2] = MCP_xAuto
        staging[i,3] = HVData
        staging[i,4] = TempData
        staging[i,5:8] = pkt.channels[1:4]
    if (len(varname) != 0):
        xrbr_hk_arr = np.concatenate((varname,staging),axis=0)
    else:
        xrbr_hk_arr = staging
    return xrbr_hk_arr


file_name = "../data/raw_data/2022_03_03_1030_LEXI_raw_2100_newMCP_copper.txt"
dat_sci = read_xrbr_sci(file_name)

# Save the data to a csv file with headers as Times, Channels 1-4
dat_sci_df = pd.DataFrame(dat_sci, columns=['TimeStamp', 'Channel1', 'Channel2', 'Channel3', 'Channel4'])
dat_sci_df.to_csv('../data/raw_data/2022_03_03_1030_LEXI_raw_2100_newMCP_copper_sci_qudsi.csv',
                  index=False, header=True, sep=',', mode='w', float_format='%.3f')

'''
file_name = "../data/raw_data/2022_03_03_1030_LEXI_raw_2100_newMCP_copper.txt"
with open(file_name, 'rb') as f:
    data = f.read()

# Convert the binary file to a numpy array
#data_array = np.frombuffer(data, dtype='>i2')
data_array = np.frombuffer(data, dtype='i4')
'''
