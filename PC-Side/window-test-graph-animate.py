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

MY_FONT = ("Times New Roman", 12); 

def getPlotXY (shift = 0): 
    x = numpy.linspace (0, 10, 1024) + shift; 
    y = numpy.sin (x); 
    return x, y; 

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
        t = time.time (); 
        if self.paused: 
            return; 
        self.draw_plots (getPlotXY (t - self.t0)); 
    def draw_plots (self, xy_data): 
        self.p1.clear (); 
        self.p1.plot (*xy_data); 
    def go_back (self, controller): 
        controller.show_frame (StartPage); 

app = FirstWindow (); 
app.mainloop (); 
