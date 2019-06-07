# @Time  : 2019-5-15 09:04:37
# @功能  ：集成测试用的各种模块/方法
import re
import time
from lxml import etree
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

def load_modes(Browser,StandardData):
    """
    载入模块,传入Browser对象和StandardData变量
    :param Browser:
    :param StandardData:
    :return:
    """
    global browser
    browser = Browser
    global standarddata
    standarddata=StandardData

def open_url(url):
    """
    打开url
    :param url:
    :return:
    """
    browser.get(url)


def input_data(data):
    """
    输入测试数据;有2种方法定位相应的元素,自动选择
    :param data:
    :return:
    """
    html=browser.page_source
    selector=etree.HTML(html)
    for k,v in data.items():
        print ("    "+k+" --> "+v)
        # 1.通过框旁边的提示符
        try:
            # 找到含有该文本的标签,取其中for属性的值
            K=selector.xpath('//label[contains(string(),"'+k+'")]/@for')
            # print (k)
            # 利用上面找到的for属性的值 找到id属性为它的输入框,输入数据
            input=browser.find_element_by_xpath("//input[@id='"+K[0]+"']")
            ActionChains(browser).double_click(input).perform()
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(v)

        # 2.通过框里面的placeholder提示符
        except :
            input=browser.find_element_by_xpath("//input[@placeholder='"+k+"']")
            ActionChains(browser).double_click(input).perform()
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(v)


def click(words):
    """
    点击按钮操作;有两种方法定位相应的元素,自动选择
    :param words: 按钮关键字
    :return:
    """
    try:
        browser.find_element_by_xpath("//input[@value='"+words+"']").click()
    except:
        button="//button[contains(string(),'" + words + "')]"
        browser.find_element_by_xpath(button).click()
    time.sleep(1)


def judge(judge_words):
    """
    根据给定关键字判断测试结果,匹配到关键字则返回False;
    :param judge_words: 用来判断测试结果的关键字
    :return:
    """
    ret=""
    for k,v in judge_words.items():
        if browser.page_source.find(k) != -1:
            ret=ret+v+";"
    if ret=="":
        ret="成功"
    print("    judge result:"+ret)
    return ret


def confim(input_data,key):
    """
    判断传入json数据的结构是否符合预期要求
    :param input_data: 需要检查的数据
    :param key: 数据在原始json中的key值
    :return:True为符合要求
    """
    key=re.sub("[\\d.]+","",key)
    if type(input_data)==type(standarddata[key]):
        return True
    else:
        return False


