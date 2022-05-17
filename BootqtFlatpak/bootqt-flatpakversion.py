import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QFileDialog, QVBoxLayout, QLabel, QMessageBox, QPlainTextEdit
from PyQt5.QtCore import QProcess

#Bootqt Flatpak version

class bootqt(QWidget):
    def __init__(self):
        #Create necessary mounting folders:
        if not os.path.exists(os.getcwd()+"/.BOOTQT_USBMOUNT"):
            os.makedirs(os.getcwd()+"/.BOOTQT_USBMOUNT")
        if not os.path.exists(os.getcwd()+"/.BOOTQT_IMGMOUNT"):
            os.makedirs(os.getcwd()+"/.BOOTQT_IMGMOUNT")

        super().__init__()
        self.setMinimumSize(400,300)
        self.setWindowTitle("Bootqt")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.selected_image = "None"
        self.textLabel = "Image selected:\n" + self.selected_image

        self.isWriting = 0;

        #Get drive list:
        drive_list = []
        lsblk_output = os.popen("lsblk").read()
        drive_list.append("Select Drive")
        for i in lsblk_output.splitlines():
            if(i[0] != "├") and (i[0] != "└") and (i[0] == "s") and (i[1] == "d"):
                i = i.split(" ")
                drive_list.append("/dev/" + i[0])

        #Drive list selection box:
        self.drives_selection_box = QComboBox()
        self.drives_selection_box.addItems(drive_list)
        layout.addWidget(self.drives_selection_box)

        #Image file select button
        self.button_selectImage = QPushButton("Select Image File")
        self.button_selectImage.clicked.connect(self.getImageFile)
        layout.addWidget(self.button_selectImage)

        #Write button
        self.button_write = QPushButton("Prepare Drive")
        self.button_write.clicked.connect(self.writeToUSB)
        layout.addWidget(self.button_write)

        #Status text
        self.statusText = QLabel()
        self.statusText.setText("Status: Ready")
        layout.addWidget(self.statusText)

        #Console
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def writeToUSB(self):
        if (self.isWriting == 1):
            error_message = QMessageBox()
            error_message.setText("Wait until the current write finishes.")
            error_message.setWindowTitle("Error")
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
            return;
        error = ""
        selected_drive = self.drives_selection_box.currentText()
        if (selected_drive == "Select Drive"):
            error = error + "No drive selected\n"
        if (self.selected_image == "None"):
            error = error + "No image selected\n"
        if (error != ""):
            error_message = QMessageBox()
            error_message.setText(error)
            error_message.setWindowTitle("Error")
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
        else:
            question_message = QMessageBox()
            start_write = question_message.question(self,"Are you sure?", "The following drive will be completely wiped:\n" + selected_drive + "\n\nThe following image will be writted to the drive:\n" + self.selected_image + "\n\nAre you sure?", question_message.Yes | question_message.No)
            if start_write == question_message.Yes:
                #Start writing
                self.isWriting = 1;
                self.statusText.setText("Status: Writing")
                self.write_command_exec = ["--host", "pkexec", "sh", "-c", "umount "+selected_drive+"*; wipefs --all "+selected_drive+"; parted --script "+selected_drive+" mklabel msdos; parted --script "+selected_drive+" mkpart pri 1MiB 100%; partprobe; mkfs.fat -F32 -I -v "+selected_drive+"1; fatlabel "+selected_drive+"1 BOOTABLEUSB; umount "+selected_drive+"*; umount \""+os.getcwd()+"/.BOOTQT_USBMOUNT\"; umount \""+os.getcwd()+"/.BOOTQT_IMGMOUNT\";  mount \""+self.selected_image+"\" \""+os.getcwd()+"/.BOOTQT_IMGMOUNT\";  mount "+selected_drive+"1 \""+os.getcwd()+"/.BOOTQT_USBMOUNT\"; cp --archive --verbose \""+os.getcwd()+"/.BOOTQT_IMGMOUNT\"/* \""+os.getcwd()+"/.BOOTQT_USBMOUNT\"/; umount \""+os.getcwd()+"/.BOOTQT_IMGMOUNT\"; umount \""+os.getcwd()+"/.BOOTQT_USBMOUNT\""]
                self.process_write = QProcess()
                self.process_write.readyReadStandardOutput.connect(self.write_stdout)
                self.process_write.readyReadStandardError.connect(self.write_stderr)
                self.process_write.finished.connect(self.write_finished)
                self.process_write.setProgram
                self.process_write.setProgram("flatpak-spawn")
                self.process_write.setArguments(self.write_command_exec)
                self.process_write.start()

    def getImageFile(self):
        if (self.isWriting == 1):
            error_message = QMessageBox()
            error_message.setText("Wait until the current write finishes.")
            error_message.setWindowTitle("Error")
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
            return;
        showDialog = QFileDialog.getOpenFileName(
            parent = self,
            caption = "Select an image file",
            filter = "Image File(*.iso *.img)"
        )
        if showDialog[0] != "":
            self.selected_image = showDialog[0]
    
    def write_stderr(self):
        data = self.process_write.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.text.appendPlainText(stderr)

    def write_stdout(self):
        data = self.process_write.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.text.appendPlainText(stdout)

    def write_finished(self):
        self.text.appendPlainText("Write finished.")
        info_message = QMessageBox()
        info_message.setText("Writing process finished.")
        info_message.setWindowTitle("Finished")
        info_message.exec_()
        self.isWriting = 0;
        self.statusText.setText("Status: Ready")

if __name__ == "__main__":
    program = QApplication(sys.argv)
    bootqt = bootqt()
    bootqt.show()
    sys.exit(program.exec_())
