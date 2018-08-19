# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:13:50 2018

@author: Ruvim Kondratyev
"""

# Following this tutorial: 
# https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/ 

import tkinter as tk; 
from tkinter import ttk; 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg; 
from matplotlib.figure import Figure; 

import matplotlib.animation; 
import matplotlib.pyplot; 

import numpy; 

import serial; # For reading Arduino data. 
import struct; # For converting binary to numbers. 

# Constants: 

DATA_ROW_COUNT = 4; # 4 rows: (time, input voltage 1, input voltage 2, output voltage) 
DATA_CHUNK_SIZE = 4 * DATA_ROW_COUNT; # 4 = size of (float) 

MY_FONT = ("Times New Roman", 12); 

N_SAMPLES_TO_PLOT = 256; # If nonzero, we plot only the last <this number> of samples (to speed up the animation by not plotting everything). 
CAP_VOLTS_DISPLAY = 3.3; 

# Getting default colors: https://matplotlib.org/devdocs/gallery/color/color_cycle_default.html
DEFAULT_COLORS = matplotlib.pyplot.rcParams['axes.prop_cycle'].by_key () ['color']; 

# Data: 

ts = numpy.array ([]); 
vs1 = numpy.array ([]); 
vs2 = numpy.array ([]); 
vsC = numpy.array ([]); 
t0 = 0; 

# All parameters, in order, as found in the "Parameters" section of the Arduino sketch. 
current_parameters = numpy.array ([.1, .8, .1, .5, 1, -1, 0, 1]); 
parameter_labels = ["P", "I", "D", "SP (V)", "w1", "w2", "Result Offset (V)", "Result Scale"]; 

# Open a serial stream: 
s = serial.Serial (); 
s.port = "COM8"; 
s.open (); 

# Checks if (the string) x is a float, like "1.0"; returns false for non-number things like "adgslkjlkgd", etc. 
def is_float (x): 
    try: 
        x = float (x); 
        return True; 
    except: 
        return False; 

# Closes the window, and closes the serial connection, so we can reconnect to the serial port in future app launches. 
def cleanUp (): 
    s.close (); # To prevent future 'access denied' errors on trying to open the same serial port. 
    app.destroy (); # Close the window. 

# Sends PID parameters over the serial stream to the Arduino. 
def sendParameters (parameters): 
    my_bytes = [struct.pack ('f', 1)]; # First float is a "1", indicating that it's a "set parameters" command. 
    for p in parameters: 
        if (len (my_bytes) < 10): 
            my_bytes.append (struct.pack ('f', p)); # Pack the parameter as a float. 
    while len (my_bytes) < 10: 
        my_bytes.append (struct.pack ('f', 0)); # Pad the rest with zeros, to make it total size 10. 
    for b in my_bytes: 
        if s.write (b) != 4: 
            print ("sendParameters (): Error sending bytes to the serial stream. \
                   Try resetting the Arduino and restarting this Python script. "); 
            return; 

# Reads a state data-point (pin voltages) from the serial stream with the Arduino. 
def readPoint (): 
    global ts, vs1, vs2, vsC, t0; 
    chunk = s.read (size = DATA_CHUNK_SIZE); 
    t = struct.unpack ('f', chunk[0:4]) [0]; 
    v1 = struct.unpack ('f', chunk[4:8]) [0]; 
    v2 = struct.unpack ('f', chunk[8:12]) [0]; 
    vC = struct.unpack ('f', chunk[12:16]) [0]; 
    if vC < 0: 
        vC = 0; 
    elif vC > CAP_VOLTS_DISPLAY: 
        vC = CAP_VOLTS_DISPLAY; 
    if ts.shape[0] == 0: # If this is the first point, set our t0. 
        t0 = t; 
    ts = numpy.append (ts, t - t0); 
    vs1 = numpy.append (vs1, v1); 
    vs2 = numpy.append (vs2, v2); 
    vsC = numpy.append (vsC, vC); 

# Checks if there is a state data-point is available (if enough bytes for a data-point available). 
def isPointAvailable (): 
    return s.inWaiting () >= DATA_CHUNK_SIZE; 

# Returns a tuple of (x, y), which can be given to a plot function. For 'x' it gives you time, 
    # but you choose what to use for the 'y'. If N_SAMPLES_TO_PLOT is nonzero, it'll limit 
    # how many to-plot samples it gives you. 
def getArduinoPoints (vs): 
    if N_SAMPLES_TO_PLOT > 0 and ts.shape[0] > N_SAMPLES_TO_PLOT: 
        return ts[-N_SAMPLES_TO_PLOT:-1], vs[-N_SAMPLES_TO_PLOT:-1]; 
    return ts, vs; # ts - ts[0] means make the time coordinate (t) relative to t0, time at 0. 

# The main window we open. 
class FirstWindow (tk.Tk): 
    def __init__ (self, *args, **kwargs): 
        tk.Tk.__init__ (self, *args, **kwargs); 
        
        tk.Tk.iconbitmap (self, default = "favicon.ico"); 
        tk.Tk.wm_title (self, "PID Remote"); 
        
        container = tk.Frame (self); 
        container.pack (side = "top", fill = "both", expand = True); 
        container.grid_rowconfigure (0, weight = 1); 
        container.grid_columnconfigure (0, weight = 1); 
        
        self.frames = {}; 
        
        for F in (Page_Graph,): 
            frame = self.frames[F] = F (container, self); 
            frame.grid (row=0, column=0, sticky="nsew"); 
        
        self.show_frame (Page_Graph); 
    def show_frame (self, cont): 
        self.frames[cont].tkraise (); 

# A frame that goes into the window. The frame has all the widgets in it, laid out in a grid. 
class Page_Graph (tk.Frame): 
    def __init__ (self, parent, controller): 
        global parameter_labels, current_parameters; 
        tk.Frame.__init__ (self, parent); 
        
        self.paused = False; 
        
        self.f = Figure (figsize = (5, 5), dpi = 90); 
        self.p1 = self.f.add_subplot (111); 
        
        self.canvas = FigureCanvasTkAgg (self.f, self); 
        self.canvas.show (); 
        self.canvas.get_tk_widget ().grid (row = len (current_parameters), column = 0, columnspan = 3); 
        
        self.anim = matplotlib.animation.FuncAnimation (self.f, 
                                       lambda frame, page, *other: page.animate (), 
                                       fargs = (self,), interval = 50); 
        
        me = self; 
        
        self.pauseText = tk.StringVar (); 
        pauseButton = tk.Button (self, bg = "#ddd", textvariable = self.pauseText, command = lambda: me.pause_resume ()); 
        self.pauseText.set ("PAUSE"); 
        pauseButton.grid (row = 1, column = 0); 
        
        self.updateButton = tk.Button (self, bg = "#ddd", text = "Update", command = lambda: me.resend_params ()); 
        self.updateButton.grid (row = 3, column = 0); 
        
        self.paramEntries = []; 
        for l, p, i in zip (parameter_labels, current_parameters, range (0, len (current_parameters))): 
            et = tk.StringVar (); 
            lt = tk.StringVar (); 
            label = ttk.Label (self, textvariable = lt); 
            entry = ttk.Entry (self, textvariable = et); 
            label.strVar = lt; 
            entry.strVar = et; # Our custom variable. 
            label.grid (row = i, column = 1); 
            entry.grid (row = i, column = 2); 
            lt.set (l); 
            et.set (p); 
            et.paramIndex = i; 
            # See https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified 
            # for listening to changes on an Entry. 
            et.trace ("w", lambda name, index, mode, sv = et: me.on_param_change (sv)); 
            entry.bind ("<Return>", lambda event: me.resend_params ()); # Detect <enter> key to mean a resend. 
            entry.bind ("<Escape>", lambda event: me.reset_params ()); # Detect <escape> key to mean a UI edit fields' reset. 
            self.paramEntries.append (entry); 
        
    # Called when a UI Entry (edit field) changes. 
    def on_param_change (self, et): 
        # Make the "Update" button orange or normal based on if the UI fields are different from the current Arduino controller settings. 
        if self.are_params_changed (): 
            self.updateButton.configure (bg = "orange"); 
        else: 
            self.updateButton.configure (bg = "#ddd"); 
    # Checks if UI fields have values different from Arduino controller current settings. 
    def are_params_changed (self): 
        global current_parameters; 
        for entry in self.paramEntries: 
            et = entry.strVar; 
            i = et.paramIndex; 
            x = et.get (); 
            if is_float (x) and float (x) != current_parameters[i]: 
                return True; 
        return False; 
    # Sends UI-supplied parameters to the Arduino controller. 
    def resend_params (self): 
        global current_parameters; 
        for entry in self.paramEntries: 
            et = entry.strVar; 
            i = et.paramIndex; 
            x = et.get (); 
            if is_float (x): 
                current_parameters[i] = float (x); 
            else: 
                et.set (current_parameters[i]); 
        sendParameters (current_parameters); 
        self.updateButton.configure (bg = "#ddd"); # Reset button color, so it's not orange anymore. 
    # Resets the UI parameter edit fields to the ones that are currently on the Arduino controller (last-sent parameters). 
    def reset_params (self): 
        global current_parameters; 
        for entry in self.paramEntries: 
            et = entry.strVar; 
            i = et.paramIndex; 
            et.set (current_parameters[i]); 
        self.updateButton.configure (bg = "#ddd"); 
    # Pause or resume the animation. Does not affect whether we're receiving data or not; just the animation redraw is affected. 
    def pause_resume (self): 
        self.paused = not self.paused; 
        if self.paused: 
            self.pauseText.set ("RESUME"); 
        else: 
            self.pauseText.set ("PAUSE"); 
    # Called all the time as an animation loop. 
    def animate (self): 
        # Receive data. 
        while isPointAvailable (): 
            readPoint (); 
        # Don't redraw if paused flag is true. 
        if self.paused: 
            return; 
        # Redraw: 
        self.draw_plots (); 
    # Redraws plots onto the canvas that we have. 
    def draw_plots (self): 
        self.p1.clear (); 
        self.p1.set_title ("PID Controller State"); 
        self.p1.set_xlabel ("Time (s)"); 
        self.p1.set_ylabel ("Voltage (V)"); 
        self.p1.set_ylim ([0, 4]); 
        e = current_parameters[3] - (vs1 * current_parameters[4] + vs2 * current_parameters[5]); 
        self.p1.plot (*getArduinoPoints (vs1), color = DEFAULT_COLORS[0]); 
        self.p1.plot (*getArduinoPoints (vs2), color = DEFAULT_COLORS[1]); 
        self.p1.plot (*getArduinoPoints (e), color = DEFAULT_COLORS[2]); 
        self.p1.plot (*getArduinoPoints (vsC), color = DEFAULT_COLORS[3]); 
        self.p1.legend (["In 1", "In 2", "e(t)", "CV Out"]); 

sendParameters (current_parameters); # In case the Arduino has different parameters to begin with, from a pervious run ... 

app = FirstWindow (); 
app.protocol ("WM_DELETE_WINDOW", cleanUp); # Detect when the window is closed, so we can do important clean-up. 
app.mainloop (); 

