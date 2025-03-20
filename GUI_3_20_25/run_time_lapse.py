# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:59:31 2025

@author: Charlie
"""
import os
import cv2


def run_time_lapse(folder_path, output_path, frame_rate):
    # List all files in the given directory and sort them
    images = sorted([img for img in os.listdir(folder_path) if img.endswith(('.jpg', '.jpeg', '.JPG'))])
    if not images:
        print("No images found in the specified folder.")
        return
    
    # Read the first image to get dimensions
    first_image_path = os.path.join(folder_path, images[0])
    frame = cv2.imread(first_image_path)
    frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
    height, width, channels = frame.shape

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, frame_rate, (width, height))

    # Process each image and add it as a frame in the video
    for image_name in images:
        image_path = os.path.join(folder_path, image_name)
        frame = cv2.imread(image_path)
        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)

        if frame is None:
            print(f"Failed to load image {image_name}. Skipping it.")
            continue
        
        out.write(frame)  # Write the frame to the video

    # Release the VideoWriter object
    out.release()
    print(f"Timelapse video saved as {output_path}")


