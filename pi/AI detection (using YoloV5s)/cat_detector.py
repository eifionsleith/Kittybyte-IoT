# cat_detector.py
import cv2
import torch
import RPi.GPIO as GPIO
import time

# GPIO setup for servo motor
FEEDER_PIN = 18  # GPIO pin for the servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(FEEDER_PIN, GPIO.OUT)

# Set up PWM for servo
servo = GPIO.PWM(FEEDER_PIN, 50)  # 50 Hz frequency
servo.start(0)  # Start with 0 duty cycle (servo in neutral position)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = 0.5  # Confidence threshold

# Initialize webcam (or Pi Camera if configured)
cap = cv2.VideoCapture(0)  # Use 0 for USB camera or Pi cam (if it works)

def set_angle(angle):
    """Rotate servo to a specific angle"""
    duty = (angle / 18) + 2.5
    GPIO.output(FEEDER_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(FEEDER_PIN, False)
    servo.ChangeDutyCycle(0)

def feed_cat():
    """Rotate servo to dispense food"""
    print("Feeding triggered!")
    set_angle(90)  # Rotate to 90 degrees to dispense food
    time.sleep(1)  # Hold position for 1 second
    set_angle(0)  # Return to original position

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame!")
            break

        # Perform inference
        results = model(frame)

        # Parse detections
        for det in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = det
            if model.names[int(cls)] == "cat":
                print(f"Cat detected with {conf:.2f} confidence!")
                feed_cat()

                # Draw a rectangle around the cat
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, "Cat Detected!", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                time.sleep(5)  # Prevent multiple feeds in a row

        # Display the result
        cv2.imshow("Cat Feeder", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    servo.stop()
    GPIO.cleanup()

