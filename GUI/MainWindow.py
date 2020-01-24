# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from Netease_Cloud_Music.Operation import *
import requests
import os


# 重写滑动条，禁用鼠标点击跳转事件 (https://github.com/PyQt5/PyQt/tree/master/QSlider)
class myQSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super(myQSlider, self).__init__(orientation, parent)

    def mousePressEvent(self, event):
        # 获取上面的拉动块位置
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        rect = self.style().subControlRect(
            QStyle.CC_Slider, option, QStyle.SC_SliderHandle, self)
        if rect.contains(event.pos()):
            # 如果鼠标点击的位置在滑块上则交给Qt自行处理
            super(myQSlider, self).mousePressEvent(event)
            return


# 主窗口类
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 获取首页歌单等信息
        self.img_url_l, self.name_list_l, self.id_list_l = wyy_first_page()
        self.singer, self.singer_id = [], []

        """初始化应用程序"""
        self.setWindowTitle("KK-Music")  # 设置窗口标题
        self.setWindowIcon(QIcon('./ico/kk-music.ico'))  # 设置应用图标
        self.music_list_id = []  # 显示列表中的音乐id存储
        self.player = QMediaPlayer()  # 音乐播放器
        self.player.setVolume(50)  # 设置初始播放音量
        self.player_list = QMediaPlaylist()  # 播放列表
        self.time = QTimer()  # 设置一个定时器
        self.time.stop()  # 最开始不打开定时器
        self.time.timeout.connect(self.music_time_line_adjust)  # 进度条的调整
        self.music_folder_path = ''  # 打开音乐文件夹的路径
        self.music_type = ['mp3', 'flac', 'wav', 'm4a', 'ogg']  # 播放的格式

        # 搜索项
        self.search_layout = QHBoxLayout()  # 创建水平布局
        self.search_text = QLabel("搜索")
        self.search = QLineEdit()  # https://bbs.deepin.org/forum.php?mod=viewthread&tid=181772
        self.search.setPlaceholderText("搜索单曲、歌单、歌手")
        self.search.setEchoMode(QLineEdit.Normal)
        self.search.returnPressed.connect(self.show_search)  # 回车事件
        self.search_layout.addWidget(self.search_text)
        self.search_layout.addWidget(self.search)

        # 首页图片歌单显示
        self.img_all_layout = QGridLayout()  # 采用栅格布局
        for i in range(8):
            self.img = QLabel()
            self.img_file = QPixmap()
            self.img_file.loadFromData(requests.get(self.img_url_l[i]).content)
            self.img.setPixmap(self.img_file)
            self.img_title = QPushButton(self.first_title_display(self.name_list_l[i]))
            self.img_title.setFlat(True)
            self.img_title.setStyleSheet("color: #079775")
            self.img_title.setObjectName(self.id_list_l[i])
            self.img_title.clicked.connect(self.show_playlist)
            if i < 4:
                line = i
            else:
                line = i % 4
            self.img_all_layout.addWidget(self.img, i//4*2, line, 1, 1)
            self.img_all_layout.addWidget(self.img_title, i//4*2+1, line, 1, 1)

        # 进度条和音量条
        self.music_time = QLabel()
        self.music_time.setPixmap(QPixmap("./ico/music.png"))
        self.music_time_start = QLabel("00:00")
        self.music_time_line = myQSlider(Qt.Horizontal)
        self.music_time_line.sliderMoved.connect(self.music_time_adjust)
        self.music_time_stop = QLabel("00:00")
        self.volume = QLabel()
        self.volume.setPixmap(QPixmap("./ico/center_volume.png"))
        self.volume_line = QSlider(Qt.Horizontal)
        self.volume_line.setRange(0, 100)  # 设置取值范围
        self.volume_line.setValue(50)
        self.volume_line.valueChanged.connect(self.volume_adjust)
        self.progress_line_layout = QGridLayout()
        self.progress_line_layout.addWidget(self.music_time, 0, 0, 1, 1)
        self.progress_line_layout.addWidget(self.music_time_start, 0, 1, 1, 1)
        self.progress_line_layout.addWidget(self.music_time_line, 0, 2, 1, 1)
        self.progress_line_layout.addWidget(self.music_time_stop, 0, 3, 1, 1)
        self.progress_line_layout.addWidget(self.volume, 0, 4, 1, 1)
        self.progress_line_layout.addWidget(self.volume_line, 0, 5, 1, 3)

        # 播放按键控制
        self.disc = QLabel()
        self.disc.setPixmap(QPixmap("./ico/disc.png"))
        self.disc.setFixedSize(64, 64)
        self.disc_title = QLabel("暂无播放歌曲")
        self.disc_title.setFixedSize(100, 64)
        self.line = QFrame()  # 创建一条分割线
        self.line.setFrameShape(QFrame.VLine)
        self.bt1 = QPushButton()
        self.bt1.setToolTip("上一首")
        self.bt1.setFlat(True)
        self.bt1.setIcon(QIcon("./ico/on.png"))
        self.bt1.setIconSize(QSize(48, 48))
        self.bt1.setFixedSize(48, 48)
        self.bt1.clicked.connect(self.previous_song)
        self.bt2 = QPushButton()
        self.bt2.setToolTip("播放/暂停")
        self.bt2.setObjectName("start")
        self.bt2.setFlat(True)
        self.bt2.setIcon(QIcon("./ico/start.png"))
        self.bt2.setIconSize(QSize(48, 48))
        self.bt2.setFixedSize(48, 48)
        self.bt2.clicked.connect(self.stop_or_start_song)
        self.bt3 = QPushButton()
        self.bt3.setToolTip("下一首")
        self.bt3.setFlat(True)
        self.bt3.setIcon(QIcon("./ico/de.png"))
        self.bt3.setIconSize(QSize(48, 48))
        self.bt3.setFixedSize(48, 48)
        self.bt3.clicked.connect(self.next_song)
        self.bt4 = QPushButton()
        self.bt4.setToolTip("导入本地音乐文件")
        self.bt4.setFlat(True)
        self.bt4.setIcon(QIcon("./ico/open_folder.png"))
        self.bt4.setIconSize(QSize(48, 48))
        self.bt4.setFixedSize(48, 48)
        self.bt4.clicked.connect(self.open_folder)
        self.bt_layout = QHBoxLayout()
        self.bt_layout.addWidget(self.disc)
        self.bt_layout.addWidget(self.disc_title)
        self.bt_layout.addWidget(self.line)
        self.bt_layout.addWidget(self.bt1)
        self.bt_layout.addWidget(self.bt2)
        self.bt_layout.addWidget(self.bt3)
        self.bt_layout.addWidget(self.bt4)

        # 歌单表格显示
        self.music_list = QListWidget()
        self.music_list.itemDoubleClicked.connect(self.music_list_song)

        # 主要布局
        self.center_layout = QVBoxLayout()
        self.center_layout.addLayout(self.search_layout)
        self.center_layout.addLayout(self.img_all_layout)
        self.center_layout.addLayout(self.progress_line_layout)
        self.center_layout.addLayout(self.bt_layout)
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addWidget(self.music_list)
        self.setLayout(self.main_layout)

    # 首页歌单标题按规定长度显示
    def first_title_display(self, title):
        if len(title) > 27:
            return title[:9] + '\n' + title[9:18] + '\n' + title[18:27] + '\n' + title[27:]
        elif len(title) > 18:
            return title[:9] + '\n' + title[9:18] + '\n' + title[18:]
        elif len(title) > 9:
            return title[:9] + '\n' + title[9:]
        else:
            return title

    # 显示歌单中的歌曲和直接播放dj电台
    def show_playlist(self):
        send = self.sender()
        id_str = send.objectName()
        id_num = id_str.split('=')[1]
        if id_str[1] == 'p':  # 判断点击的是类型是歌单
            self.name_list_l, self.music_list_id = playlist_info(id_num)
            self.music_list.clear()  # 清空当前列表
            self.player_list.clear()  # 清空歌单列表
            self.music_list.setObjectName("playlist")
            self.player_list.setCurrentIndex(0)  # 点击新的歌单后，默认播放0
            # 加入选中歌单中的歌曲名
            for i in range(len(self.name_list_l)):
                temp = QListWidgetItem(self.name_list_l[i])
                temp.setIcon(QIcon("./ico/song.png"))
                temp.setToolTip("双击播放")
                self.music_list.addItem(temp)
        elif id_str[1] == 'd':  # 判断点击的类型是dj电台
            self.player.setMedia(QMediaContent(QUrl(dj_url(id_num))))  # 设置音频网址
            self.disc_title.setText("欢迎收听\n电台栏目")
            self.set_music_time_line()

    # 显示搜索结果
    def show_search(self):
        self.name_list_l, self.music_list_id, self.singer, self.singer_id = single_search(self.search.text())
        self.music_list.clear()
        self.music_list.setObjectName("search")
        for i in range(len(self.name_list_l)):
            temp = QListWidgetItem(self.name_list_l[i] + "@---->&歌手---->  " + self.singer[i])
            temp.setIcon(QIcon("./ico/song.png"))
            temp.setToolTip("双击播放")
            self.music_list.addItem(temp)

    # 双击列表中的歌曲播放
    def music_list_song(self):
        index = self.music_list.currentRow()
        music_id = self.music_list_id[index]
        if self.music_list.objectName() == "music_folder":
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(music_id)))
            self.set_disc_title()
            self.set_music_time_line()
            return
        url = song_url(music_id)
        if url == "No":
            QMessageBox.about(self, "抱歉", "由于版权原因\n我们不能向您播放该音乐")
        else:
            self.player.stop()
            self.player.setMedia(QMediaContent(QUrl(url)))
            self.set_disc_title()
            self.set_music_time_line()

    # 进度条调节
    def music_time_line_adjust(self):
        self.music_time_line.setValue(self.music_time_line.value()+1)
        self.music_time_start.setText(
            str(self.music_time_line.value() // 60).zfill(2) + ':' + str(self.music_time_line.value() % 60).zfill(2)
        )
        if self.music_time_line.value() == 1:
            self.music_time_line.setRange(0, int(self.player.duration() / 1000))
            self.music_time_stop.setText(
                str(int(self.player.duration() / 1000) // 60).zfill(2) + ':' + str(int(self.player.duration() / 1000) % 60).zfill(2)
            )
        if self.music_time_line.value() == self.music_time_line.maximum():
            self.music_time_line.setValue(0)
            self.music_time_start.setText("00:00")
            self.music_time_stop.setText("00:00")
            self.bt2.setObjectName("start")
            self.bt2.setIcon(QIcon("./ico/start.png"))
            self.time.stop()
            self.next_song()

    # 歌曲时间调整
    def music_time_adjust(self):
        self.player.setPosition(self.music_time_line.value() * 1000)

    # 设置进度条，播放音乐
    def set_music_time_line(self):
        self.music_time_line.setValue(0)
        self.time.start(1000)
        self.player.play()
        self.bt2.setIcon(QIcon("./ico/stop.png"))
        self.bt2.setObjectName("stop")

    # 音量调节
    def volume_adjust(self):
        self.player.setVolume(self.volume_line.value())
        if self.volume_line.value() == 0:
            self.volume.setPixmap(QPixmap("./ico/no_volume.png"))
        elif self.volume_line.value() < 30:
            self.volume.setPixmap(QPixmap("./ico/small_volume.png"))
        elif self.volume_line.value() < 70:
            self.volume.setPixmap(QPixmap("./ico/center_volume.png"))
        else:
            self.volume.setPixmap(QPixmap("./ico/high_volume.png"))

    # 暂停功能或则继续播放
    def stop_or_start_song(self):
        if self.bt2.objectName() == "start":
            self.player.play()
            self.time.start(1000)
            self.bt2.setIcon(QIcon("./ico/stop.png"))
            self.bt2.setObjectName("stop")
        elif self.bt2.objectName() == "stop":
            self.player.pause()
            self.time.stop()
            self.bt2.setIcon(QIcon("./ico/start.png"))
            self.bt2.setObjectName("start")

    # 上一首功能
    def previous_song(self):
        if len(self.music_list) == 0 or self.music_list.currentRow() == -1:
            QMessageBox.about(self, "kk-music", "您的播放列表为空\n未检测到当前播放位置")
        else:
            self.player.stop()
            url = ""
            index = self.music_list.currentRow()
            while True:
                if index == 0:
                    index = len(self.music_list_id) - 1
                else:
                    index = index - 1
                if self.music_list.objectName() == "music_folder":
                    url = self.music_list_id[index]
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(url)))
                    break
                url = song_url(self.music_list_id[index])
                if url != "No":
                    self.player.setMedia(QMediaContent(QUrl(url)))
                    break
            self.music_list.setCurrentRow(index)
            self.set_disc_title()
            self.set_music_time_line()

    # 下一首功能
    def next_song(self):
        if len(self.music_list) == 0 or self.music_list.currentRow() == -1:
            QMessageBox.about(self, "kk-music", "您的播放列表为空\n未检测到当前播放位置")
        else:
            self.player.stop()
            url = ""
            index = self.music_list.currentRow()
            while True:
                if index == len(self.music_list_id) - 1:
                    index = 0
                else:
                    index = index + 1
                if "music_folder" == self.music_list.objectName():
                    url = self.music_list_id[index]
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(url)))
                    break
                url = song_url(self.music_list_id[index])
                if url != "No":
                    self.player.setMedia(QMediaContent(QUrl(url)))
                    break
            self.music_list.setCurrentRow(index)
            self.set_disc_title()
            self.set_music_time_line()

    # 打开文件夹
    def open_folder(self):
        self.music_folder_path = QFileDialog.getExistingDirectory(self, "选取音乐文件夹", self.music_folder_path)
        if self.music_folder_path != '':
            self.music_list.clear()
            self.music_list.setObjectName("music_folder")
            self.name_list_l = []
            self.music_list_id = []
            for i in os.listdir(self.music_folder_path):
                music_name, music_type = i.split('.')[0], i.split('.')[1]
                if music_type in self.music_type:
                    temp = QListWidgetItem(music_name)
                    temp.setIcon(QIcon("./ico/song.png"))
                    temp.setToolTip("双击播放")
                    self.name_list_l.append(music_name)
                    self.music_list_id.append(self.music_folder_path + '/' + i)
                    self.music_list.addItem(temp)

    # 歌曲标题显示
    def set_disc_title(self):
        index = self.music_list.currentRow()
        if self.music_list.objectName() == "playlist" or self.music_list.objectName() == "music_folder":
            self.disc_title.setText(self.name_list_l[index])
        elif self.music_list.objectName() == "search":
            self.disc_title.setText(self.name_list_l[index] + '\n' + self.singer[index])


if __name__ == '__main__':
    pass
