#!/home/cephadrius/mlc_venv/bin/python

import datetime
import glob
import math
import os
import pandas as pd
import pickle
import random
import time

import magpylib as magpy
import matplotlib.pyplot as plt
import numpy as np
from magpylib.magnet import Box
from matplotlib import cm, ticker
from mpl_toolkits import mplot3d

today_date = datetime.datetime.today().strftime('%Y-%m-%d')

# CPU 2021_01_13 changing how get magnetic field and using this file as baseline for timing
# comparison--only use getB when closest to magnets
# 2021_02_11 only straight down over MPO
# Constant -------
t1 = time.time()  # start timer to build magnets
magnetSTRENGTH = 1330  # mT for going into getB
kev = 1.0e3*1.6e-19  # convert kev to joules
mass = (1.67262192*10**-27) # proton (1.67262192*10**-27) #electrons (9.109*10**-31)# mass in kg
q = -(1.602176634*10**-19)  # charge in coulomb #do positive for electron, negative for proton
                            # since was made og for electron
c = 2.99e8  # speed of light m/s

# Dimensions of lens holder in mm
LEXIside = 36   # length of side of one lens - shelf = 40-2-2
LEXIsuppt = 5   # shelf +between lens = 2+2+1

# Magnet details: https://www.kjmagnetics.com/proddetail.asp?prod=B842SH

# Dimensions of magnet in mm: 1/2" x 1/4" x 1/8" w/mag thru 1/8" = 0.5" x 0.25" x 0.125" =
# 12.7 x 6.35 x 3.175 mm^3
magnetdimx = 3.175
magnetdimy = 12.7*3  # three mag stacked
mdimy = 12.7  # y mag dim for 1 magnet
magnetdimz = 6.35
# Magnetic strength in mT (residual magnetic field strength in bar magnet for Neo 42SH)
# 1 mT = 10 Gauss ; 13,300 Gauss listed at https://www.kjmagnetics.com/proddetail.asp?prod=B842SH ;
# 13,200 Gauss listed at https://www.kjmagnetics.com/specification.sheet.php
magnetSTRENGTH = 1330  # using max documented number for far field calcs
xedge = 2.286  # mm,= 0.09" =0.08648802"
spacing = 1.016  # mm
yspacing = 1.016  # mm (same as x spacing?)
y_up = mdimy + 2 * yspacing
y_down = mdimy
maghold = 3.4544  # mm, = 0.136"
yhold = 13.5678418  # 13.5678418mm 0.534167"
x_inneredge = ((LEXIside + magnetdimx)/2+(LEXIside+LEXIsuppt+xedge))
x_outeredge = ((LEXIside - magnetdimx)/2+(LEXIside+LEXIsuppt+xedge+spacing+2*maghold))
y_inner     = ((LEXIside + yhold)/2 + (LEXIsuppt - 1.04775))
y_mid       = ((LEXIside + yhold)/2 + (LEXIsuppt - 1.04775) + (yhold+yspacing))
y_outer     = ((LEXIside + yhold)/2 + (LEXIsuppt - 1.04775) + 2 * (yhold+yspacing))

# The magnet setup
s1  = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position= ( (LEXIside+LEXIsuppt)/2, 0, 0))
s2  = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position= (-(LEXIside+LEXIsuppt)/2,0,0))
s3  = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position= ( (LEXIside+magnetdimx)/2+(LEXIside+LEXIsuppt+xedge), 0,0))
s4  = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position= (-(LEXIside+magnetdimx)/2-(LEXIside+LEXIsuppt+xedge), 0,0))
s5  = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position=( (LEXIside+LEXIsuppt)/2, (LEXIside+LEXIsuppt), 0)) #S5
s6  = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position=(-(LEXIside+LEXIsuppt)/2, (LEXIside+LEXIsuppt), 0)) #S6
s9  = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position=( (LEXIside+LEXIsuppt)/2, -(LEXIside+LEXIsuppt), 0)) #S9
s10 = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, magnetdimy, magnetdimz),
          position=(-(LEXIside+LEXIsuppt)/2, -(LEXIside+LEXIsuppt), 0)) #S10
s7a = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
          position= ( x_inneredge,   y_mid,0)) #s7a
s7b = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
          position= ( x_inneredge, y_inner,0)) #s7b
s7c = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
          position= ( x_inneredge, y_outer,0)) #s7c
s8a = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
          position= (- x_inneredge,   y_mid,0)) #S8
s8b = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
          position= (- x_inneredge, y_inner,0)) #S8
s8c = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
          position= (- x_inneredge, y_outer,0)) #S8
s11a = Box(magnetization=(-magnetSTRENGTH,0,0), dimension=(magnetdimx,mdimy,magnetdimz),
           position= ( x_inneredge, -y_mid,0))#S11
s11b = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_inneredge, -y_inner,0))#S11
s11c = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_inneredge, -y_outer,0))#S11
s12a = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (-x_inneredge, -y_mid,0))#S12
s12b = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (-x_inneredge, -y_inner,0))#S12
s12c = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (-x_inneredge, -y_outer,0))#S12
s13a = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_outeredge,   y_mid,0))
s13b = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_outeredge,   y_inner,0))
s13c = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_outeredge,   y_outer,0))
s14a = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_outeredge,   -y_mid,0))
s14b = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_outeredge,   -y_inner,0))
s14c = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= ( x_outeredge,   -y_outer,0))
s15a = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (- x_outeredge,   y_mid,0))
s15b = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (- x_outeredge,   y_inner,0))
s15c = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (- x_outeredge,   y_outer,0))
s16a = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (- x_outeredge,   -y_mid,0))
s16b = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (- x_outeredge,   -y_inner,0))
s16c = Box(magnetization=(magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
           position= (- x_outeredge,   -y_outer,0))
# create collection
c_mag_array = magpy.Collection(s1, s2, s3, s4, s5, s6, s7a, s7b, s7c, s8a, s8b, s8c, s9, s10, s11a, s11b,
                         s11c, s12a, s12b, s12c, s13a, s13b, s13c, s14a, s14b, s14c, s15a, s15b,
                         s15c, s16a, s16b, s16c)
# ======== END MAG SETUP ========================


# Set the font size for the axes
label_size = 14  # fontsize for x and y labels
t_label_size = 8  # fontsize for tick label
c_label_size = 12  # fontsize for colorbar label
ct_tick_size = 8  # fontsize for colorbar tick labels
l_label_size = 12  # fontsize for legend label

fig_format = 'png'

fig = plt.figure(num=None, figsize=(6,6), dpi=200, facecolor='w', edgecolor='gray')
axs = plt.axes(projection='3d')
magpy.display(c_mag_array, axis=axs)
axs.set_xlabel('X (mm)', fontsize=label_size)

axs.tick_params(axis='both', direction='inout', which='major', left=True, right=True, top=True,
                 bottom=True, labelleft=True, labelright=False, labeltop=False, labelbottom=True,
                 labelsize=t_label_size)


# Plot particle trajectories in 3D for 10 randomly selected particles

# Read the data from the file
data_folder = "/media/cephadrius/endless/bu_research/lxi/data/2.0Kev"
fnames = np.sort(glob.glob(f"{data_folder}/*.p"))
np.random.seed(0)
particle_number_arr = np.random.random_integers(0, 1000, 10)
# particle_number_arr = [176]
for particle_number in particle_number_arr[0:]:
    df = pd.read_pickle(fnames[particle_number])
    x = df['pvectorlist'][:,0] * 1e3  # convert to mm
    y = df['pvectorlist'][:,1] * 1e3  # convert to mm
    z = df['pvectorlist'][:,2] * 1e3  # convert to mm
    count = 0
    print(f"Plotting particle trajectory for particle {particle_number}\n")
    fig.suptitle(f'particle {particle_number}', fontsize=label_size, color='r', y=.85)
    while count < (len(x)/1000):

        min_ind = 0
        max_ind = 1000 * (count + 1)
        axs.plot(x[min_ind:max_ind], y[min_ind:max_ind], z[min_ind:max_ind], 'k--', ms=0.5,
                 lw=0.5, alpha=0.8)

        axs.set_xlim(-65, 65)
        axs.set_ylim(-65, 65)
        axs.set_zlim(-65, 65)

        fig_folder = f"../figures/{str(particle_number).zfill(5)}"
        check_folder = os.path.isdir(fig_folder)
        # If folder doesn't exist, then create it.
        if not check_folder:
            os.makedirs(fig_folder)
            print("created folder : ", fig_folder)

        fig_name = f"{fig_folder}/particle_trajectory_{str(particle_number).zfill(5)}_{str(count).zfill(3)}.{fig_format}"
        plt.savefig(fig_name, bbox_inches='tight', pad_inches=0.05, format=fig_format, dpi=250)
        count += 1
    print(f"Created all the images for particle number {particle_number}\n")
#    plt.plot(df.)

#print(f'Figure saved as {fig_name}')
#plt.close()
#plt.show()

