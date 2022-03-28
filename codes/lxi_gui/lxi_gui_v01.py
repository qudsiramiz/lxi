import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("LXI GUI")
# Add the lxi logo
root.iconbitmap("../../figures/lxi_gui_figures/lxi_icon.ico")
root.geometry("600x600")

# Create a label widget and justify the text
my_label = tk.Label(root, text="LEXI GUI", font=(
    "Helvetica", 20), justify="center")
#my_label.pack()
my_label.grid(row=0, column=1, columnspan=4, sticky="nsew")

# Add image to frame and decrease the size of the image
#img = Image.open("../../figures/lxi_gui_figures/lxi_logo.png")
#img = img.resize((200, 200), Image.ANTIALIAS)
#img = ImageTk.PhotoImage(img)
#my_image = tk.Label(root, image=img)
#my_image.grid(row=1, column=1, columnspan=4, sticky="nsew")

# Create an input box with a label
# Add image to frame
cnt_img = Image.open("../../figures/lxi_gui_figures/cnt_fig.png")
cnt_img = cnt_img.resize((200, 100), Image.ANTIALIAS)
cnt_img = ImageTk.PhotoImage(cnt_img)
cnt_label = tk.Label(image=cnt_img)
cnt_label.grid(row=2, column=0, rowspan=3, columnspan=2)
#cnt_label = tk.Label(root, text="Counts")
#cnt_label.grid(row=6, column=0)

tmp_image = Image.open("../../figures/lxi_gui_figures/tmp_fig.png")
tmp_image = tmp_image.resize((200, 100), Image.ANTIALIAS)
tmp_image = ImageTk.PhotoImage(tmp_image)
tmp_label = tk.Label(image=tmp_image)
tmp_label.grid(row=5, column=0, rowspan=3, columnspan=2)
#tmp_label = tk.Label(root, text="Temp")
#tmp_label.grid(row=6, column=2)

vlt_image = Image.open("../../figures/lxi_gui_figures/vlt_fig.png")
vlt_image = vlt_image.resize((200, 100), Image.ANTIALIAS)
vlt_image = ImageTk.PhotoImage(vlt_image)
vlt_label = tk.Label(image=vlt_image)
vlt_label.grid(row=8, column=0, rowspan=3, columnspan=2)

# Add a blank frame to the window
#blank_frame = tk.Frame(root, width=50, height=50, borderwidth=1)
#blank_frame.grid(row=13, column=0)

# Add lxi image to spanning 4 columns and 10 rows
lxi_image = Image.open("../../figures/lxi_gui_figures/lxi_FIG.png")
lxi_image = lxi_image.resize((400, 400), Image.ANTIALIAS)
lxi_image = ImageTk.PhotoImage(lxi_image)
lxi_label = tk.Label(image=lxi_image)
lxi_label.grid(row=0, column=2, rowspan=10, columnspan=4)

# Add an input box with a label for start time
start_time = tk.Entry(root, width=30, justify="center",
                      bg="white", fg="black", borderwidth=2)
start_time.grid(row=12, column=3, columnspan=1)
start_time_label = tk.Label(root, text="Start Time", font=("Helvetica", 25))
start_time_label.grid(row=13, column=3, columnspan=1)

# Add an input box with a label for end time
end_time = tk.Entry(root, width=30, justify="center", bg="white", fg="black", borderwidth=2)
end_time.grid(row=12, column=4, columnspan=1, pady=10)
end_time_label = tk.Label(root, text="End Time", font=("Helvetica", 25))
end_time_label.grid(row=13, column=4, columnspan=1)

# Add a button to plot the data
plot_button = tk.Button(root, text="Plot", width=10, font=("Helvetica", 25),
                        command=lambda: print("Plotting..."))
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

root.mainloop()
