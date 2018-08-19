# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:07:30 2017

@author: Ruvim Kondratyev
"""

# Following this tutorial: 
# https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/ 

import tkinter as tk; 
from tkinter import ttk; 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg; 
from matplotlib.figure import Figure; 

import matplotlib.animation; 

import numpy; 
import time; 

import serial; # For reading Arduino data. 
import struct; # For converting binary to numbers. 

DATA_ROW_COUNT = 4; # 4 rows: (time, input voltage 1, input voltage 2, output voltage) 
DATA_CHUNK_SIZE = 4 * DATA_ROW_COUNT; # 4 = size of (float) 

MY_FONT = ("Times New Roman", 12); 

N_SAMPLES_TO_PLOT = 256; # If nonzero, we plot only the last <this number> of samples (to speed up the animation by not plotting everything). 
CAP_VOLTS_DISPLAY = 3.3; 

ts = numpy.array ([]); 
vs1 = numpy.array ([]); 
vs2 = numpy.array ([]); 
vsC = numpy.array ([]); 
t0 = 0; 

s = serial.Serial (); 
s.port = "COM8"; 
s.open (); 

def cleanUp (): 
    s.close (); # To prevent future 'access denied' errors on trying to open the same serial port. 
    app.destroy (); # Close the window. 

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

def isPointAvailable (): 
    return s.inWaiting () >= DATA_CHUNK_SIZE; 

def getArduinoPoints (vs): 
    if N_SAMPLES_TO_PLOT > 0 and ts.shape[0] > N_SAMPLES_TO_PLOT: 
        return ts[-N_SAMPLES_TO_PLOT:-1], vs[-N_SAMPLES_TO_PLOT:-1]; 
    return ts, vs; # ts - ts[0] means make the time coordinate (t) relative to t0, time at 0. 

class FirstWindow (tk.Tk): 
    def __init__ (self, *args, **kwargs): 
        tk.Tk.__init__ (self, *args, **kwargs); 
        
        tk.Tk.iconbitmap (self, default = "favicon.ico"); 
        tk.Tk.wm_title (self, "Test Title"); 
        
        container = tk.Frame (self); 
        container.pack (side = "top", fill = "both", expand = True); 
        container.grid_rowconfigure (0, weight = 1); 
        container.grid_columnconfigure (0, weight = 1); 
        
        self.frames = {}; 
        
        for F in (StartPage, Page2, Page3_Graph): 
            frame = self.frames[F] = F (container, self); 
            frame.grid (row=0, column=0, sticky="nsew"); 
        
        self.show_frame (StartPage); 
    def show_frame (self, cont): 
        self.frames[cont].tkraise (); 

class StartPage (tk.Frame): 
    def __init__ (self, parent, controller): 
        tk.Frame.__init__ (self, parent); 
        
        label1 = ttk.Label (self, text = "Label: ", font = MY_FONT); 
        label1.pack (pady = 10, padx = 10); 
        
        button1 = ttk.Button (self, text = "Click Me!", 
                              command = lambda: controller.show_frame (Page2)); 
        button1.pack (pady = 10, padx = 10); 
        
        button2 = ttk.Button (self, text = "Graph Test", command = lambda: controller.show_frame (Page3_Graph)); 
        button2.pack (pady = 10, padx = 10); 

class Page2 (tk.Frame): 
    def __init__ (self, parent, controller): 
        tk.Frame.__init__ (self, parent); 
        
        label1 = ttk.Label (self, text = "Second Page Label", font = MY_FONT); 
        label1.pack (pady = 10, padx = 10); 
        
        backButton = ttk.Button (self, text = "BACK", command = lambda: controller.show_frame (StartPage)); 
        backButton.pack (pady = 10, padx = 10); 

class Page3_Graph (tk.Frame): 
    def __init__ (self, parent, controller): 
        tk.Frame.__init__ (self, parent); 
        
        self.t0 = time.time (); 
        self.paused = False; 
        
        self.f = Figure (figsize = (5, 5), dpi = 90); 
        self.p1 = self.f.add_subplot (111); 
        
        self.canvas = FigureCanvasTkAgg (self.f, self); 
        self.canvas.show (); 
        self.canvas.get_tk_widget ().pack (side = tk.BOTTOM, fill = tk.BOTH, expand = True); 
        
        self.toolbar = NavigationToolbar2TkAgg (self.canvas, self); 
        self.toolbar.update (); 
        
        self.anim = matplotlib.animation.FuncAnimation (self.f, 
                                       lambda frame, page, *other: page.animate (), 
                                       fargs = (self,), interval = 50); 
        
        me = self; 
        backButton = ttk.Button (self, text = "BACK", command = lambda: me.go_back (controller)); 
        backButton.pack (pady = 10, padx = 10, side = tk.LEFT); 
        
        self.pauseText = tk.StringVar (); 
        pauseButton = ttk.Button (self, textvariable = self.pauseText, command = lambda: me.pause_resume ()); 
        self.pauseText.set ("PAUSE"); 
        pauseButton.pack (pady = 10, padx = 10, side = tk.LEFT); 
    def pause_resume (self): 
        self.paused = not self.paused; 
        if self.paused: 
            self.pauseText.set ("RESUME"); 
        else: 
            self.pauseText.set ("PAUSE"); 
    def animate (self): 
        while isPointAvailable (): 
            readPoint (); 
        if self.paused: 
            return; 
        self.draw_plots (getArduinoPoints (vs1), getArduinoPoints (vs2), getArduinoPoints (vsC)); 
    def draw_plots (self, xy_data_1, xy_data_2, xy_data_C): 
        self.p1.clear (); 
        self.p1.set_xlabel ("Time (s)"); 
        self.p1.set_ylabel ("Voltage (V)"); 
        self.p1.set_ylim ([0, 4]); 
        self.p1.plot (*xy_data_1); 
        self.p1.plot (*xy_data_2); 
        self.p1.plot (*xy_data_C); 
        self.p1.legend (["In 1", "In 2", "CV Out"]); 
    def go_back (self, controller): 
        controller.show_frame (StartPage); 

app = FirstWindow (); 
app.protocol ("WM_DELETE_WINDOW", cleanUp); # Detect when the window is closed, so we can do important clean-up. 
app.mainloop (); 

