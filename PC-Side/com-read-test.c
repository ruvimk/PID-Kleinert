
#include <stdio.h> 

int main (int argc, char * argv []) { 
	void * comPort = fopen ("COM8", "r"); 
	if (comPort) { 
		unsigned char buffer [8]; 
		size_t bRead = fread (buffer, 8, 1, comPort); 
		printf ("Read %d chunks from COM port. \n", bRead); 
		float t = ((float *) (buffer)) [0]; 
		float v = ((float *) (buffer)) [1]; 
		printf ("Values read: (t = %f, v = %f); \n", t, v); 
		fclose (comPort); 
	} else printf ("Could not open COM port for reading. \n"); 
} 

