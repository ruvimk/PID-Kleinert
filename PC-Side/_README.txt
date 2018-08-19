Project started by Ruvim Kondratyev, 
for Professor Michaela Kleinert's lab. 
November 2017 - February 2018 

Project purpose: 
PID controller for keeping a MOT happy for the Kleinert Lab. 

The most interesting/important results in this folder are: 
- pid-remote.py	-> The GUI remote for the PID controller. 
- serial 	-> A third-party library for serial port access. 
- favicon.ico	-> The icon (you can replace this) for the window. 

Current folder structure - in order of date added: 

1. tutorial-code.py			-> Ruvim found a tutorial on making windows. 
2. window-test.py 			-> Ruvim testing out how to make a two-page window. 
3. window-test-graph.py			-> Ruvim trying out graphing stuff in the window. 

The following PC-side code reads samples sent by the Arduino sketch "sketch_nov21a_data_stream_test", 
which sends one sample on every loop (): 

4. read-serial-test-.py			-> Ruvim reading serial stream from Arduino. Reads 1024 samples from serial. 
5. read-serial-test-time.py		-> Another serial read test. Trying to read samples for 2 seconds. 
6. read-serial-test-time2.py		-> Another test. Trying to read samples of 2 seconds' worth of data. 
7. com-read-test.c			-> Python reading was too slow. Wrote C code to read from serial port. Just a test. 
8. com-read.c				-> A more complete tool, except it can't read more than some hundred samples, for some reason. 

At this point, Ruvim decided it's better to just not send a data sample on every loop () 
in the Arduino code. The Python is just too slow for that (though Java and C seem to be 
fast enough). The rest of the Python code uses the "sketch_nov21a_pid_controller" sketch. 

8. window-test-arduino-animate.py	-> Reads PID state and plots it. Combines reading serial streams with the window stuff. 
9. pid-remote.py 			-> The final draft, for now, of the PID controller remote. 

Finally, these are in no particular order: 
- serial 				-> A Python package for reading/writing serial streams. 
- favicon.ico				-> An icon Ruvim made a while back (back in high school, actually). 

