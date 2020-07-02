from enum import Enum

from selenium.webdriver.common.by import By

from page_objects import BasePages


class BasePersonal(BasePages.BasePage):
    @staticmethod
    class elements(Enum):
        query_orders_button = By.XPATH("(//dl[@class='side-bet']//a)[1]")  # 投注紀錄
        query_plans_button = By.XPATH("(//dl[@class='side-bet']//a)[2]")  # 追號紀錄
        query_fund_detail_button = By.XPATH("(//dl[@class='side-bet']//a)[3]")  # 帳戶明細
        save_center_button = By.XPATH("(//dl[@class='side-safe']//a)[1]")  # 安全中心
        bind_card_button = By.XPATH("(//dl[@class='side-safe']//a)[2]")  # 銀行卡管理
        personal_info_button = By.XPATH("(//dl[@class='side-safe']//a)[3]")  # 個人資料
        safe_code_edit_button = By.XPATH("(//dl[@class='side-safe']//a)[4]")  # 密碼管理
        query_bonus_details_button = By.XPATH("(//dl[@class='side-safe']//a)[5]")  # 獎金詳情

    def side_bar_jump_to(self, button_name):
        if button_name in self.elements:
            self.driver.find_element(button_name.value).click()
            if button_name == self.elements.save_center_button:
                return Personal_AppCenterPage(self)


class Personal_AppCenterPage(BasePersonal):
    """安全中心"""

    @staticmethod
    class buttons(Enum):
        change_password = By.ID('changePWBtn')  # 修改密碼
        change_safe_password = By.ID('changeSafePW')  # 修改安全密碼
        set_safe_password = By.ID('setSafePW')  # 設置安全密碼
        get_safe_password = By.ID('getSafePW')  # 尋找密碼
        set_safe_question = By.ID('setSafeQuestion')  # 設置安全問題
        change_safe_question = By.ID('changeSafeQuestion')  # 修改安全問題
        set_email = By.ID('setEmail')  # 綁定信箱
        change_email = By.ID('changeEmail')  # 修改綁定信箱

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = '/safepersonal/safecenter'
        self.go_to()

    def jump_to(self, button):
        """
        :param button: self.buttons(Enum)
        :return: other page of module
        """
        if button in self.buttons:
            self.driver.find_element(self.buttons.change_password.value).click()
            if button == self.buttons.change_password:
                return Personal_ChangePasswordPage(self)
            elif button == self.buttons.change_safe_password:
                return Personal_ChangeSavePasswordPage(self)
        else:
            raise Exception('無對應按鈕')


class Personal_ChangePasswordPage(BasePersonal):
    """修改密碼頁"""

    @staticmethod
    class elements(Enum):
        old_password_input = By.ID('J-password')
        new_password_input = By.ID('J-password-new')
        confirm_password_input = By.ID('J-password-new2')
        submit_button = By.ID('J-button-submit-password')
        result_text = By.XPATH("//*[@id='Idivs']//*[@class='pop-text']")

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = '/safepersonal/safecodeedit'

    def change_password(self, password):
        expected = '恭喜您密码修改成功，请重新登录。'
        self.driver.find_element(self.elements.old_password_input.value).send_keys(password)
        self.driver.find_element(self.elements.new_password_input.value).send_keys(password)
        self.driver.find_element(self.elements.confirm_password_input.value).send_keys(password)
        self.driver.find_element(self.elements.submit_button.value).click()
        assert self.driver.find_element(self.elements.result_text.value).text == expected
        self.driver.find_element('closeTip1').click()
        from page_objects.BasePages import LoginPage
        return LoginPage(self.envConfig.get_domain())


class Personal_ChangeSavePasswordPage(BasePersonal):
    """修改安全密碼頁"""
    @staticmethod
    class elements(Enum):
        old_safe_password_input = By.ID('J-safePassword')
        new_safe_password_input = By.ID('J-safePassword-new')
        confirm_safe_password_input = By.ID('J-safePassword-new2')
        submit_button = By.ID('J-button-submit-safePassword')

    def __init__(self, last_page):
        super().__init__(last_page=last_page)
        self.link = '/safepersonal/safecodeedit?issafecode=1'
        if self.envConfig.get_env_id() == 0:
            self.safe_pass = 'hsieh123'
        elif self.envConfig.get_env_id() == 1:
            self.safe_pass = 'kerr123'
        else:
            raise Exception('無對應安全密碼，請至test_applycenter新增')

    def change_safe_password(self, password):
        expected = '安全密码修改成功'
        self.driver.find_element(self.elements.old_safe_password_input.value).send_keys(password)
        self.driver.find_element(self.elements.new_safe_password_input.value).send_keys(password)
        self.driver.find_element(self.elements.confirm_safe_password_input.value).send_keys(password)
        self.driver.find_element(self.elements.submit_button.value).click()
        # assert self.driver.find_element_by_xpath("//*[@id='Idivs']//*[@class='pop-text']").text == expected
