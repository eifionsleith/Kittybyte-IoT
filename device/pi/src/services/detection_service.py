import logging
import threading
from typing import Any, List, Optional, Tuple
import cv2
from queue import Queue, Empty

logger = logging.getLogger(__name__)

# -- Confguration, TODO: Move to a cfg file
DEFAULT_CLASS_FILE_PATH = "/home/pi/Desktop/Object_Detection_Files/coco.names"
DEFAULT_CONFIG_PATH = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
DEFAULT_WEIGHTS_PATH = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"
CONFIDENCE_THRESHOLD = 0.45
NMS_THRESHOLD = 0.2
TARGET_OBJECT = 'cat'

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
            self._net.setMean((127.5, 127.5, 127.5)) # pyright: ignore
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
                    if class_ids is not None and self._target_class_id in class_ids.flatten():
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

