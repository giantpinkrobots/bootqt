#Bootqt v2022.5.25
import sys
import os
import time
import locale
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QFileDialog, QVBoxLayout, QLabel, QMessageBox, QPlainTextEdit
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QIcon

class bootqt(QWidget):
    def __init__(self):
        #<Text>
        self.localename = locale.getdefaultlocale()
        if (self.localename[0].startswith("de_")):
            self.text_imageselected = "Ausgewähltes Bilddatei:"
            self.text_selectdrive = "Laufwerk auswählen"
            self.text_button_selectimagefile = "Bilddatei Auswählen"
            self.text_selectimagefile = "Wählen Sie eine Bilddatei"
            self.text_imagefile = "Bilddatei"
            self.text_button_preparedrive = "Laufwerk vorbereiten"
            self.text_status = "Status:"
            self.text_ready = "Bereit"
            self.text_writing = "Im Prozess"
            self.text_error = "Fehler"
            self.text_errorwait = "Warten Sie, bis der aktuelle Prozess beendet ist."
            self.text_nodrive = "Kein Laufwerk ausgewählt."
            self.text_noimage = "Keine Bilddatei ausgewählt."
            self.text_areyousure = "Sind Sie sicher?"
            self.text_drivewillbewiped = "Das folgende Laufwerk wird vollständig gelöscht:"
            self.text_imagewillbewritten = "Die folgende Bilddatei wird auf das Laufwerk geschrieben:"
            self.text_writestarted = "Prozess gestartet."
            self.text_writefinished = "Prozess beendet."
            self.text_finished = "Abgeschlossen"
            self.text_copied = "kopiert"
        elif (self.localename[0].startswith("tr_")):
            self.text_imageselected = "Seçilen yansıma:"
            self.text_selectdrive = "Disk Seç"
            self.text_button_selectimagefile = "Yansıma Dosyası Seç"
            self.text_selectimagefile = "Bir yansıma dosyası seç"
            self.text_imagefile = "Yansıma Dosyası"
            self.text_button_preparedrive = "Diski Hazırla"
            self.text_status = "Durum:"
            self.text_ready = "Hazır"
            self.text_writing = "Yazıyor"
            self.text_error = "Hata"
            self.text_errorwait = "Şu anki işlemin bitmesini bekleyin."
            self.text_nodrive = "Disk seçilmedi."
            self.text_noimage = "Yansıma dosyası seçilmedi."
            self.text_areyousure = "Emin misiniz?"
            self.text_drivewillbewiped = "Şu disk tamamen silinecek:"
            self.text_imagewillbewritten = "Diske şu yansıma dosyası yazılacak:"
            self.text_writestarted = "İşlem başladı."
            self.text_writefinished = "İşlem tamamlandı."
            self.text_finished = "Tamamlandı"
            self.text_copied = "kopyalandı"
        else: #Default to English
            self.text_imageselected = "Image selected:"
            self.text_selectdrive = "Select Drive"
            self.text_button_selectimagefile = "Select Image File"
            self.text_selectimagefile = "Select an image file"
            self.text_imagefile = "Image File"
            self.text_button_preparedrive = "Prepare Drive"
            self.text_status = "Status:"
            self.text_ready = "Ready"
            self.text_writing = "Writing"
            self.text_error = "Error"
            self.text_errorwait = "Wait until the current write finishes."
            self.text_nodrive = "No drive selected."
            self.text_noimage = "No image selected."
            self.text_areyousure = "Are you sure?"
            self.text_drivewillbewiped = "The following drive will be completely wiped:"
            self.text_imagewillbewritten = "The following image will be written to the drive:"
            self.text_writestarted = "Write started."
            self.text_writefinished = "Write finished."
            self.text_finished = "Finished"
            self.text_copied = "copied"
        #</Text>

        self.isFlatpak = 0 # 1 = is flatpak, 0 = is standalone python script

        super().__init__()
        self.setMinimumSize(400,300)
        self.setWindowTitle("Bootqt")
        if (self.isFlatpak == 1):
            self.setWindowIcon(QIcon("/app/lib/bootqt/bqlogo.png"))
        else:
            self.setWindowIcon(QIcon("bqlogo.png"))

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.selected_image = ""
        self.textLabel = self.text_imageselected+"\n" + self.selected_image

        self.isWriting = 0;

        #Get drive list:
        drive_list = []
        lsblk_output = os.popen("lsblk").read()
        drive_list.append(self.text_selectdrive)
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
        self.button_selectImage = QPushButton(self.text_button_selectimagefile)
        self.button_selectImage.clicked.connect(self.getImageFile)
        layout.addWidget(self.button_selectImage)

        #Write button
        self.button_write = QPushButton(self.text_button_preparedrive)
        self.button_write.clicked.connect(self.writeToUSB)
        layout.addWidget(self.button_write)

        #Status text
        self.statusText = QLabel()
        self.statusText.setText(self.text_status + " " + self.text_ready)
        layout.addWidget(self.statusText)

        #Console
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def writeToUSB(self):
        if (self.isWriting == 1):
            error_message = QMessageBox()
            error_message.setText(self.text_errorwait)
            error_message.setWindowTitle(self.text_error)
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
            return;
        error = ""
        selected_drive = self.drives_selection_box.currentText()
        if (selected_drive == self.text_selectdrive):
            error = error + self.text_nodrive+"\n"
        if (self.selected_image == ""):
            error = error + self.text_noimage+"\n"
        if (error != ""):
            error_message = QMessageBox()
            error_message.setText(error)
            error_message.setWindowTitle(self.text_error)
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
        else:
            question_message = QMessageBox()
            start_write = question_message.question(self,self.text_areyousure, self.text_drivewillbewiped+"\n" + selected_drive + "\n\n"+self.text_imagewillbewritten+"\n" + self.selected_image + "\n\n"+self.text_areyousure, question_message.Yes | question_message.No)
            if start_write == question_message.Yes:
                #Start writing
                self.isWriting = 1;
                self.statusText.setText(self.text_status + " " + self.text_writing)
                self.text.appendPlainText(self.text_writestarted+" ("+time.strftime("%H:%M:%S", time.localtime())+")")
                selected_drive_code = selected_drive.split(" ");
                self.write_command = "dd bs=4M if=\""+self.selected_image+"\" of="+selected_drive_code[0]+" status=progress oflag=sync"
                if (self.isFlatpak == 1):
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
                if (self.isFlatpak == 1):
                    self.process_write.setProgram("flatpak-spawn")
                else:
                    self.process_write.setProgram("pkexec")
                self.process_write.setArguments(self.write_command_exec)
                self.process_write.start()

    def getImageFile(self):
        if (self.isWriting == 1):
            error_message = QMessageBox()
            error_message.setText(self.text_errorwait)
            error_message.setWindowTitle(self.text_error)
            error_message.setIcon(QMessageBox.Critical)
            error_message.exec_()
            return;
        showDialog = QFileDialog.getOpenFileName(
            parent = self,
            caption = self.text_selectimagefile,
            filter = self.text_imagefile+"(*.iso *.img)"
        )
        if showDialog[0] != "":
            self.selected_image = showDialog[0]

    def write_output(self):
        output = bytes(self.process_write.readAllStandardError()).decode("utf8")
        if("bytes (" in output) and (") copied, " in output):
            output = output.replace("copied", self.text_copied)
            output = output.split("(")
            output = output[1].split(", ")
            output = output[2]+" - "+output[0]+" "+self.text_copied+" ("+output[3]+")"
        self.text.appendPlainText(output)

    def write_finished(self):
        self.text.appendPlainText(self.text_writefinished+" ("+time.strftime("%H:%M:%S", time.localtime())+")")
        info_message = QMessageBox()
        info_message.setText(self.text_writefinished)
        info_message.setWindowTitle(self.text_finished)
        info_message.exec_()
        self.isWriting = 0;
        self.statusText.setText(self.text_status + " " + self.text_ready)

if __name__ == "__main__":
    program = QApplication(sys.argv)
    bootqt = bootqt()
    bootqt.show()
    sys.exit(program.exec_())
