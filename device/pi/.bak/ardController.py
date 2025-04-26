import serial
import time

commands = ["dispense", "buzz"]

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

def send_command(command):
    if command not in commands:
        return False
    
    r_command = f"{command}\n"
    ser.write(r_command.encode('utf-8'))
    print(f"Sent command: {command}")


send_command("dispense")
send_command("buzz")

# debugging
time.sleep(5)
while ser.in_waiting:
    line = ser.readline().decode('utf-8').strip()
    print("Arduino:", line)

ser.close()
