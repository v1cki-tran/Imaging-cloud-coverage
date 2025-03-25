from datetime import datetime, timedelta
import serial
from gpiozero import LED
import RPi.GPIO as GPIO
import csv

# Import function files
from read_serial_data import read_serial_data

# Critical variables
interval = datetime.now()
now = datetime.now()
intervalInSeconds = 30
duration = 8
stop_time = now + timedelta(hours=duration)


# Open CSV file for sensor data
csvfile_sensor = open((datetime.now().strftime('%Y-%m-%d') + '_weather.csv'), 'a', newline='')
csv_writer_sensor = csv.writer(csvfile_sensor)

# Add headers to the CSV files if empty
if csvfile_sensor.tell() == 0:
    csv_writer_sensor.writerow(['Timestamp', 'Temp(C)', 'Humidity(%)', 'Pressure(hPa)', 'Pressure(PSI)', 'Dew Point', 'Dew Point Depression', 'Cloud Ceiling(m)'])


# Initialize the serial port and GPIO
ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
pin = LED(17)

# Main loop

if input("Type start: ").lower() == 'start':
    while now <= stop_time:
        now = datetime.now()

        # Check if the interval has passed
        if now >= interval:
            # Set next interval
            interval = now + timedelta(seconds=intervalInSeconds)

            # Read serial data and capture image
            read_serial_data(ser, pin, csv_writer_sensor)
            

# Cleanup 
GPIO.cleanup() 
ser.close()
csvfile_sensor.close()

