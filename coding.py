from git import *
from urllib.parse import quote
import pymysql
import xlrd
import re
import logging
import os
import os.path
import shutil
import optparse

"""
    python coding.py -m telecomback -v telecomfront -D telcomksh -u root -p password -d test -b /huxt -s src/main/resources/db/telcomksh.sql
    还未解决：
    项目文件夹已经存在会报错----------------------------已解决, 存在则删除
    数据库，表需要手动创建------------------------------已解决
    下载下来的项目的配置文件没有更改-------------------------待解决
    编译部署后还没有运行--------------------------放到程序最后运行
    log文件夹没有判断存不存在----------------------不存在则创建，存在则不变
    没有判断部署目录是否存在---------------------------存在则删除
    还没有加命令行输入数据库sql文件的路径----------------------已解决,但是要相对于maven根目录
    没有创建单独工作目录----------------------已解决
    
    一个项目一个表，共用一个测试数据库
    version表
    CREATE TABLE `version` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `filename` varchar(100) DEFAULT NULL,
      `version` varchar(1000) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8"""

PWD = os.getcwd()
LOGFILE = "log/coding.log"
# LOGFILE = "/var/log"
GITUSER = "xing_gang"
GITPASS = "Xing@qq.com"


class Downloader(object):
    def __init__(self, maven_url, maven_dir, maven_branch, maven_config_list, vue_url, vue_dir, vue_branch, vue_config_list, database_name, user_name, password, project_dir, deploy_dir, sqlfile):
        self.project_dir = project_dir
        if os.path.exists(self.project_dir):  # 如果存在则删除
            shutil.rmtree(self.project_dir)
        os.mkdir(self.project_dir)
        # self.url = url
        # self.Repo = Repo.clone_from("https://git.coding.net/myhomeCode/telecomback.git", dir)
        # self.branch_list = self.Repo.git.branch("-r").split()[3:]
        self.maven_url = maven_url
        self.maven_dir = maven_dir
        self.maven_config_list = maven_config_list
        self.vue_url = vue_url
        self.vue_dir = vue_dir
        self.vue_config_list = vue_config_list
        self.maven_branch = maven_branch
        self.vue_branch = vue_branch
        self.database_name = database_name
        self.user_name = user_name
        self.password = password
        self.sqlfile = sqlfile
        self.deploy_dir = deploy_dir    # 部署位置
        os.chdir(PWD)
        self.version_list = []    # 文件里的版本信息, 本来想以list里的map来存储，但是考虑到全自动化，编号更合适, len(version_list)就是项目总数

    def get_version(self, filename):
        # 将文件名和版本号存入self.version_list
        sheet = xlrd.open_workbook(filename).sheet_by_index(0)
        for i in zip([i for i in sheet.col_values(1)[2:] if i != ""], [i for i in sheet.col_values(4)[2:] if i != ""]):
            self.version_list.extend([i])
        conn = pymysql.connect(host='127.0.0.1', port=3306, db='version_713', user=self.user_name, passwd=self.password, charset='utf8')
        cursor = conn.cursor()
        for i in self.version_list:
            print(i)
            cursor.execute("insert into version value(NULL, %s, %s);", [i[0], i[1]])  # 插入数据库
        logging.debug(i[0] + " : " + i[1] + "  has been inserted into MySQL successfully")
        conn.commit()
        cursor.close()
        conn.close()

    def clone_version(self, pro_list):
        """git_Number为项目编号, 从0开始"""
        os.chdir(self.project_dir)
        url = pro_list[0]
        git_dir = pro_list[1]
        branch = pro_list[2]
        tmp = url.split("//")
        git_url = tmp[0] + "//" + quote(GITUSER) + ":" + quote(GITPASS) + "@" + tmp[1]
        repo = Repo.clone_from(git_url, git_dir)
        g = repo.git
        g.checkout(branch)
        os.chdir(PWD)
        logging.debug(git_dir + " : " + url + "  has been downloaded successfully")

    def find_version(self):
        pass

    def clone_all_item(self):
        for i in [[self.maven_url, self.maven_dir, self.maven_branch], [self.vue_url, self.vue_dir, self.vue_branch]]:
            self.clone_version(i)

    def vue_install(self):
        os.chdir(self.project_dir)
        os.chdir(self.vue_dir)
        result = os.popen("yarn install")  # at least need three times
        print("[+]------------------------------yarn install")
        r = result.read()

        while "Done in" not in r:
            result = os.popen("yarn install")
            print("[+]------------------------------yarn install")
            r = result.read()
            print(r)
            logging.debug(r)
            result.close()
        for i in range(3):
            result = os.popen("yarn install")
        while "Done in" not in r:
            result = os.popen("yarn install")
            print("[+]------------------------------yarn install")
            r = result.read()
            print(r)
            logging.debug(r)
            result.close()

        # os.mkdir("static")    # 貌似前端已经修复
        result = os.popen("npm run build:prod")
        print("[+]------------------------------npm run build:prod")
        logging.debug("[+]------------------------------npm run build:prod")
        tmp = result.read()
        logging.debug(tmp)
        os.chdir(PWD)

    def vue_deploy(self):
        os.chdir(self.project_dir)
        os.chdir(self.vue_dir)
        r = shutil.move("dist", self.deploy_dir)
        logging.debug("vue project move to " + r)
        os.chdir(PWD)


    def maven_config(self):
        os.chdir(self.project_dir)
        f = open(self.maven_config_list[0])
        config_list = f.readlines()
        for i in range(len(config_list)):
            if "datasource.url=" in config_list[i]:
                config_list[i] = self.maven_config_list[1]+"\n"
            elif "datasource.username=" in config_list[i]:
                config_list[i] = self.maven_config_list[2]+"\n"
            elif "datasource.password=" in config_list[i]:
                config_list[i] = self.maven_config_list[3]+"\n"
        f.close()
        f = open(self.maven_config_list[0], "w+")
        f.writelines(config_list)
        f.close()
        os.chdir(PWD)


    def vue_config(self):
        os.chdir(self.project_dir)
        f = open(self.vue_config_list[0])
        config_list = f.readlines()
        for i in range(len(config_list)):
            if "BASE_API:" in config_list[i]:
                config_list[i] = self.vue_config_list[1]+"\n"
        f.close()
        f = open(self.vue_config_list[0], "w+")
        f.writelines(config_list)
        f.close()
        os.chdir(PWD)


    def maven_install(self):
        os.chdir(self.project_dir)
        os.chdir(self.maven_dir)

        result = os.popen("mvn compile")
        print("[+]------------------------------mvn compile")
        logging.debug("[+]------------------------------mvn compile")
        tmp = result.read()
        print(tmp)
        logging.debug(tmp)
        result.close()

        result = os.popen("mvn package -Dmaven.test.skip=true")
        print("[+]------------------------------mvn package -Dmaven.test.skip=true")
        logging.debug("[+]------------------------------mvn package -Dmaven.test.skip=true")
        tmp = result.read()
        print(tmp)
        logging.debug(tmp)
        result.close()

        self.jar_file = re.findall("Building jar: (.*)", tmp)[0]
        print("[+]------------------------------Building jar :", self.jar_file)
        logging.debug("[+]------------------------------Building jar :", self.jar_file)
        os.chdir(PWD)

    def maven_deploy(self):
        os.chdir(self.project_dir)
        os.chdir(self.maven_dir)
        tmp = shutil.copy(self.jar_file, self.deploy_dir+"/back")
        logging.debug("Maven jar file deploy to " + tmp)
        os.chdir(PWD)

    def database(self):
        os.chdir(self.project_dir)
        conn = pymysql.connect("127.0.0.1", self.user_name, self.password, "", charset="utf8")
        sql = "CREATE DATABASE IF NOT EXISTS " + self.database_name
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        commands = "mysql -u" + self.user_name + " -p" + self.password + " -D" + self.database_name + " < " + self.sqlfile
        print(commands)
        logging.debug(commands)
        os.popen(commands).read()
        print("Mysql Database", self.database, "Create OK")
        os.chdir(PWD)


def get_config(filename, sheetnum):
    dir_case = filename
    data = xlrd.open_workbook(dir_case)
    sheet = data.sheets()[sheetnum]
    result = []
    d = {}
    for i in range(1, sheet.nrows):
        if sheet.cell_value(i, 0) == "":
            result[-1].append(sheet.cell_value(i, sheet.ncols-1))
            continue
        tmp = []
        for j in range(sheet.ncols):
            tmp.append(sheet.cell_value(i, j))
        result.append(tmp)
    for i in result:
        d[i[0]] = i[1:]
    return d

def main():
    if not os.path.exists("log"):  # 如果log目录不存在则创建
        os.mkdir("log")
    logging.basicConfig(level=logging.DEBUG,
                        filename=LOGFILE,
                        filemode='a',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
    # parser = optparse.OptionParser(
    #     """Usage: env.py -m <Maven Dir> -v <Vue Dir> -D <DataBase Name> -u <UserName> -p <PassWord> -d <Directory> -b <DeployDir> -s <sqlfile>
    #             python coding.py -m telecomback -v telecomfront -D telcomksh -u root -p password -d test -b /huxt -s src/main/resources/db/telcomksh.sql""",
    #     version="V0.1.00")
    # parser.add_option("-m", "--maven", action="store", type="string", dest="maven_dir", help="Must be Maven Project Directory Name")
    # parser.add_option("-v", "--vue", action="store", type="string", dest="vue_dir", help="Must be Vue Project Directory Name")
    # parser.add_option("-D", "--database", action="store", type="string", dest="database_name", help="Database Name")
    # parser.add_option("-u", "--user", action="store", type="string", dest="user_name", help="Mysql User Name")
    # parser.add_option("-p", "--password", action="store", type="string", dest="password", help="Mysql PassWord")
    # parser.add_option("-d", "--dir", action="store", type="string", dest="directory", help="Work Directory")
    # parser.add_option("-b", "--deploy", action="store", type="string", dest="deploy_dir", help="Deploy Directory")
    # parser.add_option("-s", "--sql", action="store", type="string", dest="sqlfile", help="Sqlfile Directory (Must in MavenRoot)")
    # options, args = parser.parse_args()
    # d = Downloader(options.maven_dir, options.vue_dir, options.database_name, options.user_name, options.password, options.directory, options.deploy_dir, options.sqlfile)
    filedata = get_config("version.xlsx", 1)
    for i in filedata:
        print(i, filedata[i])
    config = {
        "maven_url": filedata["back"][1].split()[0],
        "maven_dir": filedata["back"][0],
        "maven_branch": filedata["back"][1].split()[1],
        "maven_config_list": filedata["backconfig"],
        "vue_url": filedata["front"][1].split()[0],
        "vue_dir": filedata["front"][0],
        "vue_branch": filedata["front"][1].split()[1],
        "vue_config_list": filedata["frontconfig"],
        "database_name": re.findall("3306/(.*?)\?", filedata["backconfig"][1])[0],
        "user_name": re.findall("username=(.*?)$", filedata["backconfig"][2])[0],
        "password": re.findall("password=(.*?)$", filedata["backconfig"][3])[0],
        "project_dir": "tmp",
        "deploy_dir": filedata["backuri"][1],
        "sqlfile": filedata["dbsql"][0] + "\\" + filedata["dbsql"][1],
    }
    for i in config:
        print(config[i])
    # python coding.py -m telecomback -v telecomfront -D telcomksh -u root -p password -d test -b /huxt -s src/main/resources/db/telcomksh.sql
    # maven_dir, vue_dir, database_name, user_name, password, project_dir, deploy_dir, sqlfile):
    d = Downloader(**config)
    d.get_version('version.xlsx')
    d.clone_all_item()
    d.maven_config()
    d.vue_config()
    d.database()
    d.maven_install()
    d.maven_deploy()
    d.vue_install()
    d.vue_deploy()

if __name__ == '__main__':
    main()

