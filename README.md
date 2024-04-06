# DCF77 Time Signal Generator

This Python script generates a DCF77 time signal, modulates it with an amplitude modulation scheme, and saves the result as a WAV file. The DCF77 signal encodes the current time and date, along with Daylight Saving Time (DST) information, into a format that can be transmitted and decoded by radio-controlled clocks.

## Requirements

To run this script, you need Python installed on your system along with the following Python libraries:

- numpy
- scipy

You can install these dependencies using pip:

```bash
pip3 install numpy scipy
```

## Usage

To generate a DCF77 time signal, run the script and follow the on-screen prompts to input the current time, date, and DST information. The script will then generate a WAV file (`dcf77_time_signal.wav`) containing the AM-modulated DCF77 signal.

```bash
python3 dcf77.py
```
