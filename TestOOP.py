from page_objects import BasePage
from utils.TestTool import trace_log

page = BasePage.LoginPage("dev02")
page.login("twen101", "123qwe")
while True:
    for game in BasePage.GameNames:
        page.jump_to(game).bet_all()
# page.get_driver().close()