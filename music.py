#!/usr/bin/bin/env python
# -*- coding: utf-8 -*-
import sys

from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon


class MusicPlayer(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()

        self.current_index = 0
        self.sources = []
        self.current_name = ''

        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.media_object = Phonon.MediaObject(self)
        Phonon.createPath(self.media_object, self.audio_output)
        self.setup_ui()

        self.media_object.setTickInterval(1000)
        self.music_table.doubleClicked.connect(self.shift)
        self.stop_button.clicked.connect(self.stop)
        self.next_button.clicked.connect(self.next_f)
        self.pre_button.clicked.connect(self.pre_f)
        self.pause_button.clicked.connect(self.pause)
        self.media_object.currentSourceChanged.connect(self.source_changed)
        self.media_object.aboutToFinish.connect(self.about_to_finish)
        self.media_object.tick.connect(self.tick)
        self.media_object.stateChanged.connect(self.state_changed)
        self.last_select_position = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation)



    def load_lyric(self):
        pass

    def source_changed(self, source):
        #self.load_lyric()
        self.current_time_label.setText('00:00')
        file_path = source.fileName()
        file_info = QtCore.QFileInfo(file_path)
        file_name = file_info.baseName()
        self.name_label.setText(file_name)

    def tick(self, time):
        display_time = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.current_time_label.setText(display_time.toString('mm:ss'))

    def state_changed(self, new_state):
        '''当播放器状态改变时，需要改变按钮和相关label的文件。

        '''
        if new_state == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                        self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                        self.mediaObject.errorString())
        elif new_state == Phonon.PlayingState:
            total_time = self.media_object.totalTime()
            display_time = QtCore.QTime(0, (total_time / 60000) % 60, (total_time / 1000) % 60)
            self.total_time_label.setText(display_time.toString('mm:ss'))
            self.stop_button.setText(u'停止')
            self.stop_button.setEnabled(True)
            self.pause_button.setText(u'暂停')
            self.pause_button.setEnabled(True)
        elif new_state == Phonon.StoppedState:
            self.stop_button.setText(u'播放')
            self.stop_button.setEnabled(True)
            self.pause_button.setText(u'暂停')
            self.pause_button.setEnabled(False)
        elif new_state == Phonon.PausedState:
            self.stop_button.setText(u'停止')
            self.stop_button.setEnabled(True)
            self.pause_button.setText(u'恢复')
            self.pause_button.setEnabled(True)

    def about_to_finish(self):
        self.music_table.setItemSelected(self.music_table.item(self.current_index, 0), False)
        self.current_index = (self.current_index + 1) % len(self.sources)
        self.media_object.enqueue(self.sources[self.current_index])
        self.music_table.setItemSelected(self.music_table.item(self.current_index, 0), True)

    def next_f(self):
        if len(self.sources):
            self.current_index = (self.current_index + 1) % len(self.sources)
            self.media_object.stop()
            self.media_object.clearQueue()
            self.media_object.setCurrentSource(self.sources[self.current_index])
            self.media_object.play()

    def pre_f(self):
        if len(self.sources):
            self.current_index = (self.current_index - 1) % len(self.sources)
            self.media_object.stop()
            self.media_object.clearQueue()
            self.media_object.setCurrentSource(self.sources[self.current_index])
            self.media_object.play()

    def pause(self):
        if self.media_object.state() == Phonon.PlayingState:
            self.media_object.pause()
        elif self.media_object.state() == Phonon.PausedState:
            self.media_object.play()

    def stop(self):
        if self.media_object.state() == Phonon.PlayingState:
            self.media_object.stop()
        elif self.media_object.state() == Phonon.StoppedState:
            self.media_object.play()

    def shift(self):
        index = self.music_table.row((self.music_table.selectedItems()[0]))
        self.current_index = index
        self.media_object.stop()
        self.media_object.clearQueue()
        self.media_object.setCurrentSource(self.sources[index])
        self.media_object.play()

    def add_files(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, "Select Music Files",
                                                   self.last_select_position,
                                                   "Music(*.mp3 *.wma)")

        if not files:
            return

        file_info = QtCore.QFileInfo(files[0])
        self.last_select_position = file_info.absolutePath()
        for string in files:
            self.sources.append(Phonon.MediaSource(string))
            current_row = self.music_table.rowCount()
            self.music_table.insertRow(current_row)
            file_info = QtCore.QFileInfo(string)
            file_name = file_info.baseName()
            self.music_table.setItem(current_row, 0, QtGui.QTableWidgetItem(file_name))

        self.music_table.resizeColumnsToContents()

        if not self.music_table.selectedItems():
            self.music_table.setItemSelected(self.music_table.item(0, 0), True)
            self.current_index = 0
            self.media_object.setCurrentSource(self.sources[0])

    def showContextMenu(self, pos):
        pass

    def setup_ui(self):

        headers = ("Name", "")
        self.music_table = QtGui.QTableWidget(0, 1)
        self.music_table.setHorizontalHeaderLabels(headers)
        self.music_table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.music_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.music_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.music_table.customContextMenuRequested.connect(self.showContextMenu)

        self.name_label = QtGui.QLabel(self.current_name)
        label_layout = QtGui.QHBoxLayout()
        label_layout.addWidget(QtGui.QLabel(u'当前播放： '))
        label_layout.addWidget(self.name_label)

        self.seek_slider = Phonon.SeekSlider(self)
        self.seek_slider.setMediaObject(self.media_object)

        self.volume_slider = Phonon.VolumeSlider(self)
        self.volume_slider.setAudioOutput(self.audio_output)
        self.volume_slider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                         QtGui.QSizePolicy.Maximum)
        self.current_time_label = QtGui.QLabel('00:00')
        self.total_time_label = QtGui.QLabel()
        slider_layout = QtGui.QHBoxLayout()
        slider_layout.addWidget(self.current_time_label)
        slider_layout.addWidget(self.seek_slider)
        slider_layout.addWidget(self.total_time_label)
        slider_layout.addWidget(self.volume_slider)

        self.pre_button = QtGui.QPushButton(u'上一首')
        self.stop_button = QtGui.QPushButton(u'播放')
        self.pause_button = QtGui.QPushButton(u'暂停')
        self.next_button = QtGui.QPushButton(u'下一首')

        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.pre_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.next_button)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.music_table)
        main_layout.addLayout(label_layout)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(button_layout)

        self.add_file_action = QtGui.QAction("Add Files", self,
                                             triggered=self.add_files)
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.add_file_action)

        widget = QtGui.QWidget()
        widget.setLayout(main_layout)

        self.setCentralWidget(widget)
        self.setWindowTitle("Music Player")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Music Player")

    window = MusicPlayer()
    window.show()

    sys.exit(app.exec_())
