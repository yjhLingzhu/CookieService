# _*_ coding: utf-8 _*_
# @Time : 2021/4/2 13:26
# @File : settings.py
# @Author : yjh
# @Software: PyCharm

# 各个网站的用户账号密码
Accounts = {
    "zhihu": {
        "USERNAME": "17875513387",
        "PASSWORD": "***",
        "COOKIE_KEY": "zhihu:cookies",
        "MAX_COOKIE_NUMS": 1,  # redis最多存放的cookie数量
        "CHECK_INTERVAL": 1000  # cookie检测的间隔时间
    },
    "lagou": {
        "USERNAME": "17875513387",
        "PASSWORD": "***",
        "COOKIE_KEY": "lagou:cookies",
        "MAX_COOKIE_NUMS": 1,  # redis最多存放的cookie数量
        "CHECK_INTERVAL": 1000  # cookie检测的间隔时间
    }
}

# 各个网站登录url
LOGIN_URLS = {
    "zhihu": "https://www.zhihu.com/signin",
    "lagou": "https://www.lagou.com/"
}

# Chrome Driver Path
DRIVER_PATH = "D:/Workspace/python/wheels/chromedriver.exe"

# User_Agent_Type
USER_AGENT_TYPE = "random"

# 配置redis
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
