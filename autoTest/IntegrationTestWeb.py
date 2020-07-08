import datetime
import os
import unittest
from time import sleep

from bs4 import BeautifulSoup
from faker import Factory
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import random

import utils.Config
from page_objects.BasePages import LoginPage, MainPage
from page_objects.BetPages import BetPage_Xjssc
from page_objects.PersonalPages import Personal_AppCenterPage
from utils import Config, Logger
from utils.Config import LotteryData


def date_time():  # 給查詢 獎期to_date時間用, 今天時間
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    format_day = '{:02d}'.format(day)
    return '%s-%s-%s' % (year, month, format_day)


def get_order_code_web(conn, user, lottery):  # webdriver頁面投注產生定單
    with conn.cursor() as cursor:
        sql = "select order_code from game_order where userid in \
        (select id from user_customer where account = '{user}' \
        and order_time > to_date('{time}','YYYY-MM-DD')and lotteryid = {lottery_id})".format(user=user,
                                                                                             time=date_time(),
                                                                                             lottery_id=
                                                                                                           LotteryData.lottery_dict[
                                                                                                               lottery][
                                                                                                               1])
        cursor.execute(sql)
        rows = cursor.fetchall()

        order_code = []
        for i in rows:  # i 生成tuple
            order_code.append(i[0])
    conn.close()
    return order_code


def select_user_url(conn, userid):
    with conn.cursor() as cursor:
        sql = "select url from user_url where url like '%{}%' and days = -1".format(userid)
        cursor.execute(sql)
        rows = cursor.fetchall()
        user_url = []

        for i in rows:
            user_url.append(i[0])
    conn.close()
    return user_url


logger = Logger.create_logger(r"\AutoTest", 'auto_test_integration')


class IntegrationTestWeb(unittest.TestCase):
    u"瀏覽器功能測試"
    env_config = None
    user = None
    red_type = None
    driver = None
    password = None
    post_url = None
    em_url = None
    pageObject = None

    def setUp(self):
        logger.info('IntegrationTestWeb setUp : {}'.format(self._testMethodName))

    def __init__(self, case, env_config, user, red_type):
        super().__init__(case)
        self.env_config = env_config
        self.user = user
        self.password = self.env_config.get_password()
        self.red_type = red_type

    # def mul_submit(self):  # 追號
    #     try:
    #         if self.driver.find_element_by_xpath('//*[@id="J-redenvelope-switch"]/label/input').is_selected():
    #             self.driver.find_element_by_xpath('//*[@id="J-redenvelope-switch"]/label/input').click()  # 取消紅包追號
    #     except:
    #         pass
    #     self.id_element('randomone')  # 先隨機一住
    #     self.id_element('J-trace-switch')  # 追號
    #

    def test_xjssc(self):
        self.pageObject = LoginPage(env_config=self.env_config).login(user=self.user, password=self.password)
        self.pageObject = BetPage_Xjssc(self.pageObject).bet_all()
        self.getImage()

    def test_change_password(self):
        """
        修改密碼測試
        :return: None
        """
        try:
            self.pageObject = LoginPage(env_config=self.env_config) \
                .login(user=self.user, password=self.password) \
                .jump_to(page=MainPage.buttons_personal.safe_center) \
                .jump_to(button=Personal_AppCenterPage.buttons.b_change_password) \
                .change_password(password=self.password)
            url = self.pageObject.get_current_url()
            assert '/login' in url
        except Exception as e:
            from utils.TestTool import trace_log
            logger.error(e)
            raise e
        self.getImage()

    def getImage(self):
        """
        截取图片,并保存在images文件夹
        :return: 无
        """
        timestamp = datetime.time.strftime('%Y%m%d_%H.%M.%S')
        imgPath = os.path.join(Config.project_path + '/autoTest/screenshot', '{}.png'.format(str(timestamp)))

        self.pageObject.get_driver().save_screenshot(imgPath)
        print('screenshot:{}.png'.format(timestamp))

    # def test_applycenter(self):
    #     """開戶中心/安全中心/綁卡"""
    #
    #     if self.password == '123qwe':
    #         safe_pass = 'hsieh123'
    #     elif self.password == 'amberrd':
    #         safe_pass = 'kerr123'
    #     else:
    #         raise Exception('無對應安全密碼，請至test_applycenter新增')
    #
    #     user_id = utils.Config.get_user_id(utils.Config.get_conn(self.envConfig.get_env_id()),
    #                                        self.user)  # 找出用戶 Userid  , 在回傳給開戶連結
    #     user_url = select_user_url(utils.Config.get_conn(self.envConfig.get_env_id()), user_id[0])  # 找出 開戶連結
    #
    #     self.driver.get(self.post_url + '/register/?{}'.format(user_url[0]))  # 動待找尋 輸入用戶名的  開戶連結
    #     print(self.driver.title)
    #     print('註冊連結 : {}'.format(user_url[0]))
    #     user_random = random.randint(1, 100000)  # 隨機生成 kerr下面用戶名
    #     new_user = self.user + str(user_random)
    #     print(u'註冊用戶名: {}'.format(new_user))
    #     self.ID('J-input-username').send_keys(new_user)  # 用戶名
    #     self.ID('J-input-password').send_keys(self.password)  # 第一次密碼
    #     self.ID('J-input-password2').send_keys(self.password)  # 在一次確認密碼
    #     self.ID('J-button-submit').click()  # 提交註冊
    #     sleep(5)
    #     '''
    #     if self.dr.current_url == self.post_url + '/index':
    #         (u'%s註冊成功'%new_user)
    #         print(self.post_url)
    #         print(u'%s登入成功'%new_user)
    #     else:
    #         print(u'登入失敗')
    #     '''
    #     # u"安全中心"
    #     while self.driver.current_url == self.post_url + '/index':
    #         break
    #
    #     self.driver.get(self.post_url + '/safepersonal/safecodeset')  # 安全密碼連結
    #     print(self.driver.title)
    #     self.ID('J-safePassword').send_keys(safe_pass)
    #     self.ID('J-safePassword2').send_keys(safe_pass)
    #     print(u'設置安全密碼/確認安全密碼: %s' % safe_pass)
    #     self.ID('J-button-submit').click()
    #     if self.driver.current_url == self.post_url + '/safepersonal/safecodeset?act=smt':  # 安全密碼成功Url
    #         print(u'恭喜%s安全密码设置成功！' % new_user)
    #     else:
    #         print(u'安全密碼設置失敗')
    #     self.driver.get(self.post_url + '/safepersonal/safequestset')  # 安全問題
    #     print(self.driver.title)
    #     for i in range(1, 4, 1):  # J-answrer 1,2,3
    #         self.ID('J-answer%s' % i).send_keys('kerr')  # 問題答案
    #     for i in range(1, 6, 2):  # i產生  1,3,5 li[i], 問題選擇
    #         self.XPATH('//*[@id="J-safe-question-select"]/li[%s]/select/option[2]' % i).click()
    #     self.ID('J-button-submit').click()  # 設置按鈕
    #     self.ID('J-safequestion-submit').click()  # 確認
    #     if self.driver.current_url == self.post_url + '/safepersonal/safequestset?act=smt':  # 安全問題成功url
    #         print(u'恭喜%s安全问题设置成功！' % new_user)
    #     else:
    #         print(u'安全問題設置失敗')
    #     # u"銀行卡綁定"
    #     self.driver.get(self.post_url + '/bindcard/bindcardsecurityinfo/')
    #     print(self.driver.title)
    #     fake = Factory.create()
    #     card = (fake.credit_card_number(card_type='visa16'))  # 產生一個16位的假卡號
    #
    #     self.XPATH('//*[@id="bankid"]/option[2]').click()  # 開戶銀行選擇
    #     self.XPATH('//*[@id="province"]/option[2]').click()  # 所在城市  :北京
    #     self.ID('branchAddr').send_keys(u'內湖分行')  # 之行名稱
    #     self.ID('bankAccount').send_keys('kerr')  # 開戶人
    #     self.ID('bankNumber').send_keys(str(card))  # 銀行卡浩
    #     print(u'綁定銀行卡號: %s' % card)
    #     self.ID('bankNumber2').send_keys(str(card))  # 確認銀行卡浩
    #     self.ID('securityPassword').send_keys(safe_pass)  # 安全密碼
    #     self.ID('J-Submit').click()  # 提交
    #     sleep(3)
    #     if self.ID('div_ok').is_displayed():
    #         print(u'%s银行卡绑定成功！' % new_user)
    #         self.ID('CloseDiv2').click()  # 關閉
    #     else:
    #         print(u'銀行卡綁定失敗')
    #     # u"數字貨幣綁卡"
    #     self.driver.get(self.post_url + '/bindcard/bindcarddigitalwallet?bindcardType=2')
    #     print(self.driver.title)
    #     card = random.randint(1000, 1000000000)  # usdt數字綁卡,隨機生成
    #     self.ID('walletAddr').send_keys(str(card))
    #     print(u'提現錢包地址: %s' % card)
    #     self.ID('securityPassword').send_keys(safe_pass)
    #     print(u'安全密碼: %s' % safe_pass)
    #     self.ID('J-Submit').click()  # 提交
    #     sleep(3)
    #     if self.ID('div_ok').is_displayed():  # 彈窗出現
    #         print(u'%s数字货币钱包账户绑定成功！' % new_user)
    #         self.ID('CloseDiv2').click()
    #     else:
    #         print(u"數字貨幣綁定失敗")

    def tearDown(self) -> None:
        if self.pageObject:
            driver = self.pageObject.get_driver()
            driver.quit()
