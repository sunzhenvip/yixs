#
import datetime
import os
import stat
import uuid
import ddddocr
import ssl
import aiohttp
from urllib.parse import urlparse

base_captcha = "captcha"


class LoginInfo:
    def __init__(self):
        self.username = None
        self.password = None
        self.token = None
        self.captcha = None

    def set_name(self, name):
        self.username = name

    def set_password(self, password):
        self.password = password

    def set_token(self, token):
        self.token = token

    def set_captcha(self, captcha):
        self.captcha = captcha

    def full_property_data(self, name, password, token, captcha):
        self.username = name
        self.password = password
        self.token = token
        self.captcha = captcha


class LoginResponse:
    def __init__(self):
        self.code = None
        self.msg = None
        self.data = None
        self.url = None
        self.wait = None


# 字典变量字段数据自动映射到类属性中
def dict_to_obj(d, obj):
    for key, value in d.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


def create_uuid_png_name():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + "-" + str(get_timestamp_uuid) + ".png"


def cur_create_dir():  # 创建当前日期目录
    year_month_day = datetime.datetime.now().strftime('%Y-%m-%d')

    save_file_path = os.path.join(base_captcha, year_month_day)

    if not os.path.exists(save_file_path):
        os.makedirs(save_file_path)
        os.chmod(save_file_path, stat.S_IRWXU)  # Linux下可读可写

    return save_file_path


def img_ocr(img):
    ocr = ddddocr.DdddOcr()  # 实例化
    with open(str(img), 'rb') as f:  # 打开图片
        img_bytes = f.read()  # 读取图片
    res = ocr.classification(img_bytes)  # 识别
    # print(res)
    return res


def get_host_port(url):
    """解析URL获取域名和端口号"""
    parsed_url = urlparse(url)
    host_name = parsed_url.netloc.split(':')
    if len(host_name) > 1:
        return "{}_{}".format(host_name[0], host_name[1])
    else:
        return host_name[0]


def is_https(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme == 'https'


# 创建指定目录
def create_platform_address(base_dir, attachment, platform_address):
    directory = os.path.join(base_dir, attachment, platform_address)
    if not os.path.exists(directory):
        # 目录不存在，创建此目录，并设置权限为 rwxrwxrwx (即777)
        os.mkdir(directory, 0o777)
    else:
        pass


# 忽略SSL方式1
def ignore_check_ssl():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return aiohttp.TCPConnector(ssl=ssl_context)


# 忽略SSL方式2
def ignore_verify_ssl():
    return aiohttp.TCPConnector(verify_ssl=False)
