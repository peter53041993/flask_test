import random
from time import sleep

from selenium.webdriver import ActionChains

from Utils.Logger import create_logger
from selenium import webdriver
from selenium.webdriver.remote.command import Command
from enum import Enum
from Utils import Config
from Utils import TestTool
from Utils.TestTool import trace_log


class BasePage:
    logger = create_logger(r'\AutoTest', 'base_page')
    driver = None
    envConfig = None
    link = None
    user = None
    password = None

    @staticmethod
    class CustomPages(Enum):  # 部分需直接跳轉頁面
        register = "register"

    def __init__(self, env_domain=None, last_page=None):
        """
        POM物件初始化
        可能情況：
        1. 網頁新建 -> LoginPage('Dev02') -> __init__(env)
        2. 網頁移動 -> MainPage(self) -> __init__(self)
        :param env_domain:　指定測試網域，用於初始POM物件，同時新創建driver
        :param last_page: 上一個頁面的POM物件，若不為空則以此物件參數進行初始化、沿用參數
        """
        if last_page is not None:
            self.envConfig = last_page.envConfig
            self.driver = last_page.driver
            self.user = last_page.user
            self.password = last_page.password
            self.logger = last_page.logger
        else:
            if type(env_domain) is Config.EnvConfig:
                self.envConfig = env_domain
            else:
                self.envConfig = Config.EnvConfig(env_domain)
            self.get_driver()

    def get_driver(self):
        if self.driver is None:
            try:
                if 'ChromeDriver' in locals() or 'ChromeDriver' in globals():
                    self.driver = webdriver.Chrome(chrome_options=Config.chrome_options)
                else:
                    self.driver = webdriver.Chrome(Config.chromeDriver_Path, chrome_options=Config.chrome_options)
                self.driver.implicitly_wait(10)
                self.driver.set_page_load_timeout(120)
            except Exception as e:
                TestTool.trace_log(e)
        return self.driver

    def go_to(self):
        self.driver.get(self.envConfig.get_post_url() + self.link)

    def check_driver_state(self):
        try:
            self.driver.execute(Command.STATUS)
            return True
        except Exception as e:
            trace_log(e)
            return False

    def get_visibal_elements(self, elements):
        tempElements = []
        for element in elements:
            if element.get_attribute('style') != 'display:none':
                tempElements += element
        return tempElements

    def dir_jump_to(self, page_name):
        if page_name in self.CustomPages:
            if page_name == self.CustomPages.register:
                return RegPage(self)


class LoginPage(BasePage):
    @staticmethod
    class elements(Enum):
        id_input_account = 'J-user-name'
        id_input_password = 'J-user-password'
        id_button_login = 'J-form-submit'
        xpath_button_sign_up = '//*[@id="J-button-submitDev"]/li[3]/a'
        id_button_free_trial = 'freeTrial'
        id_button_save_login = 'safeLogin'
        xpath_button_forget_password = '//*[@id="J-button-submitDev"]/li[1]/a'

    def __init__(self, env_domain):
        super().__init__(env_domain)
        self.link = "/login"
        self.go_to()

    def login(self, user, password):
        self.user = user
        self.password = password
        self.driver.find_element_by_id(self.elements.id_input_account.value).send_keys(user)
        self.driver.find_element_by_id(self.elements.id_input_password.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.id_button_login.value).click()
        sleep(3)
        return MainPage(self)


class RegPage(BasePage):
    @staticmethod
    class elements(Enum):
        id_user_name_input = 'J-input-username'
        id_password_input = 'J-input-password'
        id_password_confirm = 'J-input-password2'
        id_submit = 'J-button-submit'

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        user_id = Config.get_sql_exec(self.envConfig.get_env_id(),
                                      "select id from user_customer where account = '{}'".format(self.user))
        print("user_id = {}".format(user_id[0]))
        reg_url = Config.get_sql_exec(self.envConfig.get_env_id(),
                                      "select url from user_url where days = -1 and creator = '{}'".format(user_id[0]))
        print("reg_url = {}".format(reg_url[0]))
        self.link = "/register?{url}".format(url=reg_url[0])

    def register(self):
        self.go_to()
        _random = random.randint(1, 100000)
        new_user = self.user + str(_random)
        self.driver.find_element_by_id(self.elements.id_user_name_input.value).send_keys(new_user)
        self.driver.find_element_by_id(self.elements.id_password_input.value).send_keys(self.password)
        self.driver.find_element_by_id(self.elements.id_password_confirm.value).send_keys(self.password)
        self.driver.find_element_by_id(self.elements.id_submit.value).click()
        sleep(5)
        self.user = new_user
        assert '/index' in self.driver.current_url
        return MainPage(self)


class MainPage(BasePage):
    """首頁"""

    i_user_header = 'headerUsername'

    @staticmethod
    class buttons_personal(Enum):
        bet_record = 'betRecord'
        account_detail = 'accountDetail'
        proxy_center = 'proxyCenter'
        query_report = 'queryReport'
        front_score_mall = 'frontScoreMall'
        app_center = 'safeCenter'

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = "/"

    def jump_to(self, page):
        """
        點擊對應連結按鈕
        :param page: self.Personal / self.Bet
        :return: 對應頁面 Class
        """
        if page in self.buttons_personal:
            ActionChains(self.driver).move_to_element(self.driver.find_element_by_id(self.i_user_header)).perform()
            self.driver.find_element_by_id(page.value).click()
            if page == self.buttons_personal.app_center:
                from page_objects.PersonalPages import Personal_AppCenterPage
                return Personal_AppCenterPage(self)
            else:
                raise Exception('POM尚未建立')
        else:
            raise Exception('無對應對象')
