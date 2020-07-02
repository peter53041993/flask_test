import datetime
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

import Utils.Config
from Utils import Config, Logger
from Utils.Config import LotteryData


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
        sql = "select url from user_url where url like '%{}%'".format(userid)
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
    envConfig = None
    user = None
    red_type = None
    dr = None
    password = None
    post_url = None
    em_url = None

    def setUp(self):
        logger.info('IntegrationTestWeb setUp : {}'.format(self._testMethodName))
        self.login()

    def __init__(self, case, env, user, red_type):
        super().__init__(case)
        self.envConfig = env
        self.user = user
        self.red_type = red_type
        try:
            if 'ChromeDriver' in locals() or 'ChromeDriver' in globals():
                self.dr = webdriver.Chrome(chrome_options=Config.chrome_options)
            else:
                self.dr = webdriver.Chrome(Config.chromeDriver_Path, chrome_options=Config.chrome_options)
        except Exception as e:
            from Utils.TestTool import trace_log
            trace_log(e)

    def login(self):
        self.password = self.envConfig.get_password()
        print(self.password)
        self.post_url = self.envConfig.get_post_url()
        self.em_url = self.envConfig.get_em_url()

        self.dr.get(self.post_url + '/login/index')

        print(u'登入環境: {},登入帳號: {}'.format(self.envConfig, self.user))
        # sleep(100)
        self.dr.find_element_by_id('J-user-name').send_keys(self.user)
        self.dr.find_element_by_id('J-user-password').send_keys(self.password)
        self.dr.find_element_by_id('J-form-submit').click()
        sleep(1)
        if self.dr.current_url == self.post_url + '/index':  # 判斷是否登入成功
            print('{} 登入成功'.format(self.user))
        else:
            print('{} 登入失敗'.format(self.user))

    def ID(self, element):
        return self.dr.find_element_by_id(element)

    def CSS(self, element):
        return self.dr.find_element_by_css_selector(element)

    def CLASS(self, element):
        return self.dr.find_element_by_class_name(element)

    def XPATH(self, element):
        return self.dr.find_element_by_xpath(element)

    def LINK(self, element):
        return self.dr.find_element_by_link_text(element)

    def id_element(self, element1):  # 抓取id元素,判斷提示窗

        try:
            element = self.CSS("a.btn.closeTip")
            if element.is_displayed():
                self.LINK("关 闭").click()
            else:
                self.ID(element1).click()
        except NoSuchElementException as e:
            logger.error(e)

    def css_element(self, element1):  # 抓取css元素,判斷提示窗
        try:
            element = self.CSS("a.btn.closeTip")
            if element.is_displayed():
                sleep(3)
                element.click()
                self.CSS(element1).click()
            else:
                self.CSS(element1).click()
        except NoSuchElementException as e:
            logger.error(e)
        except AttributeError as e:
            logger.error(e)

    def xpath_element(self, element1):  # 抓取xpath元素,判斷提示窗

        try:
            element = self.CSS("a.btn.closeTip")
            if element.is_displayed():
                element.click()
                self.XPATH(element1).click()
            else:
                self.XPATH(element1).click()
        except NoSuchElementException as e:
            logger.error(e)

    def link_element(self, element1):  # 抓取link_text元素,判斷提示窗
        try:
            element = self.CSS("a.btn.closeTip")
            if element.is_displayed():
                element.click()
                self.LINK(element1).click()
            else:
                self.LINK(element1).click()
        except NoSuchElementException as e:
            logger.error(e)

    def normal_type(self, game):  # 普通玩法元素
        global game_list, game_list2
        game_list = ['wuxing', 'sixing', 'qiansan', 'zhongsan', 'housan', 'qianer', 'houer', 'yixing',
                     'super2000', 'houer_2000.caojiduizhi', 'yixing_2000.caojiduizhi',
                     'special', 'longhu.special']
        game_list2 = ['wuxing', 'sixing', 'qiansan', 'zhongsan', 'housan', 'qianer', 'houer', 'yixing',
                      'special', 'longhu.special']

        '''五星'''
        wuxing_element = ['dd.danshi', 'dd.zuxuan120', 'dd.zuxuan60', 'dd.zuxuan30', "dd.zuxuan20", "dd.zuxuan10",
                          "dd.zuxuan5", "dd.yimabudingwei", "dd.ermabudingwei", "dd.sanmabudingwei", "dd.yifanfengshun",
                          "dd.haoshichengshuang", "dd.sanxingbaoxi", "dd.sijifacai"]
        '''四星'''
        sixing_element = ['li.sixing.current > dl.zhixuan > dd.danshi', 'dd.zuxuan24',
                          'dd.zuxuan12', 'dd.zuxuan6', "dd.zuxuan4",
                          "li.sixing.current > dl.budingwei > dd.yimabudingwei"
            , "li.sixing.current > dl.budingwei > dd.ermabudingwei"]
        '''前三'''
        qiansan_element = ['li.qiansan.current > dl.zhixuan > dd.danshi', 'dd.hezhi', 'dd.kuadu',
                           'dl.zuxuan > dd.hezhi', 'dd.zusan', 'dd.zuliu', 'dd.hunhezuxuan',
                           'dd.baodan', 'dd.zusandanshi', 'dd.zuliudanshi',
                           'li.qiansan.current > dl.budingwei > dd.yimabudingwei',
                           'li.qiansan.current > dl.budingwei > dd.ermabudingwei']
        '''中三'''
        zhongsan_element = ['li.zhongsan.current > dl.zhixuan > dd.danshi',
                            'li.zhongsan.current > dl.zhixuan > dd.hezhi',
                            'li.zhongsan.current>  dl.zhixuan > dd.kuadu',
                            'li.zhongsan.current > dl.zuxuan > dd.hezhi',
                            'li.zhongsan.current > dl.zuxuan > dd.zusan',
                            'li.zhongsan.current > dl.zuxuan > dd.zuliu',
                            'li.zhongsan.current > dl.zuxuan > dd.hunhezuxuan',
                            'li.zhongsan.current > dl.zuxuan > dd.baodan',
                            'li.zhongsan.current > dl.zuxuan > dd.zusandanshi',
                            'li.zhongsan.current > dl.zuxuan > dd.zuliudanshi',
                            'li.zhongsan.current > dl.budingwei > dd.yimabudingwei',
                            'li.zhongsan.current > dl.budingwei > dd.ermabudingwei']

        '''後三'''
        housan_element = ['li.housan.current > dl.zhixuan > dd.danshi',
                          'li.housan.current > dl.zhixuan > dd.hezhi',
                          'li.housan.current > dl.zhixuan > dd.kuadu',
                          'li.housan.current > dl.zuxuan > dd.hezhi',
                          'li.housan.current > dl.zuxuan > dd.zusan',
                          'li.housan.current > dl.zuxuan > dd.zuliu',
                          'li.housan.current > dl.zuxuan > dd.hunhezuxuan',
                          'li.housan.current > dl.zuxuan > dd.baodan',
                          'li.housan.current > dl.zuxuan > dd.zusandanshi',
                          'li.housan.current > dl.zuxuan > dd.zuliudanshi',
                          'li.housan.current > dl.budingwei > dd.yimabudingwei',
                          'li.housan.current > dl.budingwei > dd.ermabudingwei']

        '''前二'''
        qianer_element = ['li.qianer.current > dl.zhixuan > dd.danshi',
                          'li.qianer.current > dl.zhixuan > dd.hezhi',
                          'li.qianer.current > dl.zhixuan > dd.kuadu',
                          'li.qianer.current > dl.zuxuan > dd.fushi',
                          'li.qianer.current > dl.zuxuan > dd.danshi',
                          'li.qianer.current > dl.zuxuan > dd.hezhi',
                          'li.qianer.current > dl.zuxuan > dd.baodan']
        '''後二'''
        houer_element = ['li.houer.current > dl.zhixuan > dd.danshi',
                         'li.houer.current > dl.zhixuan > dd.hezhi',
                         'li.houer.current > dl.zhixuan > dd.kuadu',
                         'li.houer.current > dl.zuxuan > dd.fushi',
                         'li.houer.current > dl.zuxuan > dd.danshi',
                         'li.houer.current > dl.zuxuan > dd.hezhi',
                         'li.houer.current > dl.zuxuan > dd.baodan']
        '''後三2000'''
        housan_2000_element = ['li.housan_2000.current > dl.zhixuan > dd.danshi',
                               'li.housan_2000.current > dl.zhixualink_elementan > dd.kuadu',
                               'li.housan_2000.current > dl.zuxuan > dd.hezhi',
                               'li.housan_2000.current > dl.zuxuan > dd.zusan',
                               'li.housan_2000.current > dl.zuxuan > dd.zuliu',
                               'li.housan_2000.current > dl.zuxuan > dd.hunhezuxuan',
                               'li.housan_2000.current > dl.zuxuan > dd.baodan',
                               'li.housan_2000.current > dl.zuxuan > dd.zusandanshi',
                               'li.housan_2000.current > dl.zuxuan > dd.zuliudanshi',
                               'li.housan_2000.current > dl.budingwei > dd.yimabudingwei',
                               'li.housan_2000.current > dl.budingwei > dd.ermabudingwei']
        '''後二2000'''
        houer_2000_element = ['li.houer_2000.current > dl.zhixuan > dd.danshi',
                              'li.houer_2000.current > dl.zhixuan > dd.hezhi',
                              'li.houer_2000.current > dl.zhixuan > dd.kuadu',
                              'li.houer_2000.current > dl.zuxuan > dd.fushi',
                              'li.houer_2000.current > dl.zuxuan > dd.danshi',
                              'li.houer_2000.current > dl.zuxuan > dd.hezhi',
                              'li.houer_2000.current > dl.zuxuan > dd.baodan']
        '''趣味大小單雙'''
        special_big_element = ['dd.qianyi', 'dd.qianer', 'dd.houyi', 'dd.houer']

        if game == game_list[0]:
            return wuxing_element
        elif game == game_list[1]:
            return sixing_element
        elif game == game_list[2]:
            return qiansan_element
        elif game == game_list[3]:
            return zhongsan_element
        elif game == game_list[4]:
            return housan_element
        elif game == game_list[5]:
            return qianer_element
        elif game == game_list[6]:
            return houer_element
        elif game == game_list[8]:
            return housan_2000_element
        elif game == game_list[9]:
            return houer_2000_element
        elif game == game_list[11]:
            return special_big_element
        else:  # 一星只有一個玩法
            pass

    def game_ssh(self, type_='0'):  # 時彩系列  有含 普通玩法,超級2000,趣味玩法, 預設type_ 是有超級2000
        self.normal_type('wuxing')  # 先呼叫 normal_type方法, 產生game_list 列表
        if type_ == 'no':
            list_type = game_list2
        else:
            list_type = game_list
        for game in list_type:  # 產生 五星,四星,.....列表
            if game == 'special':  # 要到趣味玩法頁簽, 沒提供 css_element 的定位方法, 使用xpath
                self.xpath_element('//li[@game-mode="special"]')
            else:
                self.css_element('li.%s' % game)
            sleep(2)
            self.id_element('randomone')  # 進入tab,複式玩法為預設,值接先隨機一住
            if game in ['yixing', 'yixing_2000.caojiduizhi', 'longhu.special']:
                pass
            else:
                element_list = self.normal_type(game)  # return 元素列表
                for i in element_list:  # 普通,五星玩法 元素列表
                    self.css_element(i)
                    self.css_element('a#randomone.take-one')  # 隨機一住

    def game_ssh2(self, type_='0'):  # 吉利分彩頁面 特殊用法
        self.normal_type('wuxing')  # 先呼叫 normal_type方法, 產生game_list 列表
        if type_ == 'no':
            list_type = game_list2
        else:
            list_type = game_list
        for game in list_type:  # 產生 五星,四星,.....列表
            if game == 'special':  # 要到趣味玩法頁簽, 沒提供 css_element 的定位方法, 使用xpath
                self.xpath_element('//li[@game-mode="special"]')
            else:

                self.css_element('li.%s' % game)
            sleep(2)
            self.id_element('randomone')  # 進入tab,複式玩法為預設,值接先隨機一住
            if game in ['yixing', 'yixing_2000.caojiduizhi', 'longhu.special']:
                pass
            else:
                element_list = self.normal_type(game)  # return 元素列表
                for i in element_list:  # 普通,五星玩法 元素列表
                    self.css_element('li.%s' % game)  # 差別在這邊,需再點一次頁面元素
                    self.css_element(i)
                    self.css_element('a#randomone.take-one')  # 隨機一住

    def mul_submit(self):  # 追號
        try:
            if self.dr.find_element_by_xpath('//*[@id="J-redenvelope-switch"]/label/input').is_selected():
                self.dr.find_element_by_xpath('//*[@id="J-redenvelope-switch"]/label/input').click()  # 取消紅包追號
        except:
            pass
        self.id_element('randomone')  # 先隨機一住
        self.id_element('J-trace-switch')  # 追號

    def result(self):  # 投注結果
        soup = BeautifulSoup(self.dr.page_source, 'lxml')
        a = soup.find_all('ul', {'class': 'ui-form'})
        for i in range(7):
            for b in a:
                c = b.find_all('li')[i]
                print(c.text)

    def result_sl(self, element1, element2):
        soup = ''
        for i in range(5):
            soup = BeautifulSoup(self.dr.page_source, 'lxml')
        a = soup.find_all('ul', {'class': 'program-chase-list program-chase-list-body'})
        for a1 in a:
            a11 = a1.find_all('li')[0]
            a12 = a11.find('div', {'class': element1})
            print(element2 + a12.text)

    def submit(self, time_=2):  # 業面投注按鈕, 和result() func, 再加上業面確認按鈕
        self.id_element('J-submit-order')  # 馬上投注
        self.result()
        self.link_element("确 认")
        sleep(time_)

    def submit_message(self, lottery):  # 投注完的單號
        if '成功' in self.CLASS('pop-text').text:
            order_code_web = get_order_code_web(Utils.Config.get_conn(1), self.user, lottery)
            print("方案編號: %s" % order_code_web[-1])
        else:
            print('失敗')

    def assert_bouns(self):  # 驗證頁面是否有獎金詳情
        try:
            '''
            if '您选择的彩种目前属于休市期间' in Joy188Test2.XPATH("//h4[@class='pop-text']").text:# 休市彈窗
                Joy188Test2.XPATH('/html/body/div[17]/div[1]/i').click()
            '''
            element = WebDriverWait(self.dr, 5).until(
                EC.presence_of_element_located((By.XPATH, "//p[@class='text-title']")))
            if self.XPATH("//p[@class='text-title']").text == '请选择一个奖金组，便于您投注时使用。':  # 獎金詳情彈窗
                self.XPATH("//input[@class='radio']").click()
                self.LINK('确 认').click()
                self.dr.refresh()
        except NoSuchElementException:
            self.dr.refresh()
        except TimeoutException:
            pass

    def test_cqssc(self):
        u'重慶時彩投注'
        lottery = 'cqssc'

        sleep(1)
        self.dr.get(self.em_url + '/gameBet/cqssc')
        print(self.dr.title)
        self.assert_bouns()

        '''
        Joy188Test2.game_ssh()#所以玩法投注
        '''
        self.mul_submit()  # 追號方法

        self.submit()

        self.submit_message(lottery)

    def test_hljssc(self):  # 黑龍江

        lottery = 'hljssc'
        self.dr.get(self.em_url + '/gameBet/hljssc')
        print(self.dr.title)
        sleep(2)
        self.assert_bouns()

        '''
        Joy188Test2.game_ssh()
        '''
        self.mul_submit()
        self.submit()
        self.submit_message(lottery)

    def test_xjssc(self):

        lottery = 'xjssc'
        self.dr.get(self.em_url + '/gameBet/xjssc')
        print(self.dr.title)
        self.assert_bouns()

        # Joy188Test2.game_ssh()
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_fhxjc(self):

        lottery = 'fhxjc'
        self.dr.get(self.em_url + '/gameBet/fhxjc')
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh()

        self.mul_submit()  # 追號方法
        self.submit()
        self.submit_message(lottery)

    def test_fhcqc(self):

        lottery = 'fhcqc'
        self.dr.get(self.em_url + '/gameBet/fhcqc')
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh()
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_txffcself(self):  # 五星完髮不同

        lottery = 'txffc'
        self.dr.get(self.em_url + '/gameBet/txffc')
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_jlffc(self):  # 五星完髮不同

        lottery = 'jlffc'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        self.game_ssh2('no')  #
        # Joy188Test2.mul_submit()#追號方法
        # sleep(1000)
        self.submit()
        self.submit_message(lottery)

    def test_hnffc(self):  #

        lottery = 'hnffc'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        self.game_ssh('no')  #
        # Joy188Test2.mul_submit()#追號方法

        self.submit()
        self.submit_message(lottery)

    def test_360ffc(self):  #

        lottery = '360ffc'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        self.game_ssh('no')  #
        # Joy188Test2.mul_submit()#追號方法

        self.submit()
        self.submit_message(lottery)

    def test_shssl(self):
        lottery = 'shssl'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_sd115(self):
        lottery = 'sd115'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_jx115(self):
        lottery = 'jx115'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_gd115(self):
        lottery = 'gd115'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_sl115(self):
        lottery = 'sl115'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#

        self.XPATH("//a[@data-param='action=batchSetBall&row=0&bound=all&start=1']").click()  # 全玩法
        self.ID('J-add-order').click()  # 添加號碼
        self.ID('J-submit-order').click()  # 馬上開獎
        sleep(1)
        self.result_sl('cell1', '方案編號:')
        self.result_sl('cell2', '投注時間:')
        self.result_sl('cell4', '投注金額:')

    def test_slmmc(self):
        lottery = 'slmmc'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        while True:
            try:
                for i in range(3):
                    self.XPATH(
                        "//a[@data-param='action=batchSetBall&row=%s&bound=all']" % i).click()  # 全玩法
                break
            except ElementClickInterceptedException:
                self.dr.refresh()
                break

        self.ID('J-add-order').click()  # 添加號碼
        self.ID('J-submit-order').click()  # 馬上開獎
        sleep(1)
        self.result_sl('cell1', '方案編號:')
        self.result_sl('cell2', '投注時間:')
        self.result_sl('cell4', '投注金額:')

    def test_fhjlssc(self):

        lottery = 'fhjlssc'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_v3d(self):  #

        lottery = 'v3d'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_p5(self):  # 五星完髮不同

        lottery = 'p5'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_ssq(self):  # 五星完髮不同

        lottery = 'ssq'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_fc3d(self):  # 五星完髮不同

        lottery = 'fc3d'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_llssc(self):

        lottery = 'llssc'
        self.dr.get(self.em_url + '/gameBet/llssc')
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法

        self.submit()
        self.submit_message(lottery)

    def test_btcffc(self):
        lottery = 'btcffc'
        self.dr.get(self.em_url + '/gameBet/btcffc')
        print(self.dr.title)
        self.assert_bouns()
        # Joy188Test2.game_ssh('no')#
        self.mul_submit()  # 追號方法
        self.submit()

        self.submit_message(lottery)

    def test_ahk3(self):
        lottery = 'ahk3'
        self.dr.get(self.em_url + '/gameBet/ahk3')
        print(self.dr.title)
        self.assert_bouns()
        '''
        k3_element = ['li.hezhi.normal','li.santonghaotongxuan.normal','li.santonghaodanxuan.normal',
        'li.sanbutonghao.normal','li.sanlianhaotongxuan.normal','li.ertonghaofuxuan.normal',
        'li.ertonghaodanxuan.normal','li.erbutonghao.normal','li.yibutonghao.normal']
        for i in k3_element:            
            Joy188Test2.css_element(i)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        '''
        self.mul_submit()  # 追號方法
        self.submit()
        self.submit_message(lottery)

    def test_jsk3(self):
        lottery = 'jsk3'
        self.dr.get(self.em_url + '/gameBet/jsk3')
        print(self.dr.title)
        self.assert_bouns()
        '''
        k3_element = ['li.hezhi.normal','li.santonghaotongxuan.normal','li.santonghaodanxuan.normal',
        'li.sanbutonghao.normal','li.sanlianhaotongxuan.normal','li.ertonghaofuxuan.normal',
        'li.ertonghaodanxuan.normal','li.erbutonghao.normal','li.yibutonghao.normal']
        for i in k3_element:            
            Joy188Test2.css_element(i)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        '''
        self.mul_submit()  # 追號方法
        self.submit()

        self.submit_message(lottery)

    def test_jsdice(self):
        lottery = 'jsdice'
        self.dr.get(self.em_url + '/gameBet/jsdice')
        print(self.dr.title)
        self.assert_bouns()
        global sb_element
        # 江蘇骰寶 列表, div 1~ 52
        num = 1
        sb_element = ['//*[@id="J-dice-sheet"]/div[%s]/div' % i for i in range(1, num, 1)]  # num 控制  要投注多少玩法, 最多 到 53

        for i in sb_element:
            sleep(1)
            self.xpath_element(i)
        sleep(0.5)
        self.xpath_element('//*[@id="J-dice-bar"]/div[5]/button[1]')  # 下注
        self.result()
        self.CSS('a.btn.btn-important').click()  # 確認

        self.submit_message(lottery)

    def test_jldice(self):

        for lottery in ['jldice1', 'jldice2']:
            self.dr.get(self.em_url + '/gameBet/%s' % lottery)
            print(self.dr.title)
            self.assert_bouns()
            for i in sb_element:
                if self.ID('diceCup').is_displayed():  # 吉利骰寶 遇到中間開獎, 讓他休息,在繼續
                    sleep(15)
                else:
                    sleep(1)
                    self.xpath_element(i)
            sleep(0.5)

            if self.ID('diceCup').is_displayed():
                sleep(15)
            else:
                self.xpath_element('//*[@id="J-dice-bar"]/div[5]/a[1]')  # 下注
                self.result()
                self.XPATH('/html/body/div[14]/a[1]').click()  # 確認
            self.submit_message(lottery)

    def test_bjkl8(self):
        lottery = 'bjkl8'
        self.dr.get(self.em_url + '/gameBet/bjkl8')
        print(self.dr.title)
        self.assert_bouns()
        '''
        bjk_element = ['dd.renxuan%s'%i for i in range(1,8)]#任選1 到 任選7
        Joy188Test2.id_element('randomone')
        sleep(1)
        Joy188Test2.css_element('li.renxuan.normal')
        for element in bjk_element:
            Joy188Test2.css_element(element)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        '''

        self.mul_submit()
        self.submit()

        self.submit_message(lottery)

    def test_pk10(self):
        lottery = 'pk10'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        for i in range(2):
            self.XPATH("//a[@data-param='action=batchSetBall&row=%s&bound=all&start=1']" % i).click()
        self.ID('J-add-order').click()  # 選好了
        self.ID('J-trace-switch').click()  # 追號
        self.submit()

        self.submit_message(lottery)

    def test_xyft(self):
        lottery = 'xyft'
        self.dr.get(self.em_url + '/gameBet/%s' % lottery)
        print(self.dr.title)
        self.assert_bouns()
        for i in range(2):
            self.XPATH("//a[@data-param='action=batchSetBall&row=%s&bound=all&start=1']" % i).click()
        self.ID('J-add-order').click()  # 選好了
        self.ID('J-trace-switch').click()  # 追號
        self.submit()

        self.submit_message(lottery)

    def test_safepersonal(self):
        u"修改登入密碼"
        self.dr.get(self.post_url + '/safepersonal/safecodeedit')
        print(self.dr.title)
        if self.password == '123qwe':
            new_password = 'amberrd'
        else:
            new_password = '123qwe'
        self.ID('J-password').send_keys(self.password)
        print(u'當前登入密碼: %s' % self.password)
        self.ID('J-password-new').send_keys(new_password)
        self.ID('J-password-new2').send_keys(new_password)
        print(u'新登入密碼: %s,確認新密碼: %s' % (new_password, new_password))
        self.ID('J-button-submit-text').click()
        sleep(2)
        if self.ID('Idivs').is_displayed():  # 成功修改密碼彈窗出現
            print(u'恭喜%s密码修改成功，请重新登录。' % self.user)
            self.ID('closeTip1').click()  # 關閉按紐,跳回登入頁
            sleep(1)
            self.ID('J-user-name').send_keys(self.user)
            self.ID('J-user-password').send_keys(new_password)
            self.ID('J-form-submit').click()
            sleep(1)
            print((self.dr.current_url))
            if self.dr.current_url == self.post_url + '/index':  # 判斷是否登入成功
                print(u'%s登入成功' % self.user)
                self.dr.get(self.post_url + '/safepersonal/safecodeedit')
                self.ID('J-password').send_keys(new_password)  # 在重新把密碼改回原本的amberrd
                self.ID('J-password-new').send_keys(self.password)
                self.ID('J-password-new2').send_keys(self.password)
                self.ID('J-button-submit-text').click()
                sleep(3)
            else:
                print(u'登入失敗')
                pass

        else:
            print(u'密碼輸入錯誤')
            pass

    def test_applycenter(self):
        u'開戶中心/安全中心/綁卡'
        if self.password == '123qwe':
            safe_pass = 'hsieh123'
        elif self.password == 'amberrd':
            safe_pass = 'kerr123'
        else:
            raise Exception('無對應安全密碼，請至test_applycenter新增')

        userid = Utils.Config.select_user_id(Utils.Config.get_conn(self.envConfig.get_env_id()),
                                             self.user)  # 找出用戶 Userid  , 在回傳給開戶連結
        user_url = select_user_url(Utils.Config.get_conn(self.envConfig.get_env_id()), userid[0])  # 找出 開戶連結

        self.dr.get(self.post_url + '/register/?{}'.format(user_url[0]))  # 動待找尋 輸入用戶名的  開戶連結
        print(self.dr.title)
        print('註冊連結:%s' % user_url[0])
        global user_random
        user_random = random.randint(1, 100000)  # 隨機生成 kerr下面用戶名
        new_user = self.user + str(user_random)
        print(u'註冊用戶名: {}'.format(new_user))
        self.ID('J-input-username').send_keys(new_user)  # 用戶名
        self.ID('J-input-password').send_keys(self.password)  # 第一次密碼
        self.ID('J-input-password2').send_keys(self.password)  # 在一次確認密碼
        self.ID('J-button-submit').click()  # 提交註冊
        sleep(5)
        '''
        if self.dr.current_url == self.post_url + '/index':
            (u'%s註冊成功'%new_user)
            print(self.post_url)
            print(u'%s登入成功'%new_user)
        else:
            print(u'登入失敗')
        '''
        # u"安全中心"
        while self.dr.current_url == self.post_url + '/index':
            break

        self.dr.get(self.post_url + '/safepersonal/safecodeset')  # 安全密碼連結
        print(self.dr.title)
        self.ID('J-safePassword').send_keys(safe_pass)
        self.ID('J-safePassword2').send_keys(safe_pass)
        print(u'設置安全密碼/確認安全密碼: %s' % safe_pass)
        self.ID('J-button-submit').click()
        if self.dr.current_url == self.post_url + '/safepersonal/safecodeset?act=smt':  # 安全密碼成功Url
            print(u'恭喜%s安全密码设置成功！' % new_user)
        else:
            print(u'安全密碼設置失敗')
        self.dr.get(self.post_url + '/safepersonal/safequestset')  # 安全問題
        print(self.dr.title)
        for i in range(1, 4, 1):  # J-answrer 1,2,3
            self.ID('J-answer%s' % i).send_keys('kerr')  # 問題答案
        for i in range(1, 6, 2):  # i產生  1,3,5 li[i], 問題選擇
            self.XPATH('//*[@id="J-safe-question-select"]/li[%s]/select/option[2]' % i).click()
        self.ID('J-button-submit').click()  # 設置按鈕
        self.ID('J-safequestion-submit').click()  # 確認
        if self.dr.current_url == self.post_url + '/safepersonal/safequestset?act=smt':  # 安全問題成功url
            print(u'恭喜%s安全问题设置成功！' % new_user)
        else:
            print(u'安全問題設置失敗')
        # u"銀行卡綁定"
        self.dr.get(self.post_url + '/bindcard/bindcardsecurityinfo/')
        print(self.dr.title)
        fake = Factory.create()
        card = (fake.credit_card_number(card_type='visa16'))  # 產生一個16位的假卡號

        self.XPATH('//*[@id="bankid"]/option[2]').click()  # 開戶銀行選擇
        self.XPATH('//*[@id="province"]/option[2]').click()  # 所在城市  :北京
        self.ID('branchAddr').send_keys(u'內湖分行')  # 之行名稱
        self.ID('bankAccount').send_keys('kerr')  # 開戶人
        self.ID('bankNumber').send_keys(str(card))  # 銀行卡浩
        print(u'綁定銀行卡號: %s' % card)
        self.ID('bankNumber2').send_keys(str(card))  # 確認銀行卡浩
        self.ID('securityPassword').send_keys(safe_pass)  # 安全密碼
        self.ID('J-Submit').click()  # 提交
        sleep(3)
        if self.ID('div_ok').is_displayed():
            print(u'%s银行卡绑定成功！' % new_user)
            self.ID('CloseDiv2').click()  # 關閉
        else:
            print(u'銀行卡綁定失敗')
        # u"數字貨幣綁卡"
        self.dr.get(self.post_url + '/bindcard/bindcarddigitalwallet?bindcardType=2')
        print(self.dr.title)
        card = random.randint(1000, 1000000000)  # usdt數字綁卡,隨機生成
        self.ID('walletAddr').send_keys(str(card))
        print(u'提現錢包地址: %s' % card)
        self.ID('securityPassword').send_keys(safe_pass)
        print(u'安全密碼: %s' % safe_pass)
        self.ID('J-Submit').click()  # 提交
        sleep(3)
        if self.ID('div_ok').is_displayed():  # 彈窗出現
            print(u'%s数字货币钱包账户绑定成功！' % new_user)
            self.ID('CloseDiv2').click()
        else:
            print(u"數字貨幣綁定失敗")

    def tearDown(self) -> None:
        self.dr.quit()
