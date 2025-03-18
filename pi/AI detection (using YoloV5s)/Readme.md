# Update and get the dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-opencv -y

# Clone YOLOv5 and install dependencies
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip3 install -r requirements.txt

# Note -: Works with an external usb webcam , not tested with pi cam