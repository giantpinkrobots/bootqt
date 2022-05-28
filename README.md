# Bootqt
Bootqt - Bootable USB writer using Qt.

![Bootqt](/Screenshot-Bootqt.png?raw=true "Bootqt")

Bootqt is a simple app for making a bootable USB drive from an ISO or IMG file. It is written in Python and uses Qt technologies to provide an easy to use graphical user interface.

# How to use

- Open the app and select your drive from the "Select Drive" list.
- Press the "Select Image File" button to select an image file.
- Press "Prepare Drive" and wait until the program finishes.

# Languages

Bootqt currently supports four languages:
- English
- Danish (Dansk)
- German (Deutsch)
- Turkish (Türkçe)

To use them, download the bqi18n folder alongside the bootqt.py file. It will automatically get your locale from your computer.

Localising Bootqt is very simple. If you want to translate it to a language you speak, please feel free to do so! Or hit me up for details on how to do it.

# How to install

Bootqt requires Python and PyQt5. It is also available on Linux only. First, you have to get PyQt5. Here is how you can get it via pip:
```
pip install PyQt5
```
Afterwards just run the script like so:
```
python3 ./bootqt.py
```

# Why?

I know there are many other alternatives to Bootqt. But I wanted to try making an app using Qt. This is my first such project. Also I haven't seen such a tool that is made with Qt and integrates well with KDE Plasma.

# Special Thanks

- Thanks to [@zocker-160](https://github.com/zocker-160) for giving me support on making Bootqt Flatpak compatible, going as far as writing the initial Flatpak yml file for me.
- Thanks to my friends for their help on German and Danish localization.
