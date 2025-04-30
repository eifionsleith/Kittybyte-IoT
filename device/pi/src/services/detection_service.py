from datetime import datetime
import logging
import os
import threading
import time
from typing import Any, List, Optional, Tuple

import numpy
import cv2  # pyright: ignore
import picamera
from queue import Queue, Empty

logger = logging.getLogger(__name__)

# -- Confguration, TODO: Move to a cfg file
DEFAULT_CLASS_FILE_PATH = "/home/pi/Desktop/Object_Detection_Files/coco.names"
DEFAULT_CONFIG_PATH = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
DEFAULT_WEIGHTS_PATH = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"
CONFIDENCE_THRESHOLD = 0.45
NMS_THRESHOLD = 0.2
TARGET_OBJECT = 'cat'
# --
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10

class AIWorker:
    """
    Worker class for performing AI inference in a seperate thread.
    Processes frames from an input queue, and puts detection results
    into an output queue.
    """
    def __init__(self, 
                 class_names: List[str],
                 config_path: str,
                 weights_path: str,
                 target_object: str):
        self._config_path = config_path
        self._weights_path = weights_path
        self._target_object = target_object
        self._target_class_id = class_names.index(target_object) + 1 # Model is 1-indexed
        self._net: Optional[cv2.dnn_DetectionModel] = None # pyright: ignore
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._frame_queue = Queue(maxsize=1)
        self._detection_result_queue = Queue(maxsize=1)

    def start(self):
        """Starts the worker thread."""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._worker_loop)
            self._thread.start()
            logger.info("AI worker thread started.")

    def stop(self):
        """Stops the worker thread."""
        if self._thread is not None and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()  # Wait for the current loop to finish.
            logger.info("AI worker thread stopped.")

    def _load_model(self):
        """Loads the pre-trained AI model."""
        try:
            self._net = cv2.dnn_DetectionModel(self._weights_path, self._config_path) # pyright: ignore
            self._net.setInputSize(320, 320) # pyright: ignore
            self._net.setInputScale(1.0 / 127.5) # pyright: ignore
            self._net.setInputMean((127.5, 127.5, 127.5)) # pyright: ignore
            self._net.setInputSwapRB(True) # pyright: ignore
        except Exception as e:
            logger.error(f"AI model failed to load: {e}")
            self._stop_event.set()

    def _worker_loop(self):
        """The main loop for the thread."""
        self._load_model()

        while not self._stop_event.is_set():
            try:
                frame = self._frame_queue.get(timeout=0.05)
                if self._net is None or self._target_class_id is None:
                    # Shouldn't happen, but better to handle.
                    logger.warning("Worker received frame, but model is not configured.")
                    self._put_overwrite(self._detection_result_queue, (False, frame))
                    continue

                try:
                    class_ids, _, _ = self._net.detect(frame,
                                                       confThreshold=CONFIDENCE_THRESHOLD,
                                                       nmsThreshold=NMS_THRESHOLD)
                    cat_detected = False
                    if class_ids is not None and self._target_class_id in class_ids:
                        cat_detected = True
                    self._put_overwrite(self._detection_result_queue, (cat_detected, frame))
                
                except Exception as e:
                    logger.warning(f"Unexpected error in frame processng: {e}")
                    self._put_overwrite(self._detection_result_queue, (False, frame))

            except Empty:
                ... # Happens if the queue times out, but this is normal behaviour.
            except Exception as e:
                logger.exception(f"Unexpected error in AI worker loop: {e}")
                self._stop_event.set()
                
    @staticmethod
    def _put_overwrite(queue: Queue, item: Any):
        """
        Puts in item into the queue, dropping the oldest item if the 
        queue is currently full.
        """
        if queue.full():
            try:
                queue.get_nowait()
            except Empty: # Shouldn't happen, but better to handle
                ...       # to prevent crashes.
        queue.put_nowait(item)

    def put_frame(self, frame: Any):
        """
        Puts a frame into the queue for processing.
        Will remove oldest frame if full.
        """
        self._put_overwrite(self._frame_queue, frame)
    
    def get_detection_result(self) -> Optional[Tuple[bool, Optional[Any]]]:
        """
        Gets the latest detection result from the queue.
        Returns None if the queue is empty.
        """
        try:
            return self._detection_result_queue.get_nowait()
        except Empty:
            return None

class CatDetectionService:
    """
    Manages the cat detection system, by handling camera capture,
    then delegating to the AI worker thread held within.
    """
    def __init__(self):
        self._camera: Optional[picamera.PiCamera] = None
        
        class_names = self._initialize_class_names()
        target_object = 'cat'
        self._worker = AIWorker(class_names,
                                DEFAULT_CONFIG_PATH, 
                                DEFAULT_WEIGHTS_PATH, 
                                target_object)

        self._running = False
    
    def _initialize_class_names(self):
        """
        Reads the class names from the file.
        Filepath is currently hardcoded.
        """
        try:
            with open(DEFAULT_CLASS_FILE_PATH, "r") as f:
                class_names = f.read().rstrip("\n").split("\n")
            return class_names
        except FileNotFoundError:
            logger.error(f"CatDetectionService could not find the class names file at '{DEFAULT_CLASS_FILE_PATH}'")
        except Exception:
            logger.exception("CatDetectionService encountered an unexpected exception reading class names.")

    def _initialize_camera(self):
        """
        Initializes a the Pi Camera.
        """
        if self._camera is None:
            self._camera = picamera.PiCamera()
            self._camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT) # pyright: ignore
            self._camera.framerate = CAMERA_FPS # pyright: ignore
            logger.info("CatDetectionService has initialized the Pi camera.")
    
    def start(self):
        """
        Starts both the Pi camera and the AI worker thread.
        """
        if self._running:
            logger.warning("Attempting to start already running CatDetectionService.")
            return

        self._running = True 
        try:
            self._initialize_camera()
            self._worker.start()
            logger.info("CatDetectionService has started.")
        except Exception:
            logger.exception("CatDetectionService failed to initialize the camera.")
            self._running = False
            return 

    def stop(self):
        """
        Stops the CatDetectionService.
        """
        if not self._running or self._camera is None:
            logger.warning("Attempting to stop non-running CatDetectionService.")
            return

        self._camera.close()  # pyright: ignore
        self._camera = None
        self._worker.stop()
        logger.info("CatDetectionService has stopped.")

    def _capture_frame(self):
        """
        Captures a frame using the camera, and returns a numpy array.
        """
        if not self._camera:
            logger.warning("CatDetectionService attempting to capture image from uninitizalized camera.")
            return 

        frame_buffer = numpy.empty((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=numpy.uint8)
        self._camera.capture(frame_buffer, format="bgr", use_video_port=True) # pyright: ignore
        return frame_buffer

    def _save_frame(self, frame):
        """
        Saves the provided frame as an image to the device.
        The save path is currently hardcoded.
        """
        if frame is None:
            logger.warning("CatDetectionService attempting to save an empty frame.")
            return

        save_dir = "/home/pi/Desktop/SavedFrames/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cat_detection_{timestamp}.jpg"
        filepath = os.path.join(save_dir, filename)
        cv2.imwrite(filepath, frame)

    def capture_and_process_frame(self):
        """
        Captures a new frame and appends it to the worker threads frame queue.
        Reads the result queue for the last processed frame.

        Should be called within the application main loop.
        """
        if not self._running or self._camera is None:
            return  # This is where we'd read the motion sensor, but just skipping for now.

        #-- Take a new frame.
        new_frame = self._capture_frame()
        self._worker.put_frame(new_frame)

        #-- Read the processed frame.
        result = self._worker.get_detection_result()
        if result is not None:
            cat_detected, processed_frame = result
            if cat_detected:
                logger.info("CatDetectionService detected a cat!")
                self._save_frame(processed_frame) # We'd do more here, but just for testing.
                                        # Probably return the data for processing elsewhere?

# -- Simple Test Script
if __name__ == "__main__":

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    logger = logging.getLogger(__name__)

    cds = CatDetectionService()
    cds.start()
    while True:
        cds.capture_and_process_frame()
        time.sleep(0.05)

