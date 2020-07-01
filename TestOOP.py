from enum import Enum

from page_objects import BasePage
from utils.TestTool import trace_log


# page = BasePage.LoginPage("dev02")
# page.login("twen101", "123qwe")
# while True:
#     for game in BasePage.GameNames:
#         page.dir_jump_to(game).bet_all()
# page.get_driver().close()

main_page = BasePage.LoginPage("dev02").login('twen101','123qwe')
app_center_page = main_page.jump_to(main_page.buttons_personal.app_center)


