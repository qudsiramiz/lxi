import time
import numpy as np
import matplotlib.pyplot as plt
from magpylib.magnet import Box, Cylinder
from magpylib import Collection, display
import magpylib as magpy
from mpl_toolkits import mplot3d
from matplotlib import ticker, cm
import pickle
import math
import random
import datetime
import os
import multiprocessing as mp
import itertools


def compute_vars(*args):
    r"""
    The function takes particle number as input and gives a bunch of output and saves them an HDF
    and pickle file.

    Parameters
    ----------
    args : integer
        Input particle number for computation

    Raises
    ------
    None

    Returns
    -------
    pvectorlist : array of shape steps x 3
        p Vector list

    vvectorlist : array of shape steps x 3
        V vector list

    savedspots: array of shape steps x 3
        Saved spots

    stepsizelist: array of shape steps x 1
        Step size list

    KElist : array of shape steps x 1
        KE list

     Blist : array of shape steps x 3
         B list

     bottomplatehitnumber : array
         Bottom plate hit number
     """
    bottomplatehitnumber = 0

    numberofparticles = args[0][0]
    print(f'Computing for {round(Energy, 3)}Kev for particle number ==> {numberofparticles}')

    numberofparticles = numberofparticles +1
    # initial position of particle
    z0 = zstart  # in m
    # trying to change the x and y
    x0 = x0list[numberofparticles - 1]  # 0.01 # 1cm -->m
    y0 = y0list[numberofparticles - 1]  # 0.00
    # eventually change v directions also
    vx0 = vx0list[numberofparticles - 1]  # m/s
    vy0 = vy0list[numberofparticles - 1]
    vz0 = vz0list[numberofparticles - 1]

    # Set up initialization of variables
    Bfield = c_mag_array.getB([x0 * 1000, y0 * 1000, z0 * 1000]) # getb input = mm, output = mT
    Bfield = Bfield * 1.0e-3  # convert from mT to T
    bmag = math.sqrt(Bfield[0]**2 + Bfield[1]**2 + Bfield[2]**2)  # current field strength in
                                                                   # Tesla

    # ---------------------
    # Initializations
    posnow = np.array([x0, y0, z0])  # position now in m
    v = np.array([vx0, vy0, vz0])  # velocity m/s
    vnow = v
    vtot = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    initial_nrg = mass * c * c * ((1. - (vtot/c)**2.)**(-0.5) - 1.)
    multiplier = q/(gamma * mass)  # goes in rk4 velocity calcs
    gyro = mass * c * math.sqrt(gamma**2 - 1)/(q * bmag)

    # initialize array
    KElist = np.full(steps, np.nan)
    vvectorlist = np.full((steps, 3), np.nan)
    Blist = np.full((steps, 3), np.nan)
    pvectorlist = np.full((steps, 3), np.nan)
    stepsizelist = np.full((steps, 3), np.nan)
    # saving where it hits the walls/bottom and where hits top plate
    savedspots = np.full((steps, 3), np.nan)

    # set up time steps
    dti = dx/abs(vtot)  # dt is number of seconds for particle to pass 0.01m
    dt = dti  # have dt change so that is min of og dt and calc for velocity in x, y

    run_i = 0  # index of run so we don't run it forever
    breakit = 0  # initialize to 0 and if need to break loop, set breakit to 1
    recount = 0

    t3 = time.time()
    while (run_i < steps):
        # make sure dt is minimum of component dt so that never runs thru walls only check dt
        # every few runs
        if (recount == checktimestep):
            # do max abs vnow so don't have to check if vel is 0 (since has nrg, max vel will
            # never be 0)
            recount = 0  # reset the counter so can get next time finishes checktimesteps steps
            v4dt = max(abs(vnow[0]), abs(vnow[1]), abs(vnow[2]))  # vel max for use in velocity
                                                                  # version of dt
            dt_v = dx/v4dt
            # based off of gyroperiod and magnetic field calc'd previous
            bmag = math.sqrt(Bfield[0] * Bfield[0] + Bfield[1] * Bfield[1] +
                             Bfield[2] * Bfield[2])
            gyroperiod = 2. * 3.14159/(abs(q) * bmag/mass)
            dtB = gyroperiod/10000.
            dt = min(dti, dt_v, dtB)  # dtB is calc'd from previous run
            stepsizelist[run_i] = dt
            # Calc Energy
            vtot = math.sqrt(vnow[0] * vnow[0] + vnow[1] * vnow[1] + vnow[2] * vnow[2])  # velocity in m/s
            velratio = (vtot/c)
            KEmiddle = math.sqrt(1. - velratio * velratio)
            KE_i = KEbeginning * (1/KEmiddle - 1.)  # nrg in J
            KElist[run_i] = KE_i
            # KE_i = KEbeginning*((1.-(vtot/c)**2.)**(-0.5)-1.) # energy in J
            # if energy is beyond chosen % larger or smaller than initial energy, stop the run
            energyratio = KE_i/initial_nrg*100.  # calc nrg
            if (energyratio < min_energy_ratio) or (energyratio > max_energy_ratio):
                #print("last index run run_i= ", run_i)
                # break the loop by setting breakit so later sets runs number to max
                breakit = 1
                #print(
                #    f'outside of energy conservation limit. Ending energy ratio percentage: {energyratio}'
                #    )
            # if we've reached wall or too far away (distance or energy), break the loop
            posmag = math.sqrt(posnow[0] * posnow[0] + posnow[1] * posnow[1] +
                               posnow[2]*posnow[2])
            # set number to change distance (units meters)
            if posmag > max_distance:
                #print("last index run run_i= ", run_i)
                # break the loop by setting breakit so later sets runs number to max
                breakit = 1
                #print('Loop broken - too far from magnet at m = ', max_distance  )
            #if outside the body and below 0, it's not coming back so cut it
            if (( posnow[2] <= 0 ) and (((posnow[0] <= -LEXI_bodywidth_half) or 
                 (LEXI_bodywidth_half <= posnow[0])) or ((posnow[1] <= -LEXI_bodywidth_half) or
                 (LEXI_bodywidth_half <= posnow[1])))):
                #print("last index run run_i= ", run_i)
                # break the loop by setting breakit so later sets runs number to max
                breakit = 1
                #print('Loop broken - below 0 plane and too far from magnet')
            # if hit sides of lexi walls, stop iterating
            if ((-LEXI_bodylength <= posnow[2] <= 0) and
               (((-LEXI_bodywidth_half <= posnow[0] <= LEXI_bodywidth_half) and
               ((-outerlimit <= posnow[1] <= -innerlimit) or
               (innerlimit <= posnow[1] <= outerlimit))) or
               ((-LEXI_bodywidth_half <= posnow[1] <= LEXI_bodywidth_half) and
               ((-outerlimit <= posnow[0] <= -innerlimit) or
               (innerlimit <= posnow[0] <= outerlimit))))):
                #print(f"last index run run_i= {run_i}")
                savedspots[run_i] = posnow
                # break the loop by setting breakit so later sets runs number to max
                breakit = 1
                #print('hit within side walls ')
            # if hits bottom of lexi body!!! where the sensor is!!!! then runs = maxnumber
            if ((-LEXI_bodylength - Thicc_half <= posnow[2] <= -LEXI_bodylength + Thicc_half) and
               (-LEXI_bodywidth_half <= posnow[0] <= LEXI_bodywidth_half) and
               (-LEXI_bodywidth_half<= posnow[1] <= LEXI_bodywidth_half)):
                #print("last index run run_i= ", run_i)
                savedspots[run_i] = posnow
                # break the loop by setting breakit so later sets runs number to max
                breakit = 1
                bottomplatehitnumber = bottomplatehitnumber + 1
                #print('hit within bottomplate')
            if ((0. - Thicc_half <= posnow[2] <= 0.+ Thicc_half ) and
                (-LEXI_bodywidth_half <= posnow[0] <= LEXI_bodywidth_half) and
                (-LEXI_bodywidth_half <= posnow[1] <= LEXI_bodywidth_half)):
                # print("middle index run run_i= ", run_i)
                # don't break the loop !!! just save spot
                savedspots[run_i] = posnow
                # print('hit within top_plate ')

        # RK trace
        k1p = vnow
        k1 = (multiplier) * (np.cross(vnow,Bfield))
        k2p = vnow + k1 * dt/2.
        k2 = (multiplier) * (np.cross(vnow + dt * k1/2., Bfield))
        k3p = vnow + k2 * dt/2.
        k3 = (multiplier) * (np.cross(vnow + dt * k2/2., Bfield))
        k4p = vnow + k3 * dt
        k4 = (multiplier) * (np.cross(vnow + dt * k3, Bfield))
        vnow = vnow +(dt/6.) * (k1 + 2. * k2 + 2. * k3 + k4)
        posnow = posnow + (dt/6.) * (k1p + 2. * k2p + 2. * k3p + k4p)
        # update arrays
        pvectorlist[run_i] = posnow
        # Update values in arrays
        vvectorlist[run_i] = vnow
        Blist[run_i] = Bfield
        # get new B!!!!!
        # when get close to magnet array, use Bfield, otherwise use premade Bfield data
        # getb input = mm, output = mT
        Bfield = c_mag_array.getB([posnow[0] * 1000, posnow[1] * 1000, posnow[2] * 1000]) * 1.0e-3

        if breakit==1:
            #print("last index run run_i= ", run_i)
            run_i = steps  # break the loop by setting  runs number to max
            #print('broken loop for energy or position reasons ')
        # last thing before loop is add to index to ensure loop will end
        run_i = run_i + 1
        recount = recount +1

    t4 = time.time() # start timer to build magnets
    print('Time to step through positions [s]' , t4-t3)
    print ('Energy conservation[%]: ' , KE_i/KE_0*100.)

    folder_name = f"../data/{round(Energy, 3)}Kev/"
    # Check if directory exists, if not, create it
    check_folder = os.path.isdir(folder_name)
    # If folder doesn't exist, then create it.
    if not check_folder:
        os.makedirs(folder_name)
        print("created folder : ", folder_name)
    else:
        print('\n')
    run_name = f"{folder_name}parallel_{date}_total_number_of_particles_" +\
               f"{str(totalnumberofparticles).zfill(5)}_{random_seed}rng_{int(round(Energy, 3) * 1000)}eV_" +\
               f"{steps}steps_{str(numberofparticles).zfill(5)}_particlenumber"
    print(run_name)
    # Save np arrays to file
    # Create a dictionary with all the datasets so that the data can be saved in the pickle file
    # with associated keys
    dataset = {}
    dataset['pvectorlist'] = pvectorlist
    dataset['vvectorlist'] = vvectorlist
    dataset['savedspots'] = savedspots
    dataset['stepsizelist'] = stepsizelist
    dataset['KElist'] = KElist
    dataset['Blist'] = Blist
    dataset['bottomplatehitnumber'] = bottomplatehitnumber

    pickle.dump(dataset, open(f"{run_name}.p", "wb"))

    # # Save the dataset to an HDF file
    # dat = hf.File(f"{run_name}.h5", 'w')
    # for key in dataset.keys():
    #     dat.create_dataset(key, data=dataset[key])
    # dat.close()

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

# create magnets
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
s11a = Box(magnetization=(-magnetSTRENGTH, 0, 0), dimension=(magnetdimx, mdimy, magnetdimz),
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
c_mag_array = Collection(s1, s2, s3, s4, s5, s6, s7a, s7b, s7c, s8a, s8b, s8c, s9, s10, s11a, s11b,
                         s11c, s12a, s12b, s12c, s13a, s13b, s13c, s14a, s14b, s14c, s15a, s15b,
                         s15c, s16a, s16b, s16c)
# ======== END MAG SETUP ========================

# CUTOFFS
max_distance = 0.5  # m to cutoff calc
min_energy_ratio = 99.5  # energy can be within .5% of og
max_energy_ratio = 100.5
# using fab'd body wall dimensions
wall_half = 0.5 * 0.25 * 2.54/100.  # half * size*inches--> cm-->m
LEXI_bodylength = 15.847 * 2.54/100.  # in cm
LEXI_bodywidth_half_1 = 0.5 * 6.012 * 2.54/100.  # inches--> cm
LEXI_bodywidth_half_2 = 0.5 * 5.763 * 2.54/100.  # inches--> cm
outerlimit_1 = LEXI_bodywidth_half_1 + wall_half  # wall side on outside
innerlimit_1 = LEXI_bodywidth_half_1 - wall_half  # wall side on inside
outerlimit_2 = LEXI_bodywidth_half_2 + wall_half  # wall side on outside
innerlimit_2 = LEXI_bodywidth_half_2 - wall_half  # wall side on inside
THICKNESSOFBOTTOM = 5./100.  # thickness of bottom plate cm-->m
Thicc_half = THICKNESSOFBOTTOM/2.
# approx dimensions
LEXI_bodywidth_half = 0.5 * 5.9 * 2.54/100.  # inches--> cm
outerlimit = LEXI_bodywidth_half + wall_half  # wall side on outside
innerlimit = LEXI_bodywidth_half - wall_half  # wall side on inside

checktimestep = 10  # labeled in data save as timestepcheck
print('')
print(f'timestep mod value for checking and changing dt:{checktimestep}\n')

#for beginning of KE calc
KEbeginning = mass * c * c

t2 = time.time()  # start timer to build magnets
print('')
print(f'Time to initialize variables and set up B grid [s] {t2-t1}\n')

# plot the lexi body: IN M
halflength = 5.5120/2 * 2.54 * 1/100  # in to cm to m
xlist_body = [-halflength, 0, halflength]
xpart = [xlist_body, xlist_body, xlist_body]
ypart = xpart
xlist_body0 = [xlist_body[0], xlist_body[0], xlist_body[0]]
# xlist_body1 = [xlist_body[1], xlist_body[1], xlist_body[1] ]
xlist_body2 = [xlist_body[2], xlist_body[2], xlist_body[2]]
xpart0 = [xlist_body0, xlist_body0, xlist_body0]
ypart0 = xpart0
xpart2 = [xlist_body2, xlist_body2, xlist_body2]
ypart2 = xpart2
zbodyheight = 15.847 * 2.54/100.
zlist_body = [0, - 0.5 * zbodyheight, - zbodyheight]
zlist_body0 = [zlist_body[0], zlist_body[0], zlist_body[0]]
zlist_body1 = [zlist_body[1], zlist_body[1], zlist_body[1]]
zlist_body2 = [zlist_body[2], zlist_body[2], zlist_body[2]]
zpart = np.array([zlist_body0, zlist_body1, zlist_body2])
zpart0 = np.array([zlist_body0, zlist_body0, zlist_body0])
mposide = 4./100.  # in m
toplist = [-1.5 * mposide, -0.5 * mposide, 0.5 * mposide, 1.5 * mposide]
xpart_top, ypart_top = np.meshgrid(toplist, toplist)
ztoplist = [0., 0., 0., 0.]
zpart_top = np.array([ztoplist, ztoplist, ztoplist, ztoplist])

# ======INITIAL SETUP FINISHED (things that don't change with diff runs)======
totalnumberofparticles = 1
dx = 0.00005
# Inputs -------
steps = 50000  # number of steps totrace
# Uncomment this line and comment the next line to produce files with multiple energy values
#Energy_range = np.logspace(0.1, 1.2, 1)
Energy_range = [2.0]
for Energy in Energy_range:

    # Unit conversions
    Energy_J = Energy * kev  # units of keV #200MeV = 200*1000keV #100./1000. = 100eV -->keV
    KE_0 = Energy_J
    KE_i = KE_0
    gamma = 1. + (KE_0/(mass * c * c))
    v0 = c * math.sqrt(1. - 1./(gamma*gamma))
    vtot = v0 #total velocity magnitude needs to match v0 for energy to be correct
    zstart = 0.30 #in m

    date = f"{today_date}_FULLRUN_proton_{Energy}keV_nocmagsaved_straightdown_"
    testrun = 0  # run number from that date

    x0list = []
    y0list = []
    z0list = []
    vx0list = []
    vy0list = []
    vz0list = []
    # Added a seed for reproducibility
    random_seed = 10
    random.seed(random_seed)
    for i in range(totalnumberofparticles):
        # only doing within MPO area
        x0list.append((random.uniform(-halflength, halflength)))
        y0list.append((random.uniform(0, halflength)))
        z0list.append(zstart)
        # straightdown initial velocity
        vz0 =  -vtot
        vx0 = 0.0
        vy0 = 0.0
        vz0list.append(vz0)
        vx0list.append(vx0)
        vy0list.append(vy0)

    # NOTE: The next block of code does the exact same thing as the previous block and at better
    # speed (0.72 ms compared to 1.14 ms), however, even for same seed the list of numbers generated
    # is different depending on whether one uses for loop, as in the previous block or list
    # comprehension, as done in the next block of code. Since this part of the code is run only
    # once, either can be used, as long as one is consistent!

    # only doing within MPO area
    # x0list = np.array([random.uniform(-halflength, halflength)
    # for i in range(totalnumberofparticles)])
    # y0list = np.array([random.uniform(0, halflength) for i in range(totalnumberofparticles)])
    # z0list = np.full(totalnumberofparticles, zstart)
    # straight down initial velocity
    # vx0 = 0.0
    # vy0 = 0.0
    # vz0 = - vtot
    # vx0list = np.full(totalnumberofparticles, vx0)
    # vy0list = np.full(totalnumberofparticles, vy0)
    # vz0list = np.full(totalnumberofparticles, vz0)

    listof_xlists = np.full(totalnumberofparticles, np.nan)
    listof_ylists = np.full(totalnumberofparticles, np.nan)
    listof_zlists = np.full(totalnumberofparticles, np.nan)
    saved_xlists  = np.full(totalnumberofparticles, np.nan)
    saved_ylists  = np.full(totalnumberofparticles, np.nan)
    saved_zlists  = np.full(totalnumberofparticles, np.nan)
    listof_indexlists = np.full(totalnumberofparticles, np.nan)
    wallandbotlist_x  = np.full(totalnumberofparticles, np.nan)
    wallandbotlist_y  = np.full(totalnumberofparticles, np.nan)
    wallandbotlist_z  = np.full(totalnumberofparticles, np.nan)

    # numberofparticles = 0
    bottomplatehitnumber = 0

    #thread_num = int(sys.argv[1])

    #if __name__ == '__main__':
    p = mp.Pool(60)

    input = (i for i in itertools.combinations_with_replacement(range(totalnumberofparticles), 1))

    res = p.map(compute_vars, input)

    p.close()
    p.join()

    print(f'Took {round(time.time() - t1, 3)} seconds')

print(f'Took {round(time.time() - t1, 3)} seconds')
