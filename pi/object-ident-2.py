import cv2
import time
from datetime import datetime

# ====== Logging System ======
class CatLogger:
    def __init__(self, log_file="cat_log.txt"):
        self.cat_present = False
        self.start_time = None
        self.log_file = log_file

    def update(self, cat_detected):
        current_time = time.time()

        if cat_detected and not self.cat_present:
            self.cat_present = True
            self.start_time = current_time
            print("Cat arrived at", datetime.fromtimestamp(current_time))

        elif not cat_detected and self.cat_present:
            self.cat_present = False
            end_time = current_time
            duration = end_time - self.start_time
            self.log_event(self.start_time, end_time, duration)
            print("Cat left at", datetime.fromtimestamp(end_time), f"Stayed for {duration:.2f} seconds")

    def log_event(self, start_time, end_time, duration):
        with open(self.log_file, "a") as f:
            f.write(f"Cat visit - Start: {datetime.fromtimestamp(start_time)}, "
                    f"End: {datetime.fromtimestamp(end_time)}, "
                    f"Duration: {duration:.2f} seconds\n")

# ====== Original Detection Code ======
classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return img,objectInfo

# ====== Main Loop with Logger ======
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 2)
    cap.set(3,640)
    cap.set(4,480)

    cat_logger = CatLogger()

    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img,0.45,0.2, objects=['cat'])

        # Logging logic (unchanged detection visuals)
        cat_detected = bool(objectInfo)
        cat_logger.update(cat_detected)

        cv2.imshow("Output",img)
        cv2.waitKey(1)