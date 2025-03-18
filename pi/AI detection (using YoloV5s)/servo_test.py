# servo_test.py
import RPi.GPIO as GPIO
import time

FEEDER_PIN = 18  # GPIO Pin connected to the servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(FEEDER_PIN, GPIO.OUT)

# Set up PWM for servo motor
servo = GPIO.PWM(FEEDER_PIN, 50)  # 50 Hz frequency
servo.start(0)

def set_angle(angle):
    """Rotate servo to a specific angle"""
    duty = (angle / 18) + 2.5
    GPIO.output(FEEDER_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(FEEDER_PIN, False)
    servo.ChangeDutyCycle(0)

try:
    print("Testing servo motor...")
    set_angle(90)
    time.sleep(2)
    set_angle(0)
    time.sleep(2)
finally:
    servo.stop()
    GPIO.cleanup()
