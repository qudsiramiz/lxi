"""
import tkinter as tk
from tkinter.constants import *

window = tk.Tk()

frame_navigator = tk.PanedWindow(window, orient=VERTICAL)

frame_navigator.configure(background="white", width=300, height=300)
frame_navigator.pack_propagate(0)

searchbox = tk.Listbox(frame_navigator)
frame_navigator.add(searchbox)

template = tk.Listbox(frame_navigator, exportselection=True)
frame_navigator.add(template)

frame_navigator.pack(side=tk.TOP, expand=2, fill=tk.BOTH)

window.mainloop()

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from numpy import array, arange, sin, pi
import tkinter as tk

root = tk.Tk()
root_panel = tk.Frame(root)
root_panel.pack(side="bottom", fill="both", expand="yes")

btn_panel = tk.Frame(root_panel, height=35)
btn_panel.pack(side='top', fill="both", expand="yes")

#img_arr = mpimg.imread('img/pic.jpg')
#imgplot = plt.imshow(img_arr)

#here is the example of how I embed matplotlib graph in Tkinter,
#basically, I want to do the same with the image (imgplot)
f = Figure()
a = f.add_subplot(111)
t = arange(0.0, 3.0, 0.01)
s = sin(2*pi*t)
a.plot(t, s)

canvas = FigureCanvasTkAgg(f, master=root)
#canvas.show()
canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
canvas._tkcanvas.pack(side="top", fill="both", expand=1)

root.mainloop()


from tkinter import *
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageTk, Image

def generate_plot():
    rate = float(entry_1.get())
    years_saving = int(entry_2.get())
    initial_savings = float(entry_3.get())
    yearly_contribution = float(entry_4.get())

    model = pd.DataFrame({'time': range(years_saving)})
    model['simple_exp'] = [initial_savings*rate**year for year in model['time']]
    model['yearly_invest'] = model['simple_exp'] + [yearly_contribution*(rate**year - 1)/(rate-1) for year in model['time']]

    final = model['yearly_invest'].sort_values(ascending= False).iloc[0]

    label_5 = Label(frame, text=f"You would have saved INR {final} by retirement")
    label_5.grid(row=0, column=0)

    plt.plot(model['time'], model['yearly_invest'])
    plt.title('Retirement Savings')
    plt.xlabel('Time in Years)')
    plt.ylabel('INR (Lacs)')
    plt.savefig('plot.png')

    load = Image.open('plot.png')
    render = ImageTk.PhotoImage(load)
    img = Label(frame, image = render)
    img.image = render
    img.grid(row=1, column=0)   
    # my_label = Label(frame, image = my_img)
    # my_label.grid(row=1, column=0)

    # img = ImageTk.PhotoImage(Image.open('plot.png'))
    # img_label = Label(frame, image = img)
    # img_label.grid(row=1, column=0)

root = Tk()

label_1 = Label(root, text = 'INTEREST RATE(%)')
label_2 = Label(root, text = 'NUMBER OF YEARS IN SAVINGS')
label_3 = Label(root, text = 'INITIAL CORPUS (INR LACS)')
label_4 = Label(root, text = 'YEARLY CONTRIBUTION (INR LACS')
frame = Frame(root, width=300, height=300)
button = Button(root, text="GENERATE PLOT", command = generate_plot, padx = 5, pady=5)

entry_1 = Entry(root)
entry_2 = Entry(root)
entry_3 = Entry(root)
entry_4 = Entry(root)

label_1.grid(row=0, column=0, pady=5, padx=5)
entry_1.grid(row=0, column=1, pady=5, padx=5)

label_2.grid(row=1, column=0, pady=5, padx=5)
entry_2.grid(row=1, column=1, pady=5, padx=5)

label_3.grid(row=2, column=0, pady=5, padx=5)
entry_3.grid(row=2, column=1, pady=5, padx=5)

label_4.grid(row=3, column=0, pady=5, padx=5)
entry_4.grid(row=3, column=1, pady=5, padx=5)

button.grid(row=4,column=0, columnspan=2, pady=20, padx=5)

frame.grid(row=5, column=0, columnspan = 2, padx = 5, pady = 5)

root.mainloop()


from tkinter import *
from tkinter import font

root = Tk()
root.title('Font Families')
fonts=list(font.families())
fonts.sort()

def populate(frame):
    '''Put in the fonts'''
    listnumber = 1
    for item in fonts:
        label = "listlabel" + str(listnumber)
        label = Label(frame,text=item,font=(item, 16)).pack()
        listnumber += 1

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas = Canvas(root, borderwidth=0, background="#ffffff")
frame = Frame(canvas, background="#ffffff")
vsb = Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)

vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4,4), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

populate(frame)

root.mainloop()

"""

import tkinter as tk
import platform

# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")



# ********************************
# Example usage of the above class
# ********************************

class Example(tk.Frame):
    def __init__(self, root):

        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        
        # Now add some controls to the scrollframe. 
        # NOTE: the child controls are added to the view port (scrollFrame.viewPort, NOT scrollframe itself)
        for row in range(100):
            a = row
            tk.Label(self.scrollFrame.viewPort, text="%s" % row, width=3, borderwidth="1", 
                     relief="solid").grid(row=row, column=0)
            t="this is the second column for row %s" %row
            tk.Button(self.scrollFrame.viewPort, text=t, command=lambda x=a: self.printMsg("Hello " + str(x))).grid(row=row, column=1)

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)
    
    def printMsg(self, msg):
        print(msg)

if __name__ == "__main__":
    root=tk.Tk()
    Example(root).pack(side="top", fill="both", expand=True)
    root.mainloop()