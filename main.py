# -*- coding:utf-8 -*-
import re
import time
import os
import requests
from lxml import etree
import random
import urllib.parse
import hashlib

pl_session = requests.session()
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}


def login(user_name, user_password, base_url):
    session = requests.session()

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76"
    logging_api = f"{base_url}/member.php"  # 登录接口
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://vsdf.n.rkggs5f4e5asf.com',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': base_url,
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }
    # 表单参数
    params = {
        'mod': 'logging',
        'action': 'login',
        'loginsubmit': 'yes',
        'infloat': 'yes',
        'lssubmit': 'yes',
        'inajax': '1',
    }

    data = {
        'username': user_name,
        'password': user_password,
        'quickforward': "yes",
        'handlekey': "ls"}
    # 登录账号
    response = session.post(base_url, headers=headers, params=params, proxies=proxies)
    aa = re.findall('<input type="hidden" name="formhash" value="(.*?)" /', response.text)[0]
    data['formhash'] = aa

    res = session.post(url=logging_api, headers=headers, data=data, params=params, proxies=proxies).text

    if res:
        print(f'账号：{user_name} 登录成功！！！')
    else:
        print('出现错误，请重试！！！')
    # 获取银币数量
    user_info_url = f"{base_url}/home.php?mod=spacecp&ac=credit&showcredit=1&inajax=1&ajaxtarget=extcreditmenu_menu"
    user_info_response = session.get(url=user_info_url, headers=headers, proxies=proxies)
    if user_info_response.status_code == 200:
        print("用户信息页面获取成功:")
    else:
        print("用户信息页面获取失败")
    html_content = user_info_response.text
    yinbi = re.findall('<span id="hcredit_2">(.*?)</span>', html_content)[0]
    if yinbi:

        print('银币数量获取成功')
        print('当前银币数量:', yinbi)
        return [session, headers, aa, base_url]
    else:
        print("银币数量获取失败")
    time.sleep(3)

    # pl(session,headers)


def get_data(page_text, reppost, session, headers, base_url, tid, fid):
    # 第三次请求，获取弹出页面和一些参数
    try:
        kk = f'"{page_text}"'
        aa = etree.HTML(kk)
        formhash = aa.xpath("//input[@name='formhash']/@value")[0]
        noticeauthor = aa.xpath("//input[@name='noticeauthor']/@value")[0]
        noticeauthormsg = aa.xpath("//input[@name='noticeauthormsg']/@value")[0]
        usesig = aa.xpath("//input[@name='usesig']/@value")[0]
        reppid = aa.xpath("//input[@name='reppid']/@value")[0]
        noticetrimstr = aa.xpath("//input[@name='noticetrimstr']/@value")[0]
        converted_sentence = noticeauthormsg.replace('　', '\u3000').replace(' ', '+')

    except Exception as e:
        print(e)
    # 随机请求获取message参数
    message = ['啥也不说了，楼主就是给力', '谢谢楼主分享，祝搜书吧越办越好！', '看了LZ的帖子，我只想说一句很好很强大！', ]
    message1 = random.choice(message)
    decoded_data = {
        'formhash': formhash,
        'handlekey': 'register',
        'noticeauthor': noticeauthor,
        'noticetrimstr': noticetrimstr,
        'noticeauthormsg': converted_sentence,
        'usesig': usesig,
        'reppid': reppid,
        'reppost': reppost,
        'subject': '',
        'message': message1
    }
    params = {
        'mod': 'post',
        'infloat': 'yes',
        'action': 'reply',
        'fid': fid,
        'extra': '',
        'tid': tid,
        'replysubmit': 'yes',
        'inajax': '1',
    }
    # 使用解码后的数据调用 encode 函数
    data = encode(decoded_data)
    response = session.post(f'{base_url}/forum.php', params=params, headers=headers, data=data, proxies=proxies)
    return response.text, converted_sentence


def encode(decoded_data):
    encoded_data = []
    for key, value in decoded_data.items():
        # 对值进行编码,noticeauthor不需要
        if key == 'noticeauthor':
            encoded_value = urllib.parse.quote(value.encode('gb2312'), safe='~()*!.\'')
        else:
            encoded_value = urllib.parse.quote(value.encode('gb2312'), safe='~()*!.\'+...')
        # 将键和编码后的值用等号连接
        encoded_pair = f"{key}={encoded_value}"
        encoded_data.append(encoded_pair)
    # 将所有键值对用与号连接
    return '&'.join(encoded_data)


def get_url(session, headers, base_url):
    url = f'{base_url}/forum.php?mod=forumdisplay&fid=39&page=1'
    # print(url)
    page_text = session.get(url=url, headers=headers, proxies=proxies).text
    # 获取第二次请求的链接
    # 第二次请求的载荷
    url_number = re.findall('id="normalthread_(.*?)"', page_text)
    random_number = random.randint(1, len(url_number))
    tid = str(url_number[random_number])
    params = {
        'mod': 'viewthread',
        'tid': tid,
        'extra': 'page=1',
    }
    response = session.get(f'{base_url}/forum.php', params=params, headers=headers, proxies=proxies)

    # 第三次请求，获取弹出页面
    reppost = re.findall('<a class="fastre" href="(.*?)" onclick', response.text)[0]
    fid = reppost.split(';')[2].split('=')[1].split('&')[0]
    reppost = reppost.split(';')[4].split('=')[1].split('&')[0]
    params = {
        'mod': 'post',
        'action': 'reply',
        'fid': fid,
        'tid': tid,
        'reppost': reppost,
        'extra': 'page=1',
        'page': '1',
        'infloat': 'yes',
        'handlekey': 'reply',
        'inajax': '1',
        'ajaxtarget': 'fwin_content_reply',
    }
    # 需要修改headers通过验证
    headers['referer'] = f'{base_url}/forum.php?mod=viewthread&tid={int(tid)}&extra=page%3D1'
    response = session.get(f'{base_url}/forum.php', params=params, headers=headers, proxies=proxies)

    return response.text, reppost, session, headers, base_url, tid, fid


def write_md5_and_timestamp_to_csv(file_path, data, encoding='gbk'):
    """
    将数据的MD5加密结果和时间戳写入CSV文件，每列分别为时间戳和MD5。

    :param file_path: CSV文件路径
    :param data: 要加密的数据
    :param encoding: 文件编码方式，默认为'gbk'
    """
    # 计算MD5
    md5_hash = hashlib.md5(data.encode(encoding)).hexdigest()

    # 获取当前时间戳
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建CSV格式的字符串
    csv_line = f"{timestamp},{md5_hash}\n"

    # 写入文件，追加模式
    with open(file_path, 'a', encoding=encoding) as file:
        # 如果文件是新的，先写入列名
        if file.tell() == 0:
            file.write("Timestamp,MD5\n")
        file.write(csv_line)


if __name__ == '__main__':
    # user_name=input("输入账户名称")
    user_name = ''
    # user_password=input("输入账户密码")
    user_password = ''
    base_url = ''
    text = ''
    if os.path.exists('config.txt') == False:
        with open('config.txt', 'a+', encoding='UTF-8') as fp:
            simple_text = base_url + '\n' + 'username' + '\n' + 'userpassword'
            print(simple_text)
            fp_text = fp.write(simple_text)

    with open('config.txt', 'a+', encoding='UTF-8') as fp:
        fp.seek(0)
        fp_text = fp.readlines()
        user_name = fp_text[1].strip('\n').strip('')
        user_password = fp_text[2].strip('\n').strip('')
        base_url = fp_text[0].strip('\n').strip('')
    while True:
        try:
            if user_name == 'username':
                print(
                    f'请替换当前目录下config.txt中的username与password为你的账号密码，并且在第一行填入搜书吧的url，例如 https://www.284djs.soushu2028.com/ ,如果搜书吧域名更改，请更改为新的域名')
                break
            else:
                info = login(user_name, user_password, base_url)
                # print(info)
                break
        except Exception as ex:
            time.sleep(3)
            print('失败')
            print(ex)

    # 每天三次评论，
    i = 0
    while i < 3:
        url_list_text = get_url(info[0], info[1], base_url)
        response_text, reppost, session, headers, base_url, tid, fid = url_list_text
        list, history = get_data(response_text, reppost, session, headers, base_url, tid, fid)
        time.sleep(60)
        with open('aa.txt', 'w', encoding='gbk') as fp:

            fp.write(list + '\n')
        if '成功' in list:
            write_md5_and_timestamp_to_csv('./history_md5.csv', history)
            i = i + 1
