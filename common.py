#
import datetime
import os
import stat
import uuid
import ddddocr

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
