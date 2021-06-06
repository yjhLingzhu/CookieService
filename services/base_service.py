# _*_ coding: utf-8 _*_
# @Time : 2021/4/2 14:59
# @File : base_service.py
# @Author : yjh
# @Software: PyCharm


import abc


# 强制实现login方法，这是抽象类
class BaseService(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def login(self):
        pass

    @abc.abstractmethod
    def check_cookies(self, cookie_dict):
        pass
