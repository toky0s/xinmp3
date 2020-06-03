from PyQt5.QtWidgets import (QApplication, QWidget, QRadioButton, QPushButton, QLabel, QHBoxLayout, QGroupBox, QVBoxLayout,
                             QFileDialog, QGridLayout,QLineEdit, QButtonGroup, QMessageBox, QComboBox, QMainWindow, QDesktopWidget, QTableView, QHeaderView)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QVariant, QAbstractTableModel
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlretrieve
from datetime import datetime

import requests
import sys
import os
import json
import csv

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

class music_object:
    def __init__(self, name, singer, quality, download_time: datetime.now, save_at):
        self.name = name
        self.singer = singer
        self.download_time = download_time
        self.quality = quality
        self.save_at = save_at

    def getDatetimeString(self):
        return self.download_time.strftime("%d/%m/%Y")

    def getListInfo(self):
        return [self.name,self.singer,self.quality,self.getDatetimeString(),self.save_at]

class DownloaderThread(QThread):
    """Thread này chịu trách nhiệm tải bài hát chỉ định."""

    signal = pyqtSignal('PyQt_PyObject')
    MP3 = '.mp3'
    M4A = '.m4a'

    def __init__(self, name='', quality='', save=''):
        QThread.__init__(self)
        self.name = name
        self.quality = quality
        self.save = save

    def run(self):
        print('băt đầu tải:',self.name)
        params = {'q': self.name}
        r = requests.get('https://chiasenhac.vn/tim-kiem', params=params)
        soup_trainer = SoupStrainer(class_='media-title mt-0 mb-0')
        s = BeautifulSoup(r.text, 'lxml', parse_only=soup_trainer)
        a_tag = s.find(class_='search_title search-line-music')

        url = a_tag['href']
        file_name = a_tag['title']

        # goto music page
        print('đã tới music page')
        music_page = requests.get(url)
        s_2 = BeautifulSoup(music_page.text, 'lxml')

        signer = s_2.find_all(class_='card-body')[2].ul.li.a.text
        print('Tên ca sĩ là:', signer)
        # get link download
        list_urls = s_2.find_all(class_='download_item')
        if self.quality == '128':
            link_download = list_urls[0]['href']
            urlretrieve(link_download, self.save+'/'+file_name+DownloaderThread.MP3)
        elif self.quality == '320':
            link_download = list_urls[1]['href']
            urlretrieve(link_download, self.save+'/'+file_name+DownloaderThread.MP3)
        elif self.quality == '500':
            link_download = list_urls[2]['href']
            urlretrieve(link_download, self.save+'/'+file_name+DownloaderThread.M4A)
        print('đã tải xong')
        self.download_time = datetime.now()

        self.music_object = music_object(file_name,signer,self.quality,self.download_time,self.save)
        self.signal.emit(self.music_object)


class UpdateThumnail(QThread):
    """Thread này chịu trách nhiệm đọc input của người dùng và lấy về kết quả. Sau đó hiển thị cho người dùng."""

    def __init__(self, input: QLineEdit):
        QThread.__init__()
        self.line = input

    def run(self):
        pass


class MainFrame(QWidget):

    SETTING_FILE = 'settings.json'
    INFO_FILE = 'info.csv'
    PATHS = []

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.parent.setWindowIcon(QIcon('music-note.png'))
        self.parent.setWindowTitle('XRhythm')
        self.setupUI()

    def setupUI(self):
        self.qhbox = QHBoxLayout(self)

        self.group_box_input = QGroupBox('Input',self)
        self.grid_layout = QGridLayout()
        self.group_box_input.setLayout(self.grid_layout)
        self.label_name = QLabel('Tên nhạc:')
        self.line_name = QLineEdit()

        self.label_quality = QLabel('Chất lượng: ')

        self.bttgrp = QButtonGroup()

        self.radio_128 = QRadioButton('128kbps')
        self.radio_320 = QRadioButton('320kbps')

        self.bttgrp.addButton(self.radio_128, 0)
        self.bttgrp.addButton(self.radio_320, 1)

        self.label_save = QLabel('Lưu ở:')
        self.combobox_save = QComboBox(self)
        self.btt_browse = QPushButton('Duyệt...')
        self.btt_browse.clicked.connect(self.browse)

        self.btt_download = QPushButton('Tải')
        self.btt_download.clicked.connect(self.download)

        self.grid_layout.addWidget(self.label_name, 0, 0)
        self.grid_layout.addWidget(self.line_name, 0, 1, 1, 2)
        self.grid_layout.addWidget(self.label_quality, 1, 0)
        self.grid_layout.addWidget(self.radio_128, 1, 1)
        self.grid_layout.addWidget(self.radio_320, 1, 2)
        self.grid_layout.addWidget(self.label_save, 2, 0)
        self.grid_layout.addWidget(self.combobox_save, 2, 1)
        self.grid_layout.addWidget(self.btt_browse, 2, 2)
        self.grid_layout.addWidget(self.btt_download, 3, 0, 1, 3)

        self.qhbox.addWidget(self.group_box_input)
        self.setLayout(self.qhbox)

        self.group_box_result = QGroupBox('Result',self)
        self.qvbox_group_box_result = QVBoxLayout(self)
        self.group_box_result.setLayout(self.qvbox_group_box_result)

        self.table = QTableView(self.group_box_result)
        self.qvbox_group_box_result.addWidget(self.table)

        self.qhbox.addWidget(self.group_box_result)

        self.readSettingFile()

    def createSettingFile(self):
        with open(MainFrame.SETTING_FILE, 'r') as settingFile:
            settings = json.load(settingFile)

        if self.radio_128.isChecked():
            quality = '128'
        else:
            quality = '320'

        # get list items in combobox
        items = []
        for i in range(self.combobox_save.count()):
            items.append(self.combobox_save.itemText(i))

        settings['quality'] = quality
        settings['list_path'] = items
        settings['choice'] = self.combobox_save.currentIndex()

        with open(MainFrame.SETTING_FILE, 'w') as settingFile:
            json.dump(settings, settingFile)

    def readSettingFile(self):
        with open(MainFrame.SETTING_FILE, 'r') as settingFile:
            settings = json.load(settingFile)

        if settings['quality'] == '128':
            self.radio_128.setChecked(True)
        else:
            self.radio_320.setChecked(True)

        for i in settings['list_path']:
            self.combobox_save.addItem(i)

        self.combobox_save.setCurrentIndex(settings['choice'])

    def browse(self):
        path = QFileDialog.getExistingDirectory(self, 'Chọn nơi lưu')
        self.combobox_save.addItem(path)
        self.combobox_save.setCurrentIndex(self.combobox_save.count()-1)

    def download(self):
        print('download')
        if self.line_name.text() == '':
            QMessageBox.warning(self,'Thông báo','Bạn chưa nhập tên bài hát!')
            return
        if self.radio_128.isChecked():
            quality = '128'
        else:
            quality = '320'
        self.download_thread = DownloaderThread(
            self.line_name.text(), quality, self.combobox_save.currentText())
        self.download_thread.signal.connect(self.writeToCsvFile)
        self.download_thread.start()
    
    def writeToCsvFile(self, music_object:music_object):
        with open(self.INFO_FILE,'a',encoding='utf-8') as info_file:
            infoWriter = csv.writer(info_file)
            infoWriter.writerow(music_object.getListInfo())
        self.updateTable()

    def showMessage(self, name_music):
        self.msg_successful = QMessageBox.information(
            self, 'Thông báo cute', 'Đã tải xong bài ' + name_music)


class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 500, 100)
        self.qtRectangle = self.frameGeometry()
        self.centerPoint = QDesktopWidget().availableGeometry().center()
        self.qtRectangle.moveCenter(self.centerPoint)
        self.move(self.qtRectangle.topLeft())

        self.mainFrame = MainFrame(self)
        self.setCentralWidget(self.mainFrame)
        self.show()

    def closeEvent(self, QCloseEvent):
        self.mainFrame.createSettingFile()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = MainApp()
    sys.exit(app.exec_())
