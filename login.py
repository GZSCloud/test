# @Time  : 2019/5/10 22:11
# @功能  ：利用selenium实现简单的提交表单类型的自动化测试
from selenium import webdriver
import json
browser = webdriver.Chrome()


def login(jsonData):
    """
    通过传输为标准json字符串的参数，实现提交表单类型的自动化测试；
    支持任意多个输入框的定位和输入，此时xpath和data为数组形式；
    :param jsonData: json标准格式的字符串
    :return: True/False 在响应的页面中匹配judge_words成功返回True，不成功返回False
    """
    ##检查json串格式

    # 解析json字符串，转换成相应的数据结构
    data = json.loads(jsonData)

    # 打开网页
    browser.get(data['url'])
    ##key写成list,再从list读出
    #对moudles中的key解析成相应的xpath语句
    for k,v in data['moudles'].items():
        data['moudles'][k]="//input[@name='%s']"% v

    #对最后click的key解析成相应的xpath语句
    for k,v in data['click'].items():
        data['click'][k]="//input[@type='%s']"% v

    # 根据key和data实现自动定位到输入框并输入数据,支持一个网页中任意多个输入框的输入
    for i in range(0,len(data['moudles'])):
        name = browser.find_element_by_xpath(list(data['moudles'].values())[i])
        name.clear()
        name.send_keys(list(data['data'].values())[i])

    # 点击按钮
    browser.find_element_by_xpath(list(data['click'].values())[0]).click()


    # 在返回的网页源码中匹配相应的关键字，判断是否登陆成功
    if browser.page_source.find(data["judge_words"]) != -1:
        return False
    else:
        return True

# ["登录":"login","查询":"browse","退出","exit"]
# 标准json字符串格式，以后将支持从数据库中读取关键字自动生成json格式的字符串数组
JsonDatas = ["""{
    "url":"https://github.com/login",
    "moudles":{"登录名":"login","密码":"password"},
    "data": {"登录名":"abcd","密码":"1234"},
    "click":{"登录":"submit"},
    "judge_words":"Incorrect username or password."
}"""]

# 可以用testdata存放测试用例,写一个方法自动生成JsonDatas



if __name__ == '__main__':
    # 由于在python3中map输出的是可迭代对象，可以用list()让它自动迭代运行，否则不会运行函数
    print(list(map(login, JsonDatas)))
