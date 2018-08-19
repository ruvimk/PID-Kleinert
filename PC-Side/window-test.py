# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:07:30 2017

@author: Ruvim Kondratyev
"""

# Following this tutorial: 
# https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/ 

import tkinter as tk; 
from tkinter import ttk; 

MY_FONT = ("Times New Roman", 12); 

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
        
        for F in (StartPage, Page2): 
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

class Page2 (tk.Frame): 
    def __init__ (self, parent, controller): 
        tk.Frame.__init__ (self, parent); 
        
        label1 = ttk.Label (self, text = "Second Page Label", font = MY_FONT); 
        label1.pack (pady = 10, padx = 10); 
        
        backButton = ttk.Button (self, text = "BACK", command = lambda: controller.show_frame (StartPage)); 
        backButton.pack (pady = 10, padx = 10); 
        

app = FirstWindow (); 
app.mainloop (); 
