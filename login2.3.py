# @Time  : 2019/4/28 22:11
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

    # 解析json字符串，转换成相应的数据结构
    data = json.loads(jsonData)

    # 打开网页
    browser.get(data['url'])

    # 根据xpath语句和data实现自动定位到输入框并输入数据
    # 支持一个网页中任意多个输入框的输入
    if str(type(data['xpath'])) == "<class 'list'>":
        for i in range(0,len(data['xpath'])):
            name = browser.find_element_by_xpath(data['xpath'][i])
            name.clear()
            name.send_keys(data['data'][i])
    else:
        item = browser.find_element_by_xpath(data['xpath'])
        item.clear()
        item.send_keys(data['data'])

    #  查找提交按钮并点击
    browser.find_element_by_xpath(data['xpath_submit']).click()

    # 在网页源码中匹配相应的关键字，判断是否登陆成功
    if browser.page_source.find(data["judge_words"]) != -1:
        return False
    else:
        return True


# 标准json字符串格式，以后将支持从数据库中读取关键字自动生成json格式的字符串数组
JsonData = ["""{
    "url":"https://github.com/login",
    "xpath":["//input[@name='login'or@type='text']","//input[@type='password']"],
    "data": ["abcd","1234"],
    "xpath_submit":"//input[@type='submit']",
    "judge_words":"Incorrect username or password."
}"""]

if __name__ == '__main__':
    # 由于在python3中map输出的是可迭代对象，可以用list()让它自动迭代运行，否则不会运行函数
    print(list(map(login, JsonData)))
