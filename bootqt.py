#Bootqt v2022.5.31.1
import sys
import os
import time
import locale
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QFileDialog, QVBoxLayout, QLabel, QMessageBox, QPlainTextEdit
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QIcon

global isFlatpak, text_imageselected, text_selectdrive, text_button_selectimagefile, text_selectimagefile, text_imagefile, text_button_preparedrive, text_status, text_ready, text_writing, text_error, text_errorwait, text_nodrive, text_noimage, text_areyousure, text_drivewillbewiped, text_imagewillbewritten, text_writestarted, text_writefinished, text_finished, text_copied

isFlatpak = 0 # 1 = is flatpak, 0 = is standalone python script

#i18n
localename = locale.getdefaultlocale()
if (isFlatpak == 0): i18ndir = "./bqi18n/"
else: i18ndir = "/app/lib/bootqt/bqi18n/"
if ((localename[0].startswith("da_")) and (os.path.exists(i18ndir + "da.py"))):
    from bqi18n.da import *
elif ((localename[0].startswith("de_")) and (os.path.exists(i18ndir + "de.py"))):
    from bqi18n.de import *
elif ((localename[0].startswith("it_")) and (os.path.exists(i18ndir + "it.py"))):
    from bqi18n.it import *
elif ((localename[0].startswith("tr_")) and (os.path.exists(i18ndir + "tr.py"))):
    from bqi18n.tr import *
else: #Default to English
    text_imageselected = "Image selected:"
    text_selectdrive = "Select Drive"
    text_button_selectimagefile = "Select Image File"
    text_selectimagefile = "Select an image file"
    text_imagefile = "Image File"
    text_button_preparedrive = "Prepare Drive"
    text_status = "Status:"
    text_ready = "Ready"
    text_writing = "Writing"
    text_error = "Error"
    text_errorwait = "Wait until the current write finishes."
    text_nodrive = "No drive selected."
    text_noimage = "No image selected."
    text_areyousure = "Are you sure?"
    text_drivewillbewiped = "The following drive will be completely wiped:"
    text_imagewillbewritten = "The following image will be written to the drive:"
    text_writestarted = "Write started."
    text_writefinished = "Write finished."
    text_finished = "Finished"
    text_copied = "copied"

class bootqt(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400,300)
        self.setWindowTitle("Bootqt")
        if (isFlatpak == 1):
            self.setWindowIcon(QIcon("/app/lib/bootqt/bqlogo.png"))
        else:
            self.setWindowIcon(QIcon("./bqlogo.png"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.selected_image = ""
        self.textLabel = text_imageselected+"\n" + self.selected_image

        self.isWriting = 0;

        #Get drive list:
        drive_list = []
        lsblk_output = os.popen("lsblk").read()
        drive_list.append(text_selectdrive)
        for i in lsblk_output.splitlines():
            if(i[0] != "├") and (i[0] != "└") and (i[0] == "s") and (i[1] == "d"):
                i = i.split(" ")
                lsblk_model = os.popen("lsblk -io KNAME,MODEL | grep \""+i[0]+" \"").read()
                lsblk_model = lsblk_model.split("\n")
                drive_list.append("/dev/" + lsblk_model[0])

        #Drive list selection box:
        self.drives_selection_box = QComboBox()
        self.drives_selection_box.addItems(drive_list)
        layout.addWidget(self.drives_selection_box)

        #Image file select button
        self.button_selectImage = QPushButton(text_button_selectimagefile)
        self.button_selectImage.clicked.connect(self.getImageFile)
        layout.addWidget(self.button_selectImage)

        #Write button
        self.button_write = QPushButton(text_button_preparedrive)
        self.button_write.clicked.connect(self.writeToUSB)
        layout.addWidget(self.button_write)

        #Status text
        self.statusText = QLabel()
        self.statusText.setText(text_status + " " + text_ready)
        layout.addWidget(self.statusText)

        #Console
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def writeToUSB(self):
        if (self.isWriting == 1):
            error_message = QMessageBox()
            error_message.setText(text_errorwait)
            error_message.setWindowTitle(text_error)
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
            return;
        error = ""
        selected_drive = self.drives_selection_box.currentText()
        if (selected_drive == text_selectdrive):
            error = error + text_nodrive+"\n"
        if (self.selected_image == ""):
            error = error + text_noimage+"\n"
        if (error != ""):
            error_message = QMessageBox()
            error_message.setText(error)
            error_message.setWindowTitle(text_error)
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
        else:
            question_message = QMessageBox()
            start_write = question_message.question(self,text_areyousure, text_drivewillbewiped+"\n" + selected_drive + "\n\n"+text_imagewillbewritten+"\n" + self.selected_image + "\n\n"+text_areyousure, question_message.Yes | question_message.No)
            if start_write == question_message.Yes:
                #Start writing
                self.isWriting = 1;
                self.statusText.setText(text_status + " " + text_writing)
                self.text.appendPlainText(text_writestarted+" ("+time.strftime("%H:%M:%S", time.localtime())+")")
                selected_drive_code = selected_drive.split(" ");
                self.write_command = "dd bs=4M if=\""+self.selected_image+"\" of="+selected_drive_code[0]+" status=progress oflag=sync"
                if (isFlatpak == 1):
                    os.popen("flatpak-spawn --host umount "+selected_drive_code[0]+"*")
                    self.write_command_exec = ["--host", "pkexec", "sh", "-c", self.write_command]
                else:
                    os.popen("umount "+selected_drive_code[0]+"*")
                    self.write_command_exec = ["sh", "-c", self.write_command]
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
                self.process_write.start()

    def getImageFile(self):
        if (self.isWriting == 1):
            error_message = QMessageBox()
            error_message.setText(text_errorwait)
            error_message.setWindowTitle(text_error)
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
            return;
        showDialog = QFileDialog.getOpenFileName(
            parent = self,
            caption = text_selectimagefile,
            filter = text_imagefile+"(*.iso *.img)"
        )
        if showDialog[0] != "":
            self.selected_image = showDialog[0]

    def write_output(self):
        output = bytes(self.process_write.readAllStandardError()).decode("utf8")
        if("bytes (" in output) and (") copied, " in output):
            output = output.replace("copied", text_copied)
            output = output.split("(")
            output = output[1].split(", ")
            output = output[2]+" - "+output[0]+" "+text_copied+" ("+output[3]+")"
        self.text.appendPlainText(output)

    def write_finished(self):
        self.text.appendPlainText(text_writefinished+" ("+time.strftime("%H:%M:%S", time.localtime())+")")
        info_message = QMessageBox()
        info_message.setText(text_writefinished)
        info_message.setWindowTitle(text_finished)
        info_message.exec_()
        self.isWriting = 0;
        self.statusText.setText(text_status + " " + text_ready)

if __name__ == "__main__":
    program = QApplication(sys.argv)
    bootqt = bootqt()
    bootqt.show()
    sys.exit(program.exec_())
