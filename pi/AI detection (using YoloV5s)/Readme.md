## Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install python3 python3-pip python3-opencv -y

# Clone YOLOv5 and install Python dependencies
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip3 install -r requirements.txt
