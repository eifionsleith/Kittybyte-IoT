import time
# (!) AI Generated Test Script
import logging
import os
from queue import Empty
import cv2
import numpy as np # Import numpy
import picamera # Import picamera

# Assume the AIWorker class code is in the same file or imported
from services.detection_service import AIWorker, DEFAULT_CLASS_FILE_PATH, DEFAULT_CONFIG_PATH, DEFAULT_WEIGHTS_PATH, TARGET_OBJECT, CONFIDENCE_THRESHOLD, NMS_THRESHOLD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Camera Configuration ---
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10 # Frame rate for capture

# --- Main Script ---
if __name__ == "__main__":
    logger.info("Starting Pi camera (v1) AI detection script using picamera package.")

    # Load class names
    class_names = []
    try:
        with open(DEFAULT_CLASS_FILE_PATH, 'rt') as f:
            class_names = f.read().rstrip('\n').split('\n')
        logger.info(f"Loaded {len(class_names)} class names from {DEFAULT_CLASS_FILE_PATH}")
    except FileNotFoundError:
        logger.error(f"Class names file not found: {DEFAULT_CLASS_FILE_PATH}")
        exit()
    except Exception as e:
        logger.error(f"Error loading class names: {e}")
        exit()

    # Initialize the AIWorker
    try:
        ai_worker = AIWorker(
            class_names=class_names,
            config_path=DEFAULT_CONFIG_PATH,
            weights_path=DEFAULT_WEIGHTS_PATH,
            target_object=TARGET_OBJECT
        )
        logger.info(f"AIWorker initialized, targeting '{TARGET_OBJECT}'.")
    except ValueError as e:
         logger.error(f"Error initializing AIWorker: {e}. Ensure '{TARGET_OBJECT}' is in '{DEFAULT_CLASS_FILE_PATH}'.")
         exit()
    except FileNotFoundError as e:
         logger.error(f"AI model file not found: {e}")
         exit()
    except Exception as e:
        logger.error(f"An unexpected error occurred during AIWorker initialization: {e}")
        exit()

    # Initialize the camera (using picamera v1)
    camera = None
    # Create a NumPy array to store the frame data
    # Format is BGR for OpenCV, size is height * width * channels
    frame_buffer = np.empty((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)

    try:
        camera = picamera.PiCamera() # <-- This uses the original picamera package
        camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        camera.framerate = CAMERA_FPS
        logger.info(f"Picamera (v1) configured to {CAMERA_WIDTH}x{CAMERA_HEIGHT} @ {CAMERA_FPS} FPS.")

        # Optional: Start preview if you have a display connected
        # camera.start_preview()
        # logger.info("Camera preview started.")

        # Allow the camera to warm up
        time.sleep(2)

    except Exception as e:
        logger.error(f"Error initializing or starting camera: {e}")
        if camera:
             camera.close()
        exit()

    # Start the AI worker thread
    ai_worker.start()
    logger.info("AI worker thread started.")

    try:
        logger.info("Starting camera capture loop.")
        while True:
            # Capture a frame directly into the numpy array buffer
            # use_video_port=True is essential for continuous video capture
            # format='bgr' captures directly in the format OpenCV expects
            camera.capture(frame_buffer, format='bgr', use_video_port=True) # <-- This uses picamera capture

            # The frame is now in frame_buffer
            # Put the frame into the AI worker's queue
            ai_worker.put_frame(frame_buffer)

            # Try to get the latest detection result without blocking
            detection_result = ai_worker.get_detection_result()

            if detection_result is not None:
                cat_detected, processed_frame = detection_result
                if cat_detected:
                    logger.info(f"!!! {TARGET_OBJECT.capitalize()} detected !!!")
                # In a real application, you might want to display the frame
                # with bounding boxes drawn by the AIWorker (if it did that)
                # Or perform an action based on cat_detected

            # The camera.capture call blocks until the next frame is ready at the set framerate.
            # No additional sleep is typically needed here unless you want to process slower.
            pass

    except KeyboardInterrupt:
        logger.info("Ctrl+C detected. Stopping.")
    except Exception as e:
        logger.exception(f"An error occurred during the main loop: {e}")

    finally:
        # --- Cleanup ---
        logger.info("Stopping AI worker.")
        ai_worker.stop()

        logger.info("Stopping camera.")
        if camera:
            # Optional: Stop preview
            # camera.stop_preview()
            camera.close() # <-- Use close() for picamera v1
        logger.info("Camera stopped.")

        logger.info("Script finished.")
