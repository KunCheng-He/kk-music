# ![](https://pic.downk.cc/item/5e2ab4fc2fb38b8c3c5fa4ee.jpg)kk-music

---

## 最终效果(大概)

我的系统是manjaro

![](https://pic.downk.cc/item/5e2ac01c2fb38b8c3c606c03.png)

## 视频简单解说

bilibili： https://www.bilibili.com/video/av84993922 

## 使用方法

如果是在码云克隆项目的话改一下地址就好了

```bash
git clone https://github.com/byack/kk-music.git
cd kk-music
pip3 install -r requirements.txt
python3 kk-music.py
```

等我研究一下如何直接打包成一个可执行文件，打包完成后我会将文件上传上来的。

## 概述

最近刚学了一点爬虫，想尝试着做一点东西，所以结合了pyqt5做了一个带界面的音乐播放器，只有一些基本功能，后续我会尽量维护完善这个项目，目前数据来源与网易云音乐。

## 一些可能的问题

+ 搜索框无法输入中文：（https://bbs.deepin.org/forum.php?mod=viewthread&tid=181772）
+ 搜索错误：目前搜索使用的是selenium来爬取数据，所以需要安装相关的浏览器驱动，默认程序使用的是chromedriver，如果使用的是火狐浏览器，需要安装geckodriver，安装方法大家可以谷歌一下，都比较简单。在Linux上就是一条安装命令就可以了。

*欢迎邮箱反馈，我没有做详细的测试*

## 感谢

+ 图标来源：(https://icons8.cn/) (https://www.easyicon.net/) 内容均来源与网络，如有侵权，联系告知，我会立即删除
+ 网易云反爬代码参考：(https://blog.csdn.net/qq_36779888/article/details/90738012) 感谢大佬 (后续版本在我自己没搞懂网易云的加密机制之前，这一部分改用selenium来实现，自己写的)
+ qt5滑动条禁用点击事件代码参考：(https://github.com/PyQt5/PyQt/tree/master/QSlider) 
+ 搜索框输入中文问题，链接如上，感谢大佬

可能有些遗漏，表示感谢

## 说明

本项目仅供学习，不能用作商业用途，克隆本项目后，如有侵权行为，请自行删除， 与作者无关。

如本项目有侵权行为，我会立即删除。