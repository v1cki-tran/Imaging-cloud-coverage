import cv2
import numpy as np

def cloud_motion(seg_frame1, seg_frame2, percent_cover, image_filename, now, csv_writer_image_cloud):

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
    if 45 <= avg_angle < 135:
        direction = "North"
    elif 135 <= avg_angle < 225:
        direction = "West"
    elif 225 <= avg_angle < 315:
        direction = "South"
    else:
        direction = "East"

    _, image_name = image_filename.split("/")
    csv_writer_image_cloud.writerow([now.strftime('%Y-%m-%d %H:%M:%S'), image_name, percent_cover, avg_magnitude, direction])