#Bootqt v2026.5.13
import sys
import os
import json
import urllib.request
import subprocess
import re
import threading
import time
import tarfile
import shutil
import gzip
from PySide6.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QFileDialog, QVBoxLayout, QLabel, QMessageBox, QProgressBar, QDialog, QTabWidget
from PySide6.QtCore import QProcess, QProcessEnvironment
from PySide6.QtGui import QGuiApplication

flatpakTest = subprocess.run(["sh", "-c", "LANG=en_US.UTF-8 flatpak-spawn --help"], capture_output=True, text=True)
if ("Usage:" in flatpakTest.stdout):
    isFlatpak = 1
else:
    isFlatpak = 0

#i18n
localename = os.getenv("LANG")
if (isFlatpak == 0): i18ndir = "./bqi18n/"
else: i18ndir = "/app/lib/bootqt/bqi18n/"

# Initialize the default strings in English:
text_imageselected = "Image selected:"
text_selectdrive = "Select Drive"
text_button_selectimagefile = "Select Image File"
text_selectimagefile = "Select an image file"
text_imagefile = "Image File"
text_download = "Download"
text_button_selectdownload = "Select Download"
text_downloadselected = "Download selected:"
text_downloading = "Downloading"
text_button_preparedrive = "Prepare Drive"
text_status = "Status:"
text_ready = "Ready"
text_writing = "Writing"
text_error = "Error"
text_nodownload = "No download selected."
text_areyousure = "Are you sure?"
text_drivewillbewiped = "The following drive will be completely wiped:"
text_writestarted = "Write started."
text_writefinished = "Write finished."
text_finished = "Finished"
text_copied = "copied"

if ((localename.startswith("da_")) and (os.path.exists(i18ndir + "da.py"))):
    from bqi18n.da import *
elif ((localename.startswith("de_")) and (os.path.exists(i18ndir + "de.py"))):
    from bqi18n.de import *
elif ((localename.startswith("it_")) and (os.path.exists(i18ndir + "it.py"))):
    from bqi18n.it import *
elif ((localename.startswith("tr_")) and (os.path.exists(i18ndir + "tr.py"))):
    from bqi18n.tr import *
elif ((localename.startswith("pt_BR")) and (os.path.exists(i18ndir + "ptbr.py"))):
    from bqi18n.ptbr import *

download_options = ["Ventoy", "Ubuntu x86_64", "Fedora Workstation x86_64", 
                    "Linux Mint Cinnamon x86_64", "Clonezilla x86_64"]

class bootqt(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400,265)
        self.setMaximumSize(400,265)
        self.setWindowTitle("Bootqt")
        QGuiApplication.setDesktopFileName("io.github.giantpinkrobots.bootqt")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.selected_image = ""
        self.textLabel = text_imageselected+"\n" + self.selected_image

        self.isWriting = 0
        self.copiedamount = 0
        self.active_tab = 0
        self.downloadimage_index = -1
        self.download_url = None
        self.original_working_directory = os.getcwd()

        if (isFlatpak == 1):
            drives_command_prefix = ["flatpak-spawn", "--host"]
        else:
            drives_command_prefix = []

        lsblk_devices = subprocess.run(
            drives_command_prefix + ["lsblk", "-J", "-o", "PATH,MODEL,TYPE,TRAN,RM"],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(lsblk_devices.stdout)
        drive_list = []
        drive_list.append(text_selectdrive)

        for dev in data["blockdevices"]:
            if dev["type"] == "disk" and dev.get("tran") == "usb":
                drive_list.append(f"{dev["path"]}  —  {dev["model"]}")
        
        #Tabs for Image and Menu
        self.tabs = QTabWidget()
        
        #Tab 1: Image file select
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        self.button_selectImage = QPushButton(text_button_selectimagefile)
        self.button_selectImage.clicked.connect(self.getImageFile)
        tab1_layout.addWidget(self.button_selectImage)
        tab1_layout.addStretch()
        tab1.setLayout(tab1_layout)
        self.tabs.addTab(tab1, text_imagefile)
        
        #Tab 2: Download Image
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        self.button_downloadImage = QPushButton(text_button_selectdownload)
        self.button_downloadImage.clicked.connect(self.openImageDownloadMenu)
        tab2_layout.addWidget(self.button_downloadImage)
        tab2_layout.addStretch()
        tab2.setLayout(tab2_layout)
        self.tabs.addTab(tab2, text_download)
        
        self.tabs.currentChanged.connect(self.onTabChanged)
        layout.addWidget(self.tabs)

        #Drive list selection box:
        self.drives_selection_box = QComboBox()
        self.drives_selection_box.addItems(drive_list)
        self.drives_selection_box.currentIndexChanged.connect(self.checkReady)
        layout.addWidget(self.drives_selection_box)

        #Write button
        self.button_write = QPushButton(text_button_preparedrive)
        self.button_write.clicked.connect(self.writeToUSB)
        self.button_write.setEnabled(False)
        layout.addWidget(self.button_write)

        #Status text
        self.statusText = QLabel()
        self.statusText.setText(text_status + " " + text_ready)
        layout.addWidget(self.statusText)

        #Status text 2
        self.statusText2 = QLabel()
        self.statusText2.setText("")
        layout.addWidget(self.statusText2)

        #Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        layout.addStretch(1)

    def onTabChanged(self, i):
        self.active_tab = i
        self.checkReady();

    def checkReady(self, **args):
        self.button_write.setEnabled(False)

        if self.drives_selection_box.currentText() == text_selectdrive:
            return
        
        if self.active_tab == 0 and self.selected_image != "":
            self.button_write.setEnabled(True)
        
        elif self.active_tab == 1 and self.downloadimage_index >= 0:
            self.button_write.setEnabled(True)

    def writeToUSB(self):
        selected_drive = self.drives_selection_box.currentText()
        question_message = QMessageBox(self)
        start_write = question_message.question(self,text_areyousure, text_drivewillbewiped + "\n" + selected_drive + "\n\n" + text_areyousure, question_message.StandardButton.Yes | question_message.StandardButton.No)
        
        os.chdir(self.original_working_directory) # Reset working directory

        if start_write == question_message.StandardButton.Yes:
            #Start writing
            self.isWriting = 1
            self.button_downloadImage.setEnabled(False)
            self.button_selectImage.setEnabled(False)
            self.drives_selection_box.setEnabled(False)
            self.button_write.setEnabled(False)
            self.tabs.setEnabled(False)

            self.copiedamount = 0
            self.progressBar.setValue(0)
            selected_drive_code = selected_drive.split(" ")[0];
            print(selected_drive_code)

            if self.active_tab == 0: # Selected local image file
                image_to_write = self.selected_image

            elif self.active_tab == 1: # Download an image
                self.statusText.setText(text_status + " " + text_downloading)
                image_to_write = os.path.join(os.getcwd(), "bootqt_image_download")

                thread = threading.Thread(target=self.get_download_url)
                thread.start()

                while thread.is_alive():
                    QApplication.processEvents()
                    time.sleep(1)

                if self.downloadimage_index == 0: # Ventoy
                    self.statusText.setText(text_status + " " + text_writing)

                    with tarfile.open(os.path.join(os.getcwd(), "bootqt_image_download")) as file:
                        file.extractall(path=os.path.join(os.getcwd(), "bootqt_ventoy"))
                    
                    subdir = next(
                        d for d in os.listdir(os.path.join(os.getcwd(), "bootqt_ventoy"))
                        if os.path.isdir(os.path.join(os.path.join(os.getcwd(), "bootqt_ventoy"), d))
                    )
                    
                    ventoy_command = ["pkexec", "bash", "-c", "cd " + os.path.join(os.getcwd(), "bootqt_ventoy", subdir) + " && ./Ventoy2Disk.sh -I " + selected_drive_code]
                    
                    if (isFlatpak == 1):
                        ventoy_command = ["flatpak-spawn", "--host", "--env=LANG=en_US.UTF-8", "pkexec"] + ventoy_command

                    ventoy_process = subprocess.Popen(ventoy_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                    def spam_yes():
                        while ventoy_process.poll() is None:
                            try:
                                ventoy_process.stdin.write("y\n")
                                ventoy_process.stdin.flush()
                            except:
                                break

                            time.sleep(0.5)

                    threading.Thread(target=spam_yes, daemon=True).start()

                    while ventoy_process.poll() is None:
                        ventoy_process_line = ventoy_process.stdout.readline().strip()
                        if ventoy_process_line:
                            self.statusText2.setText(ventoy_process_line)

                        QApplication.processEvents()

                    self.write_finished()
                    return
                
                else:
                    self.progressBar.setValue(0)

            self.write_command = "dd bs=4M if=\"" + image_to_write + "\" of=" + selected_drive_code + " status=progress oflag=sync"

            if (isFlatpak == 1):
                self.selected_image_size = (os.popen("flatpak-spawn --host ls -l \"" + image_to_write + "\"").read()).split(" ")[4]
                os.popen("flatpak-spawn --host umount " + selected_drive_code + "*")
                self.write_command_exec = ["--host", "--env=LANG=en_US.UTF-8", "pkexec", "sh", "-c", self.write_command]

            else:
                self.selected_image_size = (os.popen("ls -l \"" + image_to_write + "\"").read()).split(" ")[4]
                os.popen("umount " + selected_drive_code + "*")
                self.write_command_exec = ["sh", "-c", self.write_command]

            self.selected_image_size_bytes = float(self.selected_image_size)
            self.selected_image_size = round((( (float(self.selected_image_size) / 1024 ) / 1024 ) / 1024 ), 2)
            self.statusText.setText(text_status + " " + text_writing)
            self.statusText2.setText("0B " + text_copied + " | " + text_imagefile + ": " + str(self.selected_image_size) + " GB")
            self.process_write = QProcess()
            self.process_write.readyReadStandardOutput.connect(self.write_output)
            self.process_write.readyReadStandardError.connect(self.write_output)
            self.process_write.finished.connect(self.write_finished)
            self.process_write.setProgram
            if (isFlatpak == 1):
                self.process_write.setProgram("flatpak-spawn")
            else:
                self.process_write.setProgram("pkexec")
            self.process_write.setArguments(self.write_command_exec)
            self.process_environment = QProcessEnvironment.systemEnvironment()
            self.process_environment.insert("LANG", "en_US.UTF-8")
            self.process_write.setProcessEnvironment(self.process_environment)
            self.process_write.start()

    def getImageFile(self):
        showDialog = QFileDialog.getOpenFileName(
            parent = self,
            caption = text_selectimagefile,
            filter = text_imagefile+"(*.iso *.img *.raw)"
        )

        if showDialog[0] != "":
            self.selected_image = showDialog[0]
            filename = self.selected_image.split("/")[-1]
            self.button_selectImage.setText(text_imageselected + " " + filename)
        
        self.checkReady();

    def openImageDownloadMenu(self):
        menu_dialog = QDialog(self)
        menu_dialog.setWindowTitle("Image Download")
        menu_dialog.setMinimumSize(200, 150)
        
        menu_layout = QVBoxLayout()

        i = 0
        for item in download_options:
            new_button = QPushButton(item)
            new_button.clicked.connect(lambda *args, i=i: self.imageDownloadMenuButtonClicked(i, menu_dialog))
            menu_layout.addWidget(new_button)
            i += 1
        
        menu_dialog.setLayout(menu_layout)
        menu_dialog.exec()

    def imageDownloadMenuButtonClicked(self, i, menu_dialog):
        self.downloadimage_index = i
        self.button_downloadImage.setText(text_downloadselected + " " + download_options[i])
        menu_dialog.close()
        self.checkReady()

    def write_output(self):
        output = bytes(self.process_write.readAllStandardError()).decode("utf8")
        if("bytes (" in output) and (") copied, " in output):
            try:
                self.copiedamount = int(output.split(" ")[0])
            except:
                return
            output = output.replace("copied", text_copied)
            output = output.split("(")
            output = output[1].split(", ")

            self.statusText.setText(text_status + " " + text_writing + " | " + output[3])
            self.statusText2.setText(output[0] + " " + text_copied + " | " + text_imagefile + ": " + str(self.selected_image_size) + " GB")

            #Percentage calculation
            percentage = round(((self.copiedamount / (self.selected_image_size_bytes)) * 100))
            self.progressBar.setValue(percentage)
            output = output[2]+" - "+output[0]+" "+text_copied+" ("+output[3]+")"

    def write_finished(self):
        self.progressBar.setValue(100)
        info_message = QMessageBox(self)
        info_message.setText(text_writefinished)
        info_message.setWindowTitle(text_finished)
        info_message.exec()
        self.isWriting = 0
        self.statusText.setText(text_status + " " + text_ready)
        self.statusText2.setText("")

        if self.active_tab == 1:
            try:
                if os.path.exists(os.path.join(os.getcwd(), "bootqt_image_download")):
                    os.remove(os.path.join(os.getcwd(), "bootqt_image_download"))
                if os.path.exists(os.path.join(os.getcwd(), "bootqt_ventoy")):
                    shutil.rmtree(os.path.join(os.getcwd(), "bootqt_ventoy"))
            except:
                pass

        self.button_downloadImage.setEnabled(True)
        self.button_selectImage.setEnabled(True)
        self.drives_selection_box.setEnabled(True)
        self.button_write.setEnabled(True)
        self.tabs.setEnabled(True)
    
    def get_download_url(self):
        download_url = None

        if self.downloadimage_index == 0: # Ventoy
            URL = "https://api.github.com/repos/ventoy/Ventoy/releases/latest"

            with urllib.request.urlopen(URL) as response:
                data = json.load(response)

            download_url = None

            for asset in data["assets"]:
                name = asset["name"]

                if name.endswith("-linux.tar.gz"):
                    download_url = asset["browser_download_url"]
                    break

        elif self.downloadimage_index == 1: # Ubuntu latest x86_64
            URL = "https://releases.ubuntu.com/releases/"

            with urllib.request.urlopen(URL) as response:
                html = response.read().decode()

            versions = re.findall(r'href="([0-9]+\.[0-9]+(?:\.[0-9]+)?)/"', html)
            latest_version = versions.sort(key=lambda s: [int(x) for x in s.split(".")])[-1]

            download_url = f"https://releases.ubuntu.com/{latest_version}/ubuntu-{latest_version}-desktop-amd64.iso"
        
        elif self.downloadimage_index == 2: # Fedora Workstation x86_64
            URL = "https://fedoraproject.org/releases.json"

            with urllib.request.urlopen(URL) as response:
                releases = json.load(response)

            for release in releases:
                if (
                    release.get("variant") == "Workstation"
                    and release.get("arch") == "x86_64"
                    and release.get("link", "").endswith(".iso")
                ):
                    download_url = release["link"]
                    break
        
        elif self.downloadimage_index == 3: # Linux Mint Cinnamon x86_64
            URL = "https://pub.linuxmint.io/stable/"

            with urllib.request.urlopen(URL) as response:
                raw = response.read()

            html = gzip.decompress(raw).decode("utf-8")
            dirs = re.findall(r'href="([^"]+)"', html, re.IGNORECASE)

            latest_version = dirs[-1].replace("/", "").replace("\n","")

            download_url = f"https://pub.linuxmint.io/stable/{latest_version}/linuxmint-{latest_version}-cinnamon-64bit.iso"
        
        elif self.downloadimage_index == 4: # Clonezilla x86_64
            URL = "http://free.nchc.org.tw/clonezilla-live/stable/"

            with urllib.request.urlopen(URL) as response:
                html = response.read().decode()

            files = re.findall(r'href="([^"]+)"', html, re.IGNORECASE)

            for file in files:
                if file.endswith(".iso"):
                    download_url = URL + file
                    break

        print(download_url)
        self.download_url = download_url
        self.download_image()
    
    def download_image(self):

        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size

            if total_size > 0:
                percentage = min((downloaded / total_size * 100), 100)
                self.progressBar.setValue(percentage)

        urllib.request.urlretrieve(self.download_url, os.path.join(os.getcwd(), "bootqt_image_download"), reporthook=progress)

if __name__ == "__main__":
    program = QApplication(sys.argv)
    bootqt = bootqt()
    bootqt.show()
    sys.exit(program.exec())
