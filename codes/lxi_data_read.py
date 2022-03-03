import numpy as np
import pandas as pd

# Read the binary file

file_name = "../data/raw_data/2022_03_03_1030_LEXI_raw_2100_newMCP_copper.txt"
with open(file_name, 'rb') as f:
    data = f.read()

# Convert the binary file to a numpy array
#data_array = np.frombuffer(data, dtype='>i2')
data_array = np.frombuffer(data, dtype='i4')
