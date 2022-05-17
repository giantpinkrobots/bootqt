# Bootqt
Bootqt - Bootable USB writer using Qt.

![Bootqt](/Screenshot-Bootqt.png?raw=true "Bootqt")

Bootqt is a simple app for making a bootable USB drive from an ISO or IMG file. It is written in Python and uses Qt technologies to provide an easy to use graphical user interface.

# How to use

- Open the app and select your drive from the "Select Drive" list.
- Press the "Select Image File" button to select an image file.
- Press "Prepare Drive" and wait until the program finishes.

# How to install

Bootqt requires Python and PyQt5. It is also available on Linux only. First, you have to get PyQt5. Here is how you can get it via pip:
```
pip install PyQt5
```
Afterwards just run the script like so:
```
python3 ./bootqt.py
```
Upon first usage it will create two hidden folders named ".BOOTQT_USBMOUNT" and ".BOOTQT_IMGMOUNT". These folders are necessary because the drive and the image file are mounted there. So if you have two folders named these way, you should run Bootqt in a directory that does not have such folders.

# Why?

I know there are many other alternatives to Bootqt. But I wanted to try making an app using Qt. This is my first such project. Also I haven't seen such a tool that is made with Qt and integrates well with KDE Plasma.
