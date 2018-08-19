# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 14:56:04 2017

@author: Ruvim Kondratyev
"""

import serial; # For reading Arduino data. 
import struct; # For converting binary to numbers. 

import time; # For waiting, as well as possibly (in the future) telling time. 

import matplotlib.pyplot as pp; # For plotting data. 
pp.figure (); 

s = serial.Serial (); 
s.port = "COM8"; 
s.open (); 

DATA_ROW_COUNT = 2; # 2 rows: (time, value) 
DATA_CHUNK_SIZE = 4 * DATA_ROW_COUNT; # 4 = size of (float) 

ts = []; 
vs = []; 

PLOT_DATA_DURATION = 2; # How many seconds of data to gather for the plot. 

t0 = -1; 
t = 0; 

while t0 < 0 or t - t0 < PLOT_DATA_DURATION: 
    chunk = s.read (size = DATA_CHUNK_SIZE); 
    t = struct.unpack ('f', chunk[0:4]) [0]; 
    v = struct.unpack ('f', chunk[4:8]) [0]; 
    if t0 < 0: 
        t0 = t; 
    ts.append (t); 
    vs.append (v); 

s.close (); 

pp.plot (ts, vs); 
