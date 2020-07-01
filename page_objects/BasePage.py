import random
from time import sleep

from selenium.webdriver import ActionChains

from utils.Logger import create_logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from enum import Enum

from utils import Config
from utils import TestTool
from utils.TestTool import trace_log

logger = None


class GameNames(Enum):
    CQSSC = "CQSSC"
    JLFFC = "JLFFC"
    FFC360 = "360FFC"
    XJSSC = "XJSSC"
    HLJSSC = "HLJSSC"
    SHSSL = "SHSSL"
    TJSSC = "TJSSC"
    TXFFC = "TSFFC"
    FHJLSSC = "FHJLSSC"
    FHCQC = "FHCQC"
    FHXJC = "FHXJC"
    F5C360 = "3605FC"
    V3D = "V3D"
    SLMMC = "SLMMC"
    BTCFFC = "BTCFFC"
    LLSSC = "LLSSC"


class BasePage:
    logger = create_logger(r'\BasePage')
    driver = None
    envConfig = None
    link = None
    user = None
    password = None

    def __init__(self, env_domain, driver=None):
        if type(env_domain) is Config.EnvConfig:
            self.envConfig = env_domain
        else:
            self.envConfig = Config.EnvConfig(env_domain)
        if driver is None:
            self.get_driver()
        else:
            self.driver = driver

    def get_driver(self):
        if self.driver is None:
            try:
                if 'ChromeDriver' in locals() or 'ChromeDriver' in globals():
                    self.driver = webdriver.Chrome(chrome_options=Config.chrome_options)
                else:
                    self.driver = webdriver.Chrome(Config.chromeDriver_Path, chrome_options=Config.chrome_options)
                self.driver.implicitly_wait(1)
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

    def dir_jump_to(self, names):
        if names == GameNames.JLFFC:
            return BetPage_Jlffc(self)
        elif names == GameNames.CQSSC:
            return BetPage_Cqssc(self)
        elif names == GameNames.FFC360:
            return BetPage_360ffc(self)
        elif names == GameNames.BTCFFC:
            return BetPage_Btcffc(self)
        elif names == GameNames.F5C360:
            return BetPage_3605fc(self)
        elif names == GameNames.FHCQC:
            return BetPage_Fhcqc(self)
        elif names == GameNames.FHJLSSC:
            return BetPage_Fhjlssc(self)
        elif names == GameNames.HLJSSC:
            return BetPage_Hljssc(self)
        elif names == GameNames.LLSSC:
            return BetPage_Llssc(self)
        elif names == GameNames.FHXJC:
            return BetPage_Fhxjc(self)
        elif names == GameNames.SHSSL:
            return BetPage_Shssl(self)
        elif names == GameNames.SLMMC:
            return BetPage_Slmmc(self)
        elif names == GameNames.TJSSC:
            return BetPage_Tjssc(self)
        elif names == GameNames.TXFFC:
            return BetPage_Txffc(self)
        elif names == GameNames.V3D:
            return BetPage_V3d(self)
        elif names == GameNames.XJSSC:
            return BetPage_Xjssc(self)

    def register(self):
        user_id = Config.get_sql_exec(self.envConfig.get_env_id(),
                                      "select id from user_customer where account = '{}'".format(self.user))
        self.link = Config.get_sql_exec(self.envConfig.get_env_id(),
                                        "select url from user_url where url like '%{}%'".format(user_id))
        self.driver.get(self.envConfig.get_post_url() + '/register/?{}'.format(self.link[0]))
        _random = random.randint(1, 100000)
        new_user = self.user + _random
        self.driver.find_element_by_id('J-input-username').send_key(new_user)
        self.driver.find_element_by_id('J-input-password').send_key(self.password)
        self.driver.find_element_by_id('J-input-password2').send_key(self.password)
        self.driver.find_element_by_id('J-button-submit').click()
        sleep(5)
        self.user = new_user


class BaseBetPage(BasePage):
    """
        提供投注頁基本功能
    """
    gameTypes = None  # 普通 超級2000 趣味
    gameMethod = None  # 五星 四星 etc

    _waitTime = 0.2

    submitId = "J-submit-order"
    randomOneId = "randomone"
    randomFiveId = "randomfive"

    getTypesXpath = "//*[@id='change']/ul[1]/li"  # 普通/超級2000/趣味玩法測標籤
    currentMethodsXpath = "//*[@id='change']/ul[2]/li[@style!='display: none;']"  # 五星/四星玩法組
    currentGamesXpath = "//ul[@class='play-select-content clearfix']/li[contains(@class,'current')]//dd"  # 複式/和值等玩法
    visibleGameXpath = "//ul[@class='play-select-content clearfix']/li[contains(@class,'current')]//dd"  # 可點選遊戲清單
    submitBetXpath = "//a[@class='btn confirm' and @style!='display:none']"  # 確認按鈕
    betSuccessXpath = "//*[text()='恭喜您投注成功~!']"  # 投注結果訊息

    closePeriodPopupXpath = "//a[@class='btn closeTip' and @style != 'display:none']"  # 提示彈窗關閉鈕預設(時彩系列)

    def go_to(self):
        self.driver.get(self.envConfig.get_em_url() + self.link)

    def check_prize_select_popup(self):
        try:
            title = self.driver.find_element_by_class_name('text-title').text
            if title.find('选择一个奖金组'):  # 若顯示獎金組選擇彈窗
                self.driver.find_elements_by_name('radionGourp')[0].click()  # 選擇首個獎金組
                self.driver.find_element_by_xpath("//a[@class='btn confirm' and @style!='display:none']").click()
        except:
            pass

    def get_types(self):
        self.gameTypes = self.driver.find_elements_by_xpath(self.getTypesXpath)

    def get_current_methods(self):
        return self.driver.find_elements_by_xpath(self.currentMethodsXpath)

    def get_current_games(self):
        return self.driver.find_elements_by_xpath(self.currentGamesXpath)

    def add_random_bet_1(self):
        try:
            self.driver.find_element_by_id(self.randomOneId).click()
        except Exception as e:
            trace_log(e)

    def add_random_bet_5(self):
        try:
            self.driver.find_element_by_id(self.randomFiveId)
        except Exception as e:
            trace_log(e)

    def submit_bet(self):
        try:
            self.driver.find_element_by_id(self.submitId).click()
            self.driver.find_element_by_xpath(self.submitBetXpath).click()
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located((By.XPATH, self.betSuccessXpath)))
        except Exception as e:
            trace_log(e)

    def bet_all(self, index_t=0, index_m=0, index_g=0):
        """
        投注所有彩種，考量因跨期導致彈窗中段的可能，添加三個參數供接續測試
        :param index_t: 起始type
        :param index_m: 起始method
        :param index_g: 起始game
        """
        _temp_t = index_t  # 紀錄當前type
        _temp_m = index_m  # 紀錄當前method
        _temp_g = index_g  # 紀錄當前game
        if self.gameTypes is not None:
            try:
                logger.debug("len(self.gameTypes) : %s" % len(self.gameTypes))
                for gType in range(index_t, len(self.gameTypes)):
                    _temp_t = gType
                    logger.debug("_temp_t:%s" % _temp_t)
                    logger.info(">>>>>%s" % self.gameTypes[gType].get_attribute('innerHTML'))
                    self.gameTypes[gType].click()
                    self._bet_all(index_m, index_g)
                    index_m = 0  # 當本輪皆添加後需初始話避免後續短少
                self.submit_bet()
            except Exception as e:
                trace_log(e)
                self.check_period_popup()  # 排除臨時顯示彈窗
                logger.warning("Retry bet all with type:%s, method:%s, game:%s" % (index_t, index_m, index_g))
                self.bet_all(_temp_t, _temp_m, _temp_g)  # 從中斷點再次運行
        else:
            try:
                self._bet_all(index_m, index_g)
                self.submit_bet()
            except Exception as e:
                trace_log(e)
                self.check_period_popup()  # 排除臨時顯示彈窗
                logger.warning("Retry bet all with type:%s, method:%s, game:%s" % (index_t, index_m, index_g))
                self.bet_all(_temp_t, _temp_m, _temp_g)  # 從中斷點再次運行

    def _bet_all(self, index_m=0, index_g=0):
        _temp_m = index_m  # 紀錄當前method
        _temp_g = index_g  # 紀錄當前game
        try:
            methods = self.get_current_methods()
            for method in range(index_m, len(methods)):
                _temp_m = method
                logger.debug("_temp_m:%s" % _temp_m)
                methods[method].click()
                logger.info(">>>%s method clicked" % methods[method].get_attribute('innerHTML'))
                sleep(self._waitTime)  # 供JS運行時間
                games = self.get_current_games()
                for game in range(index_g, len(games)):
                    _temp_g = game
                    logger.debug("_temp_g:%s" % _temp_g)
                    if self.link == '/gameBet/jlffc':
                        methods[method].click()  # 為配合吉利分分彩新增
                        logger.info(">>>%s method clicked." % methods[method].get_attribute('innerHTML'))
                    games[game].click()
                    logger.info(">%s game clicked." % games[game].get_attribute('innerHTML'))
                    self.add_random_bet_1()
                    sleep(self._waitTime)
                index_g = 0  # 當本輪皆添加後需初始話避免後續短少
        except Exception as e:
            print(e)
            trace_log(e)
            self.check_period_popup()  # 排除臨時顯示彈窗
            logger.warning("Retry bet all with method:%s, game:%s" % (index_m, index_g))
            self._bet_all(_temp_m, _temp_g)  # 從中斷點再次運行

    def check_period_popup(self):
        try:
            element = self.driver.find_element_by_xpath(self.closePeriodPopupXpath)
            element.click()
        except:
            pass


class AppCenterPage(BasePage):
    """安全中心"""

    class buttons(Enum):
        change_password = 'changePWBtn'

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/safepersonal/safecenter'
        self.go_to()

    def jump_to(self, button):
        """
        :param button: self.buttons(Enum)
        :return: other page of module
        """
        if button == self.buttons.change_password:
            self.driver.find_element_by_id(self.buttons.change_password.value).click()
            return ChangePasswordPage(self)
        else:
            raise Exception('無對應按鈕')


class ChangePasswordPage(BasePage):
    """修改密碼頁"""

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/safepersonal/safecodeedit'
        self.go_to()
        if self.envConfig.get_env_id() == 0:
            self.safe_pass = 'hsieh123'
        elif self.envConfig.get_env_id() == 1:
            self.safe_pass = 'kerr123'
        else:
            raise Exception('無對應安全密碼，請至test_applycenter新增')

    def change_password(self, password):
        expected = '恭喜您密码修改成功，请重新登录。'
        self.driver.find_element_by_id('J-password').send_key(password)
        self.driver.find_element_by_id('J-password-new').send_key(password)
        self.driver.find_element_by_id('J-password-new2').send_key(password)
        self.driver.find_element_by_id('J-button-submit-password').click()
        assert self.driver.find_element_by_xpath("//*[@id='Idivs']//*[@class='pop-text']").text == expected
        self.driver.find_element_by_id('closeTip1').click()
        return LoginPage(self.envConfig.get_domain())


class BetPage_Cqssc(BaseBetPage):
    """
    重慶時時彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/cqssc'
        self.go_to()
        self.check_guide()
        self.check_prize_select_popup()
        self.get_types()

    def check_guide(self):
        try:
            element = self.driver.find_element_by_class_name('guide20000-close')
            element.click()
        except Exception:
            pass


class BetPage_Xjssc(BaseBetPage):
    """
    新疆時時彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/xjssc'
        self.go_to()
        self.check_guide()
        self.check_prize_select_popup()
        self.get_types()

    def check_guide(self):
        try:
            element = self.driver.find_element_by_class_name('guide20000-close')
            element.click()
        except Exception:
            pass


class BetPage_Hljssc(BaseBetPage):
    """
    黑龍江時時彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/hljssc'
        self.go_to()
        self.check_guide()
        self.check_prize_select_popup()
        self.get_types()

    def check_guide(self):
        try:
            element = self.driver.find_element_by_class_name('guide20000-close')
            element.click()
        except Exception:
            pass


class BetPage_Shssl(BaseBetPage):
    """
    上海時時樂彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/shssl'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_Tjssc(BaseBetPage):
    """
    天津時時彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/tjssc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_Txffc(BaseBetPage):
    """
    騰訊分分彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/txffc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_Fhjlssc(BaseBetPage):
    """
    吉利時時彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/fhjlssc'
        self.go_to()
        self.check_guide()
        self.check_prize_select_popup()
        self.get_types()

    def check_guide(self):
        try:
            element = self.driver.find_element_by_class_name('guide20000-close')
            element.click()
        except Exception:
            pass


class BetPage_Fhcqc(BaseBetPage):
    """
    重慶全球彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/fhcqc'
        self.go_to()
        self.check_guide()
        self.check_prize_select_popup()
        self.get_types()

    def check_guide(self):
        try:
            element = self.driver.find_element_by_class_name('guide20000-close')
            element.click()
        except Exception:
            pass


class BetPage_Fhxjc(BaseBetPage):
    """
    新疆全球彩彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/fhxjc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_3605fc(BaseBetPage):
    """
    360五分彩彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/3605fc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_V3d(BaseBetPage):
    """
    勝利3D投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.currentMethodsXpath = "//*[@id='change']/ul[2]/li"
        self.link = '/gameBet/v3d'
        self.go_to()
        self.check_prize_select_popup()


class BetPage_Slmmc(BaseBetPage):
    """
    順利秒秒彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/slmmc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()

    def check_guide(self):
        """
        處理秒秒彩加注說明彈窗
        :return: None
        """
        try:
            element = self.driver.find_element_by_class_name('guide20000-close guide20000-close2')
            element.click()
        except Exception:
            pass


class BetPage_Btcffc(BaseBetPage):
    """
    比特幣分分彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/btcffc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_Llssc(BaseBetPage):
    """
    樂利時時彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/llssc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_360ffc(BaseBetPage):
    """
    360分分彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/360ffc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage_Jlffc(BaseBetPage):
    """
    吉利分分彩投注頁
    """

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
        self.link = '/gameBet/jlffc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()
        self.closePeriodPopupXpath = "//div[@class='j-ui-miniwindow pop w-9' and contains(@style,'display: " \
                                     "block')]//a[@class='close closeBtn'] "


class LoginPage(BasePage):
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
        self.driver.find_element_by_id(self.id_input_account).send_keys(user)
        self.driver.find_element_by_id(self.id_input_password).send_keys(password)
        self.driver.find_element_by_id(self.id_button_login).click()
        sleep(3)
        return MainPage(self)

    def to_game_page(self):
        return BetPage_Cqssc(self)


class MainPage(BasePage):
    """首頁"""

    i_user_header = 'headerUsername'

    class buttons_personal(Enum):
        bet_record = 'betRecord'
        account_detail = 'accountDetail'
        proxy_center = 'proxyCenter'
        query_report = 'queryReport'
        front_score_mall = 'frontScoreMall'
        app_center = 'safeCenter'

    def __init__(self, last_page):
        super().__init__(last_page.envConfig, last_page.driver)
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
                return AppCenterPage(self)
            else:
                raise Exception('POM尚未建立')
        else:
            raise Exception('無對應對象')
