# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 18:28:53 2025

@author: Charlie G
"""
# Import libraries
from picamera2 import Picamera2
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import numpy as np
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import cv2
import psutil
from datetime import datetime, timedelta
from time import sleep
import os
import matplotlib.pyplot as plt
import matplotlib
import csv
from gpiozero import LED
import RPi.GPIO as GPIO
import serial
from threading import *
import threading
import pandas as pd
######################
# Import fuction files
from cloud_detection import cloud_detection
from read_serial_data import read_serial_data
from cloud_motion import cloud_motion
from capture_image import capture_image
from run_time_lapse import run_time_lapse




# Changes the matplot lib backend(?)
matplotlib.use('TkAgg')
# Main window

window = ttk.Window(themename='journal')
window.title('Eyez on the Skiez 2025 senior capstone')
window.geometry('1280x720')
#window.iconbitmap("Icon.xbm")
window.resizable(False,False)
window.bind('<Escape>', lambda event: window.quit())
###################################################
#Key variables
camera = Picamera2()
config = camera.create_preview_configuration(main={"size": (720,540)})
camera.configure(config)
camera.start()
hour=8 # Duration

intervalInSeconds = 30

#points = [] # points for creating a polygon mask
xax,yax,__ = camera.capture_array().shape
circle_mask = np.zeros((xax,yax), dtype=np.uint8)
center = (720//2, 540//2)
cv2.circle(circle_mask, center, 266, 255, -1)
mask=[[[]]]
interval = datetime.now()
# Booleans for tracking system functions
camera_running = True
masked = False
csved = False
cwd = os.getcwd()
fps = 24

stop_event=threading.Event()


#############################################################
#Arrows for buttons
more =Image.open("rightarrow.jpg")
less=Image.open("leftarrow.jpg")
morei=more.resize((30,30))
lessi=less.resize((30,30))
moreii=ImageTk.PhotoImage(morei)
lessii=ImageTk.PhotoImage(lessi)
############################################

# Initialize the serial port and GPIO
ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
pin = LED(17)

########################################################
# Define functions specific to GUI
######################################
# Duration functions
def morehours():
	global hour, fps
	if (hour >= 1) and (hour <12):
		hour = hour+1
		duration_label.configure(text=f"Duration : {int(hour)} hours")
	elif hour < 1:
		hour = hour+.25
		duration_label.configure(text=f"Duration : {int(hour*60)} minutes")
	elif hour >= 12:
		hour = 12
	timelapse_label.configure(text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")
    
def lesshours():
	global hour, fps
	if hour > 1:
		hour = hour-1
		duration_label.configure(text=f"Duration : {int(hour)} hours")
	elif (hour <= 1) and (hour > .25):
		hour = hour-.25
		duration_label.configure(text=f"Duration : {int(hour*60)} minutes")
	elif hour <= .25:
		hour = .25
		duration_label.configure(text=f"Duration : {int(hour*60)} minutes")
	timelapse_label.configure(text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")

# Interval functions
def moresecs():
    global intervalInSeconds, fps
    intervalInSeconds = intervalInSeconds+5
    interval_label.configure(text=f"Photo taken every {intervalInSeconds} seconds")
    timelapse_label.configure(text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")
    
def lesssecs():
    global intervalInSeconds, fps
    if intervalInSeconds > 5:
        intervalInSeconds = intervalInSeconds-5
    elif intervalInSeconds == 5:
        intervalInSeconds = 5
    interval_label.configure(text=f"Photo taken every {intervalInSeconds} seconds")
    timelapse_label.configure(text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")

def morefps():
    global fps
    fps=fps+1
    timelapse_label.configure(text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")

def lessfps():
    global fps
    if fps == 15:
        fps = 15
    else:
        fps = fps - 1
    timelapse_label.configure(text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")
        
# Change CWD
def change_directory():
    global cwd
    directory = filedialog.askdirectory()
    file_label.configure(text = f"Files saved at: {directory}")
    cwd = directory
    return directory

#Camera functions
def stopcam():
    global camera_running, camera
    camera_running=False
    camera.stop()
    camera_label.pack_forget()
    camera_button.config(text='Open Camera', command=cam_function)

def pausecam():
	global camera
	camera.stop()

def cam_function():
	global camera_running, camera
	print("enter cam_function()")
	camera_running=True
	camera.start(show_preview=False)
	
	camera_button.config(text="Close camera", command=stopcam)
	camera_label.pack()
	show_frame()
          
def show_frame():
	global masked, mask, camera_running, circle_mask
	if camera_running == True:
		if masked==True:
			real_mask = cv2.bitwise_and(mask,circle_mask)
		else:
			real_mask = circle_mask
		camera_frame = camera.capture_array()
		camera_frame = Image.fromarray(camera_frame)
		camera_frame = np.float32(camera_frame)
		mimg = cv2.bitwise_and(camera_frame, camera_frame, mask=real_mask)
		img = Image.fromarray(mimg.astype(np.uint8))
		imgtk = ImageTk.PhotoImage(image=img)
		camera_label.imgtk = imgtk
		camera_label.configure(image=imgtk)
		camera_label.after(10, show_frame)


#####################################################################

#Tim's polygon code!
def onclick(event):
    """Callback function for mouse click events."""
    global img_copy, points

    # Append the clicked point to the list
    points.append((int(event.xdata), int(event.ydata)))
    print(int(event.xdata))
    # Draw a small circle at the clicked point
    cv2.circle(img_copy, (int(event.xdata), int(event.ydata)), 5, (255, 0, 0), -1)
    plt.imshow(img_copy)
    plt.draw()

def create_mask(image, points):
    """Create a mask from the polygon points."""
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(points, np.int32)], 255)
    return mask

def main():
    global img_copy, points, masked, mask
    

    # Load the image
    image = camera.capture_array()
    if image is None:
        print("Error: Could not load the image. Please check the path.")
        return
    img_copy = image.copy()  # Create a copy of the image for displaying points
    
    points=[]

    # Display the image and register the click event
    fig, ax = plt.subplots()
    ax.imshow(image)
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.title("Click once to set new image circle diameter, then close")
    plt.show(block=True)

    if len(points) < 3:
        print("Error: A polygon requires at least 3 points.")
        return

    # Create the mask
    mask = create_mask(image, points)
    

    # Save the mask
    global mask_path
    full_mask = cv2.resize(mask, (4056,3040))
    mask_path = cwd+'/'+ datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'_polygon_mask.png'
    cv2.imwrite(mask_path, full_mask)
    print(f"Mask saved as {mask_path}.")

    masked = True
    crop_button.config(text='Discard mask', command=destroy_mask)
    

def destroy_mask():
    global masked, mask
    masked=False
    mask = [[[]]]
    crop_button.config(text='Crop image', command = main)
    
##########################################################################
# Run Code!

def are_north():
    sleep(1)
    tk.messagebox.showwarning("North?", "Are you pointed North?")

def stop_running():
	stop_event.set()
	run_button.configure(text="Run", command=threading)

def csvs(directory):
	# Open CSV file for image, cloud coverage, and timestamp
	csvfile_image_cloud = open((os.path.join(directory, datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data.csv')), 'a', newline='')
	csv_writer_image_cloud = csv.writer(csvfile_image_cloud)

	if csvfile_image_cloud.tell() == 0:
		csv_writer_image_cloud.writerow(['Timestamp', 'Image Filename', 'Cloud Coverage (%)', 'Avg Magnitude', 'Direction'])

	# Open CSV file for sensor data
	csvfile_sensor = open((datetime.now().strftime('%Y-%m-%d') + '_weather.csv'), 'a', newline='')
	csv_writer_sensor = csv.writer(csvfile_sensor)

	# Add headers to the CSV files if empty
	if csvfile_sensor.tell() == 0:
		csv_writer_sensor.writerow(['Timestamp', 'Temp(C)', 'Humidity(%)', 'Pressure(hPa)', 'Pressure(PSI)', 'Dew Point', 'Dew Point Depression', 'Cloud Ceiling(m)'])
	return csv_writer_sensor, csv_writer_image_cloud, csvfile_sensor, csvfile_image_cloud

def weather_plots(csv, directory):
	print("Started plotting weather")
	global temp, humidity, pressure1, pressure2, dewpoint, dewpointdep, cloudc # Call variables from checkboxes
	csvfile = pd.read_csv(csv) # Calls our global booleans and reads the csv
	
	plot_bools = [0] # start with a False or 0 in the list so the program doesn't plot timestamp v timestamp
	plot_bools.extend([temp.get(), humidity.get(), pressure1.get(), # Add booleans to list, use .get() to define them as 1 or 0
	pressure2.get(), dewpoint.get(), dewpointdep.get(), cloudc.get()])
	tuple(plot_bools) # Only tuples can be keys in a dictionary
	
	headings = csvfile.columns 
	plot_dict={}
	size = np.arange(0,len(headings),1,dtype=int)
	for num in size:
		plot_dict[headings[num]]=plot_bools[num] # Assemble dictionary from our booleans and their cooresponding headings
	n=0
	for cols in headings:	
		if plot_dict[cols]:
			if len(csvfile[headings[n]])<2:
				print(f"Error, {headings[n]} not found")
			else:
				plt.figure(figsize=(8,6))
				csvfile.plot(0,cols)
				plt.ylabel(cols) 
				plt.xticks(fontsize=4, rotation=25)
				plt.locator_params(axis='x', nbins=8)
				plt.title(cols)
				print(f"Plot {headings[n]} made succesfully")
								
				fig=plt.gcf() # Save out the plots
				fig.canvas.draw()
				fig_array=np.array(fig.canvas.renderer._renderer)
				fig_bgr = cv2.cvtColor(fig_array, cv2.COLOR_RGB2BGR)
				cv2.imwrite(os.path.join(directory, datetime.now().strftime('%Y-%m-%d') + '_weather'+headings[n]+'.png'),fig_bgr)  
		n+=1

def cloud_plots(csv, directory):
	print("started plotting clouds")
	global cloudcover, avgmag, direction
	if direction.get():
		plot_direction(csv, directory)
	csvfile = pd.read_csv(csv)
	plot_bools = [0,0]
	plot_bools.extend([cloudcover.get(), avgmag.get(), 0]) 
	tuple(plot_bools)
	
	headings = csvfile.columns 
	plot_dict={}
	size = np.arange(0,len(headings),1,dtype=int)
	
	for num in size:
		plot_dict[headings[num]]=plot_bools[num] # Assemble dictionary from our booleans and their cooresponding headings
	n=0
	for cols in headings:	
		if plot_dict[cols]:
			if len(csvfile[headings[n]])<2:
				print(f"Error, {headings[n]} not found")
			elif (csvfile[headings[n]])[1] == float:
				print("No way Jose! Those are strings!")
			else:
				plt.figure(figsize=(8,6))
				csvfile.plot(0,cols)
				plt.xticks(fontsize=4, rotation=25)
				plt.locator_params(axis='x', nbins=8)
				plt.title(cols)
				plt.ylabel(cols) 
				print(f"Plot {headings[n]} made succesfully")
								
				fig=plt.gcf() # Save out the plots
				fig.canvas.draw()
				fig_array=np.array(fig.canvas.renderer._renderer)
				fig_bgr = cv2.cvtColor(fig_array, cv2.COLOR_RGB2BGR)
				cv2.imwrite(os.path.join(directory, datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data'+ headings[n]+'.png'),fig_bgr) 
		n+=1

def plot_direction(csv, directory):
	global avgmag, direction
	print("we're plotting direction now!")
	csvfile = pd.read_csv(csv)
	headings = csvfile.columns
	
	x=[]
	y=[]
	u=[]
	v=[]
	
	for direc in csvfile[headings[4]]:
		if direc.lower() == 'north':
			u.append(0)
			v.append(1)
		elif direc.lower() == 'south':
			u.append(0)
			v.append(-1)
		elif direc.lower() == 'east':
			u.append(1)
			v.append(0)
		elif direc.lower() == 'west':
			u.append(-1)
			v.append(0)
	for mag in csvfile[headings[3]]:
		y.append(mag)
	
	for time in csvfile[headings[0]]:
		x.append(time)
	
	plt.figure(figsize=(8,6))
	csvfile.plot(0,3,linestyle='dashed')
	plt.quiver(x,y,u,v, angles='xy', scale_units='xy', scale=.25)
	plt.xticks(fontsize=4, rotation=25)
	plt.locator_params(axis='x', nbins=8)
	plt.title("Direction and magnitude")
	plt.ylabel('Average magnitude') 
	
	fig=plt.gcf() # Save out the plots
	fig.canvas.draw()
	fig_array=np.array(fig.canvas.renderer._renderer)
	fig_bgr = cv2.cvtColor(fig_array, cv2.COLOR_RGB2BGR)
	cv2.imwrite(os.path.join(directory, datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data'+ 'Direction'+'.png'),fig_bgr)

def Run():
	global interval, intervalInSeconds, camera, masked, mask_path, cwd, fps
	framesps = fps
	csv_writer_sensor, csv_writer_image_cloud, csvfile_sensor, csvfile_image_cloud = csvs(cwd)
	now = datetime.now()
	stop_time = now + timedelta(hours=hour)
	run_button.configure(text = "Stop system", command = stop_running)
	are_north()
	bour = (hour*60)*(60/intervalInSeconds)
	incriment = (1/bour)*100
	percent = 0
	pausecam()
	print("camera is stopped here")
	config = camera.create_still_configuration(main={"size": (4608, 2592)})
	camera.configure(config)
	print("camera configured.")
	camera.start(show_preview=False)
	print("camera started back up")
	
	__,file_name = capture_image(camera, cwd)
	input_image1, _, _ = cloud_detection(file_name, masked, mask_path)
	
	while now <= stop_time:
		now = datetime.now()

		# Check if the interval has passed
		if now >= interval:
			# Read serial data and capture image
			read_serial_data(ser, pin, csv_writer_sensor)
			folder_name, file_name = capture_image(camera, cwd)
			input_image2, mean_cover, image_filename = cloud_detection(file_name, masked, mask_path)
			cloud_motion(input_image1, input_image2, mean_cover, image_filename, now, csv_writer_image_cloud)
            
			input_image1 = input_image2

			# Set next interval
			interval = now + timedelta(seconds=intervalInSeconds)
            
			# update progressbar
			percent = percent + incriment
			progress_bar.step(incriment)
			print(f"{percent}% completed")
			window.update_idletasks()
		elif now >= stop_time:
			print("shoot finsished")
			stop_running()
		if stop_event.is_set():
			print("shoot suspended")
			break
	# Create time lapse
	csvfile_sensor.close()
	csvfile_image_cloud.close()
	
	run_time_lapse(cwd+'/'+folder_name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.mp4', fps)
	weather_plots(os.path.join(cwd, datetime.now().strftime('%Y-%m-%d') + '_weather.csv'), cwd)
	cloud_plots(os.path.join(cwd, datetime.now().strftime('%Y-%m-%d') + '_image_cloud_data.csv'), cwd)
	print("Done plotting!")
	run_button.configure(text="Run", command=threading)
	stop_event.clear()
    
def threading():
    t1=Thread(target=Run)
    t1.start()
    
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
# Run frame!
run_frame=ttk.Frame(master=tab1)
run_button=ttk.Button(master=run_frame, text="Run", command = threading)
run_button.pack(fill='both', pady=10)

run_frame.pack()
#################################
# Camera Frame!
camera_frame = ttk.Frame(master=tab1)
camera_button = ttk.Button(master=camera_frame, text='Open Camera', command = cam_function)
crop_button = ttk.Button(master=camera_frame, text='Crop image', command = main)
camera_label=ttk.Label(master=camera_frame)
camera_button.pack(side='right', padx=10)
crop_button.pack(side='right')
camera_label.pack()

camera_frame.pack()
###################################



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
# file path finder frame
file_frame = ttk.Frame(master=tab2)
file_label = ttk.Label(master = file_frame, text = f"Files saved at: {cwd}")
file_button = ttk.Button(master = file_frame, text = "Change...", command = change_directory)

file_label.pack()
file_button.pack(side='right')

file_frame.pack()
#################################
# Time lapse frame
timelapse_frame = ttk.Frame(master=tab2)
timelapse_label = ttk.Label(master = timelapse_frame, text= f"Time lapse fps:{fps} ({((hour*3600)/intervalInSeconds)/fps}s)")
more_fps = ttk.Button(master=timelapse_frame, image=moreii, command=morefps)
less_fps = ttk.Button(master=timelapse_frame, image=lessii, command=lessfps)

less_fps.pack(side='left')
timelapse_label.pack(side='left', padx=10)
more_fps.pack(side='left')

timelapse_frame.pack()
####################################
# Serial Data frame!
serial_frame = ttk.Frame(master=tab2)
serial_button =ttk.Button(master=serial_frame, text='Read weather data',
                          command = read_serial_data)
serial_label = ttk.Label(master=serial_frame, text="No data yet!")
serial_label.pack()
serial_button.pack()

serial_frame.pack(pady=10)
##################################
# Plot Options menu!
plot_menubutton=ttk.Menubutton(master=tab2, text='graphs to plot')
plot_menubutton.plot_menu = tk.Menu(master=plot_menubutton, tearoff=0)
plot_menubutton['menu'] = plot_menubutton.plot_menu

# setting all plots to save out with these booleans, there must be a nicer way and I'm got the feeling that tkinter doesn't actually run in python

# Weather variables
temp = tk.IntVar(master=window, value = 1)
humidity = tk.IntVar(master=window, value = 1)
pressure1= tk.IntVar(master=window, value = 1)
pressure2 = tk.IntVar(master=window, value = 1)
dewpoint = tk.IntVar(master=window, value = 1)
dewpointdep = tk.IntVar(master=window, value = 1)
cloudc = tk.IntVar(master=window, value = 1)

#cloud variables
cloudcover = tk.IntVar(master=window, value = 1)
avgmag = tk.IntVar(master=window, value = 1)
direction = tk.IntVar(master=window, value = 0)

plot_menubutton.plot_menu.add_checkbutton(label='Temp(C)', variable=temp)
plot_menubutton.plot_menu.add_checkbutton(label='Humidity(%)', variable=humidity)
plot_menubutton.plot_menu.add_checkbutton(label='Pressure(hPa)', variable=pressure1)
plot_menubutton.plot_menu.add_checkbutton(label='Pressure(PSI)',  variable=pressure2)
plot_menubutton.plot_menu.add_checkbutton(label='Dew point',  variable=dewpoint)
plot_menubutton.plot_menu.add_checkbutton(label='Dew point depression',  variable=dewpointdep)
plot_menubutton.plot_menu.add_checkbutton(label='Cloud ceiling(m)',  variable=cloudc)

plot_menubutton.plot_menu.add_checkbutton(label = 'Cloud cover(%)',  variable=cloudcover)
plot_menubutton.plot_menu.add_checkbutton(label = 'Average magnitude',  variable=avgmag)
plot_menubutton.plot_menu.add_checkbutton(label = 'Direction',  variable=direction)


plot_menubutton.pack()
##################################################
notebook.pack()
##################################





# Run the code!!
window.mainloop()
