# _*_ coding: utf-8 _*_
# @Time : 2021/4/2 16:19
# @File : server.py
# @Author : yjh
# @Software: PyCharm

import json
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

import redis


# 确保每个网站都会被单独运行
class CookieServer:

    def __init__(self, settings):
        self.settings = settings
        self.redis_cli = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        self.service_list = []

    def register(self, cls):
        self.service_list.append(cls)

    def login_service(self, service):
        while 1:
            service_cli = service(self.settings)
            service_name = service_cli.name
            cookie_nums = self.redis_cli.scard(self.settings.Accounts[service_name]["COOKIE_KEY"])
            if cookie_nums < self.settings.Accounts[service_name]["MAX_COOKIE_NUMS"]:
                print("{name}登录获取新的cookies".format(name=service_name))
                cookie_dict = service_cli.login()
                self.redis_cli.sadd(self.settings.Accounts[service_name]["COOKIE_KEY"], json.dumps(cookie_dict))
            else:
                print("{service_name} 的cookie池已满，等待3s".format(service_name=service_name))
                time.sleep(3)

    def check_cookie_service(self, service):
        while 1:
            service_cli = service(self.settings)
            service_name = service_cli.name
            all_cookies = self.redis_cli.smembers(self.settings.Accounts[service_name]["COOKIE_KEY"])
            print("{0}目前可用的cookie数量： {1}".format(service_name, len(all_cookies)))
            if len(all_cookies) != 0:
                for cookie_str in all_cookies:
                    print("获取到cookie: {}".format(cookie_str))
                    cookie_dict = json.loads(cookie_str)
                    valid = service_cli.check_cookies(cookie_dict)
                    if valid:
                        print("{name}的一个cookie有效".format(name=service_name))
                    else:
                        print("{name}的一个cookie已经失效， 删除该cookie".format(name=service_name))
                        self.redis_cli.srem(self.settings.Accounts[service_name]["COOKIE_KEY"], cookie_str)
            # 设置间隔，防止出现请求过于频繁，导致本来没失效的cookie失效了
            interval = self.settings.Accounts[service_name]["CHECK_INTERVAL"]
            print("{}s 后重新开始检测cookie".format(interval))
            time.sleep(interval)

    def start(self):
        task_list = []
        print("启动登录服务")
        login_executor = ThreadPoolExecutor(max_workers=5)  # 创建线程池
        for service in self.service_list:
            task = login_executor.submit(partial(self.login_service, service))  # partial函数可以将函数和参数打包形成一个新的函数
            task_list.append(task)

        print("启动cookie检测服务")
        check_executor = ThreadPoolExecutor(max_workers=5)  # 创建线程池
        for service in self.service_list:
            task = check_executor.submit(partial(self.check_cookie_service, service))
            task_list.append(task)

        for future in as_completed(task_list):
            data = future.result()
            print(data)


