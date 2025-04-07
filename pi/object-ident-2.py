import cv2
from datetime import datetime

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

# Cat visit tracking variables
current_visit_start = None
consecutive_misses = 0

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
    return img, objectInfo

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 2)
    cap.set(3,640)
    cap.set(4,480)
    
    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to capture image")
                break
                
            result, objectInfo = getObjects(img,0.45,0.2, objects=['cat'])
            cat_detected = bool(objectInfo)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Update visit tracking
            global current_visit_start, consecutive_misses
            
            if cat_detected:
                consecutive_misses = 0
                if current_visit_start is None:
                    current_visit_start = datetime.now()
                    print(f"\n🐱 Cat arrived at {current_time}")
            else:
                consecutive_misses += 1
                if current_visit_start is not None and consecutive_misses >= 3:
                    duration = (datetime.now() - current_visit_start).total_seconds()
                    print(f"🐾 Cat left at {current_time} (Visited for {duration:.1f} seconds)")
                    current_visit_start = None
            
            cv2.imshow("Output",img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping cat monitoring...")
    finally:
        # Log final visit if still ongoing
        if current_visit_start is not None:
            duration = (datetime.now() - current_visit_start).total_seconds()
            print(f"🐾 Final visit logged at {current_time} (Visited for {duration:.1f} seconds)")
        
        cap.release()
        cv2.destroyAllWindows()