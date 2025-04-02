Instructions from: https://core-electronics.com.au/guides/object-identify-raspberry-pi/#Set 

Install files to home / desktop, as file path is specified

Open Terminal:

sudo apt-get update && sudo apt-get upgrade

sudo nano /etc/dphys-swapfile
               
Then change the number on CONF_SWAPSIZE = 100 to CONF_SWAPSIZE=2048. Having done this press Ctrl-X, Y, and then Enter Key to save these changes. This change is only temporary and you should change it back after completing this. To have these changes affect anything we must restart the swapfile by entering the following command to the terminal. Then we will resume Terminal Commands as normal.

sudo apt-get install build-essential cmake pkg-config

sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev

sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

sudo apt-get install libxvidcore-dev libx264-dev

sudo apt-get install libgtk2.0-dev libgtk-3-dev

sudo apt-get install libatlas-base-dev gfortran

sudo pip3 install numpy

wget -O opencv.zip https://github.com/opencv/opencv/archive/4.4.0.zip

wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.4.0.zip

unzip opencv.zip

unzip opencv_contrib.zip

cd ~/opencv-4.4.0/

mkdir build

cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \

                                -D CMAKE_INSTALL_PREFIX=/usr/local \

                                -D INSTALL_PYTHON_EXAMPLES=ON \

                                -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-4.4.0/modules \

                                -D BUILD_EXAMPLES=ON ..

make -j $(nproc)

sudo make install && sudo ldconfig

sudo reboot

At this point the majority of the installation process is complete and you can now change back the Swapfile so that the CONF_SWAPSIZE = 100. 

