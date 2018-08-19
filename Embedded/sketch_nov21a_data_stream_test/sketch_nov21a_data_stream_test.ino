
/* setup (): Called at the beginning of the program to initialize things. 
 *  
 */
void setup() { 
  pinMode (14, INPUT); 
  Serial.begin (9600); 
}

/* loop (): Called from a loop. 
 *  
 *  This function sends a float (number, 4 bytes), between 0 and 1, 
 *  of the analog reading from pin 14. 
 */
void loop() { 
  float v = float (analogRead (14)) / 1023.0; // Read and divide by 1023, the max. possible reading. 
  byte * pv = (byte *) (&v); // Gets a pointer to the number above. 
  float t = float (micros ()) / 1e6f; // Timer, in microseconds. Wraps around back to 0 every 70 or so minutes. 
  byte * pt = (byte *) (&t); 
  Serial.write (pt, 4); // Write time. 
  Serial.write (pv, 4); // Write value, 4 bytes, the size of a 'float'. 
}

