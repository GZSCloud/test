#@功能：利用selenium实现简单的自动登录测试
#@时间: 2019年4月28日20:59
from selenium import webdriver
browser = webdriver.Chrome()
url = 'https://github.com/login'
browser.get(url)

def login(item):
    '''
    通过xpath语句匹配合适的标签名和属性名，找到登录框的用户名输入框，密码输入框和登录按钮；
    用send_keys()输入测试值提交表单进行登录，通过返回的网页中的关键字判断是否登录成功。

    :param item: item列表应有两个元素，测试用的用户名和密码
    :return: True/False 登录成功返回True，不成功返回False
    '''

    # 找到用户名输入框：为input标签且name属性等于'login'或者type属性等于'text'
    name=browser.find_element_by_xpath("//input[@name='login'or@type='text']")
    name.clear()
    name.send_keys(item[0])

    # 找到密码输入框：为input标签且type属性等于'password'
    passwd=browser.find_element_by_xpath("//input[@type='password']")
    passwd.clear()
    passwd.send_keys(item[1])

    # 找到为input标签且type属性值为'submit'的"提交"按钮并点击
    browser.find_element_by_xpath("//input[@type='submit']").click()

    # 在网页源码中匹配相应的关键字，判断是否登陆成功
    if browser.page_source.find("Incorrect username or password.") != -1:
        return False
    else:
        return True


# 由于在python3中map输出的是可迭代对象，可以用list()让它自动迭代运行，否则不会运行函数
print(list(map(login,[["abcd","1234"],["hubu","1234"],["cdef","1234"]])))