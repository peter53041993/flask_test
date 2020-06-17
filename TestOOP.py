from PageObjects import BasePage
from Utils.TestTool import traceLog

page = BasePage.LoginPage("dev02")
try:
    page.login("twen101", "123qwe")
    page = page.to_game_page()
    page.bet_all()
except Exception as e:
    traceLog(e)
page.get_driver().close()