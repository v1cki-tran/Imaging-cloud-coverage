#from picamera2 import Picamera2
from datetime import datetime
import os

# Critical variables
#camera = Picamera2()

def capture_image(camera):
    folder_name = 'images_' + datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Construct the file path with the 'images' folder
    camera.start()
    file_name = os.path.join(folder_name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
    camera.capture_file(file_name)
    camera.stop()
    return file_name 

#camera.stop()