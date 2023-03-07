import requests, base64
from bs4 import BeautifulSoup


# 作者：用户6188283673752
# 链接：https://juejin.cn/post/7180164119629627448
# 来源：稀土掘金
# 著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
def login(email, pwd):
    login_page_url = 'https://so.gushiwen.cn/user/login.aspx?from=http://so.gushiwen.cn/user/collect.aspx'
    response = requests.get(login_page_url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    viewstate = soup.select('#__VIEWSTATE')[0]['value']
    viewstategenerator = soup.select('#__VIEWSTATEGENERATOR')[0]['value']
    print(viewstate)
    print(viewstategenerator)


if __name__ == "__main__":
    # login("1293334778@qq.com", "aaaa")
    # 发送 GET 请求获取页面内容
    url = 'http://www.ximimim.top:1008/admin/common/login.shtml'
    response = requests.get(url)

    # 使用 BeautifulSoup 解析 HTML 页面
    soup = BeautifulSoup(response.content, 'html.parser')

    # 获取 __token__ 的值
    token = soup.find('input', {'name': '__token__'}).get('value')
    print(token)

    # 获取验证码图片并保存到文件中
    captcha = soup.find('img', {'id': 'captcha'})
    captcha_data = captcha.get('src').split(',')[-1]
    captcha_binary = base64.b64decode(captcha_data)

    with open('captcha.png', 'wb') as f:
        f.write(captcha_binary)
