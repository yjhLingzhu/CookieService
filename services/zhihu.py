# _*_ coding: utf-8 _*_
# @Time : 2021/4/1 16:22
# @File : zhihu.py
# @Author : yjh
# @Software: PyCharm

import os
import time
import pickle

import redis
from selenium import webdriver
import requests
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
# 目录文件  在下面
import undetected_chromedriver as uc

from tools.zhihu_loger import Code
from services.base_service import BaseService


class ZhiHuLoginService(BaseService):
    name = "zhihu"

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

        # 连接本地chrome，非纯净版
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(executable_path=settings.DRIVER_PATH, options=chrome_options)
        ###################################################

        self.wait = WebDriverWait(self.browser, 120)
        self.url = settings.LOGIN_URLS[self.name]
        self.sli = Code()
        self.user = settings.Accounts[self.name]["USERNAME"]
        self.password = settings.Accounts[self.name]["PASSWORD"]
        self.retry = retry  # 重试次数
        self.cookies = {}
        self.user_agent = UserAgent()  # 随机user_agent
        self.settings = settings

    def login(self):
        try:
            self.browser.maximize_window()  # 将窗口最大化防止定位错误
        except Exception as e:
            pass

        # 请求网址
        self.browser.get(self.url)

        while not self.check_login():  # 没登录成功
            self.browser.find_element_by_css_selector('.SignFlow-tabs .SignFlow-tab:nth-child(2)').click()
            time.sleep(2)
            print('点击输入密码界面')

            # 输入账号
            username = self.wait.until(
                Ec.element_to_be_clickable((By.CSS_SELECTOR, '.SignFlow-accountInput input'))
            )
            username.send_keys(self.user)
            # 输入密码
            password = self.wait.until(
                Ec.element_to_be_clickable((By.CSS_SELECTOR, ".SignFlow-password .Input-wrapper input"))
            )
            password.send_keys(self.password)

            # 登录框
            submit = self.wait.until(
                Ec.element_to_be_clickable((By.CSS_SELECTOR, '.Button.SignFlow-submitButton'))
            )
            submit.click()
            time.sleep(3)

            k = 1
            # while True:
            while k < self.retry:
                # self.browser.switch_to.frame("tcaptcha_iframe")
                # 获取滑动前页面的url网址
                # 1. 获取原图
                bg_img = self.wait.until(
                    Ec.presence_of_element_located((By.CSS_SELECTOR, '.yidun_bgimg img.yidun_bg-img'))
                )
                # 获取滑块链接
                front_img = self.wait.until(
                    Ec.presence_of_element_located(
                        (By.CSS_SELECTOR, ".yidun_bgimg img.yidun_jigsaw")))
                # 获取验证码滑动距离
                distance = self.sli.get_element_slide_distance(front_img, bg_img)
                print('滑动距离是', distance)

                # 2. 乘缩放比例， -去  滑块前面的距离  下面给介绍
                # distance = distance * 340 / 680 - 35          # 这里是原来的
                distance = (distance * 340 / 680) * 2  # 这里通过实验，滑动距离应该是之前的两倍
                print('实际滑动距离是', distance)

                # 滑块对象
                element = self.browser.find_element_by_css_selector(
                    '.yidun_control .yidun_slider')
                # 滑动函数
                self.sli.slide_verification(self.browser, element, distance)

                # TODO 验证是否通过滑块
                # 滑动之后的url链接
                time.sleep(2)
                end_url = self.browser.current_url
                print(end_url)

                if self.check_login():
                    # self.save_cookies()
                    # print(self.cookies)
                    k = self.retry + 1
                else:
                    # reload = self.browser.find_element_by_css_selector("#reload div")
                    # self.browser.execute_script("arguments[0].click();", reload)
                    # time.sleep(5)

                    k += 1
        # 登录成功
        self.save_cookies()
        return self.cookies

    def check_login(self):
        try:
            self.browser.find_element_by_css_selector("#Popover15-toggle")
            return True
        except Exception as e:
            return False

    def check_cookies(self, cookie_dict):
        user_agent = getattr(self.user_agent, self.settings.USER_AGENT_TYPE)
        # cookie = ""
        # for k, v in cookie_dict.items():
        #     cookie += k + "=" + v + ";"
        #
        # cookie = cookie[:len(cookie)-1]
        headers = {
            "User-Agent": user_agent,
        }
        proxy = {
                    'http': '183.166.132.127:9999',
        }
        # print(user_agent)
        response = requests.get(self.url, headers=headers, cookies=cookie_dict, allow_redirects=False)
        print(response.status_code)
        # with open("a.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)
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
        # pickle.dump(cookies, open("D:/Workspace/python/exercise/CookieService/tools/cookies/zhihu.cookies", "wb"))
        for cookie in cookies:
            self.cookies[cookie.get("name")] = cookie.get('value')


if __name__ == "__main__":
    import settings
    import json

    zhihu = ZhiHuLoginService(settings)
    # cookies = zhihu.login()
    # print(cookies)

    redis_cli = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
    all_cookies = redis_cli.srandmember("zhihu:cookies")
    cooikie_dict = json.loads(all_cookies)
    # print(cooikie_dict)
    valid = zhihu.check_cookies(cooikie_dict)
    if valid:
        print("有效")
    else:
        print("无效")
