'''
import os
path1=os.path.abspath('.')   # 表示当前所处的文件夹的绝对路径
print(path1)
path2=os.path.abspath('..')  # 表示当前所处的文件夹上一级文件夹的绝对路径
print(path2)
'''

from setuptools import setup, find_packages
setup(
    name = "coding",
    version = "0.1",
    packages = find_packages(),
)