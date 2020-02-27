# ![](https://pic.downk.cc/item/5e2ab4fc2fb38b8c3c5fa4ee.jpg)kk-music

---

## 最终效果(大概)

我的系统是manjaro

![](https://pic.downk.cc/item/5e3fe9462fb38b8c3c5287c7.png)

## 视频简单解说

bilibili第一次解说： https://www.bilibili.com/video/av84993922 

bilibili第二次更新视频介绍：https://www.bilibili.com/video/av88042021/

## 可执行包下载

由于在github上传打包好的文件超过10MB不允许上传，所以，本项目仍然会继续更新，可以自行打包，也可以到码云平台下载：https://gitee.com/byack/kk-music/releases

目前我只打包了window平台的进行尝试

+ 解压压缩包后，双击exe文件就可以运行了，请保证解压文件目录的完整性，ico文件夹中包含了图标文件，my_playlist文件夹为自己的歌单，均要与可执行文件在统一路径下

## 使用方法

克隆本项目，如果是在码云克隆项目的话改一下地址就好了

```bash
git clone https://github.com/byack/kk-music.git
cd kk-music
pip3 install -r requirements.txt
python3 kk-music.py
```

## 概述

最近刚学了一点爬虫，想尝试着做一点东西，所以结合了pyqt5做了一个带界面的音乐播放器，只有一些基本功能，后续我会尽量维护完善这个项目，目前数据来源与网易云音乐。

## 一些可能的问题

+ 搜索框无法输入中文：（https://bbs.deepin.org/forum.php?mod=viewthread&tid=181772）

*欢迎邮箱反馈，我没有做详细的测试*

## 暂时我遇见的还未解决的Bug

+ 先点击播放首页电台，然后点击首页歌单或是搜索歌曲，出现播放无声，需要暂停再播放，无声时进度也是进展的，暂停播放后等同于重头播放，会导致进度对不上，需要拖动进度条矫正进度显示

+ 先点击歌单，然后播放歌单中的歌曲，然后使用搜索功能，报错为：非法指令

    ```
    Process finished with exit code 132 (interrupted by signal 4: SIGILL)
    ```

+ 首次运行下一首线程时，终端会有如下报告，但运行暂时无异常

    ```
    QObject::connect: Cannot queue arguments of type 'QItemSelection'
    (Make sure 'QItemSelection' is registered using qRegisterMetaType().)
    QObject::connect: Cannot queue arguments of type 'QItemSelection'
    (Make sure 'QItemSelection' is registered using qRegisterMetaType().)
    ```

+ **哪位大佬如果看出了问题所在教教我吧，感谢**

## 感谢

+ 图标来源：(https://icons8.cn/) (https://www.easyicon.net/) 内容均来源与网络，如有侵权，联系告知，我会立即删除
+ 网易云反爬代码参考：(https://blog.csdn.net/qq_36779888/article/details/90738012) 感谢大佬 (已经找到直接可用的API)
+ qt5滑动条禁用点击事件代码参考：(https://github.com/PyQt5/PyQt/tree/master/QSlider) (现在采用的其它方法禁用点击跳转，将点击跳转的值设置为0，就可以达到禁用点击跳转的效果)
+ 搜索框输入中文问题，链接如上，感谢大佬

可能有些遗漏，表示感谢

## 说明

本项目仅供学习，不能用作商业用途，克隆本项目后，如有侵权行为，请自行删除， 与作者无关。

如本项目有侵权行为，我会立即删除。