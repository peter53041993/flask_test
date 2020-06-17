import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from Utils import Config
from Utils import TestTool
from Utils.TestTool import traceLog


def sleep(sec):
    time.sleep(sec)


class NoSuchElementError(Exception):
    pass


class BasePage:
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


class BaseBetPage(BasePage):
    gameTypes = None  # 普通 超級2000 趣味
    gameMethod = None  # 五星 四星 etc
    gameName = None  # 遊戲名稱

    visibleGameXpath = "//ul[@class='play-select-content clearfix']/li[contains(@class,'current')]//dd"  # 可點選遊戲清單

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
        self.gameTypes = self.driver.find_elements_by_xpath('//*[@id="change"]/ul[1]/li')

    def get_current_methods(self):
        return self.driver.find_elements_by_xpath("//*[@id='change']/ul[2]/li[@style!='display: none;']")

    def get_current_games(self):
        return self.driver.find_elements_by_xpath(
            "//ul[@class='play-select-content clearfix']/li[contains(@class,'current')]//dd")

    def get_current_game(self, index):
        return self.driver.find_element_by_xpath(
            "(//ul[@class='play-select-content clearfix']/li[contains(@class,'current')]//dd)[%s]" % index)

    def add_random_bet_1(self):
        try:
            self.driver.find_element_by_id('randomone').click()
        except Exception as e:
            traceLog(e)

    def add_random_bet_5(self):
        try:
            self.driver.find_element_by_id('randomfive')
        except Exception as e:
            traceLog(e)

    def submit_bet(self):
        try:
            self.driver.find_element_by_id('J-submit-order').click()
            self.driver.find_element_by_xpath("//a[@class='btn confirm' and @style!='display:none']").click()
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//*[text()='恭喜您投注成功~!']")))
        except NoSuchElementError as e:
            traceLog(e)


class BetPageCqssc(BaseBetPage):

    def __init__(self, env, driver):
        super().__init__(env, driver)
        self.link = '/gameBet/cqssc'
        self.gameName = 'cqssc'
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

    def bet_all(self):
        print("len(gameType) : %s" % len(self.gameTypes))
        for gameType in self.gameTypes:
            gameType.click()
            print(gameType.get_attribute("innerHTML"))
            methods = self.get_current_methods()
            print("len(methods) : %s" % len(methods))
            for method in methods:
                method.click()
                sleep(0.2)
                print(method.get_attribute("innerHTML"))
                games = self.get_current_games()
                print("len(games) : %s" % len(games))
                for index in range(len(games)):
                    self.get_current_game(index + 1).click()
                    self.add_random_bet_1()
        self.submit_bet()


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

    def to_game_page(self):
        return BetPageCqssc(self.envConfig, self.driver)
