# @Time  : 2019-5-15 08:38:38
# @功能  ：利用selenium实现简单的提交表单类型的自动化测试
import json
import time
import models
from selenium import webdriver


browser = webdriver.Chrome()
def login(jsonData):
    """
    主要方法,通过传输为标准json字符串的参数，实现提交表单类型的自动化测试；\n
    :param jsonData: json标准格式的字符串\n
    :return: 测试错误信息/测试结果信息
    """
    print("[start]")

    # 解析json字符串，转换成相应的数据结构, 检查json的语法;
    try:
        data = json.loads(jsonData)
    except:
        return "json格式错误"

    #检查json转换后的数据格式是否符合预期
    for key in data:
        if(models.confim(data[key],key)==False):
            return "数据格式错误--"+key

    # 遍历data里面的数据,并选取相应的方法执行操作;
    res=[]
    for key in data:
        if key.find('open_url')==0:
            models.open_url(data[key])
            print('[ok]--'+key)
            continue
        elif key.find('input_data')==0:
            models.input_data(data[key])
            print('[ok]--'+key)
            continue
        elif key.find('click')==0:
            models.click(data[key])
            print('[ok]--'+key)
            continue
        elif key.find('judge_words')==0:
            res.append(models.judge(data[key]))
            print('[ok]--'+key)
            continue
        elif key.find('sleep')==0:
            time.sleep(data[key])
            print('[ok]--'+key)
            continue
    print ("[done]\n")
    # 返回测试结果字符串列表,因为可能有多个结果判断操作
    return res


# 测试数据基本做到了一个key值执行一次操作,按顺序从上至下执行;
# 由于key值不能重复,第二次及以后执行同样操作时,用操作名+数字代替,例如click2,click3;
JsonDatas = ["""{
    "open_url":"https://github.com/login",
    "input_data": {"Username or email address":"abcd","Password":"1234"},
    "click":"Sign in",
    "judge_words":{"Incorrect username or password.":"用户名或者密码错误"}
    }""",
    """{
    "open_url":"http://39.98.190.128/index.html#/login",
    "input_data": {"请输入用户名":"admin","请输入密码":"1234"},
    "click":"登录",
    "click2":"残忍拒绝",
    "click3":"登录",
    "judge_words":{"请输入正确的用户名":"用户名不合规","用户名或密码错误":"用户名或密码错误"}
}"""]

# 标准样本数据,包含已定义了的所有模块,用于与输入的数据类型比较,看是否符合预期
StandardData={
    "open_url":"1",
    "input_data": {"a":"1"},
    "click":"a",
    "judge_words":{"a":"1"},
    "sleep":1
}

if __name__ == '__main__':
    # 由于在python3中map输出的是可迭代对象，可以用list()让它自动迭代运行，否则不会运行函数
    # print(list(map(login, JsonDatas)))
    models.load_modes(browser,StandardData)
    n=1
    s=""
    for result in map(login, JsonDatas):
        s=s+">测试用例%d:%s\n" % (n, result)
        n+=1
    print("[测试结果]")
    print (s)
