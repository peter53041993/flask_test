from enum import Enum

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from page_objects import BasePages
from utils.TestTool import trace_log


class BasePersonal(BasePages.BasePage):
    @staticmethod
    class personal_elements(Enum):
        query_orders_button = "(//dl[@class='side-bet']//a)[1]"  # 投注紀錄
        query_plans_button = "(//dl[@class='side-bet']//a)[2]"  # 追號紀錄
        query_fund_detail_button = "(//dl[@class='side-bet']//a)[3]"  # 帳戶明細
        save_center_button = "(//dl[@class='side-safe']//a)[1]"  # 安全中心
        bind_card_button = "(//dl[@class='side-safe']//a)[2]"  # 銀行卡管理
        personal_info_button = "(//dl[@class='side-safe']//a)[3]"  # 個人資料
        safe_code_edit_button = "(//dl[@class='side-safe']//a)[4]"  # 密碼管理
        query_bonus_details_button = "(//dl[@class='side-safe']//a)[5]"  # 獎金詳情

    def personal_jump_to(self, button_name):
        if button_name in self.personal_elements:
            self.driver.find_element_by_xpath(button_name.value).click()
            if button_name == self.personal_elements.save_center_button:
                return Personal_AppCenterPage(self)


class Personal_AppCenterPage(BasePersonal):
    """安全中心"""

    @staticmethod
    class buttons(Enum):
        b_change_password = 'changePWBtn'  # 修改密碼
        b_change_safe_password = 'changeSafePW'  # 修改安全密碼
        b_set_safe_password = 'setSafePW'  # 設置安全密碼
        b_get_safe_password = 'getSafePW'  # 尋找密碼
        b_set_safe_question = 'setSafeQuestion'  # 設置安全問題
        b_change_safe_question = 'changeSafeQuestion'  # 修改安全問題
        b_set_email = 'setEmail'  # 綁定信箱
        b_change_email = 'changeEmail'  # 修改綁定信箱

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = '/safepersonal/safecenter'
        self.go_to()

    def jump_to(self, button):
        """
        :param button: self.buttons(Enum)
        :return: other page of module
        """
        self.logger.info('Personal_AppCenterPage.jump_to : {}'.format(button.value))
        if button in self.buttons:
            if button == self.buttons.b_change_password:
                self.driver.find_element_by_id(self.buttons.b_change_password.value).click()
                return Personal_ChangePasswordPage(self)
            elif button == self.buttons.b_change_safe_password:
                self.driver.find_element_by_id(self.buttons.b_change_safe_password.value).click()
                return Personal_ChangeSavePasswordPage(self)
        else:
            raise Exception('無對應按鈕')


class Personal_ChangePasswordPage(BasePersonal):
    """修改密碼頁"""

    @staticmethod
    class elements(Enum):
        old_password_input = 'J-password'
        new_password_input = 'J-password-new'
        confirm_password_input = 'J-password-new2'
        submit_button = 'J-button-submit-password'
        result_text = "//*[@id='Idivs']//*[@class='pop-text']"

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = '/safepersonal/safecodeedit'

    def change_password(self, password: str) -> BasePages.LoginPage:
        """
        修改密碼腳本，含結果文字驗證
        :param password: 新密碼
        :return: 返還登入頁
        """
        self.logger.info('change_password(password = {})'.format(password))
        expected = '恭喜您密码修改成功，请重新登录。'
        self.driver.find_element_by_id(self.elements.old_password_input.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.new_password_input.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.confirm_password_input.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.submit_button.value).click()
        pop_up_text = self.driver.find_element_by_xpath(self.elements.result_text.value).get_attribute('innerHTML')
        assert pop_up_text == expected
        print('彈窗提示：{}'.format(pop_up_text))
        self.driver.find_element_by_id('closeTip1').click()
        from page_objects.BasePages import LoginPage
        return LoginPage(last_page=self)


class Personal_ChangeSavePasswordPage(BasePersonal):
    """修改安全密碼頁"""

    @staticmethod
    class elements(Enum):
        old_safe_password_input = 'J-safePassword'
        new_safe_password_input = 'J-safePassword-new'
        confirm_safe_password_input = 'J-safePassword-new2'
        submit_button = 'J-button-submit-safePassword'

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = '/safepersonal/safecodeedit?issafecode=1'
        if self.env_config.get_env_id() == 0:
            self.safe_pass = 'hsieh123'
        elif self.env_config.get_env_id() == 1:
            self.safe_pass = 'kerr123'
        else:
            raise Exception('無對應安全密碼，請至test_applycenter新增')

    def change_safe_password(self, password):
        expected = '安全密码修改成功'
        self.driver.find_element_by_id(self.elements.old_safe_password_input.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.new_safe_password_input.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.confirm_safe_password_input.value).send_keys(password)
        self.driver.find_element_by_id(self.elements.submit_button.value).click()
        # assert self.driver.find_element_by_xpath("//*[@id='Idivs']//*[@class='pop-text']").text == expected
