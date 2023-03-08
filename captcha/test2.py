import requests, json

base_url = "http://www.ximimim.top:1008"
route_login = "/admin/common/login.shtml"
route_captcha = "/captcha.shtml"

if __name__ == "__main__":

    # 登录请求
    response = requests.get(base_url + route_login)

    # 获取session信息
    cookies = response.cookies.get_dict()
    session_id = cookies.get('session_id')

    print(session_id)
    # 请求参数
    # data = {'name': username, 'password': password, 'captcha': code, '__token__': token}
    # data = "name={0}&password={1}&captcha={2}&__token__={3}".format("admin", "qq123456", "UFJ4",
    #                                                                 "4da28463606c1dad7a352b52bd62816692809652")
    # header = {
    #     'X-Requested-With': 'XMLHttpRequest',
    #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #     'Cookie': 'PHPSESSID=gq0npeainecd9vn5si0vqb08g0'
    # }
    # #  + secrets.token_hex(13),
    # # data = urllib3.urlencode(postData)
    # # res = requests.post(url=base_url + route_login, data=data, headers=header, verify=False)
    # res = requests.post(url=base_url + route_login, data=data, headers=header)
    # result = json.loads(res.text)
    # print(result)
