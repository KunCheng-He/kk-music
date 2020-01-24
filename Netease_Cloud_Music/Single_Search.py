import requests
import random
import base64
from Crypto.Cipher import AES
import json
import binascii


class Music_api:
    # 设置从JS文件提取的RSA的模数、协商的AES对称密钥、RSA的公钥等重要信息
    def __init__(self):
        self.modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.nonce = '0CoJUm6Qyw8W8jud'
        self.pubKey = '010001'
        self.url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="
        self.HEADER = {}
        self.setHeader()
        self.secKey = self.getRandom()

    # 生成16字节即256位的随机数
    def getRandom(self):
        string = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        res = ""
        for i in range(16):
            res += string[int(random.random() * 62)]
        return res

    # AES加密，用seckey对text加密
    def aesEncrypt(self, text, secKey):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(secKey.encode('utf-8'), 2, '0102030405060708'.encode('utf-8'))
        ciphertext = encryptor.encrypt(text.encode('utf-8'))
        ciphertext = base64.b64encode(ciphertext).decode("utf-8")
        return ciphertext

    # 快速模幂运算，求 x^y mod mo
    def quickpow(self, x, y, mo):
        res = 1
        while y:
            if y & 1:
                res = res * x % mo
            y = y // 2
            x = x * x % mo
        return res

    # rsa加密
    def rsaEncrypt(self, text, pubKey, modulus):
        text = text[::-1]
        a = int(binascii.hexlify(str.encode(text)), 16)
        b = int(pubKey, 16)
        c = int(modulus, 16)
        rs = self.quickpow(a, b, c)
        return format(rs, 'x').zfill(256)

    # 设置请求头
    def setHeader(self):
        self.HEADER = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0"
        }

    def search(self, s, offset, type="1"):
        text = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "#/discover": "",
            "s": s,
            "type": type,
            "offset": offset,
            "total": "true",
            "limit": "30",
            "csrf_token": ""
        }
        text = json.dumps(text)
        params = self.aesEncrypt(self.aesEncrypt(text, self.nonce), self.secKey)
        encSecKey = self.rsaEncrypt(self.secKey, self.pubKey, self.modulus)
        data = {
            'params': params,
            'encSecKey': encSecKey
        }
        result = requests.post(url=self.url,
                               data=data,
                               headers=self.HEADER).json()
        return result

    # 获取指定音乐列表(相当于主函数)
    def get_music_list(self, keywords):
        music_list = []
        for offset in range(1):
            result = Music_api().search(keywords, str(offset))
            result = result['result']['songs']
            for music in result:
                # if music['copyright'] == 1 and music['fee'] == 8:
                if (music['privilege']['fee'] == 0 or music['privilege']['payed']) and music['privilege']['pl'] > 0 and \
                        music['privilege']['dl'] == 0:
                    continue
                if music['privilege']['dl'] == 0 and music['privilege']['pl'] == 0:
                    continue
                    # if music['fee'] == 8:
                music_list.append(music)
        return music_list


if __name__ == '__main__':
    result = Music_api().search("天气之子", 0)
    for i in result['result']['songs']:
        print(i)