# _*_ coding: utf-8 _*_
# @Time : 2021/4/1 16:22
# @File : run.py
# @Author : yjh
# @Software: PyCharm


from server import CookieServer
from services.zhihu import ZhiHuLoginService
from services.lagou import LaGouLoginService

import settings

srv = CookieServer(settings)

# 注册需要登录的服务
srv.register(ZhiHuLoginService)
# srv.register(LaGouLoginService)

# 启动cookie服务
print("启动cookie池服务")
srv.start()
