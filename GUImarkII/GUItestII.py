# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 18:28:53 2025

@author: Charlie
"""
from picamera2 import Picamera2
import tkinter as tk
from tkinter import messagebox
import numpy as np
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import cv2
import psutil
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib
import csv
from gpiozero import LED
import RPi.GPIO as GPIO
import serial



# Changes the matplot lib backend(?)
matplotlib.use('TkAgg')
# Main window

window = ttk.Window(themename='journal')
window.title('Eyez on the Skiez 2025 senior capstone')
window.geometry('1280x720')
#window.iconbitmap("icon.ico")
window.resizable(False,False)
window.bind('<Escape>', lambda event: window.quit())
###################################################
#Key variables
camera = Picamera2()
config = camera.create_preview_configuration(main={"size": (960,540)})
camera.configure(config)
camera.start()
hour=8 # Duration

intervalInSeconds = 30

points = [] # points for creating a polygon mask
mask=[[[]]]
now = datetime.now()
stop_time = now + timedelta(hours=hour)
interval = datetime.now()
# Booleans for tracking system functions
camera_running = True
masked = False
csved = False
#############################################################
#Arrows for buttons
more =Image.open("rightarrow.jpg")
less=Image.open("leftarrow.jpg")
morei=more.resize((30,30))
lessi=less.resize((30,30))
moreii=ImageTk.PhotoImage(morei)
lessii=ImageTk.PhotoImage(lessi)

######################################
# Duration functions
def morehours():
    global hour
    hour = hour+1
    duration_label.configure(text=f"Duration : {hour} hours")
    
def lesshours():
    global hour
    if hour > 1:
        hour = hour-1
    elif hour == 1:
        hour = 1
    duration_label.configure(text=f"Duration : {hour} hours")

# Interval functions
def moresecs():
    global intervalInSeconds
    intervalInSeconds = intervalInSeconds+5
    interval_label.configure(text=f"Photo taken every {intervalInSeconds} seconds")
    
def lesssecs():
    global intervalInSeconds
    if intervalInSeconds > 5:
        intervalInSeconds = intervalInSeconds-5
    elif intervalInSeconds == 5:
        intervalInSeconds = 5
    interval_label.configure(text=f"Photo taken every {intervalInSeconds} seconds")



#Camera functions
def stopcam():
    global camera_running, camera
    camera_running=False
    camera.stop()
    camera_label.pack_forget()
    camera_button.config(text='Open Camera', command=cam_function)

def cam_function():
    global camera_running, camera
    camera_running=True
    #camera.start()

    camera_button.config(text="Close camera", command=stopcam)
    camera_label.pack()
    show_frame()
        
def show_frame():
    global masked, mask, camera_running
    if camera_running == True:
        if masked==False:
            camera.start(show_preview=False)
            camera_frame = camera.capture_array()
            img = Image.fromarray(camera_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
            camera_label.after(10, show_frame)
        elif masked == True:
            camera.start(show_preview=False)
            camera_frame = camera.capture_array()
    
            camera_frame = Image.fromarray(camera_frame)
            camera_frame = np.float32(camera_frame)
            mimg = cv2.bitwise_and(camera_frame, camera_frame, mask=mask)
            img = Image.fromarray(mimg.astype(np.uint8))
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            
            camera_label.configure(image=imgtk)
            camera_label.after(10, show_frame)



#Tim's polygon code!
def onclick(event):
    """Callback function for mouse click events."""
    global points, img_copy

    # Append the clicked point to the list
    points.append((int(event.xdata), int(event.ydata)))
    print(int(event.xdata))

    # Draw a small circle at the clicked point
    cv2.circle(img_copy, (int(event.xdata), int(event.ydata)), 5, (255, 0, 0), -1)
    plt.imshow(img_copy)
    plt.draw()

def create_mask(image, polygon_points):
    """Create a mask from the polygon points."""
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(polygon_points, np.int32)], 255)
    return mask

def main():
    global img_copy, points, masked, mask
    

    # Load the image
    image = camera.capture_array()
    if image is None:
        print("Error: Could not load the image. Please check the path.")
        return

    img_copy = image.copy()  # Create a copy of the image for displaying points

    # Display the image and register the click event
    fig, ax = plt.subplots()
    ax.imshow(image)
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.title("Click points to create a polygon, then close the window.")
    plt.show(block=True)

    if len(points) < 3:
        print("Error: A polygon requires at least 3 points.")
        return

    # Create the mask
    mask = create_mask(image, points)

    # Save or display the mask
    #mask_path = 'polygon_mask.png'
    #cv2.imwrite(mask_path, mask)
    #print(f"Mask saved as {mask_path}.")

    # Optionally show the mask
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow('Mask', cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB))
    cv2.waitKey(10)
    cv2.destroyAllWindows()
    masked = True
    crop_button.config(text='Discard mask', command=destroy_mask)

def destroy_mask():
    global masked, mask
    masked=False
    mask = [[[]]]
    crop_button.config(text='Crop image', command = main)
    
    
# Image capture code!
def capture_image():
    global mask, masked, camera_running, cap
    if camera_running == True:
        folder_name = 'images_' + datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Construct the file path with the 'images' folder
        camera.start()
        file_name = os.path.join(folder_name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
        if masked == False:
            camera.capture_file(file_name)
            frame = camera.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(file_name, frame)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            test_img.imgtk = imgtk
            test_img.configure(image=imgtk)
            camera.stop()
            return (file_name)
        elif masked == True:
            __, frame = cap.read()
            mframe = cv2.bitwise_and(frame, frame, mask=mask)
            cv2.imwrite(file_name, mframe)
            camera.capture_file(file_name)
            mframe = cv2.cvtColor(mframe, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(mframe)
            imgtk = ImageTk.PhotoImage(image=img)
            test_img.imgtk = imgtk
            test_img.configure(image=imgtk)
            camera.stop()
            return (file_name)
    elif camera_running == False:
        camera_running ==True
        cap = cv2.VideoCapture(0)
        camera.start()
        
        folder_name = 'images_' + datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Construct the file path with the 'images' folder
        camera.start()
        file_name = os.path.join(folder_name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
        if masked == False:
            camera.capture_file(file_name)
            frame = camera.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite(file_name, frame)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            test_img.imgtk = imgtk
            test_img.configure(image=imgtk)
            camera.stop()
            return (file_name)
        elif masked == True:
            __, frame = cap.read()
            mframe = cv2.bitwise_and(frame, frame, mask=mask)
            cv2.imwrite(file_name, mframe)
            camera.capture_file(file_name)
            mframe = cv2.cvtColor(mframe, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(mframe)
            imgtk = ImageTk.PhotoImage(image=img)
            test_img.imgtk = imgtk
            test_img.configure(image=imgtk)
            camera.stop()
            return (file_name)

#Cloud detection code...


# Weather station functions


# Open CSV file for sensor data
def start_csvs():
    global csved, pin, ser, csv_writer_sensor
    csved = True 
    csvfile_sensor = open((datetime.now().strftime('%Y-%m-%d') + '_weather.csv'), 
                      'a', newline='')
    csv_writer_sensor = csv.writer(csvfile_sensor)

    # Open CSV file for image, cloud coverage, and timestamp
    csvfile_image_cloud = open((datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data.csv'),
                           'a', newline='')
    csv_writer_image_cloud = csv.writer(csvfile_image_cloud)

    # Add headers to the CSV files if empty
    if csvfile_sensor.tell() == 0:
        csv_writer_sensor.writerow(['Timestamp', 'Temp(C)', 'Humidity(%)', 
                                'Pressure(hPa)', 'Pressure(PSI)', 'Dew Point', 
                                'Dew Point Depression', 'Cloud Ceiling'])

    if csvfile_image_cloud.tell() == 0:
        csv_writer_image_cloud.writerow(['Timestamp', 'Image Filename', 
                                     'Cloud Coverage (%)'])

    # Initialize the serial port and GPIO
    ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
    pin = LED(17)

def read_serial_data():
    # Read data from the serial port and write to CSV
    global pin, ser, csv_writer_sensor, csved
    if csved == False:
        start_csvs()
    
    pin.on()
    value = ser.readline()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pin.off()

    # Check if we have data
    if value:
        try:
            value_in_string = value.decode('UTF-8', errors='ignore') 
        except UnicodeDecodeError as e:
            print(f"Error decoding data: {e}")
            value_in_string = "Error decoding"  
    else:
        value_in_string = "No data" 
    
    # Split the values based on the comma and space
    print("Received data:", value_in_string)
    values = value_in_string.split(", ")
    extracted_values = [timestamp]
    
    # Iterate over the values and extract the necessary data (assuming 'key: value' format)
    for value in values:
        if ': ' in value:
            try:
                key, val = value.split(": ")
                extracted_values.append(val.strip())  # Store the extracted value
            except ValueError:
                print(f"Error splitting value: {value}")
    
    print("Extracted values:", extracted_values) 

    # Check if the number of extracted values matches the expected columns
    if len(extracted_values) == 8: 
        csv_writer_sensor.writerow(extracted_values)
        serial_label.configure(text=f"Weather station data: {extracted_values}")
    else:
        print(f"Error: Incorrect number of extracted values. Expected 8, got {len(extracted_values)}.")

    


# Run Code!

def are_north():
    messagebox.askquestion("North?", "Are you pointed North?")

def Run():
    global now, interval, intervalInSeconds, stop_time, camera, camera_running
    are_north()
    camera_running==True
    camera.stop()
    config = camera.create_still_configuration(main={"size": (4608, 2592)})
    camera.configure(config)
    camera.start()
    bour = (hour*60)*(60/intervalInSeconds)
    incriment = (1/bour)*100
    percent = 0
    while now <= stop_time:
        now = datetime.now()

        # Check if the interval has passed
        if now >= interval:
            # Read serial data and capture image
            read_serial_data()
            file_name = capture_image()
            #cloud_detection(file_name)

            # Set next interval
            interval = now + timedelta(seconds=intervalInSeconds)
            percent = percent + incriment
            progress_bar.step(percent)
            window.update_idletasks()
        
#############################
# Window 
notebook=ttk.Notebook(window)

##########################
# Creating the home tab
tab1=ttk.Frame(notebook)
notebook.add(tab1, text='Home')

########################################
#Progress Bar!
progress_frame = ttk.Frame(master=tab1)
progress_bar=ttk.Progressbar(master=progress_frame, orient = 'horizontal', 
                             length = 500, mode = 'determinate')
progress_bar.pack()
progress_frame.pack()

##############################
# Duration Frame!
duration_frame = ttk.Frame(master=tab1)
duration_label = ttk.Label(master=duration_frame, text=f"Duration:{hour} hours", 
                           font='Calibri 24')
more_duration = ttk.Button(master=duration_frame, image=moreii, command=morehours)
less_duration = ttk.Button(master=duration_frame, image=lessii, command=lesshours)

less_duration.pack(side='left')
duration_label.pack(side='left', padx=10)
more_duration.pack(side='left')

duration_frame.pack(pady=10)
######################################
# Camera Frame!
camera_frame = ttk.Frame(master=tab1)
camera_button = ttk.Button(master=camera_frame, text='Open Camera', command = cam_function)
crop_button = ttk.Button(master=camera_frame, text='Crop image', command = main)
camera_label=ttk.Label(master=camera_frame)
camera_button.pack(side='right')
crop_button.pack(side='right')
camera_label.pack()

camera_frame.pack()
###################################

# Run frame!
run_frame=ttk.Frame(master=tab1)
run_button=ttk.Button(master=run_frame, text="Run", command = Run)
run_button.pack(fill='both')

run_frame.pack()
#################################

#Next Tab!


##############################
# Creating the settings tab
tab2=ttk.Frame(notebook)
notebook.add(tab2, text='Settings')
################################
# Interval frame!
interval_frame = ttk.Frame(master=tab2)
interval_label = ttk.Label(master=interval_frame, text=f"Photo taken every {intervalInSeconds} seconds", font='Calibri 24')
more_interval = ttk.Button(master=interval_frame, image=moreii, command=moresecs)
less_interval = ttk.Button(master=interval_frame, image=lessii, command=lesssecs)

less_interval.pack(side='left')
interval_label.pack(side='left', padx=10)
more_interval.pack(side='left')

interval_frame.pack(pady=10)
#################################


# Next Tab!


################################
# Creating the plots tab
tab3=ttk.Frame(notebook)
notebook.add(tab3, text='Plots')
################################
# Serial data frame!
serial_frame = ttk.Frame(master=tab3)
serial_button =ttk.Button(master=serial_frame, text='Read weather data',
                          command = read_serial_data)
serial_label = ttk.Label(master=serial_frame, text="No data yet!")
serial_label.pack()
serial_button.pack()

serial_frame.pack(side='left')
#################################
# test image frame!
test_img_frame = ttk.Frame(master=tab3)
test_img = ttk.Label(master=test_img_frame)
test_img_label = ttk.Label(master=test_img_frame, text="No image yet!")

test_img.pack()
test_img_label.pack()

test_img_frame.pack(side='right')
##################################
notebook.pack()
##################################





# Run the code!!
window.mainloop()
