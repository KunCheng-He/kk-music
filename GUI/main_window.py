from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap, QIcon
from GUI.music_window import Ui_kk_music
from Netease_Cloud_Music import NCOperation
import threading
import random
import requests
import time
import json
import os


# 首页歌单标题按规定长度显示
def first_title_display(title):
    if len(title) > 18:
        return title[:9] + '\n' + title[9:18] + '\n' + title[18:]
    elif len(title) > 9:
        return title[:9] + '\n' + title[9:]
    else:
        return title


# 定义一个数据表的类，用来存储数据
class GUI_Data:
    def __init__(self):
        self.img_url = []  # 首页图片显示的url
        self.bt_name = []  # 首页按键的标题
        self.bt_id = []  # 首页按键的id值

        self.music_name = []  # 歌曲列表显示区域
        self.music_id = []  # 歌曲列表显示的ID

        self.pre_music_index = 0  # 上一首歌的index

        self.folder_path = ''  # 打开音乐文件夹的路径
        self.music_type = ['mp3', 'flac', 'wav', 'm4a', 'ogg']  # 播放的格式

        self.my_playlist_name = []  # 我的歌单名
        self.my_playlist_text = {}  # 我的歌单数据


# 主窗口
class Main_window(QWidget, Ui_kk_music):
    def __init__(self):
        super(Main_window, self).__init__()
        self.setupUi(self)

        # 一些量的定义
        self.disc.setObjectName("")
        self.copyright_flag = False  # 版权标志位
        self.date = GUI_Data()  # 数据表
        self.lock = threading.Lock()  # 数据锁
        self.player = QMediaPlayer()  # 音乐播放器
        self.player.setVolume(50)  # 设置初始播放音量
        self.time = QTimer()  # 设置一个定时器
        self.music_start_stop.setObjectName("start")
        self.time.start(1000)  # 定时一秒
        self.img_list = [
            self.img0, self.img1, self.img2, self.img3,
            self.img4, self.img5, self.img6, self.img7
        ]
        self.title_list = [
            self.title0, self.title1, self.title2, self.title3,
            self.title4, self.title5, self.title6, self.title7
        ]

        # 首页显示和本地歌单加载
        self.first_page_thread()
        self.load_my_playlist_thread()

        # 逻辑处理
        self.initUI()

    # 后台的逻辑处理
    def initUI(self):
        self.time.timeout.connect(self.timeout_process)  # 计时时间到了以后的处理函数
        self.music_start_stop.clicked.connect(self.stop_or_start_song)  # 播放暂停
        self.volume_line.valueChanged.connect(self.volume_adjust)  # 拖动音量条改变音量
        self.time_line.sliderMoved.connect(self.music_time_adjust)  # 拖动进度条改变播放进度
        self.time_line.sliderReleased.connect(self.music_time_adjust_over)  # 拖动进度条调整完成，拖动调节分成两步，播放本地音乐时可去除杂音
        self.listview.itemDoubleClicked.connect(self.music_double_click_thread)  # 双击播放音乐
        self.src_choose.currentTextChanged.connect(self.first_page_thread)  # 更改音乐源时触发的事件
        self.search_edit.returnPressed.connect(self.search_thread)  # 搜索结果
        self.localhost.clicked.connect(self.local_music_thread)  # 打开本地音乐
        self.downloads.clicked.connect(self.downloads_music_thread)  # 下载音乐
        self.song_modle.clicked.connect(self.change_modle)  # 播放模式改变
        self.music_next.clicked.connect(self.next_music_thread)  # 下一首线程
        self.music_pre.clicked.connect(self.pre_music_thread)  # 上一首线程
        self.new_playlist.clicked.connect(self.create_playlist_thread)  # 新建我的歌单线程
        self.delete_playlist.clicked.connect(self.delete_my_playlist)  # 删除我的歌单
        self.add_to_playlist.clicked.connect(self.add_my_playlist_thread)  # 将当前播放音乐加入我的歌单线程
        self.myplaylist_list.itemDoubleClicked.connect(self.click_my_playlist_thread)
        for i in self.title_list:
            i.clicked.connect(self.first_playlist_dj)  # 首页歌单和电台点击播放

    # 首页变换线程
    def first_page_thread(self):
        first_page_display = threading.Thread(target=self.set_first_date)
        first_page_display.start()

    # 我的歌单加载线程
    def load_my_playlist_thread(self):
        load_playlist = threading.Thread(target=self.load_playlist)
        load_playlist.start()

    # 首页点击线程
    def first_click_thread(self):
        first_click = threading.Thread(target=self.first_playlist_dj)
        first_click.start()

    # 双击播放线程
    def music_double_click_thread(self):
        double_click = threading.Thread(target=self.list_view_song)
        double_click.start()

    # 搜索线程
    def search_thread(self):
        if self.search_edit.text():
            search = threading.Thread(target=self.show_search)
            search.start()

    # 下载线程
    def downloads_music_thread(self):
        if self.disc_title.text():
            self.date.folder_path = QFileDialog.getExistingDirectory(self, "下载保存路径", self.date.folder_path)
            down = threading.Thread(target=self.downloads_music)
            down.start()

    # 本地音乐线程
    def local_music_thread(self):
        self.date.folder_path = QFileDialog.getExistingDirectory(self, "选取音乐文件夹", self.date.folder_path)
        local = threading.Thread(target=self.open_folder_song)
        local.start()

    # 下一首线程
    def next_music_thread(self):
        next_music = threading.Thread(target=self.next_music)
        next_music.start()

    # 上一首线程
    def pre_music_thread(self):
        pre_music = threading.Thread(target=self.pre_music)
        pre_music.start()

    # 新建歌单线程
    def create_playlist_thread(self):
        text, ok = QInputDialog.getText(self, "新建歌单", "请输入歌单名")
        create = threading.Thread(target=self.create_my_playlist, args=(text, ok))
        create.start()

    # 加入我的歌单线程
    def add_my_playlist_thread(self):
        if self.disc_title.text():
            text, ok = QInputDialog.getItem(self, "选择要加入的歌单", "歌单名", self.date.my_playlist_name, 0, False)
            add_playlist = threading.Thread(target=self.add_my_playlist, args=(text, ok))
            add_playlist.start()

    # 点击显示我的歌单线程
    def click_my_playlist_thread(self):
        temp = threading.Thread(target=self.click_my_playlist)
        temp.start()

    # 计时时间到了做处理
    def timeout_process(self):
        if self.music_start_stop.objectName() == "stop":
            time_value = self.time_line.value()
            self.time_line.setValue(time_value + 1)
            self.time_pre.setText(
                str((time_value + 1) // 60).zfill(2) + ':' + str((time_value + 1) % 60).zfill(2)
            )
            if self.time_pre.text() == self.time_next.text():
                self.player_stop_setting()
                self.time_pre.setText("00:00")
                self.time_line.setValue(0)
                self.next_music_thread()
            if self.time_pre.text() == "00:02":
                time_long = self.player.duration()  # 获取到实际这首歌的播放长度
                self.time_line.setRange(0, int(time_long / 1000) + 1)  # 设置进度条范围
                self.time_next.setText(  # 设置音频长度的显示
                    str(int(time_long / 1000) // 60).zfill(2) + ':' + str(int(time_long / 1000) % 60).zfill(2)
                )

    # 获取首页数据
    def set_first_date(self):
        if self.src_choose.currentText() == "网易云":
            self.lock.acquire()  # 上锁
            self.listview.clear()
            self.date.img_url, self.date.bt_name, self.date.bt_id = NCOperation.wyy_first_page()
            for i in range(8):
                img = QPixmap()
                img.loadFromData(requests.get(self.date.img_url[i]).content)
                self.img_list[i].setPixmap(img)
                self.title_list[i].setText(first_title_display(self.date.bt_name[i]))
                self.title_list[i].setObjectName(self.date.bt_id[i])
            self.lock.release()  # 解锁
        elif self.src_choose.currentText() == "QQ音乐":
            self.listview.clear()
            self.message_label.setText("后续跟进")
            time.sleep(1)
            self.message_label.clear()

    # 首页点击歌单显示和dj电台播放
    def first_playlist_dj(self):
        send = self.sender()
        id_str = send.objectName()
        self.lock.acquire()
        self.listview_lable.setObjectName("internet")
        if self.src_choose.currentText() == "网易云":
            if id_str[1] == 'p':
                self.date.music_name, self.date.music_id = NCOperation.playlist_info(id_str.split('=')[1])
                self.listview.clear()  # 列表清空
                for i in range(len(self.date.music_name)):  # 加入选中歌单中的歌曲名
                    temp = QListWidgetItem(self.date.music_name[i])
                    temp.setIcon(QIcon("./ico/song.png"))
                    temp.setToolTip("双击播放")
                    self.listview.addItem(temp)
            elif id_str[1] == 'd':
                self.player.setMedia(QMediaContent(QUrl(NCOperation.dj_url(id_str.split('=')[1]))))  # 设置音频网址
                text = self.date.bt_name[self.date.bt_id.index(id_str)]
                self.disc_title.setText(text)  # 显示播放的音频名字
                self.disc.setObjectName("")
                self.listview.setCurrentRow(-1)
                self.player_setting()
        elif self.src_choose.currentText() == "QQ音乐":
            self.message_label.setText("后续跟进")
        self.lock.release()

    # 播放和暂停
    def stop_or_start_song(self):
        if self.music_start_stop.objectName() == "start":
            if self.disc_title.text():
                self.player.play()
                self.music_start_stop.setObjectName("stop")
                self.music_start_stop.setIcon(QIcon("./ico/stop.png"))
        elif self.music_start_stop.objectName() == "stop":
            self.player.pause()
            self.music_start_stop.setObjectName("start")
            self.music_start_stop.setIcon(QIcon("./ico/start.png"))

    # 调节音量
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

    # 调节播放进度
    def music_time_adjust(self):
        self.player.pause()
        self.player.setPosition(self.time_line.value() * 1000)

    # 调节进度完成
    def music_time_adjust_over(self):
        self.player.play()

    # 每一次播放都需要做的一些操作
    def player_setting(self):
        self.time_line.setValue(0)
        self.time_pre.setText("00:00")
        self.player.play()
        self.music_start_stop.setIcon(QIcon("./ico/stop.png"))
        self.music_start_stop.setObjectName("stop")

    # 每一次停止都需要做的一些操作
    def player_stop_setting(self):
        self.player.stop()
        self.music_start_stop.setObjectName("start")
        self.music_start_stop.setIcon(QIcon("./ico/start.png"))

    # 双击列表中的歌曲播放
    def list_view_song(self):
        index = self.listview.currentRow()  # 获取双击的标签的索引值
        music_id = self.date.music_id[index]
        self.lock.acquire()
        if self.listview_lable.objectName() == "local":
            self.player_stop_setting()
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(music_id)))
            self.disc.setObjectName("")
            self.disc_title.setText(self.date.music_name[index])
            self.player_setting()
            self.copyright_flag = False
        elif self.listview_lable.objectName() == "playlist":
            src, num = music_id.split("$&")
            if src == "网易云":
                url = NCOperation.song_url(num)
                self.player_stop_setting()
                self.player.setMedia(QMediaContent(QUrl(url)))
                self.disc.setObjectName(url)
                self.disc_title.setObjectName("网易云$&" + music_id)
                self.disc_title.setText(self.date.music_name[index])
                self.player_setting()
                self.copyright_flag = False
            elif src == "QQ音乐":
                pass
        elif self.listview_lable.objectName() == "internet":
            if self.src_choose.currentText() == "网易云":
                url = NCOperation.song_url(music_id)
                if url == "":
                    self.message_label.setText("没有版权")
                    time.sleep(1)
                    self.message_label.setText("")
                    self.copyright_flag = True
                else:
                    self.player_stop_setting()
                    self.player.setMedia(QMediaContent(QUrl(url)))
                    self.disc.setObjectName(url)
                    self.disc_title.setObjectName("网易云$&" + music_id)
                    self.disc_title.setText(self.date.music_name[index])
                    self.player_setting()
                    self.copyright_flag = False
            elif self.src_choose.currentText() == "QQ音乐":
                pass
        self.lock.release()

    # 显示搜索结果
    def show_search(self):
        self.lock.acquire()
        if self.src_choose.currentText() == "网易云":
            self.date.music_name, self.date.music_id = NCOperation.single_search(self.search_edit.text())
            self.listview.clear()
            self.listview_lable.setObjectName("internet")
            for i in range(len(self.date.music_name)):
                temp = QListWidgetItem(self.date.music_name[i])
                temp.setIcon(QIcon("./ico/song.png"))
                temp.setToolTip("双击播放")
                self.listview.addItem(temp)
        elif self.src_choose.currentText() == "QQ音乐":
            self.message_label.setText("后续跟进")
            time.sleep(1)
            self.message_label.clear()
        self.lock.release()

    # 下载当前播放歌曲(电台我觉得需求不大，不提供下载)
    def downloads_music(self):
        self.lock.acquire()
        if self.date.folder_path != '':
            if self.disc.objectName() != '':
                write_bin = threading.Thread(target=self.write_music_bin)
                write_bin.start()
                self.message_label.setText("下载完毕")
                time.sleep(1)
                self.message_label.clear()
            else:
                self.message_label.setText("不支持下载")
                time.sleep(1)
                self.message_label.clear()
        self.lock.release()

    # 线程后台下载音频，防止阻塞卡顿(之所以不全部在线程里来完成，是因为在线程中创建窗口会有异常，暂未解决)
    def write_music_bin(self):
        with open(self.date.folder_path + '/' + self.disc_title.text() + '.mp3', 'wb') as f:
            f.write(requests.get(self.disc.objectName()).content)

    # 播放本地音乐
    def open_folder_song(self):
        self.lock.acquire()
        if self.date.folder_path != '':
            self.listview.clear()
            self.listview_lable.setObjectName("local")
            self.date.music_name = []
            self.date.music_id = []
            for i in os.listdir(self.date.folder_path):
                music_name, music_type = i.split('.')[0], i.split('.')[1]
                if music_type in self.date.music_type:
                    temp = QListWidgetItem(music_name)
                    temp.setIcon(QIcon("./ico/song.png"))
                    temp.setToolTip("双击播放")
                    self.date.music_name.append(music_name)
                    self.date.music_id.append(self.date.folder_path + '/' + i)
                    self.listview.addItem(temp)
        self.lock.release()

    # 播放模式切换
    def change_modle(self):
        if self.song_modle.toolTip() == "列表循环":
            self.song_modle.setIcon(QIcon("./ico/cycle_one.png"))
            self.song_modle.setToolTip("单曲循环")
        elif self.song_modle.toolTip() == "单曲循环":
            self.song_modle.setIcon(QIcon("./ico/random.png"))
            self.song_modle.setToolTip("随机播放")
        elif self.song_modle.toolTip() == "随机播放":
            self.song_modle.setIcon(QIcon("./ico/cycle.png"))
            self.song_modle.setToolTip("列表循环")

    # 播放歌曲切换设置
    def change_music(self):
        index = self.listview.currentRow()
        if not len(self.date.music_name) == 1:
            if not self.copyright_flag:
                self.date.pre_music_index = index
            if self.song_modle.toolTip() == "列表循环":
                if index == (len(self.date.music_name) - 1):
                    index = 0
                else:
                    index = index + 1
            elif self.song_modle.toolTip() == "随机播放":
                while True:
                    # 随机播放，防止下一首是本首歌
                    num = random.randint(0, len(self.date.music_name) - 1)
                    if not num == index:
                        index = num
                        break
        self.listview.setCurrentRow(index)

    # 下一首歌曲
    def next_music(self):
        if self.listview.currentRow() == -1:
            self.message_label.setText("播放列表为空")
            time.sleep(1)
            self.message_label.clear()
        else:
            self.change_music()
            self.list_view_song()
            while self.copyright_flag:  # 防止歌单中下一首是没有版权的歌曲导致播放停止
                self.change_music()
                self.list_view_song()

    # 上一首歌曲
    def pre_music(self):
        index = self.date.pre_music_index
        self.listview.setCurrentRow(index)
        self.list_view_song()

    # 新建我的歌单
    def create_my_playlist(self, text, ok):
        self.lock.acquire()
        if ok:
            with open("./my_playlist/" + text + ".json", 'w', encoding='utf-8') as f:
                json.dump({"playlist": []}, f, ensure_ascii=False)
            self.date.my_playlist_name.append(text)
            self.date.my_playlist_text[text] = {"playlist": []}
            temp = QListWidgetItem(text)
            temp.setIcon(QIcon("./ico/my_playlist"))
            temp.setToolTip("双击显示")
            self.myplaylist_list.addItem(temp)
        self.lock.release()

    # 删除我的歌单
    def delete_my_playlist(self):
        text, ok = QInputDialog.getItem(self, "选择要删除的歌单", "歌单名", self.date.my_playlist_name, 0, False)
        if ok:
            os.remove("./my_playlist/" + text + ".json")
            self.load_my_playlist_thread()

    # 加载我的歌单
    def load_playlist(self):
        self.lock.acquire()
        self.myplaylist_list.clear()
        self.date.my_playlist_name = []
        self.date.my_playlist_text = {}
        for i in os.listdir("./my_playlist"):
            name = i.split('.')[0]
            self.date.my_playlist_name.append(name)
            temp = QListWidgetItem(name)
            temp.setIcon(QIcon("./ico/my_playlist"))
            temp.setToolTip("双击显示")
            self.myplaylist_list.addItem(temp)
            with open("./my_playlist/" + i, 'r', encoding='utf-8') as f:
                self.date.my_playlist_text[name] = json.loads(f.readline())  # 将其中的数据加载进来
        self.lock.release()

    # 加入我的歌单当中
    def add_my_playlist(self, text, ok):
        if ok:
            if self.disc.objectName() == "":
                self.message_label.setText("不支持加入")
            else:
                data = [self.disc_title.text(), self.disc_title.objectName()]
                if data in self.date.my_playlist_text[text]["playlist"]:
                    self.message_label.setText("已经存在")
                else:
                    self.date.my_playlist_text[text]["playlist"].append(data)
                    with open("./my_playlist/" + text + ".json", 'w', encoding='utf-8') as f:
                        json.dump(self.date.my_playlist_text[text], f, ensure_ascii=False)
                    self.message_label.setText("加入成功")
            time.sleep(1)
            self.message_label.clear()

    # 双击我的歌单显示歌单歌曲
    def click_my_playlist(self):
        self.lock.acquire()
        index = self.myplaylist_list.currentRow()
        name = self.date.my_playlist_name[index]
        self.listview_lable.setObjectName("playlist")
        self.listview.clear()
        self.date.music_name = []
        self.date.music_id = []
        for i in self.date.my_playlist_text[name]["playlist"]:
            self.date.music_name.append(i[0])
            self.date.music_id.append(i[1])
            temp = QListWidgetItem(i[0])
            temp.setIcon(QIcon("./ico/song.png"))
            temp.setToolTip("双击播放")
            self.listview.addItem(temp)
        self.lock.release()

    # 关闭窗口改写
    def closeEvent(self, event):
        result = QMessageBox.question(self, "退出", "确认退出程序吗?", QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
