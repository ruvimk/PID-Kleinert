Project started by Ruvim Kondratyev, 
for Professor Michaela Kleinert's lab. 
November 2017 - February 2018 

Project purpose: 
PID controller for keeping a MOT happy for the Kleinert Lab. 

This is the sketch for the embedded side of the PID controller. 

Currently, it needs a computer to send parameters to it. 
For the future, eventually we may implement EEPROM parameter 
saving, so that the sketch can read previous parameters from 
EEPROM without needing a computer at all times. That work is 
for the future though. 

The main function of the sketch is to repeat the following steps in a loop (): 
- Read voltages from two pins (pin numbers defined on lines 1 and 2 of the code). 
- Create a linear combination of the voltages. 
- Use this result as the process variable (PV) in a PID algorithm. 
- [Read about PID on Wikipedia. It takes P, I, D, and SP parameters.] 
- Take the result of the PID algorithm, and map it to an output voltage. 
- Output this voltage to a third pin (pin number on line 3 of the code). 

The pin numbers can be controlled by changing the #define macros on 
lines 1, 2, and 3 of the source code. 

The other controllable #define is on line 5 of the source code: the 
maximum voltage readable/writable for the current board. For a Teensy 3.6, 
this value is 3.3 V. 


Description of parameters: 

P, I, D are the typical PID parameters. Description can be found on Wikipedia. 

SP is the setpoint. Also on Wikipedia. 

w1 and w2 (v1_weight and v2_weight in the code) are the weights, or 
algebraic coefficients, to be used in the linear combination of the 
two input voltages. So, for a difference of the voltages, use "1" and "-1" 
for these two parameters. 

In particular, the following steps occur: 
v1 = input 1 voltage 
v2 = input 2 voltage 

Then the PID algorithm goes like: 
PV = w1 * v1 + w2 * v2 
e = SP - PV 
u = P * e + I * integral (e) + D * derivative (e) 

where P, I, D are dimensionless scalars. 

SP and PV have units of volts (V). 

The output voltage on the third pin is determined by an additional 
mapping, for maximum flexibility: 
vC = (u + offset) * scale 

where offset and scale are just linear mapping parameters. 

