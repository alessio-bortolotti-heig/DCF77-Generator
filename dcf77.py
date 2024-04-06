import numpy as np
from scipy.io.wavfile import write
import datetime

sampling_rate = 1024

def encode_time_to_dcf77(hour, minute, day, month, year, dst_status, dst_change):
    """
    Encode the given time, date, DST status, and DST change flag into the DCF77 format.
    
    Parameters:
    - hour: Hour (0-23)
    - minute: Minute (0-59)
    - day: Day of the month (1-31)
    - month: Month (1-12)
    - year: Year (four digits)
    - dst_status: Daylight Saving Time status (0 for standard time, 1 for DST)
    - dst_change: Flag indicating a change to/from DST is imminent (0 for no change, 1 for change within 1 hour)
    
    Returns:
    - A numpy array of 59 bits representing the encoded time and date according to DCF77 protocol.
    """
    bits = np.zeros(59, dtype=int)
    
    # Encode minutes and parity bit for minutes
    minute_bits = np.array([int(x) for x in '{:07b}'.format(minute)])
    bits[21:28] = minute_bits
    bits[28] = sum(minute_bits) % 2  # Parity (P1)

    # Encode hours and parity bit for hours
    hour_bits = np.array([int(x) for x in '{:06b}'.format(hour)])
    bits[29:35] = hour_bits
    bits[35] = sum(hour_bits) % 2  # Parity (P2)

    # Encode day of the month
    bits[36:42] = [int(x) for x in '{:06b}'.format(day)]

    # Encode day of the week
    day_of_week = datetime.date(year, month, day).weekday() + 1
    bits[42:45] = [int(x) for x in '{:03b}'.format(day_of_week)]

    # Encode month
    bits[45:50] = [int(x) for x in '{:05b}'.format(month)]

    # Encode year (last two digits)
    bits[50:58] = [int(x) for x in '{:08b}'.format(year % 100)]

    # Encode parity for date (P3)
    date_bits = np.array([bits[i] for i in range(36, 58)])
    bits[58] = sum(date_bits) % 2

    # Encode DST status and change
    bits[17] = dst_status
    bits[18] = dst_change

    return bits

def generate_am_modulated_signal(dcf77_bits, carrier_frequency=77500, sampling_rate=441000, bit_duration=1.0):
    """
    Generate an amplitude-modulated DCF77 signal with a carrier frequency of 77.5 kHz.
    
    Parameters:
    - dcf77_bits: A numpy array of 59 bits representing the encoded time and date.
    - carrier_frequency: The frequency of the carrier wave.
    - sampling_rate: The sampling rate for the generated signal.
    - bit_duration: The duration of each bit in seconds (typically 1 second).
    
    Returns:
    - A numpy array representing the generated AM signal.
    """
    # Calculate the number of samples per bit
    samples_per_bit = int(sampling_rate * bit_duration)
    # Create a time array for the entire duration of the bits
    t = np.linspace(0, 59, samples_per_bit * 59, endpoint=False)
    # Generate the carrier wave
    carrier_wave = np.sin(2 * np.pi * carrier_frequency * t)
    # Initialize the modulated signal
    modulated_signal = np.zeros_like(t)

    for i, bit in enumerate(dcf77_bits):
        start_sample = i * samples_per_bit
        if bit == 0:
            # Reduce amplitude for the first 100ms for bit 0
            end_sample = start_sample + int(0.1 * sampling_rate)
        else:
            # Reduce amplitude for the first 200ms for bit 1
            end_sample = start_sample + int(0.2 * sampling_rate)
        modulated_signal[start_sample:end_sample] = carrier_wave[start_sample:end_sample] * 0.1

    # Fill the rest of the signal with the full amplitude carrier wave
    for i in range(59):
        start_sample = i * samples_per_bit
        end_sample = (i + 1) * samples_per_bit
        modulated_signal[start_sample:end_sample] += carrier_wave[start_sample:end_sample] * 0.9

    return modulated_signal

def save_to_wav(signal, sampling_rate=441000, filename='dcf77_time_signal.wav'):
    """
    Save the generated DCF77 signal to a WAV file.
    
    Parameters:
    - signal: A numpy array representing the generated signal.
    - sampling_rate: The sampling rate for the WAV file.
    - filename: The filename for the saved WAV file.
    """
    max_val = 2**15 - 1
    signal_normalized = np.int16(signal / np.max(np.abs(signal)) * max_val)
    write(filename, sampling_rate, signal_normalized)

def input_with_validation(prompt, type_fn=int, condition_fn=lambda x: True, error_message="Invalid value"):
    while True:
        try:
            value = type_fn(input(prompt))
            if condition_fn(value):
                return value
            else:
                print(error_message)
        except ValueError:
            print(error_message)

def main():
    """
    Main function to encode a given time and date into the DCF77 format,
    generate a corresponding AM signal, and save it to a WAV file.
    """
    hour = input_with_validation("Hour (0-23): ", int, lambda x: 0 <= x <= 23, "The hour must be between 0 and 23.")
    minute = input_with_validation("Minute (0-59): ", int, lambda x: 0 <= x <= 59, "The minute must be between 0 and 59.")
    day = input_with_validation("Day (1-31): ", int, lambda x: 1 <= x <= 31, "The day must be between 1 and 31.")
    month = input_with_validation("Month (1-12): ", int, lambda x: 1 <= x <= 12, "The month must be between 1 and 12.")
    year = input_with_validation("Year: ", int, lambda x: x > 0, "The year must be a positive number.")
    dst_status = input_with_validation("DST Status (0 for standard, 1 for DST): ", int, lambda x: x in [0, 1], "The DST status must be 0 (standard) or 1 (DST).")
    dst_change = input_with_validation("DST Change (0 for no change, 1 for change within 1 hour): ", int, lambda x: x in [0, 1], "The DST change must be 0 (no change) or 1 (change within 1 hour).")

    dcf77_bits = encode_time_to_dcf77(hour, minute, day, month, year, dst_status, dst_change)
    am_signal = generate_am_modulated_signal(dcf77_bits, sampling_rate=sampling_rate)
    save_to_wav(am_signal, sampling_rate=sampling_rate)

if __name__ == "__main__":
    main()
