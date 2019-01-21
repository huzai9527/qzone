from selenium import webdriver
import re
import json
import requests
import pandas as pd
import time
driver = webdriver.Chrome()
# 登录网站
driver.get('https://i.qq.com')
# 选择账号密码登录
driver.switch_to_frame('login_frame')
# 点击输入框获取输入
driver.find_element_by_id('switcher_plogin').click()
# 输入账号
driver.find_element_by_id('u').send_keys('369212851')
# 输入密码
driver.find_element_by_id('p').send_keys('Zxh@199822.')
# 点击登录
driver.find_element_by_id('login_button').click()
time.sleep(5)
def get_g_tk(cookie):
    hashes = 5381
    for letter in cookie['p_skey']:
        hashes += (hashes << 5) + ord(letter)
    return hashes & 0x7fffffff

# 获取登录之后的cookie信息
cookie = {}
for elem in driver.get_cookies():
    cookie[elem['name']] = elem['value']
# 获取g_tk
g_tk = get_g_tk(cookie)
# 利用xpath获取登录之后的网页源代码
html = driver.page_source

# 通过xpath 获得登录后的token
pattern = re.compile(r'window.g_qzonetoken = \(function\(\){ try{return "(.*?)";}')
token = re.findall(pattern, html)[0]
print(token)
headers = {
    'authority': 'user.qzone.qq.com',
    'method': 'GET',
    'scheme': 'https',
    'accept-language': 'zh-CN,zh;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}

def get_resp(cookie, g_tk, token, page):
    session = requests.session()
    # 将cookie字典转换成RequestsCookieJar
    c = requests.utils.cookiejar_from_dict(cookie)
    # 将headers 放入session
    session.headers = headers
    # RequestsCookieJar复制给session
    session.cookies = c
    # 访问留言板的url
    url = f'https://user.qzone.qq.com/proxy/domain/m.qzone.qq.com/cgi-bin/new/get_msgb?uin=369212851&hostUin=369212851&start={page}&num=10&g_tk={g_tk}&qzonetoken={token}'
    print(url)
    response = session.get(url)
    # 截取无用的字符
    resp_text = response.text[10: -3]
    # 转为json
    resp_json = json.loads(resp_text)
    return resp_json
def replace_html(raw):
    #         dr =re.compile(r'<[^>]+>',re.S)
    dr = re.compile(r'</?\w+[^>]*>', re.S)
    htmlStr = re.sub(dr,'', raw)
    dr = re.compile(r'&nbsp;')
    htmlStr = re.sub(dr,'', htmlStr)
    s = 'http://www.manzuo.com/openPlatform/oauth20/authorize?redirect_uri=http%3a%2f%2fdwz.cn/1NcflA?sid=PvPDgeTLYbHD&amp;qzone.qq.com'
    dr = re.compile(s)
    htmlStr = re.sub(dr,'', htmlStr)



    return htmlStr



def get_zone_xx(cookie, g_tk, token, page=0):
    # 初始化请求为了取总条数
    resp_json = get_resp(cookie, g_tk, token, page)
    # 总条数
    total = resp_json['data']['total']
    print(f'共{total}条留言信息')
    # 总页数
    size = int(total/10 + 1)
    # 已经读取的信息条数
    use_page = 0
    # 保存每条数据信息，生成csv文件用
    content_arr = []
    for i in range(0, size):
        # 请求每一页的内容
        resp_json = get_resp(cookie, g_tk, token, i)
        # 当条数大于或等于总条数 跳出循环
        if use_page >= total:
            break
        # 从每页数据中取出需要的字段值
        for comment in resp_json['data']['commentList']:
            use_page += 1
            print(f'当前正在读取第{use_page}条')
            page_json = []
            # 留言日期
            page_json.append(comment['pubtime'])
            # 昵称
            page_json.append(comment['nickname'])
            # 内容
            content = replace_html(comment['htmlContent'])
            # 将内容写入文本 生成词云用
            with open('zone_text111.txt', 'a') as f:
                f.write(content)

            page_json.append(content)
            content_arr.append(page_json)
            df = pd.DataFrame(data=content_arr,
                              columns=['留言日期', '昵称', '留言内容'])
            df.to_csv('QQ_ZONE.csv', index=False, encoding='utf-8_sig')
            print('已保存为csv文件.')
get_zone_xx(cookie,g_tk,token,0)
