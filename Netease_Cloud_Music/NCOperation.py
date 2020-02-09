import os
import requests
import random
from pyquery import PyQuery as pq


# 发送请求时的头文件
heades = [
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}
]


# 下载首页推荐歌单封面
def down_img(img_url_list, path='./ico'):
    # 如果路径不存在就创建
    try:
        if not os.path.exists(path):
            os.mkdir(path)
    except FileNotFoundError:
        print("多层路径不存在，只能创建一层路径，程序终止。")
        exit(0)
    n = 0
    for j in img_url_list:
        date = requests.get(j, headers=heades[random.randint(0, len(heades)-1)])  # 进行请求
        with open("{}/{}.jpeg".format(path, n), "wb") as f:
            f.write(date.content)  # 写入数据
            # print(j)
            n += 1
    print("下载完毕，保存路径：" + path)


# 获取首页,反回图片、名字、id号
def wyy_first_page():
    # 先对首页进行简单处理
    url = "https://music.163.com/discover"
    response = requests.get(url, headers=heades[random.randint(0, len(heades)-1)])
    doc = pq(response.text)
    playlist = doc('li .u-cover.u-cover-1')  # 筛选出首页推荐的歌单
    playlist.find('.icon-play').remove()  # 移除多余的信息，便于后续提取信息
    playlist.find('div:contains(getPlayCount)').siblings().remove()
    playlist.find('div:contains(getPlayCount)').remove()

    # 获取首页推荐的歌单图片的url
    img = playlist.find('img').items()
    img_url_l = [i.attr('src') for i in img]  # 获取到所有歌单封面的url

    # 获取推荐歌单的名字
    name_list_l = [i.attr.title for i in playlist.find('a').items()]

    # 获取歌单的键值id
    id_list_l = [i.attr.href for i in playlist.find('a').items()]
    return [img_url_l, name_list_l, id_list_l]


# 通过歌单playlist_id获取歌单信息
def playlist_info(playlist_id):
    url = "https://music.163.com/playlist?id=" + playlist_id
    response = requests.get(url, headers=heades[random.randint(0, len(heades)-1)])
    doc = pq(response.text)
    num = int(doc('.sub.s-fc3 #playlist-track-count').text())  # 获取这个歌单的歌曲总数
    li = doc('li:lt({})'.format(num)).find('a')  # lt()获取之前的
    song_id_l = [i.attr('href')[9:] for i in li.items()]  # 歌曲id
    song_name_l = [i.text() for i in li.items()]  # 歌名
    return [song_name_l, song_id_l]


# 传入dj电台的id号，获取dj电台的音频文件
def dj_url(dj_id):
    url = "https://api.imjad.cn/cloudmusic/?type=dj&id=" + dj_id
    response = requests.get(url, headers=heades[random.randint(0, len(heades)-1)]).json()
    return response['data'][0]['url']


# 通过指定的歌曲song_id获取歌曲的音频二进制文件
def song_url(song_id, br=320000):
    # 通过urls获取歌曲下载链接
    urls = "https://api.imjad.cn/cloudmusic/?type=song&id={}&br={}".format(song_id, br)
    url = requests.get(urls).json()['data'][0]['url']
    return url


# 单曲搜索
def single_search(name):
    song_name, song_id, singer = [], [], []
    url = "http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={" + name + "}&type=1&offset=0&total=true&limit=30"
    data = requests.get(url, headers=heades[random.randint(0, len(heades)-1)])
    songs = data.json()['result']['songs']
    for i in songs:
        song_name.append(i['name'] + "  <-歌手-->  " + i['artists'][0]['name'])
        song_id.append(str(i['id']))
    return song_name, song_id


if __name__ == '__main__':
    a, b = single_search("你好")
    print(a)
    print(b)
