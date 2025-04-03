#from picamera2 import Picamera2
from datetime import datetime
import os
import cv2
import numpy as np

# Critical variables
#camera = Picamera2()

def capture_image(camera, directory):
    folder_name = 'images_' + datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    camera.stop()
    config = camera.create_still_configuration(main={"size": (4056, 3040)})
    camera.configure(config)
    camera.start()
    # Construct the file path with the 'images' folder
    
    file_name = os.path.join(folder_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")

    camera.capture_file(file_name)
    camera.stop()
    return folder_name, file_name
