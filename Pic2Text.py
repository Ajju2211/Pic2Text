import sys
import os
from time import sleep
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
import cv2
from qcrop.ui import QCrop
import numpy as np
import pytesseract
from PIL import Image
os.environ['TESSDATA_PREFIX'] = os.path.join('Tesseract-OCR','tessdata')
pytesseract.pytesseract.tesseract_cmd = os.path.join('Tesseract-OCR\\tesseract.exe')
from textblob import TextBlob
from cam import Cam

class App:
    def __init__(self) -> None:
        self.filePath,self.originalImage,self.croppedImage,self.lang,self.output,self.langName,self.langCode="","","","","","English","eng"
        self.text = ""
        self.langsMap1={'English':'eng','Hindi':'hin','Tamil':'tam','Telugu':'tel','Urdu':'urd'}
        self.langsMap2={'English':'en','Hindi':'hi','Tamil':'ta','Telugu':'te','Urdu':'ur'}
    def ocr(self):
        self.langCode = self.langsMap1[self.langName]
        self.text = ""
        self.text = pytesseract.image_to_string(Image.fromarray(self.croppedImage),lang=self.langCode)
def numpyQImage(image):
    qImg = QtGui.QImage()
    if image.dtype == np.uint8:
        if len(image.shape) == 2:
            channels = 1
            height, width = image.shape
            bytesPerLine = channels * width
            qImg = QtGui.QImage(
                image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8
            )
            qImg.setColorTable([QtGui.qRgb(i, i, i) for i in range(256)])
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                height, width, channels = image.shape
                bytesPerLine = channels * width
                qImg = QtGui.QImage(
                    image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888
                )
            elif image.shape[2] == 4:
                height, width, channels = image.shape
                bytesPerLine = channels * width
                fmt = QtGui.QImage.Format_ARGB32
                qImg = QtGui.QImage(
                    image.data, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32
                )
    return qImg

def convertQImageToMat(incomingImage):
    '''  Converts a QImage into an opencv MAT format  '''

    incomingImage = incomingImage.convertToFormat(4)

    width = incomingImage.width()
    height = incomingImage.height()

    ptr = incomingImage.bits()
    ptr.setsize(incomingImage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
    return arr

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("ui/ocrMainwindow.ui",self)
        self.uploadB.clicked.connect(self.uploadCall)
        self.cameraB.clicked.connect(self.cameraCall)
    def uploadCall(self):
        app = App()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file, _ = QFileDialog.getOpenFileName(self,"Open any image", "","All Files (*);;Jpeg (*.jpeg);;Png (*.png);;Jpg (*.jpg)", options=options)
        if not file:
            print('Error while loading file path')
            return
        app.filePath = file
        img=cv2.imread(file)
        app.originalImage = img
        app.croppedImage =  self.cropImage(QtGui.QPixmap.fromImage(numpyQImage(img)))
        # cv2.imshow('demo',app.croppedImg)
        self.gotoscreen2(app)
        # cv2.imwrite("original.jpeg",img)
    def cropImage(self,original_image):
        crop_tool = QCrop(original_image)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ICONS/LOGO.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        crop_tool.setWindowIcon(icon)
        status = crop_tool.exec()
        if status == 1:
            cropped_image = crop_tool.image
            qImg = cropped_image.toImage()
            return convertQImageToMat(qImg)
        else:
            qImg = original_image.toImage()
            crop_tool.close()
            return convertQImageToMat(qImg)
    def cameraCall(self):
        app = App()
        def cb():
            app.filePath = 'original.jpeg'
            app.originalImage = Cam.currentFile
            # cv2.imshow('demo',app.originalImage)
            app.croppedImage = self.cropImage(QtGui.QPixmap.fromImage(numpyQImage(app.originalImage)))
            # cv2.imshow('demo', app.croppedImage)
            self.gotoscreen2(app);
            # widget.setCurrentIndex(widget.currentIndex()-1)
        c=Cam(cb)
        widget.addWidget(c)
        widget.setCurrentIndex(widget.currentIndex()+1)
        # cv2.imwrite("original.jpeg",img)
    # testing
    def gotoscreen2(self,app):
        second = Preview(app)
        widget.addWidget(second)
        widget.setCurrentIndex(widget.currentIndex()+1)

class Preview(QMainWindow):
    def __init__(self,app):
        super(Preview, self).__init__()
        loadUi("ui/ocrOriginalPreview.ui",self)
        self.app = app
        pixmap = QtGui.QPixmap(numpyQImage(self.app.croppedImage))
        self.originalpreview.setPixmap(pixmap)
        self.originalpreview.resize(pixmap.width(),pixmap.height())
        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.conv.clicked.connect(self.gotoscreen3)
        
    def selectionChange(self):
        self.app.langName =self.comboBox.itemText(self.comboBox.currentIndex())
    def gotoscreen3(self):
        opWin = Output(self.app)
        self.app.ocr()
        widget.addWidget(opWin)
        widget.setCurrentIndex(widget.currentIndex()+1)
class Output(QMainWindow):
    def __init__(self,app):
        super(Output, self).__init__()
        loadUi("ui/ocrOutput.ui",self)
        self.app = app
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 10, 1331, 561))
        self.plainTextEdit.setInputMethodHints(QtCore.Qt.ImhMultiLine)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setPlainText(self.app.text)
        self.message = QtWidgets.QLabel(self.centralwidget)
        self.message.setGeometry(QtCore.QRect(180, 620, 241, 31))
        font = QtGui.QFont()
        font.setFamily("Poor Richard")
        font.setPointSize(24)
        self.message.setFont(font)
        self.message.setObjectName("message")
        _translate = QtCore.QCoreApplication.translate
        self.message.setText(_translate("PIC2TEXT", "Ready to Download"))
        self.downloadB.clicked.connect(self.downloadFile)
    
    def downloadFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save File","","All Files (*);;Text Files (*.txt)", options=options)
        if not fileName:
            return
        file2=open(fileName+".txt",'w')
        file2.write(self.app.text)
        file2.close()


# main
app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainWin = MainWindow()
icon = QtGui.QIcon()
icon.addPixmap(QtGui.QPixmap("ICONS/LOGO.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
widget.setWindowIcon(icon)
widget.addWidget(mainWin)
widget.setFixedHeight(800)
widget.setFixedWidth(1050)
widget.show()

try:
    sys.exit(app.exec())
except:
    print("Exiting")
