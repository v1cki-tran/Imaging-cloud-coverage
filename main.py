from picamera2 import Picamera2
from datetime import datetime, timedelta
import serial
from gpiozero import LED
import RPi.GPIO as GPIO
import csv

# Critical variables
camera = Picamera2()
interval = datetime.now()
now = datetime.now()
intervalInSeconds = 30
duration = 8
stop_time = now + timedelta(hours=duration)

# Import function files
from cloud_detection import cloud_detection
from read_serial_data import read_serial_data
from cloud_motion import cloud_motion
from run_preview import run_preview
from capture_image import capture_image

# Open CSV file for image, cloud coverage, and timestamp
csvfile_image_cloud = open((datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data.csv'), 'a', newline='')
csv_writer_image_cloud = csv.writer(csvfile_image_cloud)

if csvfile_image_cloud.tell() == 0:
    csv_writer_image_cloud.writerow(['Timestamp', 'Image Filename', 'Cloud Coverage (%)', 'Avg Magnitude', 'Direction'])

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
run_preview(camera)

file_name = capture_image(camera)
input_image1, _, _ = cloud_detection(file_name)

if input("Type start: ").lower() == 'start':
    while now <= stop_time:
        now = datetime.now()

        # Check if the interval has passed
        if now >= interval:
            # Set next interval
            interval = now + timedelta(seconds=intervalInSeconds)

            # Read serial data and capture image
            read_serial_data(ser, pin, csv_writer_sensor)
            file_name = capture_image(camera)
            input_image2, mean_cover, image_filename = cloud_detection(file_name)
            cloud_motion(input_image1, input_image2, mean_cover, image_filename, now, csv_writer_image_cloud)

            input_image1 = input_image2
            
# Cleanup 
GPIO.cleanup() 
ser.close()
csvfile_sensor.close()
csvfile_image_cloud.close()
camera.stop()
