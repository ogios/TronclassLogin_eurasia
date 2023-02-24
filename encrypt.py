import math
import random
from Crypto.Cipher import AES
import base64

aes_chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
aes_chars_len = len(aes_chars)
def randomString(length:int):
    retStr = ""
    for i in range(length):
        retStr += aes_chars[math.floor(random.random() * aes_chars_len)]
    return retStr

def getAesString(data:str, key0:str, iv0:str):
    key0 = key0.strip()
    key = key0.encode("utf-8")
    iv = iv0.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    blockSize = AES.block_size
    x = blockSize - (len(data) % blockSize)
    if x != 0:
        data += chr(x)*x
    data = data.encode()
    msg = cipher.encrypt(data)
    return base64.b64encode(msg).decode()


def encrypt(data, aeskey):
    return getAesString(
        randomString(64) + data,
        aeskey,
        randomString(16)
    )
# data = "YJtyb5Kwtta6mhDQzpAtmYrkKhNsa5H5wF3ajkMf28ff2N4MHhhFsZiFykEES7RD123456"
# iv = "PyMwrwkybMeH82HG"
# print(data)
# print(iv)
# c = getAesString(
#     data,
#     "gxOYlTE45BB1NCMU",
#     iv
# )
# tc = c.decode()
# print(tc)



# print(encrypt("123456", "gxOYlTE45BB1NCMU"))
