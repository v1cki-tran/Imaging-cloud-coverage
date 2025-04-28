# Imaging cloud coverage with low-cost ground-based photography
## Table of Contents
- Introduction
  - [Operating Conditions](#operating-conditions)
  - [How to use](#how-to-use)
- [Software](#software)
  - [Cloud Detection](#cloud-detection-algorithm)
  - [Cloud Movement](#cloud-movement)
- [Hardware](#hardware)
  - [Camera and Lens](#camera-and-lens)
  - [Housing](#housing)
  - [Weather Station](#weather-station)
  - [Hardware Links](#hardware-links)
- [Examples](#examples)
- Credits
  
# Introduction
This project focuses on designing and developing a cloud imaging system that captures whole-sky photographs, computes cloud coverage, monitors cloud movement, and outputs both graphical and time-lapse data. This is a final capstone project for the class of 2025 Photographic Sciences at the Rochester Institute of Technology. This project was purpose built for DIRS Group at RIT. Since 1999, the Rochester Institute of Technology (RIT) has provided thermal infrared (TIR) reference data for calibrating Landsat thermal sensors and plays a key role in validating their corresponding products.​ Landsat 9 launched by NASA in 2021 in order to gather data about the Earths surface. Landsat reads groud temperature using IR imaging. Clouds block the readings and affect the data. This project will be used along with ground-based instrumentation to measure surface temperature and cloud coverage. This will provide critical cloud coverage information for validating ground temperature readings and Landsat’s thermal imaging products.

## Operating Conditions
The user is required to have a USB flash drive of at least 128 GB for the system to store the data. 

The ideal environment for the system is a flat, open area with full access to the sky, with little to no buildings and trees. 

The system can NOT operate in the following conditions:
- Nighttime 
- Heavy rain
- Snow
- Temperatures under 32° F 
- Temperatures over 95° F


## How to use
The system is simple to use and quick to set up. Our system features a touch screen on the outside of the box where the whole system can be controlled using a GUI. 
The GUI will automatically start when the system is powered on. The user will then perform the following steps:
-	Set up the system facing north
-	Open the image preview and determine if image is good
-	Select settings for system to run by selecting:
  - Duration of image capture
  - Interval images are taken
  - The data that is graphed
  - The location the data will be saved to
-	The user will be prompted to face the system north if they haven’t done so already
-	The system will then run. 
The outputs will then be saved to the selected folder as the system runs and when it is finished.  

# Software
The system runs from a Gui.
When running from the GUI the flow of the software runs in the flow that is shown below.

<img width="600" alt="Flowchart" src="https://github.com/user-attachments/assets/c4ab52ce-1054-4e98-968a-c61c15ead67e" />

The GUI pulls from multiple python files which each run part of the system. The included files are:
-	GUI_4_3_25.py
-	capture_image.py
-	cloud_detection.py
-	cloud_motion.py
-	read_serial_data.py
-	run_camera.py
-	run_path_selection.py
-	run_time_lapse.py
-	run_weather.py

### Cloud Detection Algorithm
Cloud detection algorithms use different methods to select the pixels were clouds are in an image. There are multiple ways to detect clouds in an image. Different thresholding techniques, neural network models, channel comparison. Our approach used different thresholding techniques combined in order to segment out the clouds. 
The methods used are as follows:
-	Otsu of Y channel - Using a binary and otsu method on the Y channel 
-	Green and Blue - Equalized channels and divided green by blue
-	Red and Blue - Equalized channels and divided red by blue
-	Red and Green - Equalized channels and divided red by green
-	Binary Pattern - Binary pattern of the green channel with a binary threshold

The methods output a binary mask of the clouds where white is a cloud and black is not. An example of the selection of clouds by each method can be seen below.

 <img width="650" alt="image" src="https://github.com/user-attachments/assets/b716db4a-aeba-48e6-ada7-cb52683d51bc" />
 
The binary images are then combined into a final segmentation. If the pixel is a cloud pixel in 4 of the segmentation methods, it is selected as a cloud in the final image. This requirement for 4 of the 5 images to agree prevents false positives. That number of agreeing methods can be changed in the code. 
Another way that our code provides more accurate data is by weighting the segmentation for the cloud coverage percentage. The cloud segmentation is weighted from the center of the image to the outsides. The reason being is because of perspective. The clouds will bunch up in the outer view of the image meaning there may appear to be a high density but may be lower. For that reason the clouds on the edge count less towards the percentage.
An example of the combined images and the weighted image used for percentage is displayed below.

<img width="650" alt="image" src="https://github.com/user-attachments/assets/9de1c915-b1d7-453a-990c-a962e03e149a" />

All of this is encompassed in the cloud_detection.py file.


### Cloud Movement 
The movement of the clouds is done in a simple but effective way. The motion of the clouds is compared between two consecutive images using optical flow. The optical flow of the images is then averaged. That direction of movement along with the fact that the system is set up to face north by the user allows us to give a general direction. The method is simple but works for our use.

Below is an visual representation of what we are doing:

<img src="https://github.com/user-attachments/assets/22691841-8136-4aea-8bf0-245a8269ea83" width="650"/>

# Hardware
Our goal was to create a low cost system that anyone could make themselves. Our system requires only $___ in parts to build.
The selection of our components was chosen with not only cost but ease of use and amount of resouirces on the products. 
A [full list of links](#hardware-links) can be found at the end of this section.

<img src="https://github.com/user-attachments/assets/46cc2b84-4ffa-40f8-ba6f-fffd5ed3a060" width="650"/>

### Camera and Lens
The camera and lens selection had the following criteria:
-	The camera needed to be able to connect to our processor
-	The lens and camera needed to give as wide of a view of the sky as possible

The decision to choose the [Raspberry pi HQ sensor](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/) which features:
-	IMX477 sensor
-	4056 × 3040 pixel resolution
-	6.287mm × 4.712 mm, (7.9mm diagonal) sensor
-	1.55 μm × 1.55 μm pixel size
-	1/2.3” optical format
-	Built in IR cut filter
-	M12 mount

The lens required in the system is the [Eda Technology 1.55mm lens](https://edatec.cn/storage/file/ED-LENS-M12-230155-12%20Datasheet.pdf)
-	Product number: ED-LENS-M12-230155-12
-	1.55mm effective focal length
-	M12 mount
-	f/2.0
-	1/2.3” optical format
-	195 degree fov with 1/2.3” sensor

The lens was selected has an image circle around 5mm which only just is larger than the height of the selected sensor. That is required for us capture a wide field of view in order to see clouds in all directions.

### Housing
In order to save costs our housing was designed and created using CAD software and 3D printed. The housing has two main parts: the body and the lid. 
There also handles, a lens cover, an optional optical window, and a sun shield for the screen. 


<img src="https://github.com/user-attachments/assets/f9ef8104-6e44-4b39-ba2f-47c65724b655" width="600"/>

An AutoCAD .dwg file is provided of the CAD design in the github. 

### Weather Station
The weather station uses the following components:
-	Arduino Nano
-	TXB0104 Level Shifter
-	SHT-30 Temperature-Humidity Sensor
-	MPRLS Pressure Sensor
The Arduino Nano seamlessly connects to the Raspberry Pi and as the Pi calls is the Nano sends the weather information from the sensors to the Pi. The housing has ports in the rear where the sensors are exposed to the outside air for more accurate data. 

### Hardware links
Camera Link: https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/ 
https://www.digikey.com/en/products/detail/raspberry-pi/SC0870/17278640 
Lens Link: https://edatec.cn/storage/file/ED-LENS-M12-230155-12%20Datasheet.pdf 
https://www.digikey.com/en/products/detail/edatec/ED-LENS-M12-230155-12/20195789 

# Examples

# Credits

