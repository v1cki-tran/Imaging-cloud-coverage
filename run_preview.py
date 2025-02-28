import time
import cv2


def run_preview(camera):
    camera.stop()
    camera_config = camera.create_preview_configuration(main={"size": (4608, 2592)})
    camera.configure(camera_config)
    camera.start()

    print("Preview started. Press any key to exit.")

    try:
        screen_width = 1280  # Adjust as needed
        screen_height = 720  # Adjust as needed

        while True:
            frame = camera.capture_array()
            
            # Resize the frame to fit the screen and maintain aspect ratio
            aspect_ratio = frame.shape[1] / frame.shape[0] 
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)

            if new_height > screen_height:  # Scale based on larger dimension
                new_height = screen_height
                new_width = int(screen_height * aspect_ratio)

            resized_frame = cv2.resize(frame, (new_width, new_height))
            resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            cv2.imshow("Camera Preview", resized_frame)  # Show resized preview

            if cv2.waitKey(1) != -1:
                break

            time.sleep(0.1)

    finally:
        cv2.destroyAllWindows()
        camera.stop()

