from PyQt5.QtWidgets import QApplication, QWidget, QRadioButton, QPushButton, QLabel, QFileDialog, QGridLayout, QLineEdit, QButtonGroup
import sys
from threading import Thread
import requests
from bs4 import BeautifulSoup, SoupStrainer


class DownloaderThread(Thread):

    def __init__(self, name, quality, save):
        super().__init__(self)
        self.name = name
        self.quality = quality
        self.save = save

    def run(self):
        params = {'q':self.name}
        r = requests.get('https://chiasenhac.vn/tim-kiem', params=params)
        soup_trainer = SoupStrainer(class_={'list-unstyled list_music music_kq'})





class MainApp(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('XRhythm')
        self.setupUI()

    def setupUI(self):
        self.grid_layout = QGridLayout()
        self.label_name = QLabel('Tên nhạc:')
        self.line_name = QLineEdit()

        self.label_quality = QLabel('Chất lượng: ')

        self.bttgrp = QButtonGroup()
        self.radio_128 = QRadioButton('128kbps')
        self.radio_320 = QRadioButton('320kbps')
        self.bttgrp.addButton(self.radio_128,0)
        self.bttgrp.addButton(self.radio_320,1)

        self.label_save = QLabel('Lưu ở:')
        self.line_save = QLineEdit()
        self.btt_browse = QPushButton('Duyệt...')
        self.btt_browse.clicked.connect(self.browse)

        self.btt_download = QPushButton('Tải')

        self.grid_layout.addWidget(self.label_name,0,0)
        self.grid_layout.addWidget(self.line_name,0,1,1,2)
        self.grid_layout.addWidget(self.label_quality,1,0)
        self.grid_layout.addWidget(self.radio_128,1,1)
        self.grid_layout.addWidget(self.radio_320,1,2)
        self.grid_layout.addWidget(self.label_save,2,0)
        self.grid_layout.addWidget(self.line_save,2,1)
        self.grid_layout.addWidget(self.btt_browse,2,2)
        self.grid_layout.addWidget(self.btt_download,3,0,1,3)

        self.setLayout(self.grid_layout)
        self.show()

    def browse(self):
        path = QFileDialog.getExistingDirectory(self,'Chọn nơi lưu')
        self.line_save.setText(path)

    def download(self):
        # check exist dir
        # download
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = MainApp()
    sys.exit(app.exec_())