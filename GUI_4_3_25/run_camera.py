from picamera2 import Picamera2
from datetime import datetime, timedelta
import csv

# Import function files
from cloud_detection import cloud_detection
from cloud_motion import cloud_motion
from run_preview import run_preview
from capture_image import capture_image

# Critical variables
camera = Picamera2()
interval = datetime.now()
now = datetime.now()
intervalInSeconds = 30
duration = 8
stop_time = now + timedelta(hours=duration)

# Open CSV file for image, cloud coverage, and timestamp
csvfile_image_cloud = open((datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data.csv'), 'a', newline='')
csv_writer_image_cloud = csv.writer(csvfile_image_cloud)

if csvfile_image_cloud.tell() == 0:
    csv_writer_image_cloud.writerow(['Timestamp', 'Image Filename', 'Cloud Coverage (%)', 'Avg Magnitude', 'Direction'])

   

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
            file_name = capture_image(camera)
            input_image2, mean_cover, image_filename = cloud_detection(file_name)
            cloud_motion(input_image1, input_image2, mean_cover, image_filename, now, csv_writer_image_cloud)

            input_image1 = input_image2
            

# Cleanup 
csvfile_image_cloud.close()
