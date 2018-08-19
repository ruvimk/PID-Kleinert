#include <stdio.h> 
#include <stdlib.h> 
#include <time.h> 

int main (int argc, char * argv []) { 
	// Print help if not enough command line arguments: 
	if (argc < 4) { 
		printf ("Usage: com-read PORT NUMBERCOUNT OUTPUT\n\n"); 
		printf ("where \n"); 
		printf ("PORT is the name of a port (e.g., COM1, COM2, COM3, etc.), \n"); 
		printf ("NUMBERCOUNT is the number of 'float' numbers to read, \n"); 
		printf ("OUTPUT is the filename where to save the data read. \n"); 
		return 0; 
	} 
	// Get the command line arguments: 
	char * comName = argv[1]; 
	size_t numberCountTotal = atoi (argv[2]); 
	char * saveName = argv[3]; 
	// Do the COM reading: 
	void * comPort = fopen (comName, "r"); 
	int errorlevel = 1; 
	if (comPort) { 
		void * outFile = fopen (saveName, "w"); 
		if (outFile) { 
			size_t bufSize = numberCountTotal < 1024 ? numberCountTotal : 1024 * sizeof (float); 
			unsigned char buffer [bufSize]; // Note: This syntax is invalid in C++, but is perfectly fine in C. 
			size_t readElems = 0; 
			size_t writtenElems = 0; 
			while (readElems < numberCountTotal) { 
				size_t needRead = numberCountTotal - readElems < bufSize / sizeof (float) ? numberCountTotal - readElems : bufSize / sizeof (float); 
				size_t bRead = fread (buffer, sizeof (float), needRead, comPort); 
				if (!bRead) { 
					// printf ("Could not read any more bytes from COM port. Quitting ... \n"); 
					// break; 
					printf ("Could not read any more bytes from COM port. Read so far: %d floats. Waiting ... \n", readElems); 
					usleep (10 * 1000); 
					continue; 
				} 
				writtenElems += fwrite (buffer, sizeof (float), bRead, outFile); 
				if (writtenElems < bRead) { 
					printf ("Problem writing to output file. Quitting ... \n"); 
					break; 
				} 
				readElems += bRead; 
			} 
			printf ("Total floats read from [%s]: %d\n", comName, readElems); 
			printf ("Total floats written to [%s]: %d\n", saveName, writtenElems); 
			printf ("Done. \n"); 
			if (writtenElems == numberCountTotal) errorlevel = 0; // No error. 
			fclose (outFile); 
		} else printf ("Could not open [%s] for writing. \n", saveName); 
		fclose (comPort); 
	} else printf ("Could not open COM port [%s] for reading. \n", comName); 
	return errorlevel; 
} 

