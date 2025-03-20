import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from skimage.feature import local_binary_pattern
from skimage import data, img_as_float
from skimage import exposure

def cloud_detection(file_name):

    image = cv2.imread(file_name)
    #equalize image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    if image is None:
        print(f"Error in cloud_detection: No image found")

    ycbcr_img = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    y_channel = ycbcr_img[:, :, 0]
    y_channel_eq = clahe.apply(y_channel)

    blue_channel, green_channel, red_channel = cv2.split(image)
    red_channel_eq = clahe.apply(red_channel)
    green_channel_eq = clahe.apply(green_channel)
    blue_channel_eq = clahe.apply(blue_channel)

    # Get dimensions
    height, width = y_channel.shape
    total_pixels = height * width

    # Detect sun and create sun mask
    _, sun_mask = cv2.threshold(y_channel, 250, 255, cv2.THRESH_BINARY)
    if (np.sum(sun_mask) / 255) > 100:  # Check if sun is detected
        moment = cv2.moments(sun_mask)
        if moment["m00"] != 0:
            sun_x = int(moment["m10"] / moment["m00"])
            sun_y = int(moment["m01"] / moment["m00"])
    
        sun_detection = np.zeros_like(sun_mask, dtype=np.uint8)
        size = int(height / 6)
        cv2.circle(sun_detection, (sun_x, sun_y), size, 255, -1)

        sun_pixels = np.sum(sun_mask) / 255
        useful_pixels = total_pixels - sun_pixels
 
    else:
        useful_pixels = total_pixels
        sun_detection = np.zeros_like(sun_mask, dtype=np.uint8)

    ##################################################################################

    ##################################################################################
    """Otsu Y Method"""
    otsu_thresh, _ = cv2.threshold(y_channel_eq, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adjusted_thresh = max(otsu_thresh - 39, 0)  # Lower threshold by 39 (tweak as needed)
    _, thresh = cv2.threshold(y_channel_eq, adjusted_thresh, 255, cv2.THRESH_BINARY)
    binary_image_1 = cv2.subtract(thresh, sun_detection)

    ##################################################################################

    ##################################################################################
    """GB green blue ratio"""
    gb_image = cv2.divide(green_channel_eq.astype(np.float32), blue_channel.astype(np.float32))
    _, binary_image_2 = cv2.threshold(gb_image, 0.75, 255, cv2.THRESH_BINARY) #(0.75)
    binary_image_2 = np.clip(binary_image_2 - sun_detection, 0, 255)
    #use equalize blue channel

    ##################################################################################

    ##################################################################################
    """RB red blue ratio"""

    rb_image = cv2.divide(red_channel_eq.astype(np.float32), blue_channel.astype(np.float32))
    _, binary_image_3 = cv2.threshold(rb_image, 0.68, 255, cv2.THRESH_BINARY) #(0.8 changed to 0.92)
    binary_image_3 = np.clip(binary_image_3 - sun_detection, 0, 255)
    #use equalize blue channel

    ##################################################################################

    ##################################################################################
    """Binary pattern """
    green_channel_eq = clahe.apply(green_channel)

    radius = 1
    n_points = int(8 * radius)
    lbp = local_binary_pattern(green_channel_eq, n_points, radius, method='uniform')

    # Normalize LBP to [0, 1], then scale to [0, 255]
    ldp_255 = cv2.normalize(lbp, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Make the gausinan adaptive to the image
    g1 = int(width/45)
    if g1 % 2 == 0:
        g1 = g1 + 1

    blurred = cv2.GaussianBlur(ldp_255, (g1, g1), 0) 

    # Apply thresholding
    _, binary_image_4 = cv2.threshold(blurred, 135, 255, cv2.THRESH_BINARY) #(150, 255)
    binary_image_4 = np.clip(binary_image_4 - sun_detection, 0, 255)

    ##################################################################################

    ##################################################################################
    # Count the number of non-zero pixels (cloud pixels)
    agreement_threshold = 3  # We need at least 3 masks to agree
    combined_agree_mask = np.where(((binary_image_1 / 255) + (binary_image_2 / 255) + (binary_image_3 / 255) + (binary_image_4 / 255)) >= agreement_threshold, 255, 0).astype(np.uint8)
    cloud_pixels = np.sum(combined_agree_mask)/255
    percent_cover = round((cloud_pixels / useful_pixels) * 100, 2) if useful_pixels > 0 else 0

    '''
    if useful_pixels > 0:
        mean = round((25 / (255.0 * useful_pixels)) * (np.sum(binary_image_1) + np.sum(binary_image_2) + np.sum(binary_image_3) + np.sum(binary_image_4)), 2)
    else:
        mean = 0
    '''
    return combined_agree_mask, percent_cover, file_name
