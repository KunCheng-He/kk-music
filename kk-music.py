"""
作者：byack
邮箱：18788748257@163.com
注解：本项目仅供学习，不用于任何商业用途，刚学了爬虫和Pyqt5，功能比较少，后续我会尽量跟进，不断跟新，图标和部分代码，
    还有一些网易云接口均来源于网络，在次表示感谢
"""

from PyQt5.QtWidgets import QApplication, QWidget
from GUI.main_window import Main_window
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main_window()
    ui.show()
    sys.exit(app.exec_())

