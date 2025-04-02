import cv2
import numpy as np

def cloud_motion(seg_frame1, seg_frame2, percent_cover, image_filename, now, csv_writer_image_cloud, motion_mask):

    seg_frame1 = cv2.bitwise_and(seg_frame1, seg_frame1, mask=motion_mask)
    seg_frame2 = cv2.bitwise_and(seg_frame2, seg_frame2, mask=motion_mask)
    
    # Ensure binary masks (clouds = 255, background = 0)
    _, seg_frame1 = cv2.threshold(seg_frame1, 127, 255, cv2.THRESH_BINARY)
    _, seg_frame2 = cv2.threshold(seg_frame2, 127, 255, cv2.THRESH_BINARY)
    flow = cv2.calcOpticalFlowFarneback(seg_frame1, seg_frame2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Calculate magnitude and angle of flow vectors
    flow_x, flow_y = flow[..., 0], flow[..., 1]
    magnitude, angle = cv2.cartToPolar(flow_x, flow_y, angleInDegrees=True)
    cloud_mask = seg_frame1 > 0
    avg_magnitude = np.mean(magnitude[cloud_mask])
    avg_angle = np.mean(angle[cloud_mask])

    # Determine the cardinal direction (currently abaritrary numbers) 
    if 247.5 <= avg_angle < 292.5:
        direction = "North"
    elif 292.51 <= avg_angle < 337.5:
        direction = "North-East"
    elif 337.51 <= avg_angle < 22.5:
        direction = "East"
    elif 22.51 <= avg_angle < 67.5:
        direction = "South-East"
    elif 67.51 <= avg_angle < 112.5:
        direction = "South"
    elif 112.51 <= avg_angle < 157.5:
        direction = "South-West"
    elif 157.51 <= avg_angle < 202.5:
        direction = "West"
    else:
        direction = "North-West"

    _, image_name = image_filename.split("/")
    csv_writer_image_cloud.writerow([now.strftime('%Y-%m-%d %H:%M:%S'), image_name, percent_cover, avg_magnitude, direction])
