#from picamera2 import Picamera2
from datetime import datetime
import os
import cv2
import numpy as np

# Critical variables
#camera = Picamera2()

def capture_image(camera, masked, mask, directory):
    folder_name = 'images_' + datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    camera.stop()
    config = camera.create_still_configuration(main={"size": (4608, 3040)})
    camera.configure(config)
    camera.start()
    # Construct the file path with the 'images' folder
    
    file_name = os.path.join(folder_name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
    if masked == False:
        camera.capture_file(file_name)
        camera.stop()
        return folder_name, file_name
    elif masked == True:
        camera_frame = camera.capture_array()
        mask = cv2.resize(mask, (4608, 3040), interpolation = cv2.INTER_AREA)
        mimg = cv2.bitwise_and(camera_frame, camera_frame, mask=mask)
        img = cv2.cvtColor(mimg, cv2.COLOR_BGR2RGB)
        img.astype(np.uint8)
        cv2.imwrite(file_name, img)
        camera.stop()
        return folder_name, file_name
