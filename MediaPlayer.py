import sys
import os
import csv
import subprocess
import LoginPart.Login as Login
import SearchPart.tag as Tag
import SettingPart.Setting as Setting
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QFileDialog, QLineEdit, QListWidget, QSlider, QShortcut
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QKeySequence

Form = uic.loadUiType(os.path.join(os.getcwd(), 'Mediaplayer.ui'))[0]


class MediaPlayer(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)
        # Video Part
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.videowidget)
        self.setWindowTitle(" Media Player")
        self.sch_listWidget = QListWidget(self)
        self.search_lineEdit = QLineEdit(self)
        self.sch_listWidget.setVisible(False)
        self.search_lineEdit.setVisible(False)
        self.mouseReleaseEvent = self.MainWindow_Event
        self.resizeEvent = self.main_size_Change
        self.search_Thread = None
        self.write_Bookmark = QLineEdit(self)
        self.write_Bookmark.setVisible(False)
        self.write_Bookmark.returnPressed.connect(self.save_Bookmarks)
        self.movie_Name = None

        self.search_lineEdit.setPlaceholderText("search Tags here")
        self.write_Bookmark.setPlaceholderText("write bookmark here")


        # Create Tags
        self.TagDB = None

        # create Volume Slide
        self.Slider_Volume = Slider(self)
        self.Slider_Volume.setOrientation(Qt.Horizontal)
        self.horizontalLayout_3.addWidget(self.Slider_Volume, 0)
        self.Slider_Volume.setMaximumWidth(90)
        self.Slider_Volume.setMaximumHeight(20)

        # create Play Slider
        self.Slider_Play = Slider(self)
        self.Slider_Play.setOrientation(Qt.Horizontal)
        self.Slider_Play.resize(644, 22)
        self.horizontalLayout_4.addWidget(self.Slider_Play, 1)
        self.horizontalLayout_4.addWidget(self.label_Time, 0)

        # PushButtton
        self.pushButton_Start.setEnabled(False)
        self.pushButton_Start.clicked.connect(self.start)

        self.pushButton_volume.setEnabled(False)
        self.pushButton_volume.clicked.connect(self.volumeOnOff)

        self.pushButton_stop.setEnabled(False)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_stop.setToolTip("Stop")

        self.pushButton_next.setEnabled(False)
        self.pushButton_next.clicked.connect(self.next)
        self.pushButton_next.setToolTip("Next")

        self.pushButton_previous.setEnabled(False)
        self.pushButton_previous.clicked.connect(self.previous)
        self.pushButton_previous.setToolTip("Previous")

        self.pushButton_open.clicked.connect(self.Load_video)
        self.pushButton_open.setToolTip("Open")

        self.pushButton_Search.clicked.connect(self.sch_icon_Event)
        self.pushButton_Search.setToolTip("Search")

        self.pushButton_BookMark.setVisible(False)
        self.pushButton_BookMark.clicked.connect(self.add_BookMarks)
        self.pushButton_BookMark.setToolTip("Add BookMark")

        self.pushButton_Setting.clicked.connect(self.Settingshow)
        self.pushButton_Setting.setToolTip("Setting")

        # Slider Play
        self.Slider_Play.setRange(0, 0)
        self.player.positionChanged.connect(self.Position_changed)
        self.player.durationChanged.connect(self.Duration_changed)
        self.Slider_Play.setUP_Slider.connect(self.Set_Position)

        # Slider Volume
        self.Slider_Volume.setRange(0, 0)
        self.Slider_Volume.setUP_Slider.connect(self.Set_volume)

        # Tool Bar
        self.actionOpen.triggered.connect(self.Load_video)
        self.actionLogOut.triggered.connect(self.Logout)
        self.actionExit.triggered.connect(lambda: self.close())
        self.actionFullScreen.triggered.connect(self.fullscreen)

        # Search
        self.sch_listWidget.itemDoubleClicked.connect(self.item_Event)
        self.search_lineEdit.textChanged.connect(self.search_Tag)

        # self.lineEdit_GoTo.textChanged.connect(self.GoTO)

        # Shortcut
        QShortcut(QKeySequence('Ctrl+B'),
                  self).activated.connect(self.add_BookMarks)
        QShortcut(QKeySequence('Ctrl+Z'),
                  self).activated.connect(self.stop)
        QShortcut(QKeySequence('Ctrl+M'),
                  self).activated.connect(self.volumeOnOff)
        QShortcut(QKeySequence('Ctrl+S'),
                  self).activated.connect(self.sch_icon_Event)
        QShortcut(QKeySequence('Ctrl+O'),
                  self).activated.connect(self.Load_video)

    def add_BookMarks(self):
        if self.player.isVideoAvailable() or self.player.isAudioAvailable():
            self.write_Bookmark.resize(
                int((200 / 800) * self.size().width()), self.pushButton_BookMark.geometry().height())
            self.write_Bookmark.move(
                int(self.pushButton_BookMark.x()+25), 31)
            self.write_Bookmark.setVisible(True)
            self.write_Bookmark.setFocus()

    # KeyPress Event
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and self.pushButton_Start.isEnabled():
            self.start()
        if event.key() == Qt.Key_PageDown and self.pushButton_next.isEnabled():
            self.next()
        if event.key() == Qt.Key_PageUp and self.pushButton_previous.isEnabled():
            self.previous()
        if event.key() == Qt.Key_5:
            self.fullscreen()

    def fullscreen(self):

        self.pushButton_Start.setVisible(self.isFullScreen())
        self.pushButton_stop.setVisible(self.isFullScreen())
        self.pushButton_previous.setVisible(self.isFullScreen())
        self.pushButton_open.setVisible(self.isFullScreen())
        self.pushButton_next.setVisible(self.isFullScreen())
        self.pushButton_Setting.setVisible(self.isFullScreen())
        self.pushButton_volume.setVisible(self.isFullScreen())
        self.Slider_Play.setVisible(self.isFullScreen())
        self.Slider_Volume.setVisible(self.isFullScreen())
        self.label_Time.setVisible(self.isFullScreen())
        self.menubar.setVisible(self.isFullScreen())
        self.pushButton_Search.setVisible(self.isFullScreen())
        self.pushButton_BookMark.setVisible(self.isFullScreen())

        if not self.isFullScreen():
            self.verticalLayout.removeWidget(self.videowidget)
            screenWidth = QApplication.desktop().screenGeometry().width()
            screenHeight = QApplication.desktop().screenGeometry().height()
            self.videowidget.resize(screenWidth, screenHeight)
            self.videowidget.move(0, 0)
            self.showFullScreen()

        else:
            self.verticalLayout.addWidget(self.videowidget, 1)
            self.verticalLayout.removeItem(self.horizontalLayout_4)
            self.verticalLayout.addLayout(self.horizontalLayout_4, 0)
            self.showNormal()

    def Settingshow(self):
        settingw = Setting.SettingWindow(self)
        settingw.show()

    def start(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.pushButton_Start.setEnabled(True)
            self.pushButton_Start.setIcon(QIcon('./Icons/play.png'))
            self.pushButton_Start.setToolTip("Play")

        else:
            self.player.play()
            self.pushButton_Start.setEnabled(True)
            self.pushButton_Start.setIcon(QIcon('./Icons/pause.png'))
            self.pushButton_Start.setToolTip("Pause")

    def stop(self):
        if self.player.isAudioAvailable() or self.player.isVideoAvailable():
            self.player.stop()
            self.pushButton_next.setEnabled(False)
            self.pushButton_previous.setEnabled(False)
            self.pushButton_volume.setEnabled(False)
            self.pushButton_Start.setEnabled(False)
            self.pushButton_stop.setEnabled(False)
            self.pushButton_BookMark.setVisible(False)

    def next(self):
        self.FileName = self.Files[self.Files.index(self.FileName)+1]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(
            os.path.join(self.File_Path, self.FileName))))
        self.setWindowTitle(f" Media Player - {self.FileName}")
        self.start()
        if self.FileName == self.Files[-1]:
            self.pushButton_next.setEnabled(False)
        else:
            self.pushButton_previous.setEnabled(True)

    def previous(self):
        self.FileName = self.Files[self.Files.index(self.FileName)-1]
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(
            os.path.join(self.File_Path, self.FileName))))
        self.setWindowTitle(f" Media Player - {self.FileName}")
        self.start()
        if self.FileName == self.Files[0]:
            self.pushButton_previous.setEnabled(False)
        else:
            self.pushButton_next.setEnabled(True)

    def Load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open video", directory=os.path.join(os.getcwd(), 'Video'))

        if file_path:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.start()
            self.pushButton_volume.setEnabled(True)
            self.pushButton_volume.setIcon(QIcon('./Icons/unmute.png'))
            self.pushButton_volume.setToolTip("Mute")
            if not self.isFullScreen():
                self.pushButton_BookMark.setVisible(True)
            self.pushButton_stop.setEnabled(True)
            self.Slider_Volume.setRange(0, self.player.volume())
            self.Set_volume(80)
            self.FileName = file_path.split("/")[-1]
            self.setWindowTitle(f" Media Player - {self.FileName}")
            self.File_Path = file_path.replace(f"/{self.FileName}", "")
            self.Files = os.listdir(self.File_Path)
            if not self.FileName == self.Files[0]:
                self.pushButton_previous.setEnabled(True)
            if not self.FileName == self.Files[-1]:
                self.pushButton_next.setEnabled(True)

    def Position_changed(self, position):
        if position > self.player.duration():
            position = self.player.duration()
        hour = position//(1000*3600)
        minute = (position % (1000*3600))//(60*1000)
        second = ((position % (1000*3600)) % (60*1000))//1000
        # Show Time
        self.label_Time.setText(
            f'{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(second).zfill(2)}')
        # Automatic Next
        if self.player.duration() and position == self.player.duration():
            if self.pushButton_next.isEnabled():
                self.next()
            else:
                self.stop()
        self.Slider_Play.setValue(position)

    def Duration_changed(self, duration):
        self.Slider_Play.setRange(0, duration)

    def Set_Position(self, position):
        if self.Slider_Play.width()-1 <= position:
            position = self.Slider_Play.width()-1
            self.player.pause()
            self.pushButton_Start.setEnabled(True)
            self.pushButton_Start.setIcon(QIcon('./Icons/play.png'))
            self.pushButton_Start.setToolTip("Paly")

        # if not (position < 0 and position > self.Slider_Play.width()):
        position = int(self.player.duration() *
                       (position / self.Slider_Play.width()))
        self.Slider_Play.setValue(position)
        self.player.setPosition(position)

    def Set_volume(self, volume):
        # self.Slider_Volume.setValue(volume)
        if 100 <= volume:
            volume = 100
        elif volume <= 0:
            volume = 0
        if not volume:
            self.player.setMuted(True)
            self.pushButton_volume.setIcon(QIcon('./Icons/mute.png'))
            self.pushButton_volume.setToolTip("UnMute")

        else:
            self.player.setMuted(False)
            self.pushButton_volume.setIcon(QIcon('./Icons/unmute.png'))
            self.pushButton_volume.setToolTip("Mute")

        self.Slider_Volume.setValue(volume)
        self.player.setVolume(volume)

    def volumeOnOff(self):
        if self.player.isAudioAvailable() or self.player.isVideoAvailable():
            if self.player.isMuted():
                self.player.setMuted(False)
                self.pushButton_volume.setIcon(QIcon('./Icons/unmute.png'))
                self.pushButton_volume.setToolTip("Mute")

            else:
                self.player.setMuted(True)
                self.pushButton_volume.setIcon(QIcon('./Icons/mute.png'))
                self.pushButton_volume.setToolTip("UnMute")

    def save_Bookmarks(self):
        self.write_Bookmark.setVisible(False)
        try:
            path = os.path.join(os.getcwd(), "bookmarks")
            os.mkdir(path)
        except:
            pass

        try:
            with open("LoginPart/User.csv") as iFile:
                User = csv.reader(iFile, delimiter=',')
                for row in User:
                    admin = row[0]
            with open(f"{os.getcwd()}/bookmarks/{admin}.csv", "a", newline="") as csvfile:
                employee_writer = csv.writer(csvfile, delimiter=',')
                employee_writer.writerow(
                    [self.FileName, self.write_Bookmark.text(), self.label_Time.text()])
        except:
            pass
        self.write_Bookmark.setText("")

    def sch_icon_Event(self):

        # create QLineEdit
        self.search_lineEdit.resize(
            int((200 / 800) * self.size().width()), self.pushButton_Search.geometry().height())
        # Is not FullScreen
        if not self.isFullScreen():
            self.search_lineEdit.move(
                int(self.pushButton_Search.x() - (200 / 800) * self.size().width()), 31)

        # Is FullScreen
        else:
            self.search_lineEdit.move(
                int((600 / 800) * self.size().width())-self.pushButton_Search.geometry().width(), 31)

        self.search_lineEdit.setVisible(True)
        self.search_lineEdit.setFocus()

    def MainWindow_Event(self, type):

        self.search_lineEdit.setText("")
        self.search_lineEdit.setVisible(False)

        self.write_Bookmark.setText("")
        self.write_Bookmark.setVisible(False)

        self.sch_listWidget.setVisible(False)
        self.sch_listWidget.clear()

    def main_size_Change(self, val):

        self.write_Bookmark.resize(
            int((200 / 800) * self.size().width()), self.pushButton_Search.geometry().height())
        self.write_Bookmark.move(
            int(self.pushButton_BookMark.x() + self.pushButton_Search.geometry().width()), 31)

        self.sch_listWidget.resize(
            int((200 / 800) * self.size().width()), int((200 / 600) * self.size().height()))
        self.sch_listWidget.move(
            int(self.pushButton_Search.x() - (200 / 800) * self.size().width()), 52)

        self.search_lineEdit.resize(
            int((200 / 800) * self.size().width()), self.pushButton_Search.geometry().height())
        self.search_lineEdit.move(
            int(self.pushButton_Search.x() - (200 / 800) * self.size().width()), 31)

    def item_Event(self, item):
        print(item.text())

    def search_Tag(self, val):

        # create QListWidget
        self.sch_listWidget.resize(
            int((200 / 800) * self.size().width()), int((200 / 600) * self.size().height()))
        # Is Not FullScreen
        if not self.isFullScreen():
            self.sch_listWidget.move(
                int(self.pushButton_Search.x() - (200 / 800) * self.size().width()), 52)

        # Is FullScreen
        else:
            self.sch_listWidget.move(
                int((600 / 800) * self.size().width())-self.pushButton_Search.geometry().width(), 52)

        self.sch_listWidget.setVisible(True)

        # start search thread
        self.search_Thread = search_thread(self, val)
        self.search_Thread.update_schTag.connect(self.update_Tags)
        self.search_Thread.start()

    def update_Tags(self, tagsList):
        self.sch_listWidget.clear()

        for key in tagsList:
            self.sch_listWidget.addItem(key)

        self.search_Thread = None

    # def GoTO(self, time):
    #     self.Slider_Play.setValue(int(time)*1000)
    #     self.player.setPosition(int(time)*1000)

    def Create_Tags(self, directory):
        self.TagDB = Tag.tag("SearchPart/1")

    def Logout(self):
        os.remove("LoginPart/User.csv")
        self.close()
        self.player.stop()
        subprocess.call(['python', 'MediaPlayer.py'])


# Custome play slider
class Slider(QSlider):
    setUP_Slider = QtCore.pyqtSignal(int)

    def __init__(self, MediaPlayer):
        QSlider.__init__(self, parent=MediaPlayer)

    def mousePressEvent(self, position):
        self.setUP_Slider.emit(position.pos().x())

    def mouseMoveEvent(self, position):
        self.setUP_Slider.emit(position.x())


# thread for searching in tags
class search_thread(QtCore.QThread):
    update_schTag = QtCore.pyqtSignal(list)

    def __init__(self, window, val):
        self.val = val
        self.Parent = window
        QtCore.QThread.__init__(self, parent=window)

    def run(self):
        if self.Parent.TagDB:
            sch_Tags = self.Parent.TagDB.find_Closest_to(self.val)
            self.update_schTag.emit(sch_Tags)
        else:
            self.update_schTag.emit([])


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    if os.path.exists("LoginPart/User.csv"):
        Mainw = MediaPlayer()
        Mainw.show()
        app.exec_()
    else:
        Loginw = Login.LoginWindow()
        Loginw.show()
        app.exec_()
        if Loginw.LoginAccept():
            Mainw = MediaPlayer()
            Mainw.show()
            app.exec_()
