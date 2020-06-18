import time
from utils.Logger import create_logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from enum import Enum

from utils import Config
from utils import TestTool
from utils.TestTool import traceLog


def sleep(sec):
    time.sleep(sec)


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
    global logger
    logger = create_logger(r'\BasePage')
    driver = None
    envConfig = None
    link = None

    def __init__(self, env, driver=None):
        if type(env) is Config.EnvConfig:
            self.envConfig = env
        else:
            self.envConfig = Config.EnvConfig(env)
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
                TestTool.traceLog(e)
        return self.driver

    def go_to(self):
        self.driver.get(self.envConfig.get_post_url() + self.link)

    def check_driver_state(self):
        try:
            self.driver.execute(Command.STATUS)
            return True
        except Exception as e:
            traceLog(e)
            return False

    def get_visibal_elements(self, elements):
        tempElements = []
        for element in elements:
            if element.get_attribute('style') != 'display:none':
                tempElements += element
        return tempElements

    def jump_to(self, names):
        if names == GameNames.JLFFC:
            return BetPageJlffc(self.envConfig, self.driver)
        elif names == GameNames.CQSSC:
            return BetPageCqssc(self.envConfig, self.driver)
        elif names == GameNames.FFC360:
            return BetPage360ffc(self.envConfig, self.driver)
        elif names == GameNames.BTCFFC:
            return BetPageBtcffc(self.envConfig, self.driver)
        elif names == GameNames.F5C360:
            return BetPage3605fc(self.envConfig, self.driver)
        elif names == GameNames.FHCQC:
            return BetPageFhcqc(self.envConfig, self.driver)
        elif names == GameNames.FHJLSSC:
            return BetPageFhjlssc(self.envConfig, self.driver)
        elif names == GameNames.HLJSSC:
            return BetPageHljssc(self.envConfig, self.driver)
        elif names == GameNames.LLSSC:
            return BetPageLlssc(self.envConfig, self.driver)
        elif names == GameNames.FHXJC:
            return BetPageFhxjc(self.envConfig, self.driver)
        elif names == GameNames.SHSSL:
            return BetPageShssl(self.envConfig, self.driver)
        elif names == GameNames.SLMMC:
            return BetPageSlmmc(self.envConfig, self.driver)
        elif names == GameNames.TJSSC:
            return BetPageTjssc(self.envConfig, self.driver)
        elif names == GameNames.TXFFC:
            return BetPageTxffc(self.envConfig, self.driver)
        elif names == GameNames.V3D:
            return BetPageV3d(self.envConfig, self.driver)
        elif names == GameNames.XJSSC:
            return BetPageXjssc(self.envConfig, self.driver)


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
            traceLog(e)

    def add_random_bet_5(self):
        try:
            self.driver.find_element_by_id(self.randomFiveId)
        except Exception as e:
            traceLog(e)

    def submit_bet(self):
        try:
            self.driver.find_element_by_id(self.submitId).click()
            self.driver.find_element_by_xpath(self.submitBetXpath).click()
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located((By.XPATH, self.betSuccessXpath)))
        except Exception as e:
            traceLog(e)

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
                traceLog(e)
                self.check_period_popup()  # 排除臨時顯示彈窗
                logger.warning("Retry bet all with type:%s, method:%s, game:%s" % (index_t, index_m, index_g))
                self.bet_all(_temp_t, _temp_m, _temp_g)  # 從中斷點再次運行
        else:
            try:
                self._bet_all(index_m, index_g)
                self.submit_bet()
            except Exception as e:
                traceLog(e)
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
            traceLog(e)
            self.check_period_popup()  # 排除臨時顯示彈窗
            logger.warning("Retry bet all with method:%s, game:%s" % (index_m, index_g))
            self._bet_all(_temp_m, _temp_g)  # 從中斷點再次運行

    def check_period_popup(self):
        try:
            element = self.driver.find_element_by_xpath(self.closePeriodPopupXpath)
            element.click()
        except:
            pass


class BetPageCqssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
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


class BetPageXjssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
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


class BetPageHljssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
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


class BetPageShssl(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/shssl'
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


class BetPageTjssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/tjssc'
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


class BetPageTxffc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/txffc'
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


class BetPageFhjlssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
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


class BetPageFhcqc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
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


class BetPageFhxjc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/fhxjc'
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


class BetPage3605fc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/3605fc'
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


class BetPageV3d(BaseBetPage):

    def __init__(self, env, driver):
        self.currentMethodsXpath = "//*[@id='change']/ul[2]/li"
        super().__init__(env, driver)
        self.link = '/gameBet/v3d'
        self.go_to()
        self.check_prize_select_popup()


class BetPageSlmmc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/slmmc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPageBtcffc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/btcffc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPageLlssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/llssc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPage360ffc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/360ffc'
        self.go_to()
        self.check_prize_select_popup()
        self.get_types()


class BetPageJlffc(BaseBetPage):
    def __init__(self, env, driver):
        super().__init__(env, driver)
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

    def __init__(self, env):
        super().__init__(env)
        self.link = "/login"
        self.go_to()

    def login(self, account, password):
        self.driver.find_element_by_id(self.id_input_account).send_keys(account)
        self.driver.find_element_by_id(self.id_input_password).send_keys(password)
        self.driver.find_element_by_id(self.id_button_login).click()
        sleep(3)

    def to_game_page(self):
        return BetPageCqssc(self.envConfig, self.driver)
