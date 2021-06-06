# _*_ coding: utf-8 _*_
# @Time : 2021/4/2 14:05
# @File : lagou.py
# @Author : yjh
# @Software: PyCharm


# _*_ coding: utf-8 _*_
# @Time : 2021/4/1 16:22
# @File : zhihu.py
# @Author : yjh
# @Software: PyCharm

import os
import time
import pickle

from selenium import webdriver
import requests
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
# 目录文件  在下面
import undetected_chromedriver as uc

from services.base_service import BaseService


class LaGouLoginService(BaseService):
    name = "lagou"

    def __init__(self, settings, retry=5):

        ###################################################
        # 用uc包装chrome，纯净版

        # # self.display = Display(visible=0, size=(800, 800))
        # # self.display.start()
        # # 创建一个参数对象，用来控制chrome以无界面模式打开
        # chrome_options = webdriver.ChromeOptions()
        # # chrome_options.add_argument('--headless')  # # 浏览器不提供可视化页面
        # chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速,GPU加速可能会导致Chrome出现黑屏，且CPU占用率高达80%以上
        # # chrome_options.add_argument('--no-sandbox')
        # # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        #
        # self.browser = uc.Chrome(executable_path=settings.DRIVER_PATH)
        ###################################################

        # 连接本地chrome，非纯净版   chrome.exe --remote-debugging-port=9222
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(executable_path=settings.DRIVER_PATH, options=chrome_options)
        ###################################################

        self.wait = WebDriverWait(self.browser, 120)
        self.url = settings.LOGIN_URLS[self.name]
        self.user = settings.Accounts[self.name]["USERNAME"]
        self.password = settings.Accounts[self.name]["PASSWORD"]
        self.retry = retry  # 重试次数
        self.cookies = {}
        self.user_agent = UserAgent()
        self.settings = settings

    def login(self):
        try:
            self.browser.maximize_window()  # 将窗口最大化防止定位错误
        except Exception as e:
            pass

        # 请求网址
        self.browser.get(self.url)

        while not self.check_login():       # 没登录成功
            self.browser.find_element_by_css_selector('a[data-lg-webtj-_address_id="1p4n"]').click()
            time.sleep(2)
            print('点击输入密码界面')

            # 输入账号
            username = self.wait.until(
                Ec.element_to_be_clickable((By.CSS_SELECTOR, '.input_border input[type="text"]'))
            )
            username.send_keys(self.user)
            # 输入密码
            password = self.wait.until(
                Ec.element_to_be_clickable((By.CSS_SELECTOR, '.input_border input[type="password"]'))
            )
            password.send_keys(self.password)

            # 登录框
            submit = self.wait.until(
                Ec.element_to_be_clickable((By.CSS_SELECTOR, '.login-btn.login-password.sense_login_password.btn-green'))
            )
            submit.click()
            time.sleep(3)

        # 登录成功
        self.save_cookies()
        return self.cookies

    def check_login(self):
        try:
            self.browser.find_element_by_css_selector(".user_dropdown")
            return True
        except Exception as e:
            return False

    def check_cookies(self, cookie_dict):
        response = requests.get(self.url, headers={"User-Agent": getattr(self.user_agent, self.settings.USER_AGENT_TYPE)},
                                cookies=cookie_dict, allow_redirects=False)
        if response.status_code != 200:
            return False
        else:
            return True

    def save_cookies(self):
        '''
        登录成功后 保存账号的cookies
        :return:
        '''
        cookies = self.browser.get_cookies()
        print(os.path.dirname(os.path.abspath(__file__)))
        # pickle.dump(cookies, open("D:/Workspace/python/exercise/CookieService/tools/cookies/lagou.cookies", "wb"))
        for cookie in cookies:
            self.cookies[cookie.get("name")] = cookie.get('value')


if __name__ == "__main__":
    import settings
    import redis
    import json
    lagou = LaGouLoginService(settings)
    # cookies = lagou.login()
    # print(cookies)

    ###################################################
    # redis_cli = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
    # all_cookies = redis_cli.srandmember("lagou:cookies")
    # cooikie_dict = json.loads(all_cookies)
    # # print(cooikie_dict)
    # valid = lagou.check_cookies(cooikie_dict)
    # if valid:
    #     print("有效")
    # else:
    #     print("无效")

    ###################################################
