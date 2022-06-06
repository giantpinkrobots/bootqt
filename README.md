# Bootqt

<a href='https://flathub.org/apps/details/io.github.giantpinkrobots.bootqt'><img width='240' alt='Download on Flathub' src='https://flathub.org/assets/badges/flathub-badge-en.png'/></a>

Bootqt - Bootable USB writer using Qt.

![Bootqt](/screenshots/Screenshot-Bootqt-1.png?raw=true "Bootqt")

Bootqt is a simple app for making a bootable USB drive from an ISO or IMG file. It is written in Python and uses Qt technologies to provide an easy to use graphical user interface.

*** Bootqt is for Linux only at the time. ***

# How to use

- Open the app and select your drive from the "Select Drive" list.
- Press the "Select Image File" button to select an image file.
- Press "Prepare Drive" and wait until the program finishes.

# Languages

Bootqt currently supports five languages:
- English
- Danish (Dansk)
- German (Deutsch)
- Italian (Italiano)
- Turkish (Türkçe)

To use them, download the bqi18n folder alongside the bootqt.py file. It will automatically get your locale from your computer.

Localising Bootqt is very simple. If you want to translate it to a language you speak, please feel free to do so! Or hit me up for details on how to do it.

# How to install

If your computer has [Flatpak support](https://flatpak.org/setup/), you can install Bootqt through the Flathub repo by just searching for Bootqt in your application store (Discover, Software, etc) or by going to [this page](https://flathub.org/apps/details/io.github.giantpinkrobots.bootqt) and getting the flatpakref file by pressing Install. Then, just run the flatpakref file to open it via your application store.

Or you can install it through the terminal:
```
flatpak install flathub io.github.giantpinkrobots.bootqt
```
If you don't have the Flathub repo enabled, you have to run this command first to add it to your computer:
```
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```
#
If you don't want to install through Flatpak, you have to download the "bootqt.py" file (not the one in the flatpak directory) and download the "bqi18n" folder if you want localization to work. Then, you'll need PyQt5. Here is how you can get it via pip:
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
- Thanks to [@albanobattistella](https://github.com/albanobattistella) for Italian localization.
