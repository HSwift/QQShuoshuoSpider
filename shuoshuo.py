# coding=utf-8
# platform=win10 1703
# python=3.5
# author=swift
import os
import re
import urllib.request
import time
# edit it
cookie = ""  # 一定要最完整的(含p_skey,skey,rv2)
uin = ""  # 要爬的QQ号
hostuin = ""  # 自己的QQ号
count = 20  # 要爬的说说数量
# end
# global
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'
g_tk = ""
likedb = {}
global r_c  # 实际说说的总数
# end


def getNewGTK():
    skey_t = ""
    skey = ""
    p_skey = ""
    rv2 = ""
    # get p_skey
    t = re.search(r'p_skey=(?P<p_skey>[^;]*)', cookie)
    if t is not None:
        p_skey = t.group()
    p_skey = p_skey[7:]
    # get skey
    t = re.search(r'skey=(?P<skey>[^;]*)', cookie)
    if t is not None:
        skey = t.group()
    skey = skey[5:]
    t = re.search(r'rv2=(?P<rv2>[^;]*)', cookie)
    if t is not None:
        rv2 = t.group()
    rv2 = rv2[3:]
    # get rv2
    skey_t = p_skey or (skey or rv2)
    print("skey_t=", skey_t)
    hash_t = 5381
    for i in range(0, len(skey_t)):
        hash_t = hash_t + int(hash_t << 5) + ord(skey_t[i])
        hash_t = hash_t & 0x7fffffff  # 稍微优化一下
    print("g_tk=", hash_t)
    return str(hash_t)


def getlike(unikey):
    # 获取每条说说的赞的情况
    url = 'https://h5.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?uin=' + \
        hostuin + '&unikey=' + unikey + \
        '&begin_uin=0&query_count=60&if_first_page=1&g_tk=' + g_tk
    req = urllib.request.Request(url)
    req.add_header(
        'accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    req.add_header('cookie', cookie)
    req.add_header('pragma', 'no-cache')
    req.add_header('upgrade-insecure-requests', '1')
    req.add_header('user-agent', useragent)
    try:
        res = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)
        os._exit(0)
    except urllib.error.HTTPError as e:
        print(e.code, e.reason)
        os._exit(0)
    html = res.read().decode("utf-8", "ignore")
    likelist = re.findall(r'"fuin":([^"]+),', html)
    for item in likelist:
        if item in likedb:
            likedb[item] += 1
        else:
            likedb[item] = 1


def getmood(start_pos):
    # 获取每一页上所有说说的tid
    start_pos = str(start_pos)
    url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=' + uin + '&inCharset=utf-8&inCharset=utf-8&outCharset=utf-8&hostUin=' + uin + \
        '&notice=0&sort=0&pos=' + start_pos + \
        '&num=20&cgi_host=http%3A%2F%2Ftaotao.qq.com%2Fcgi-bin%2Femotion_cgi_msglist_v6&code_version=1&format=jsonp&need_private_comment=1&g_tk=' + g_tk
    req = urllib.request.Request(url)
    req.add_header(
        'accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    req.add_header('cookie', cookie)
    req.add_header('pragma', 'no-cache')
    req.add_header('upgrade-insecure-requests', '1')
    req.add_header('user-agent', useragent)
    try:
        res = urllib.request.urlopen(req)
    except error.URLError as e:
        print(e.reason)
        os._exit(0)
    except error.HTTPError as e:
        print(e.code, e.reason)
        os._exit(0)
    html = res.read().decode("gb2312", "ignore")
    # 获取tid似乎会把转发说说一起获取,暂时没有想到什么好的解决方法
    tid = re.findall(r'"tid":"([^"]+)"', html)
    if len(tid) == 0:
        print("[!]ERROR: shuoshuo.count = 0 or invalid cookie")
        os._exit(0)
    global r_c
    for unikey in tid:
        if len(unikey) == 24:
            r_c += 1
            print(unikey)
            unikey = "http://user.qzone.qq.com/" + uin + "/mood/" + unikey + ".1"
            time.sleep(0.3)  # 每次间隔0.3s.但是tx能允的最小间隔我并不知道
            getlike(unikey)


def mainloop():
    global r_c
    r_c = 0
    i = 0
    while (i < count):
        getmood(i)
        i += 20


def output(record):
    global r_c
    for i in record:
        ratio = round((float(i[1]) / r_c) * 100, 2)
        print(i[0], i[1], ratio)


g_tk = getNewGTK()
mainloop()
record = sorted(
    likedb.items(), key=lambda item: item[1], reverse=True)  # 按value排序
output(record)
os.system("pause")
