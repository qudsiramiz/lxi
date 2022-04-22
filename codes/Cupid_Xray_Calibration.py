from ctypes import c_uint8, c_uint16, c_uint32, c_int16, c_float, Structure
from struct import pack, unpack
from os.path import getsize
from sys import argv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LogNorm
import re, datetime, os
import numpy as np
import matplotlib.gridspec as gridspec
from bitstring import BitArray
#matplotlib.rcParams['pdf.fonttype'] = 42

plt.rcParams['axes.grid'] = True
filepath = os.getenv('DROPBOXBU')

class xray_pkt(Structure):
    #Defining the X-ray packet structure that is saved to XRBR from the instrument
    # 16-byte Science Telemetry packets for each event
	# byte   0-  1 = 0xFE6B
	# byte   2-  3 = 0x2840
	# byte   4-  5 = Time tag
        # bit15: Telemetry Type=0
        # bit14: =1 if cmded event
        # bit13- 0: MS 14-bits of MET
	# byte   6-  7 = Time tag (cont.)
        # bit15- 0:  LS 16-bits of MET (LSbit=1msec)
    # byte   8-  9 = ch1 16-bit data (0xDDDD)
    # byte 10- 11 = ch2 16-bit data (0xDDDD)
    # byte 12- 13 = ch3 16-bit data (0xDDDD)
    # byte 14- 15 = ch4 16-bit data (0xDDDD)

    # 16-byte HK packet
    # sent whenever HV state changes or once every second (whichever comes first)
	# byte  0-  1 = 0xFE6B
	# byte  2-  3 = 0x2840
    # byte  4-  5 = Time tag
    #     bit15: Telemetry Type=1
    #     bit14: =0
    #     bit13- 0: MS 14-bits of MET
	# byte   6-  7 = Time tag (cont.)
    #     bit15- 0:  LS 16-bits of MET (LSbit=1msec)
    # byte  8-  9 = Status
	# 	bit15: 1=MCP HV changed, 0=1sec HK packet
	# 	bit14:
    #         if bit15=1, 1=auto MCP HV change, 0=manual MCP HV change
	# 	    if bit15=0, =0 unused
	# 	bit13: =0 unused
	# 	bit12: =0 unused
	# 	bit11- 0:
    #         if bit15=1, MCP HV
    #         if bit15=0, thermistor data
    # byte10- 11 = delta Event Count (since last HK packet)
    # byte12- 13 = delta Dropped Event Count (due to threshold test, since last HK packet)
    # byte14- 15 = delta Lost Event Count (due to FIFO overflow, since last HK packet)

    _fields_ = [('sync', c_uint32), ('time', c_uint32),
                ('channels', c_uint16 * 4)]

    def __init__(self, unpacked):
        self.sync = unpacked[0]
        self.time = unpacked[1]
        self.channels = unpacked[2:6]

class xrfs_pkt(Structure):
    _fields_ = [('sync', c_uint16), ('time', c_uint32),
                ('x', c_uint16), ('y', c_uint16)]

    def __init__(self, unpacked):
        self.sync, self.time, self.x, self.y = unpacked

xrfs_unpack = '<HIHH'

# Xray packet formatter
xray_unpack = '>II4H'

    # > = Big Endian
    # I = Unsigned Int = Sync
    # I = Unsigned Int = Time
    # 4H = Unsigned Short = 4 Channels
# t_cut is the limit between a science TLM packet that is not commanded, and one that is commanded.
# 1073741824 in bit form is 01000000000000000000000000000000, and the 1 is in the 31st spot, which
# makes the 1 a commanded event marker in the science TLM packet in bit 14 (see above).
# HK data would have a 1 in the 32nd spot, which would make the number larger than this.
t_cut = 1073741824

def read_xrfs(filename, varname):
    f = open(filename, 'rb')
    contents = f.read()
    starts = [m.start() for m in re.finditer(b'\x51\xfa', contents)]
    stops = starts[1:]
    stops.append(getsize(filename) - starts[0])
    len = stops[0] - starts[0]
    for idx, s in enumerate(starts):
        stuff = unpack(xrfs_unpack, contents[s:s+len])
        data = xrfs_pkt(stuff)
        #if (data.time < t_cut):
        varname.append(data)

    f.close()

def read_xray(filename, varname):
    # Function to read SCIENCE data out of xrbr file
    file = open(filename, 'rb')
    contents = file.read()
    starts = [m.start() for m in re.finditer(b'\xfe\x6b', contents)]
    stops = starts[1:]
    stops.append(starts[-1]+16)
    for idx, s in enumerate(starts):
        stuff = unpack(xray_unpack, contents[s:s+16])
        data = xray_pkt(stuff)
        if (int(data.sync) == 4268435520) and (data.time < t_cut):
            varname.append(data)
    file.close()
def read_xray_all(filename, varname):
    # Function to read ALL telemetry in the xrbr file
    file = open(filename, 'rb')
    contents = file.read()
    starts = [m.start() for m in re.finditer(b'\xfe\x6b', contents)]
    stops = starts[1:]
    stops.append(starts[-1]+16)
    for idx, s in enumerate(starts):
        stuff = unpack(xray_unpack, contents[s:s+16])
        data = xray_pkt(stuff)
        varname.append(data)
    file.close()
def read_xray_commanded(filename, varname):
    # Function to read COMMANDED EVENT data out of XRBR file
    file = open(filename, 'rb')
    contents = file.read()
    starts = [m.start() for m in re.finditer(b'\xfe\x6b', contents)]
    stops = starts[1:]
    stops.append(starts[-1]+16)
    for idx, s in enumerate(starts):
        stuff = unpack(xray_unpack, contents[s:s+16])
        data = xray_pkt(stuff)
        if (int(data.sync) == 4268435520) and (data.time > t_cut) and (data.time < 2147483647):
            varname.append(data)
    file.close()
def read_xray_hk(filename, varname):
    # Function to read HOUSEKEEPING data out of XRBR file
    f = open(filename, 'rb')
    contents = f.read()
    starts = [m.start() for m in re.finditer(b'\xfe\x6b', contents)]
    stops = starts[1:]
    stops.append(starts[-1]+16)
    for idx, s in enumerate(starts):
        stuff = unpack(xray_unpack, contents[s:s+16])
        data = xray_pkt(stuff)
        # 2147483648
        # This time demarkation is for HK packets from the xray that would have
        # a Telemetry Type of 1 in bit 31 of the 0-31 bit 4 byte Time Tag data
        # (bytes 4-7)
        if (int(data.sync) == 4268435520) and (data.time >= 2147483647):
            varname.append(data)
    f.close()
def plot_xrbr(filename):
    xrdata = []
    read_xray(filename,xrdata)
    times = np.transpose([d.time for d in xrdata])
    x0r, x1r, y0r, y1r = np.transpose([d.channels for d in xrdata])
    # TIME CUTTING
    # print(times[5010])
    # Tmask = np.where((times > (2152680-2147484)*1000) & (times < (2152680+300-2147484)*1000))
    # Tmask = np.where((times < 2147483647) & (times > 152000))# (2154880-2147484)*1000) & (times < (2154880+300-2147484)*1000))
    # times = times[Tmask]
    # x0r = x0r[Tmask]
    # x1r = x1r[Tmask]
    # y0r = y0r[Tmask]
    # y1r = y1r[Tmask]

    #####
    ADC_Vrange = 4.5
    VperC = ADC_Vrange/65536.
    x0 = x0r * VperC
    x1 = x1r * VperC
    y0 = y0r * VperC
    y1 = y1r * VperC
    # ### TEST PLOTTING ###
    hist_fig = plt.figure(figsize=(10, 6))
    ax1=hist_fig.add_subplot(121, label="x0x1color")
    ax2=hist_fig.add_subplot(122, label="y0y1color")
    channelbins = 100
    #['viridis', 'plasma', 'inferno', 'magma']
    binedges = np.linspace(1,5,101)
    h1, xedges, yedges, im1= ax1.hist2d(x0,x1,bins=binedges,cmap='inferno',norm=LogNorm())
    h2, xedges, yedges, im2= ax2.hist2d(y0,y1,bins=binedges,cmap='inferno',norm=LogNorm())
    cb1 = hist_fig.colorbar(im1,ax=ax1,orientation='horizontal')
    cb2 = hist_fig.colorbar(im2,ax=ax2,orientation='horizontal')

    ax1.set_xlabel('x0')
    ax1.set_ylabel('x1')
    ax2.set_xlabel('y0')
    ax2.set_ylabel('y1')
    cb1.set_label('Counts for X')
    cb2.set_label('Counts for Y')

    Title1 = hist_fig.suptitle('X-ray Channel Comparison Histograms '+filename, fontsize = 'xx-large')
    Title1.set_y(0.94)
    hist_fig.savefig(filename+'_channelcompare.png')
    plt.close()

    lo_thold =2.1#16019.
    hi_thold = 3.3#62622.
    # offset = 1.3
    offsetx0 = 1#14563.
    offsetx1 = 1#14563.
    offsety0 = 1#14563.
    offsety1 = 1#14563.

    mask_x0 = np.where((x0 < hi_thold) & (x0 > lo_thold))
    mask_x1 = np.where((x1 < hi_thold) & (x1 > lo_thold))
    mask_y0 = np.where((y0 < hi_thold) & (y0 > lo_thold))
    mask_y1 = np.where((y1 < hi_thold) & (y1 > lo_thold))

    mask_x = np.intersect1d(mask_x0,mask_x1)
    mask_y = np.intersect1d(mask_y0,mask_y1)

    pass_mask = np.intersect1d(mask_x,mask_y)

    x0pass = (x0[pass_mask]) - offsetx0
    x1pass = (x1[pass_mask]) - offsetx1
    y0pass = (y0[pass_mask]) - offsety0
    y1pass = (y1[pass_mask]) - offsety1

    tvalid = times[pass_mask]
    tstart = tvalid[0]
    tend = tvalid[-2]
    dt = (tend/1000 - tstart/1000)
    print(tvalid[0])
    print(tvalid[-2])
    print(dt)

    nbins = 100

    # NOMINAL CALCULATION OF MCP POSITION
    x =(x0pass/(x0pass+x1pass))#-0.5
    y =(y0pass/(y0pass+y1pass))#-0.5
    # ALIGNMENT CORRECTION DEVELOPED BY C. O'Brien
    x_offset = 0.0006
    y_offset = 0.0061

    x_offset = 0.4866
    y_offset = 0.5201
    M_inv = np.array([[1.0275, -0.14678],[-0.13380, 1.0293]])
    x_shift = x - x_offset
    y_shift = y - y_offset
    x = (x_shift * M_inv[0,0] + y_shift * M_inv[0,1])
    y = (x_shift * M_inv[1,0] + y_shift * M_inv[1,1])

    #THE *2/0.0614 IS A NORMALIZATION FACTOR LIKE SIEGMUND et. al. 1986
    #THIS SCALES IT TO CM SCALE ON THE DETECTOR
    x = (x)*2/0.0614
    y = (y)*2/0.0614
    #####
    plotwidth = 4.6

    XCenterPlus = np.where(y > -1)
    XCenterMinus = np.where(y < 1)
    XMask = np.intersect1d(XCenterPlus,XCenterMinus)
    XCenter = x[XMask]

    YCenterPlus = np.where(x > -1)
    YCenterMinus = np.where(x < 1)
    YMask = np.intersect1d(YCenterPlus,YCenterMinus)
    YCenter = y[YMask]

    left, width = 0.15, 0.55
    bottom, height = 0.15, 0.55
    spacing = 0.03

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]
# GENERATE THE LINEAR SCALE PLOT
    lin_fig = plt.figure(figsize=(10, 10))
    ax = lin_fig.add_axes(rect_scatter)
    ax_histx = lin_fig.add_axes(rect_histx, sharex=ax)
    ax_histy = lin_fig.add_axes(rect_histy, sharey=ax)
    cax = lin_fig.add_axes([0.2, 0.08, 0.45, 0.01])
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
    #['viridis', 'plasma', 'inferno', 'magma']
    # binedges = np.linspace(-nbins/2,nbins/2,nbins+1)
    # binedges = np.linspace(-nbins,nbins,nbins+1)
    binedges = np.linspace(-plotwidth/2,plotwidth/2,int(nbins))

    # binedges = np.linspace(0,nbins,nbins+1)
    h2, xedges, yedges, im= ax.hist2d(x,y,bins=binedges,cmap='inferno')
    cb = lin_fig.colorbar(im,cax=cax,orientation='horizontal')
    cb.set_ticks([0, 25, 50])
    cb.set_ticklabels([str(0/dt), str(np.around((25/dt),decimals=4)), str(np.around((50/dt),decimals=4))])
    ax.set_xlim((-plotwidth/2,plotwidth/2))
    ax.set_ylim((-plotwidth/2,plotwidth/2))
    # ax.set_xlim((-nbins/2,nbins/2))
    # ax.set_ylim((-nbins/2,nbins/2))
    # ax.set_xlim((-nbins,nbins))
    # ax.set_ylim((-nbins,nbins))
    # ax.set_xlim(((-nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    # ax.set_ylim(((-nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    #ARROWS FOR CUPID COORDINATES
    ArrSize = .5
    ZeroLoc = 1.9
    LabLoc = ZeroLoc-ArrSize-ArrSize/5
    ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = 'r')
    ax.text(ZeroLoc,-LabLoc, '+X',color='r',fontsize='small',horizontalalignment='center')
    ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = 'r')
    ax.text(LabLoc,-ZeroLoc, '+Y',color='r',fontsize='small',horizontalalignment='center' )
    ax.text(ZeroLoc-0.35,-ZeroLoc-0.2, 'CuPID S/C Coords',color='r',fontsize='small',horizontalalignment='center' )

    ax.set_xlabel('X Detector Position [cm]')
    ax.set_ylabel('Y Detector Position [cm]')
    ax.set_title('2D Histogram of MCP')
    cb.set_label('Count Rate (cnts/s)')
    # ax.axvline(0,color="r",alpha=0.5)
    # ax.axhline(0,color="b",alpha=0.5)
    #

    MCPCirc = patches.Circle((0,0),radius=2,linewidth=2, edgecolor='white', facecolor='none')
    ax.add_patch(MCPCirc)
    ax.text(-0.3,-2.1, 'Size of MCP',color='white',fontsize='small',horizontalalignment='center' )

    # Rectx = -50
    # Recty = -15
    # Recth = 15
    # Rectw = 20
    # rect = patches.Rectangle((Rectx, Recty), Rectw, Recth, linewidth=2, edgecolor='r', facecolor='none')
    # ax.add_patch(rect)
    # Xsplotch = np.where((x > Rectx) & (x < Rectx+Rectw))
    # Ysplotch = np.where((y > Recty) & ( y< Recty+Recth))
    # Insplotch = np.intersect1d(Xsplotch,Ysplotch)
    # X_bad= (x[Insplotch])
    # Y_bad = (y[Insplotch])
    # NCounts = len(X_bad)
    # print(NCounts)
    # ax.text(Rectx+10,Recty-10, str(NCounts)+' cnts in red box',color='r',fontsize='small',horizontalalignment='center' )


    fmax = np.amax(h2)
    indfmax = np.where(h2 == fmax)
    hmax = fmax/2
    minmatrix = abs(h2-hmax)
    indhmax = np.where(minmatrix == np.amin(minmatrix))

    ax_histx.hist(XCenter, bins=binedges,color='b')#the X axis histogram at y = .5
    ax_histx.set_title('1D Histogram at Y = 1/2')
    ax_histx.set_ylabel('Counts (total)')
    ax_histy.hist(YCenter, bins=binedges, orientation='horizontal',color='r')
    ax_histy.set_title('1D Histogram at X = 1/2')
    ax_histy.set_xlabel('Counts (total)')
    lowstring = 'Low: '
    highstring = 'High: '
    #offstring = 'Offset: '+ (str(offsetx0))+', '+ (str(offsetx1)) + ', ' + (str(offsety0)) + ', ' + (str(offsety1))
    BinNumber = '#Bins = '
    lin_fig.text(0.83, 0.9, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.87, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.85, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.83,  lowstring+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.81,  highstring+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.79,  BinNumber+(str(nbins)), fontsize=12, horizontalalignment='center',verticalalignment='center')

    lin_fig.savefig(filename+'_linscale.png')
    lin_fig.savefig(filename+'_linscale.svg', format='svg', dpi=1000, bbox_inches=None, pad_inches=0.3)

    plt.close()
#
# #GENERATE THE LOG SCALE PLOT
    log_fig = plt.figure(figsize=(10, 10))
#
    ax = log_fig.add_axes(rect_scatter)
    ax_histx = log_fig.add_axes(rect_histx, sharex=ax)
    ax_histy = log_fig.add_axes(rect_histy, sharey=ax)
    cax = log_fig.add_axes([0.2, 0.08, 0.45, 0.01])
#
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
#
    # binedges = np.linspace(-nbins/2,nbins/2,nbins+1)
    binedges = np.linspace(-plotwidth/2,plotwidth/2,int(nbins))
    h2, xedges, yedges, im= ax.hist2d(x,y,bins=binedges,cmap='inferno', norm=LogNorm(vmin=1,vmax=10*(1+np.floor(np.amax(h2)/10))))
    cb = log_fig.colorbar(im,cax=cax,orientation='horizontal')
    cb.set_ticks([1, 25, 50])
    cb.set_ticklabels([str(np.around((1/dt),decimals=4)), str(np.around((25/dt),decimals=4)), str(np.around((50/dt),decimals=4))])
    minorticks = im.norm(np.arange(1, 50, 2))
    cb.ax.xaxis.set_ticks(minorticks, minor=True)
    ax.set_xlim((-plotwidth/2,plotwidth/2))
    ax.set_ylim((-plotwidth/2,plotwidth/2))
    # ax.set_xlim((-nbins/2,nbins/2))
    # ax.set_ylim((-nbins/2,nbins/2))
    # ax.set_xlim(((-nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    # ax.set_ylim(((-nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    # ax.set_xlim((-nbins,nbins))
    # ax.set_ylim((-nbins,nbins))
    # ArrSize = nbins/20
    # ArrLoc = 45/100
    # ZeroLoc = ArrLoc*nbins
    # LabLoc = ZeroLoc-ArrSize-ArrSize/5
    # ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = 'r')
    # ax.text(ZeroLoc,-LabLoc, 'CuPID +X',color='r',fontsize='small',horizontalalignment='center')
    # ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = 'r')
    # ax.text(LabLoc,-ZeroLoc, 'CuPID +Y',color='r',rotation = 90,fontsize='small',horizontalalignment='center', )
    ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = 'r')
    ax.text(ZeroLoc,-LabLoc, '+X',color='r',fontsize='small',horizontalalignment='center')
    ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = 'r')
    ax.text(LabLoc,-ZeroLoc, '+Y',color='r',fontsize='small',horizontalalignment='center' )
    ax.text(ZeroLoc-0.35,-ZeroLoc-0.2, 'CuPID S/C Coords',color='r',fontsize='small',horizontalalignment='center' )

    MCPCirc = patches.Circle((0,0),radius=2,linewidth=2, edgecolor='red', facecolor='none')
    ax.add_patch(MCPCirc)
    ax.text(-0.3,-2.1, 'Size of MCP',color='red',fontsize='small',horizontalalignment='center' )
    rect1 = patches.Rectangle((-0.64,-2.14), 0.65, 0.15, linewidth=1, edgecolor='red', facecolor='white')
    ax.add_patch(rect1)
    rect2 = patches.Rectangle((1.09,-2.14), 0.93, 0.15, linewidth=1, edgecolor='red', facecolor='white')
    ax.add_patch(rect2)
    ax.set_xlabel('X Detector Position [cm]')
    ax.set_ylabel('Y Detector Position [cm]')
    ax.set_title('CuPID X-ray Background')
    cb.set_label('Count rate (cnts/s)')
    #ax.axvline(0,color="r",alpha=0.5)
    #ax.axhline(0,color="b",alpha=0.5)
#
    ax_histx.hist(XCenter, bins=binedges,color='b')#the X axis histogram at y = .5
    ax_histx.set_yscale('log')
    ax_histx.set_title('1D Histogram at Y = 1/2')
    ax_histx.set_ylabel('Counts (total)')
    ax_histy.hist(YCenter, bins=binedges, orientation='horizontal',color='r')
    ax_histy.set_xscale('log')
    ax_histy.set_title('1D Histogram at X = 1/2')
    ax_histy.set_xlabel('Counts (total)')
#
    BinNumber = '#Bins = '
    log_fig.text(0.83, 0.9, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.87, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.85, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.83,  lowstring+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.81,  highstring+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.79,  BinNumber+(str(nbins)), fontsize=12, horizontalalignment='center',verticalalignment='center')

    log_fig.savefig(filename+'_logscale.png')
    log_fig.savefig(filename+'_logscale.svg', format='svg', dpi=1000, bbox_inches=None, pad_inches=0.3)

    plt.close()

#
#
# GENERATE THE CHANNEL HISTOGRAM
    hist_fig = plt.figure()
    hist_fig.set_size_inches(10,10)
    ax1=hist_fig.add_subplot(221, label="x0")
    ax2=hist_fig.add_subplot(222, label="x1")
    ax3=hist_fig.add_subplot(223, label="y0")
    ax4=hist_fig.add_subplot(224, label="y1")
    binedgeshist = np.linspace(0.5,5,100)
    x0hist= ax1.hist(x0,bins=binedgeshist, color='b')
    x1hist= ax2.hist(x1,bins=binedgeshist, color='r')
    y0hist= ax3.hist(y0,bins=binedgeshist, color='g')
    y1hist= ax4.hist(y1,bins=binedgeshist, color='c')
    ax1.set_ylabel('Count')
    ax3.set_ylabel('Count')
    ax3.set_xlabel('Voltage')
    ax4.set_xlabel('Voltage')
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])
    ax4.set_yticklabels([])
    ax1.set_title('x0 Channel Values (Channel 1)')
    ax2.set_title('x1 Channel Values (Channel 2)')
    ax3.set_title('y0 Channel Values (Channel 3)')
    ax4.set_title('y1 Channel Values (Channel 4)')
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    Title1 = hist_fig.suptitle('X-ray Channels Histograms '+filename, fontsize = 'xx-large')
    Title1.set_y(0.94)
    #Title2 = hist_fig.suptitle(filename)
    #Title2.set_y(0.92)
    hist_fig.savefig(filename+'_channelhistogram.png')
    plt.close()

def plot_xrbrcommanded(filename):
    xrdata = []
    read_xray_commanded(filename,xrdata)
    times = np.transpose([d.time for d in xrdata])
    x0r, x1r, y0r, y1r = np.transpose([d.channels for d in xrdata])
    #####
    ADC_Vrange = 4.5
    VperC = ADC_Vrange/65536.
    x0 = x0r * VperC
    x1 = x1r * VperC
    y0 = y0r * VperC
    y1 = y1r * VperC
    # ### TEST PLOTTING ###
    hist_fig = plt.figure(figsize=(10, 6))
    ax1=hist_fig.add_subplot(121, label="x0x1color")
    ax2=hist_fig.add_subplot(122, label="y0y1color")
    channelbins = 100
    #['viridis', 'plasma', 'inferno', 'magma']
    binedges = np.linspace(1,5,101)
    h1, xedges, yedges, im1= ax1.hist2d(x0,x1,bins=binedges,cmap='inferno',norm=LogNorm())
    h2, xedges, yedges, im2= ax2.hist2d(y0,y1,bins=binedges,cmap='inferno',norm=LogNorm())
    cb1 = hist_fig.colorbar(im1,ax=ax1,orientation='horizontal')
    cb2 = hist_fig.colorbar(im2,ax=ax2,orientation='horizontal')

    ax1.set_xlabel('x0')
    ax1.set_ylabel('x1')
    ax2.set_xlabel('y0')
    ax2.set_ylabel('y1')
    cb1.set_label('Counts for X')
    cb2.set_label('Counts for Y')

    Title1 = hist_fig.suptitle('X-ray Commanded Channel Comparison Histograms '+filename, fontsize = 'xx-large')
    Title1.set_y(0.94)
    hist_fig.savefig(filename+'_commandedchannelcompare.png')
    plt.close()

    lo_thold =0#16019.
    hi_thold = 4.5#62622.
    offset = 1
    # offsetx0 = 1#14563.
    # offsetx1 = 1#14563.
    # offsety0 = 1#14563.
    # offsety1 = 1#14563.
    #
    mask_x0 = np.where((x0 < hi_thold) & (x0 > lo_thold))
    mask_x1 = np.where((x1 < hi_thold) & (x1 > lo_thold))
    mask_y0 = np.where((y0 < hi_thold) & (y0 > lo_thold))
    mask_y1 = np.where((y1 < hi_thold) & (y1 > lo_thold))

    mask_x = np.intersect1d(mask_x0,mask_x1)
    mask_y = np.intersect1d(mask_y0,mask_y1)

    pass_mask = np.intersect1d(mask_x,mask_y)

    x0pass = (x0[pass_mask]) - offset
    x1pass = (x1[pass_mask]) - offset
    y0pass = (y0[pass_mask]) - offset
    y1pass = (y1[pass_mask]) - offset

    tvalid = times[pass_mask]

    nbins = 80

    # NOMINAL CALCULATION OF MCP POSITION
    x =(x0pass/(x0pass+x1pass))
    y =(y0pass/(y0pass+y1pass))
    # ALIGNMENT CORRECTION DEVELOPED BY C. O'Brien
    x_offset = 0.5006
    y_offset = 0.5061
    M_inv = np.array([[1.0275, -0.14678],[-0.13380, 1.0293]])
    x_shift = x - x_offset
    y_shift = y - y_offset
    x = (x_shift * M_inv[0,0] + y_shift * M_inv[0,1]) + 0.5
    y = (x_shift * M_inv[1,0] + y_shift * M_inv[1,1]) + 0.5
    # THE -0.5 IS INTHERE TO SHIFT IT TO 0,0
    # THE *7 IS A NORMALIZATION FACTOR LIKE SIEGMUND et. al. 1986
    x = (x-0.5)*7*nbins
    y = (y-0.5)*7*nbins
    #x =((x0pass/(x0pass+x1pass))-0.5)*10*nbins
    #x =((x0pass/(x0pass+x1pass))-0.5)*7*nbins
    #y =((y0pass/(y0pass+y1pass))-0.5)*10*nbins
    #y =((y0pass/(y0pass+y1pass))-0.5)*7*nbins
    # x = (((x0pass - offsetx0) - (x1pass - offsetx1)))*nbins
    # y = (((y0pass - offsety0) - (y1pass - offsety1)))*nbins
    # fig1 = plt.figure()
    # fig1.set_size_inches(8,10)
    # ax1=fig1.add_subplot(111, label="1")
    # A, = ax1.plot(x)
    # plt.savefig(filename+'_TEST.png')
    #


    #x = ((x0pass - offsetx0) / ((x0pass-offsetx0) + (x1pass - offsetx1)))*nbins
    #y = ((y0pass - offsety0) / ((y0pass-offsety0) + (y1pass - offsety1)))*nbins
    #####
    XCenterPlus = np.where(y > -1)
    XCenterMinus = np.where(y < 1)
    XMask = np.intersect1d(XCenterPlus,XCenterMinus)
    XCenter = x[XMask]

    YCenterPlus = np.where(x > -1)
    YCenterMinus = np.where(x < 1)
    YMask = np.intersect1d(YCenterPlus,YCenterMinus)
    YCenter = y[YMask]

    left, width = 0.15, 0.55
    bottom, height = 0.15, 0.55
    spacing = 0.03

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]
# GENERATE THE LINEAR SCALE PLOT
    lin_fig = plt.figure(figsize=(10, 10))
    ax = lin_fig.add_axes(rect_scatter)
    ax_histx = lin_fig.add_axes(rect_histx, sharex=ax)
    ax_histy = lin_fig.add_axes(rect_histy, sharey=ax)
    cax = lin_fig.add_axes([0.2, 0.08, 0.45, 0.01])
    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
    #['viridis', 'plasma', 'inferno', 'magma']
    binedges = np.linspace(-nbins/2,nbins/2,nbins+1)
    # binedges = np.linspace(-nbins,nbins,nbins+1)
    # binedges = np.linspace(0,nbins,nbins+1)
    h2, xedges, yedges, im= ax.hist2d(x,y,bins=binedges,cmap='inferno')
    cb = lin_fig.colorbar(im,cax=cax,orientation='horizontal')
    ax.set_xlim((-nbins/2,nbins/2))
    ax.set_ylim((-nbins/2,nbins/2))
    # ax.set_xlim((-nbins,nbins))
    # ax.set_ylim((-nbins,nbins))
    # ax.set_xlim(((nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    # ax.set_ylim(((nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    #ARROWS FOR CUPID COORDINATES
    ArrSize = nbins/20
    ArrLoc = 39/100
    ZeroLoc = ArrLoc*nbins
    LabLoc = ZeroLoc-ArrSize-ArrSize/5
    ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = 'r')
    ax.text(ZeroLoc,-LabLoc, 'CuPID +X',color='r',fontsize='small',horizontalalignment='center')
    ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = 'r')
    ax.text(LabLoc,-ZeroLoc, 'CuPID +Y',color='r',rotation = 90,fontsize='small',horizontalalignment='center' )
    ax.set_xlabel('X Position Bin')
    ax.set_ylabel('Y Position Bin')
    ax.set_title('2D Histogram of MCP')
    cb.set_label('Counts (total)')
    ax.axvline(0,color="r",alpha=0.5)
    ax.axhline(0,color="b",alpha=0.5)

    fmax = np.amax(h2)
    indfmax = np.where(h2 == fmax)
    hmax = fmax/2
    minmatrix = abs(h2-hmax)
    indhmax = np.where(minmatrix == np.amin(minmatrix))

    ax_histx.hist(XCenter, bins=binedges,color='b')#the X axis histogram at y = .5
    ax_histx.set_title('1D Histogram at Y = 1/2')
    ax_histx.set_ylabel('Counts (total)')
    ax_histy.hist(YCenter, bins=binedges, orientation='horizontal',color='r')
    ax_histy.set_title('1D Histogram at X = 1/2')
    ax_histy.set_xlabel('Counts (total)')
    lowstring = 'Low: '
    highstring = 'High: '
    #offstring = 'Offset: '+ (str(offsetx0))+', '+ (str(offsetx1)) + ', ' + (str(offsety0)) + ', ' + (str(offsety1))
    BinNumber = '#Bins = '
    lin_fig.text(0.83, 0.9, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.87, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.85, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.83,  lowstring+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.81,  highstring+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.79,  BinNumber+(str(nbins)), fontsize=12, horizontalalignment='center',verticalalignment='center')

    #lin_fig.text(0.83, 0.79,  offstring, fontsize=12, horizontalalignment='center',verticalalignment='center')

    lin_fig.savefig(filename+'_linscaleCommanded.png')
    plt.close()

def rate_xrbr(filename):
    xrbr_all = []
    read_xray(filename,xrbr_all)
    times = np.transpose([d.time for d in xrbr_all])
    x0r, x1r, y0r, y1r = np.transpose([d.channels for d in xrbr_all])
    ADC_Vrange = 4.5
    VperC = ADC_Vrange/65536.
    x0 = x0r * VperC
    x1 = x1r * VperC
    y0 = y0r * VperC
    y1 = y1r * VperC
    lo_thold =2.1#16019.
    hi_thold = 3.3#62622.
    offset = 1

    mask_x0 = np.where((x0 < hi_thold) & (x0 > lo_thold))
    mask_x1 = np.where((x1 < hi_thold) & (x1 > lo_thold))
    mask_y0 = np.where((y0 < hi_thold) & (y0 > lo_thold))
    mask_y1 = np.where((y1 < hi_thold) & (y1 > lo_thold))
    mask_x = np.intersect1d(mask_x0,mask_x1)
    mask_y = np.intersect1d(mask_y0,mask_y1)
    pass_mask = np.intersect1d(mask_x,mask_y)
    tvalid = times[pass_mask]
    x0pass = (x0[pass_mask]) - offset
    x1pass = (x1[pass_mask]) - offset
    y0pass = (y0[pass_mask]) - offset
    y1pass = (y1[pass_mask]) - offset

    nbins = 80
    x =(x0pass/(x0pass+x1pass))
    y =(y0pass/(y0pass+y1pass))
    # ALIGNMENT CORRECTION DEVELOPED BY C. O'Brien
    ###############
    x_offset = 0.5006
    y_offset = 0.5061
    M_inv = np.array([[1.0275, -0.14678],[-0.13380, 1.0293]])
    x_shift = x - x_offset
    y_shift = y - y_offset
    x = (x_shift * M_inv[0,0] + y_shift * M_inv[0,1]) + 0.5
    y = (x_shift * M_inv[1,0] + y_shift * M_inv[1,1]) + 0.5
    ###############
    # THE -0.5 IS INTHERE TO SHIFT IT TO 0,0
    # THE *7 IS A NORMALIZATION FACTOR LIKE SIEGMUND et. al. 1986
    x = (x-0.5)*7*nbins
    y = (y-0.5)*7*nbins

    times = times/1000
    intT = times.astype(int)
    intTvalid = tvalid.astype(int)
    Rectx = -22
    Recty = 0
    Recth = 22
    Rectw = 22
    # rect = patches.Rectangle((Rectx, Recty), Rectw, Recth, linewidth=2, edgecolor='r', facecolor='none')
    # ax.add_patch(rect)
    Xsplotch = np.where((x > Rectx) & (x < Rectx+Rectw))
    Ysplotch = np.where((y > Recty) & ( y< Recty+Recth))
    Insplotch = np.intersect1d(Xsplotch,Ysplotch)
    X_sig= (x[Insplotch])
    Y_sig = (y[Insplotch])
    NCounts = len(X_sig)
    # print(NCounts)
    ###############
    # Count = []
    # CountRate = []
    # CountRateValid = []
    # for T in range(0,len(intT)-1):
    #     Count.append([intT[T]])
    #     if intT[T+1] == intT[T]:
    #         pass
    #     if intT[T+1] != intT[T]:
    #         CountRate.append([intT[T],len(Count)])
    #         Count = []
    #
    # np.savetxt(filename+'CountRate.csv',CountRate,delimiter=',',newline='\n',header='time,DeltaEventCount', fmt='%.5f')
    #################
    totalcounts = len(intT)
    totalcountsvalid = len(intTvalid)
    duration = np.max(times) - times[0]
    ratetotal = totalcounts/duration
    ratevalid = totalcountsvalid/duration
    ratesignal = NCounts/duration
    the_data = np.array([totalcounts,totalcountsvalid,duration,ratetotal,ratevalid,ratesignal]).reshape(1,6)
    np.savetxt(filename+'_CountRateSummary.csv',the_data,delimiter=',',newline='\n',header='totalcounts,totalvalidcounts,duration,ratetotal,ratevalid,ratesignal', fmt='%.5f')

def countratecompare(filename):
    xrbr_all = []
    read_xray(filename,xrbr_all)
    times = np.transpose([d.time for d in xrbr_all])
    x0r, x1r, y0r, y1r = np.transpose([d.channels for d in xrbr_all])
    ADC_Vrange = 4.5
    VperC = ADC_Vrange/65536.
    x0 = x0r * VperC
    x1 = x1r * VperC
    y0 = y0r * VperC
    y1 = y1r * VperC
    lo_thold =2.1#16019.
    hi_thold = 3.3#62622.
    offset = 1

    mask_x0 = np.where((x0 < hi_thold) & (x0 > lo_thold))
    mask_x1 = np.where((x1 < hi_thold) & (x1 > lo_thold))
    mask_y0 = np.where((y0 < hi_thold) & (y0 > lo_thold))
    mask_y1 = np.where((y1 < hi_thold) & (y1 > lo_thold))
    mask_x = np.intersect1d(mask_x0,mask_x1)
    mask_y = np.intersect1d(mask_y0,mask_y1)
    pass_mask = np.intersect1d(mask_x,mask_y)
    tvalid = times[pass_mask]
    # x0pass = (x0[pass_mask]) - offset
    # x1pass = (x1[pass_mask]) - offset
    # y0pass = (y0[pass_mask]) - offset
    # y1pass = (y1[pass_mask]) - offset
    #
    # nbins = 80
    # x =(x0pass/(x0pass+x1pass))
    # y =(y0pass/(y0pass+y1pass))
    # # ALIGNMENT CORRECTION DEVELOPED BY C. O'Brien
    # ###############
    # x_offset = 0.5006
    # y_offset = 0.5061
    # M_inv = np.array([[1.0275, -0.14678],[-0.13380, 1.0293]])
    # x_shift = x - x_offset
    # y_shift = y - y_offset
    # x = (x_shift * M_inv[0,0] + y_shift * M_inv[0,1]) + 0.5
    # y = (x_shift * M_inv[1,0] + y_shift * M_inv[1,1]) + 0.5
    # ###############
    # # THE -0.5 IS INTHERE TO SHIFT IT TO 0,0
    # # THE *7 IS A NORMALIZATION FACTOR LIKE SIEGMUND et. al. 1986
    # x = (x-0.5)*7*nbins
    # y = (y-0.5)*7*nbins

    times = times/1000
    tvalid = tvalid/1000
    intT = times.astype(int)
    intTvalid = tvalid.astype(int)
    # Rectx = -22
    # Recty = 0
    # Recth = 22
    # Rectw = 22
    # # rect = patches.Rectangle((Rectx, Recty), Rectw, Recth, linewidth=2, edgecolor='r', facecolor='none')
    # # ax.add_patch(rect)
    # Xsplotch = np.where((x > Rectx) & (x < Rectx+Rectw))
    # Ysplotch = np.where((y > Recty) & ( y< Recty+Recth))
    # Insplotch = np.intersect1d(Xsplotch,Ysplotch)
    # X_sig= (x[Insplotch])
    # Y_sig = (y[Insplotch])
    # NCounts = len(X_sig)
    # print(NCounts)
    ###############
    Count_T = []
    CountRate_T = []
    for T in range(0,len(intT)-1):
        Count_T.append([intT[T]])
        if intT[T+1] == intT[T]:
            pass
        if intT[T+1] != intT[T]:
            CountRate_T.append([intT[T],len(Count_T)])
            Count_T = []
    ###############
    Count_Tvalid = []
    CountRate_Tvalid = []
    for T in range(0,len(intTvalid)-1):
        Count_Tvalid.append([intTvalid[T]])
        if intTvalid[T+1] == intTvalid[T]:
            pass
        if intTvalid[T+1] != intTvalid[T]:
            CountRate_Tvalid.append([intTvalid[T],len(Count_Tvalid)])
            Count_Tvalid = []

    AllCounts = np.asarray(CountRate_T)
    ValidCounts = np.asarray(CountRate_Tvalid)

    # np.savetxt(filename+'CountRateAllvsValid.csv',CountRate,delimiter=',',newline='\n',header='time,DeltaEventCount,DeltaValidEventCount', fmt='%.5f')
    f, (Counts) = plt.subplots(1,1,figsize=(8,5))
    plt.title('Counts in XRBR')
    color = 'tab:red'
    Counts.set_xlabel('time (s)')
    Counts.set_ylabel('Delta Event Count', color=color)
    Counts.plot(AllCounts[:,0],AllCounts[:,1],color=color)
    Counts.tick_params(axis='y', labelcolor=color)

    Valid = Counts.twinx()  # instantiate a second axes that shares the same x-axis
    #
    color = 'tab:blue'
    Valid.set_ylabel('Valid Counts in XRBR', color=color)  # we already handled the x-label with ax1
    Valid.plot(ValidCounts[:,0], ValidCounts[:,1], color=color)
    Valid.tick_params(axis='y', labelcolor=color)

    f.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig(filename+'CountCompare.png')
    #################
    # totalcounts = len(intT)
    # totalcountsvalid = len(intTvalid)
    # duration = np.max(times) - times[0]
    # ratetotal = totalcounts/duration
    # ratevalid = totalcountsvalid/duration
    # ratesignal = NCounts/duration
    # the_data = np.array([totalcounts,totalcountsvalid,duration,ratetotal,ratevalid,ratesignal]).reshape(1,6)
    # np.savetxt(filename+'_CountRateSummary.csv',the_data,delimiter=',',newline='\n',header='totalcounts,totalvalidcounts,duration,ratetotal,ratevalid,ratesignal', fmt='%.5f')


def csvw_xrbr_hk(filename):
    xrbr_arr = []
    read_xray_hk(filename,xrbr_arr)
    npkts = len(xrbr_arr)
    csv_staging = np.zeros([npkts,8])
    for i in range(npkts):
        pkt = xrbr_arr[i]
        csv_staging[i,0] = pkt.time/1000.
        Status = pkt.channels[0]
        StatusBit = "{0:016b}".format(Status)
        if StatusBit[0] == '1': #
            MCP_xHV = 1
            if StatusBit[1] == '1':
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
        csv_staging[i,1] = MCP_xHV
        csv_staging[i,2] = MCP_xAuto
        csv_staging[i,3] = HVData
        csv_staging[i,4] = TempData
        csv_staging[i,5:8] = pkt.channels[1:4]
    np.savetxt(filename+'_hk.csv',csv_staging,delimiter=',',newline='\n',header='time,MCP_Delta_HV,MCP_Auto/Manual,HV_Setting,Temp_Data,Delta_Event_Count,Delta_Dropped_Event_Count,Delta_Lost_Event_Count', fmt='%.5f')

def csvw_xrbr_all(filename):
    xrbr_arr = []
    read_xray_all(filename,xrbr_arr)
    npkts = len(xrbr_arr)
    csv_staging = np.zeros([npkts,6])
    for i in range(npkts):
        pkt = xrbr_arr[i]
        csv_staging[i,0] = pkt.time/1000.
        csv_staging[i,1:5] = pkt.channels[:]
        csv_staging[i,5] = pkt.sync
    np.savetxt(filename+'_all.csv',csv_staging,delimiter=',',newline='\n',header='time,x0,x1,y0,y1,sync', fmt='%.5f')

def csvw_xrbr_commanded(filename):
    xrbr_arr = []
    read_xray_commanded(filename,xrbr_arr)
    npkts = len(xrbr_arr)
    csv_staging = np.zeros([npkts,6])
    for i in range(npkts):
        pkt = xrbr_arr[i]
        csv_staging[i,0] = pkt.time/1000.
        csv_staging[i,1:5] = pkt.channels[:]
        csv_staging[i,5] = pkt.sync
    np.savetxt(filename+'_commanded.csv',csv_staging,delimiter=',',newline='\n',header='time,x0,x1,y0,y1,sync', fmt='%.5f')

def csvw_xrbr_science(filename):
    xrbr_arr = []
    read_xray(filename,xrbr_arr)
    npkts = len(xrbr_arr)
    csv_staging = np.zeros([npkts,6])
    for i in range(npkts):
        pkt = xrbr_arr[i]
        csv_staging[i,0] = pkt.time/1000.
        csv_staging[i,1:5] = pkt.channels[:]
        csv_staging[i,5] = pkt.sync
    np.savetxt(filename+'_science.csv',csv_staging,delimiter=',',newline='\n',header='time,x0,x1,y0,y1,sync', fmt='%.5f')

def plot_xrfs(filename):
    xrfs_data = []
    read_xrfs(filename,xrfs_data)
    times = np.transpose([d.time for d in xrfs_data])
    x = np.transpose([d.x for d in xrfs_data])/50000.
    y = np.transpose([d.y for d in xrfs_data])/50000.
    nbins = 100
    x = (x-0.5)*7*nbins
    y = (y-0.5)*7*nbins
    lo_thold = 1.1#16019.
    hi_thold = 4.3#62622.
    offset = 1
    offsetx0 = 1#14563.
    offsetx1 = 1#14563.
    offsety0 = 1#14563.
    offsety1 = 1#14563.
    XCenterPlus = np.where(y > -1)
    XCenterMinus = np.where(y < 1)
    XMask = np.intersect1d(XCenterPlus,XCenterMinus)
    XCenter = x[XMask]

    YCenterPlus = np.where(x > -1)
    YCenterMinus = np.where(x < 1)
    YMask = np.intersect1d(YCenterPlus,YCenterMinus)
    YCenter = y[YMask]

    left, width = 0.15, 0.55
    bottom, height = 0.15, 0.55
    spacing = 0.03

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]
# GENERATE THE LINEAR SCALE PLOT
    lin_fig = plt.figure(figsize=(10, 10))

    ax = lin_fig.add_axes(rect_scatter)
    ax_histx = lin_fig.add_axes(rect_histx, sharex=ax)
    ax_histy = lin_fig.add_axes(rect_histy, sharey=ax)
    cax = lin_fig.add_axes([0.2, 0.08, 0.45, 0.01])

    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
    #['viridis', 'plasma', 'inferno', 'magma']
    binedges = np.linspace(-nbins/2,nbins/2,nbins+1)
    # binedges = np.linspace(0,nbins,nbins+1)
    h2, xedges, yedges, im= ax.hist2d(x,y,bins=binedges,cmap='inferno')
    cb = lin_fig.colorbar(im,cax=cax,orientation='horizontal')
    ax.set_xlim((-nbins/2,nbins/2))
    ax.set_ylim((-nbins/2,nbins/2))
    # ax.set_xlim(((nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    # ax.set_ylim(((nbins/2-.2*nbins),(nbins/2+.2*nbins)))
    ax.set_xlabel('X Position Bin')
    ax.set_ylabel('Y Position Bin')
    ax.set_title('2D Histogram of MCP')
    cb.set_label('Counts (total)')
    ax.axvline(0,color="r",alpha=0.5)
    ax.axhline(0,color="b",alpha=0.5)

    fmax = np.amax(h2)
    indfmax = np.where(h2 == fmax)
    hmax = fmax/2
    minmatrix = abs(h2-hmax)
    indhmax = np.where(minmatrix == np.amin(minmatrix))

    ax_histx.hist(XCenter, bins=binedges,color='b')#the X axis histogram at y = .5
    ax_histx.set_title('1D Histogram at Y = 1/2')
    ax_histx.set_ylabel('Counts (total)')
    ax_histy.hist(YCenter, bins=binedges, orientation='horizontal',color='r')
    ax_histy.set_title('1D Histogram at X = 1/2')
    ax_histy.set_xlabel('Counts (total)')
    lowstring = 'Low: '
    highstring = 'High: '
    offstring = 'Offset: '+ (str(offsetx0))+', '+ (str(offsetx1)) + ', ' + (str(offsety0)) + ', ' + (str(offsety1))
    BinNumber = '#Bins = '
    lin_fig.text(0.83, 0.9, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.87, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.85, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.83,  lowstring+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.81,  highstring+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.79,  offstring, fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.77,  BinNumber+(str(nbins)), fontsize=12, horizontalalignment='center',verticalalignment='center')

    lin_fig.savefig(filename+'_linscale.png')
    plt.close()

if __name__ == '__main__':
    name=argv[1]
    if name[0:4] == 'xrbr':
        # rate_xrbr(name)
        plot_xrbr(name)
        #countratecompare(name)
        #plot_xrbrcommanded(name)

        #csvw_xrbr_all(name)
        # csvw_xrbr_hk(name)
        #csvw_xrbr_commanded(name)
        #csvw_xrbr_science(name)
    if name[0:4] == 'xrfs':
        #rate_xrbr(name)
        #plot_xrfs(name)
        csvw_xrbr(name)
