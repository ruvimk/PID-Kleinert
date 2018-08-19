#define IN_PIN_1 14 
#define IN_PIN_2 15 
#define OUT_PIN_CV A21 

#define MAX_VOLTS 3.3 

// Parameters: 

float pid_param_p = 0.1f; // PID proportinal factor. 
float pid_param_i = 0.8f; // PID integral factor. 
float pid_param_d = 0.1f; // PID derivative factor. 

float pid_param_sp = 0.5f; // PID setpoint, which we want the voltage difference to approach. 

float inp_param_v1_weight = +1; 
float inp_param_v2_weight = -1; 

float result_map_param_offset = 0; 
float result_map_param_scale = 1; 

// State that needs to be modifiable from the global scope: 
float pidIntegral = 0; // For keeping track of the integral term, I. 

/* computeControlFunction (): Performs the PID algorithm on the difference between two input voltages. 
 *  
 *  It uses the global variables pid_param_* as parameters. 
 */
float computeControlFunction (float voltage1, float voltage2) { 
  // The static variables are basically global variables private to this function, so we use them to keep track of the PID state: 
  static float prevTime = getCurrentTime (); // For calculating dt. 
  static float prevResult = 0; // If dt is 0 (not enough time passed to calculate I and D terms), then we need this to return whatever result we had previously from when we *could* calculate I and D. 
  static float pidPrevE = 0; // For calculating the derivative term, D. 
  // Important variables: time, time-step, and our previous answer in case the time-step isn't large enough to calculate anything now: 
  float t = getCurrentTime (); 
  float dt = t - prevTime; 
  float result = prevResult; 
  // If the time-step is large enough (nonzero), calculate stuff: 
  if (dt > 0) { 
    // Calculate the Proportional, Integral, and Derivative terms: 
    float e = pid_param_sp - (inp_param_v1_weight * voltage1 + inp_param_v2_weight * voltage2); 
    pidIntegral += e * dt; 
    float P = pid_param_p * e; 
    float I = pid_param_i * pidIntegral; 
    float D = pid_param_d * (e - pidPrevE) / dt; 
    result = (P + I + D + result_map_param_offset) * result_map_param_scale; 
    pidPrevE = e; 
  } 
  prevTime = t; // For calculating the next time-step, dt. 
  return prevResult = result; // Save a copy of the result into prevResult before returning that value. 
}

/* clamp (): Clamps a value between a minimum and a maximum. 
 *  
 *  Parameters: value, v_min, v_max. 
 *  
 *  Returns 'value' if it is between v_min and v_max; 
 *  otherwise, returns v_min if value is less than v_min, 
 *  and returns v_max if value is greater than v_max. 
 */
float clamp (float value, float v_min, float v_max) { 
  return value > v_max ? v_max : (value < v_min ? v_min : value); 
}

/* readSerialFloat (): Reads a binary (4 bytes) float (single-precision 32-bit floating-point number) from the serial stream. 
 *  
 */
float readSerialFloat () { 
  float result = 0; 
  byte * buf = ((byte *) (&result)); 
  buf[0] = Serial.read (); 
  buf[1] = Serial.read (); 
  buf[2] = Serial.read (); 
  buf[3] = Serial.read (); 
  return result; 
}

/* setup (): Called at the beginning of the program to initialize things. 
 *  
 */
void setup() { 
  pinMode (IN_PIN_1, INPUT); 
  pinMode (IN_PIN_2, INPUT); 
  pinMode (OUT_PIN_CV, OUTPUT); // We will analogWrite () our control variable here. 
  Serial.begin (9600); 
  // Whenever the Arduino board starts, let's just send 4 zeros to the PC to let it know that yeah, we just got started. In case the PC needs to know that. 
  float zero = 0; 
  byte * pZero = ((byte *) (&zero)); 
  for (size_t i = 0; i < 4; i++) 
    Serial.write (pZero, sizeof (float)); 
}

/* getCurrentTime (): Returns the CPU time, in seconds. Uses Arduino's micros () to measure microseconds, and accounts for wrap-around, so that 
 *                    no getCurrentTime () call returns a reading that is less than the previous reading. In other words, if 70 minutes is the 
 *                    limit until a wrap-around occurs for micros (), then this function will return 71 at 71 minutes, rather than returning the 
 *                    1 that a simple call to micros () would do. So there is wrap-around checking. 
 */
float getCurrentTime () { 
  static float adjustT = 0; // Adjusts for wrap-around. 
  static float prevT = 0; // Previous measured time. 
  float t = float (micros ()) / 1e6f + adjustT; // The micros () gives us the CPU time, in microseconds. Wraps around back to 0 every 70 or so minutes. We convert it to seconds here. 
  if (t < prevT) { 
    // A wrap-around to 0 must have occurred. Let's make up for that by adding a wrap-around constant here ... 
    unsigned long maxVal = (unsigned long) (-1); // '-1' cast to an (unsigned) gives the maximum possible value you can represent, so it's the same as 0xFFFFFFFF.... however many Fs. 
    float additionalAdjust = (float) maxVal / 1e6f; // We convert to seconds. 
    // Now add that to 't' as well as to 'adjustT' so that future 't's are calculated correctly until the next wrap-around. 
    adjustT += additionalAdjust; 
    t += additionalAdjust; 
  } 
  return prevT = t; // For wrap-around checking for next time. 
} 

/* loop (): Called from a loop. 
 *  
 *  This function sends pin state by Serial. 
 */
void loop() { 
  static unsigned long prevLog = millis (); // Only the *first* time loop () is run, millis () will be read and assigned to prevLog. That's what a 'static' assignment is. 
  unsigned long now = millis (); // This millis () assignment will run *every* time loop () runs. That's what a normal assignment is. 
  // Read input pins: 
  float v1 = float (analogRead (IN_PIN_1)) / 1023.0 * MAX_VOLTS; // Convert to volts. 
  float v2 = float (analogRead (IN_PIN_2)) / 1023.0 * MAX_VOLTS; // Convert to volts. 
  float cv = computeControlFunction (v1, v2); // Do PID on the voltages. 
  analogWrite (OUT_PIN_CV, (int) clamp (cv / MAX_VOLTS * 255.0, 0, 255)); // Convert voltage to a value between 0 and 255 before writing it. Make sure it's between 0 and 255 with the clamp () function. 
  // Log the pin status every 20 ms ... 
  if (now - prevLog >= 20) { 
    // Get pointers to the actual raw binary byte data for the numbers we need to send: 
    byte * pv1 = (byte *) (&v1); // Gets a pointer to the number for voltage 1. 
    byte * pv2 = (byte *) (&v2); // ... voltage 2. 
    byte * pvC = (byte *) (&cv); // ... control variable. 
    float t = getCurrentTime (); 
    byte * pt = (byte *) (&t); 
    // Send the bytes over the serial connection: 
    Serial.write (pt, sizeof (float)); // Write time. 
    Serial.write (pv1, sizeof (float)); // Write value, 4 bytes, the size of a 'float'. 
    Serial.write (pv2, sizeof (float)); // Write voltage 2. 
    Serial.write (pvC, sizeof (float)); // Write control variable. 
    // Check off when we did this, so that we know when to do this log again next time ... 
    prevLog = now; 
  } 
  // Check if there is data available in the serial stream: 
  while (Serial.available () >= 10 * sizeof (float)) { 
    float data [10]; // Read 10 floats. Let's just say that each "packet" should always be 10 floats in size, just to keep things simple alignment-wise. 
    for (size_t i = 0; i < 10; i++) 
      data[i] = readSerialFloat (); 
    // Check the first float in the array, which tells us what this command or "packet" is about: 
    if (data[0] == 1) { 
      // Let "1" be the command to set parameters. Then floats data[1] through data[8] will be the parameter data. 
      pid_param_p = data[1]; 
      pid_param_i = data[2]; 
      pid_param_d = data[3]; 
      pid_param_sp = data[4]; 
      inp_param_v1_weight = data[5]; 
      inp_param_v2_weight = data[6]; 
      result_map_param_offset = data[7]; 
      result_map_param_scale = data[8]; 
      // Reset the integral sum, to avoid a mess of an integral term: 
      pidIntegral = 0; 
    }
  }
}

