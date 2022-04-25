import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import PhotoImage, font
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import importlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import lxi_gui_plot_routines as plot_routines

importlib.reload(plot_routines)

sci_file_name = "/home/cephadrius/Desktop/git/lxi/data/processed_data/sci/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_qudsi.csv"
hk_file_name = "/home/cephadrius/Desktop/git/lxi/data/processed_data/hk/2022_04_21_1431_LEXI_raw_LEXI_unit_1_mcp_unit_1_eBox-1987_qudsi.csv"

def open_file_sci():
    # define a global variable for the file name
    global sci_file_name
    file_val = filedialog.askopenfilename(initialdir = "../../data/processed_data/sci/", 
    title = "Select file", filetypes = (("csv files","*.csv"),("all files","*.*")))
    print(f"Loaded {file_val} in the data base")
    #df = pd.read_csv(file_val)

    sci_file_name = file_val
    return file_val

def open_file_hk():
    # define a global variable for the file name
    global hk_file_name
    file_val = filedialog.askopenfilename(initialdir = "../../data/processed_data/hk/", 
    title = "Select file", filetypes = (("csv files","*.csv"),("all files","*.*")))
    print(f"Loaded {file_val} in the data base")
    #df = pd.read_csv(file_val)

    hk_file_name = file_val
    return file_val

def read_csv_sci(file_val=None, t_start=None, t_end=None):
    """
    Reads a csv file and returns a pandas dataframe for the selected time range along with x and
    y-coordinates.

    Parameters
    ----------
    file_val : str
        Path to the input file. Default is None.
    t_start : float
        Start time of the data. Default is None.
    t_end : float
        End time of the data. Default is None.
    """
    if file_val is None:
        file_val = sci_file_name

    global df_slice_sci
    df = pd.read_csv(file_val)

    # Replace index with timestamp
    df.set_index('TimeStamp', inplace=True)

    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_sci = df.loc[t_start:t_end]

    # Find the x and y coordinates from the voltage values.
    df_slice_sci['x_val'] = df_slice_sci.Channel1/(df_slice_sci.Channel1 + df_slice_sci.Channel2)
    df_slice_sci['y_val'] = df_slice_sci.Channel3/(df_slice_sci.Channel3 + df_slice_sci.Channel4)

    return df_slice_sci

def read_csv_hk(file_val=None, t_start=None, t_end=None):

    if file_val is None:
        file_val = hk_file_name
    
    global df_slice_hk
    df = pd.read_csv(file_val)

    # Replace index with timestamp
    df.set_index('TimeStamp', inplace=True)

    # Sort the dataframe by timestamp
    df = df.sort_index()

    if t_start is None:
        t_start = df.index.min()
    if t_end is None:
        t_end = df.index.max()

    # Select dataframe from timestamp t_start to t_end
    df_slice_hk = df.loc[t_start:t_end]

    return df_slice_hk

def plot_data(file_name_sci=None, file_name_hk=None, t_start=None, t_end=None):

    # Check if type of start_time is int or float
    if file_name_sci is None:
        file_name_sci = file_name_sci
    
    if file_name_hk is None:
        file_name_hk = file_name_hk

    # Try to convedt the start_time and end_time to float or int
    try:
        t_start = float(start_time.get())
    except:
        pass
    try:
        t_end = float(end_time.get())
    except:
        pass
    if not isinstance(t_start, (int, float)):
        t_start = None
    
    if not isinstance(t_end, (int, float)):
        t_end = None

    # Read entries from the text boxes
    try :
        x_min = float(x_min_entry.get())
    except:
        x_min = None
    try :
        x_max = float(x_max_entry.get())
    except:
        x_max = None
    try :
        y_min = float(y_min_entry.get())
    except:
        y_min = None
    try :
        y_max = float(y_max_entry.get())
    except:
        y_max = None
    try :
        bins = int(hist_bins_entry.get())
    except:
        bins = None
    try :
        cmin = int(c_min_entry.get())
    except:
        cmin = None
    try :
        density = bool(int(density_entry.get()))
    except:
        density = None

    if norm_entry.get() == "linear":
        norm = "linear"
    elif norm_entry.get() == "log":
        norm = "log"
    else:
        norm = None

    print(f"Density is {density}")

    df_slice_hk = read_csv_hk(file_val=file_name_hk, t_start=t_start, t_end=t_end)
    df_slice_sci = read_csv_sci(file_val=file_name_sci, t_start=t_start, t_end=t_end)

    # Display the time series plot
    fig1 = plot_routines.plot_time_series(df=df_slice_hk, ms=2, alpha=1)
    """
    # Resize the figure to fit the canvas in terms of pixels
    fig1_width = fig1.get_figwidth()
    fig1_height = fig1.get_figheight()
    fig1_dpi = fig1.get_dpi()
    fig1_width_px = fig1_width * fig1_dpi
    fig1_height_px = fig1_height * fig1_dpi
    fig1.set_size_inches(fig1_width * 200/fig1_width_px, fig1_height * 600/fig1_height_px)
    canvas1 = FigureCanvasTkAgg(fig1, master=root)
    canvas1.get_tk_widget().grid(row=1, column=0, rowspan=3, columnspan=2)
    canvas1._tkcanvas.grid(row=1, column=0, rowspan=3, columnspan=2)
    """
    load1 = Image.open("figures/time_series_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load1 = load1.resize((int(fig1.get_figwidth() * 100), int(fig1.get_figheight() * 75)))
    render1 = ImageTk.PhotoImage(load1)
    img1 = tk.Label(image=render1)
    img1.image = render1
    img1.grid(row=2, column=0, rowspan=5, columnspan=2, sticky="w")

    fig2 = plot_routines.plot_histogram(df=df_slice_sci, x_min=x_min, x_max=x_max, y_min=y_min,
                                        y_max=y_max, bins=bins, density=density, norm=norm)
    load2 = Image.open("figures/xy_plot.png")
    # Resize the image to fit the canvas (in pixels)
    load2 = load2.resize((int(fig2.get_figwidth() * 500/5), int(fig2.get_figheight() * 500/6)))
    render2 = ImageTk.PhotoImage(load2)
    img2 = tk.Label(image=render2)
    img2.image = render2
    img2.grid(row=2, column=3, rowspan=5, columnspan=5, sticky="e")


root = tk.Tk()
#root.rowconfigure(9, {'minsize': 30})
#root.columnconfigure(9, {'minsize': 30})
root.title("LEXI GUI")
# Add the lxi logo
#img = tk.PhotoImage(file="../../figures/lxi_gui_figures/lxi_icon.ico")
#root.tk.call('wm', 'iconphoto', root._w, img)
#root.iconbitmap("../../figures/lxi_gui_figures/lxi_icon.ico")
root.geometry("900x800")
root.resizable(True, True)

# Create a label widget and justify the text
#my_label = tk.Label(root, text="LEXI GUI", font=(
#    "Helvetica", 20), justify="center")
#my_label.pack()
#my_label.grid(row=0, column=1, columnspan=4, sticky="nsew")

# Choose a font style for GUI
font_style = font.Font(family="Helvetica", size=12)
font_style_box = font.Font(family="Helvetica", size=12, weight="bold")
font_style_big = font.Font(family="Helvetica", size=25)

# insert a file load button
sci_file_load_button = tk.Button(root, text="Load Science File", command=open_file_sci,
                                font=font_style)
sci_file_load_button.grid(row=0, column=0, columnspan=2, pady=0, sticky="w")

hk_file_load_button = tk.Button(root, text="Load HK File", command=open_file_hk,
                                font=font_style)
hk_file_load_button.grid(row=0, column=2, columnspan=2, pady=0, sticky="w")

# Add an input box with a label for start time
start_time = tk.Entry(root, width=30, justify="center",
                      bg="white", fg="black", borderwidth=2)
start_time.insert(0, "YYYY-MM-DD HH:MM:SS")
start_time.grid(row=12, column=3, columnspan=1, pady=5, ipadx=10, ipady=10)
start_time_label = tk.Label(root, text="Start Time", font=font_style)
start_time_label.grid(row=13, column=3, columnspan=1)

# Add an input box with a label for end time
end_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
end_time.insert(0, "YYYY-MM-DD HH:MM:SS")
end_time.grid(row=12, column=4, columnspan=1, pady=5, ipadx=10, ipady=10)
end_time_label = tk.Label(root, text="End Time", font=font_style)
end_time_label.grid(row=13, column=4, columnspan=1)

# Add a button to plot the data
plot_button = tk.Button(root, text="Plot", width=10, font=font_style_big, command=plot_data)
plot_button.grid(row=14, column=3, columnspan=2)
# Add a button to the window to get start time
#start_button = tk.Button(root, text="Start", command=lambda: print("Start"))
#start_button.grid(row=13, column=3, columnspan=1)

# Add buttons for plotting values
x_min_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
x_min_entry.insert(0, 0)
x_min_entry.grid(row=1, column=9, columnspan=1, sticky="n")
x_min_label = tk.Label(root, text="X Min", font=font_style_box)
x_min_label.grid(row=1, column=10, columnspan=1, sticky="n")

x_max_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
x_max_entry.insert(0, "X Maximum")
x_max_entry.grid(row=2, column=9, columnspan=1, sticky="n")
x_max_label = tk.Label(root, text="X Max", font=font_style_box)
x_max_label.grid(row=2, column=10, columnspan=1, sticky="n")

y_min_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
y_min_entry.insert(0, "Y Minimum")
y_min_entry.grid(row=3, column=9, columnspan=1, sticky="n")
y_min_label = tk.Label(root, text="Y Min", font=font_style_box)
y_min_label.grid(row=3, column=10, columnspan=1, sticky="n")

y_max_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
y_max_entry.insert(0, "Y Maximum")
y_max_entry.grid(row=4, column=9, columnspan=1, sticky="n")
y_max_label = tk.Label(root, text="Y Max", font=font_style_box)
y_max_label.grid(row=4, column=10, columnspan=1, sticky="n")

hist_bins_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
hist_bins_entry.insert(0, "Bins")
hist_bins_entry.grid(row=5, column=9, columnspan=1, sticky="n")
hist_bins_label = tk.Label(root, text="Bins", font=font_style_box)
hist_bins_label.grid(row=5, column=10, columnspan=1, sticky="n")

c_min_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
c_min_entry.insert(0, "Colorbar Mininimum")
c_min_entry.grid(row=6, column=9, columnspan=1, sticky="n")
c_min_label = tk.Label(root, text="C Min", font=font_style_box)
c_min_label.grid(row=6, column=10, columnspan=1, sticky="n")

c_max_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
c_max_entry.insert(0, "Colorbar Maximum")
c_max_entry.grid(row=7, column=9, columnspan=1, sticky="n")
c_max_label = tk.Label(root, text="C Max", font=font_style_box)
c_max_label.grid(row=7, column=10, columnspan=1, sticky="n")

density_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
density_entry.insert(0, "Density")
density_entry.grid(row=8, column=9, columnspan=1, sticky="n")
density_label = tk.Label(root, text="Density", font=font_style_box)
density_label.grid(row=8, column=10, columnspan=1, sticky="n")

norm_entry = tk.Entry(root, width=10, justify="center", bg="white", fg="black", borderwidth=2)
norm_entry.insert(0, "Norm style")
norm_entry.grid(row=9, column=9, columnspan=1, sticky="n")
norm_label = tk.Label(root, text="Norm", font=font_style_box)
norm_label.grid(row=9, column=10, columnspan=1, sticky="n")

# Add a quit button
quit_button = tk.Button(
    root, text="Quit", command=root.destroy, font=font_style_big)
quit_button.grid(row=14, column=0, columnspan=2)
# Print the value in the entry box


root.mainloop()
