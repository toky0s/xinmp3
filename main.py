from PyQt5.QtWidgets import (QApplication, QWidget, QRadioButton, QPushButton, QLabel, 
QFileDialog, QGridLayout, QLineEdit, QButtonGroup, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlretrieve
import requests
import sys


class DownloaderThread(QThread):

    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, name='', quality='', save=''):
        QThread.__init__(self)
        self.name = name
        self.quality = quality
        self.save = save

    def run(self):
        params = {'q':self.name}
        r = requests.get('https://chiasenhac.vn/tim-kiem', params=params)
        soup_trainer = SoupStrainer(class_='media-title mt-0 mb-0')
        s = BeautifulSoup(r.text,'lxml',parse_only=soup_trainer)
        a_tag = s.find(class_='search_title search-line-music')

        url = a_tag['href']
        file_name = a_tag['title']

        # goto music page
        music_page = requests.get(url)
        soup_trainer_2 = SoupStrainer(class_='download_item')
        s_2 = BeautifulSoup(music_page.text,'lxml',parse_only=soup_trainer_2)

        # get link download
        list_urls = s_2.find_all(class_='download_item')
        if self.quality == 1:
            # 128kbps
            link_download = list_urls[0]['href']
        else:
            #320kbps
            link_download = list_urls[1]['href']
        urlretrieve(link_download,self.save+'/'+file_name+'.mp3')
        self.signal.emit(file_name)


class MainApp(QWidget):

    quality = 1

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
        self.radio_128.toggled.connect(lambda:self.change_value(self.radio_128))
        self.radio_128.setChecked(True)

        self.radio_320 = QRadioButton('320kbps')
        self.radio_320.toggled.connect(lambda:self.change_value(self.radio_320))
        self.bttgrp.addButton(self.radio_128,0)
        self.bttgrp.addButton(self.radio_320,1)

        self.label_save = QLabel('Lưu ở:')
        self.line_save = QLineEdit()
        self.btt_browse = QPushButton('Duyệt...')
        self.btt_browse.clicked.connect(self.browse)

        self.btt_download = QPushButton('Tải')
        self.btt_download.clicked.connect(self.download)

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

        self.a = DownloaderThread()
        self.a.signal.connect(self.showMessage)
        self.show()

    def change_value(self, b):
        if b.text() == '128kbps':
            MainApp.quality = 1
        else:
            MainApp.quality = 2

    def browse(self):
        path = QFileDialog.getExistingDirectory(self,'Chọn nơi lưu')
        self.line_save.setText(path)

    def check_valid(self):
        return True

    def download(self):
        if self.check_valid:
            self.name = self.line_name.text()
            self.save= self.line_save.text()

            self.a.name=self.name
            self.a.quality=MainApp.quality
            self.a.save=self.save
            self.a.start()
        else:
            pass

    def showMessage(self, name_music):
        self.msg_successful = QMessageBox.information(self,'Thông báo cute','Đã tải xong bài '+ name_music)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = MainApp()
    sys.exit(app.exec_())