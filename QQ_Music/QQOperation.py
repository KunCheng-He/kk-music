from pyquery import PyQuery as pq
import requests
import random


# 发送请求时的头文件
heades = [
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}
]


# QQ音乐首页歌单爬取
def qq_first_page():
    response = requests.get("https://y.qq.com/", headers=heades[random.randint(0, len(heades)-1)])
    doc = pq(response.text)
    li = doc('div ul .playlist__item.slide__item')
    id_list_l = [i.attr('data-disstid') for i in li.items()]
    img_url_l = [i.attr('src') for i in li.find('img').items()]
    name_list_l = [i.text() for i in li.find('span').items()]
    return img_url_l[:5], name_list_l[:5], id_list_l[:5]


if __name__ == '__main__':
    a, b, c = qq_first_page()
    print(a)
    print(b)
    print(c)

