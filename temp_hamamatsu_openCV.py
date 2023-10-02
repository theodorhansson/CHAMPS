#%%

import hamamatsu_sdk  # Import the Hamamatsu SDK module

# Initialize the camera
camera = hamamatsu_sdk.Camera()

# Configure camera settings (e.g., exposure, frame rate, etc.)
camera.set_exposure_time(10)  # Set exposure time to 10 ms
camera.set_frame_rate(30)     # Set frame rate to 30 fps

# Start streaming
camera.start_streaming()

try:
    while True:
        # Capture a frame
        frame = camera.capture_frame()

        # Process and display the frame as needed

except KeyboardInterrupt:
    pass

# Stop streaming and release the camera
camera.stop_streaming()
camera.close()