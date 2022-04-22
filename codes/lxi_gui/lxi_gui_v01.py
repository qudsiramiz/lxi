import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage, font
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np

def open_file():
    # define a global variable for the file name
    global file_name
    file_val = filedialog.askopenfilename(initialdir = "../../data/processed_data/sci/", 
    title = "Select file", filetypes = (("csv files","*.csv"),("all files","*.*")))
    print(f"Loaded {file_val} in the data base")
    #df = pd.read_csv(file_val)

    file_name = file_val
    return file_val

def read_csv(file_val=None, t_start=None, t_end=None):
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
        file_val = file_name

    global df_slice
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
    df_slice = df.loc[t_start:t_end]

    # Find the x and y coordinates from the voltage values.
    df_slice['x_val'] = df_slice.Channel1/(df_slice.Channel1 + df_slice.Channel2)
    df_slice['y_val'] = df_slice.Channel3/(df_slice.Channel3 + df_slice.Channel4)

    return df_slice

def plot_data(file_name=None, t_start=None, t_end=None):

    # Check if type of start_time is int or float
    if file_name is None:
        file_name = file_name

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

    print(t_start, t_end)
    df_slice = read_csv(file_val=file_name, t_start=t_start, t_end=t_end)

    ms = 1  # Marker size
    # Plot the data
    fig = plt.figure(num=None, figsize=(4,12), dpi=200, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0, hspace=0)
    gs = gridspec.GridSpec(3, 1, width_ratios=[1])

    # Plot the counts data
    axs1 = plt.subplot(gs[0, 0])
    axs1.plot(df_slice.index, df_slice.Channel1, color='black', marker='.', ms=ms, linestyle='None')
    axs1.set_ylabel('Counts', fontsize=20)
    axs1.set_xlabel('Time', fontsize=20)
    axs1.set_xlim(np.nanmin(df_slice.index), np.nanmax(df_slice.index))

    # Plot the Temperature data and share the x-axis)
    axs2 = plt.subplot(gs[1, 0], sharex=axs1)
    axs2.plot(df_slice.index, df_slice.Channel2, color='black', marker='.', ms=ms, linestyle='None')
    axs2.set_ylabel('Temperature (K)', fontsize=20)
    axs2.set_xlabel('Time', fontsize=20)

    # Plot the Voltage data
    axs3 = plt.subplot(gs[2, 0], sharex=axs1)
    axs3.plot(df_slice.index, df_slice.Channel3, color='black', marker='.', ms=ms, linestyle='None')
    axs3.set_ylabel('Voltage (V)', fontsize=20)
    axs3.set_xlabel('Time', fontsize=20)

    save_file_path = "figures/"
    # Check if the save folder exists, if not then create it
    if not Path(save_file_path).exists():
        Path(save_file_path).mkdir(parents=True, exist_ok=True)

    plt.savefig(f"{save_file_path}/time_series_plot.png", dpi=300, bbox_inches='tight', pad_inches=0.05, facecolor='w', edgecolor='w', transparent=False)

    tmp_image = Image.open("figures/time_series_plot.png")
    tmp_image = tmp_image.resize((200, 100), Image.ANTIALIAS)
    tmp_image = ImageTk.PhotoImage(tmp_image)
    tmp_label = tk.Label(image=tmp_image)
    tmp_label.grid(row=5, column=0, rowspan=3, columnspan=2)


root = tk.Tk()
root.title("LEXI GUI")
# Add the lxi logo
#img = tk.PhotoImage(file="../../figures/lxi_gui_figures/lxi_icon.ico")
#root.tk.call('wm', 'iconphoto', root._w, img)
#root.iconbitmap("../../figures/lxi_gui_figures/lxi_icon")
#root.geometry("620x600")


# Create a label widget and justify the text
my_label = tk.Label(root, text="LEXI GUI", font=(
    "Helvetica", 20), justify="center")
#my_label.pack()
my_label.grid(row=0, column=1, columnspan=4, sticky="nsew")

# insert a file load button
file_load_button = tk.Button(root, text="Load File", command=open_file,
                                font=("Helvetica", 25))
file_load_button.grid(row=1, column=0, columnspan=2, pady=5)

# Display the file path in the GUI
file_path = tk.Label(root, text="", font=("Helvetica", 25))
file_path.grid(row=2, column=0, columnspan=2, pady=5)


# Add image to frame and decrease the size of the image
#img = Image.open("../../figures/lxi_gui_figures/lxi_logo.png")
#img = img.resize((200, 200), Image.ANTIALIAS)
#img = ImageTk.PhotoImage(img)
#my_image = tk.Label(root, image=img)
#my_image.grid(row=1, column=1, columnspan=4, sticky="nsew")

# Create an input box with a label
# Add image to frame
#cnt_img = Image.open("../../figures/lxi_gui_figures/cnt_fig.png")
#cnt_img = cnt_img.resize((200, 100), Image.ANTIALIAS)
#cnt_img = ImageTk.PhotoImage(cnt_img)
#cnt_label = tk.Label(image=cnt_img)
#cnt_label.grid(row=2, column=0, rowspan=3, columnspan=2)
#cnt_label = tk.Label(root, text="Counts")
#cnt_label.grid(row=6, column=0)


#vlt_image = Image.open("../../figures/lxi_gui_figures/vlt_fig.png")
#vlt_image = vlt_image.resize((200, 100), Image.ANTIALIAS)
#vlt_image = ImageTk.PhotoImage(vlt_image)
#vlt_label = tk.Label(image=vlt_image)
#vlt_label.grid(row=8, column=0, rowspan=3, columnspan=2)

tmp_image = Image.open("figures/time_series_plot.png")
tmp_image = tmp_image.resize((200, 100), Image.ANTIALIAS)
tmp_image = ImageTk.PhotoImage(tmp_image)
tmp_label = tk.Label(image=tmp_image)
tmp_label.grid(row=5, column=0, rowspan=3, columnspan=2)

# Add a blank frame to the window
#blank_frame = tk.Frame(root, width=50, height=50, borderwidth=1)
#blank_frame.grid(row=13, column=0)

# Add lxi image to spanning 4 columns and 10 rows
lxi_image = Image.open("../../figures/lxi_gui_figures/lxi_fig.png")
lxi_image = lxi_image.resize((400, 400), Image.ANTIALIAS)
lxi_image = ImageTk.PhotoImage(lxi_image)
lxi_label = tk.Label(image=lxi_image)
lxi_label.grid(row=0, column=2, rowspan=10, columnspan=4)

# Add an input box with a label for start time
start_time = tk.Entry(root, width=30, justify="center",
                      bg="white", fg="black", borderwidth=2)
start_time.insert(0, "YYYY-MM-DD HH:MM:SS")
start_time.grid(row=12, column=3, columnspan=1, pady=5, ipadx=10, ipady=10)
start_time_label = tk.Label(root, text="Start Time", font=("Helvetica", 25))
start_time_label.grid(row=13, column=3, columnspan=1)

# Add an input box with a label for end time
end_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
end_time.insert(0, "YYYY-MM-DD HH:MM:SS")
end_time.grid(row=12, column=4, columnspan=1, pady=5, ipadx=10, ipady=10)
end_time_label = tk.Label(root, text="End Time", font=("Helvetica", 25))
end_time_label.grid(row=13, column=4, columnspan=1)

# Add a button to plot the data
plot_button = tk.Button(root, text="Plot", width=10, font=("Helvetica", 25),
                        command=plot_data)
plot_button.grid(row=14, column=3, columnspan=2)
# Add a button to the window to get start time
#start_button = tk.Button(root, text="Start", command=lambda: print("Start"))
#start_button.grid(row=13, column=3, columnspan=1)

# Add a button to the window to get stop time
#stop_button = tk.Button(root, text="Stop", command=lambda: print("Stop"))
#stop_button.grid(row=13, column=4, columnspan=1)

# Add a quit button
quit_button = tk.Button(
    root, text="Quit", command=root.destroy, font=("Helvetica", 25))
quit_button.grid(row=14, column=0, columnspan=2)
# Print the value in the entry box


root.mainloop()
