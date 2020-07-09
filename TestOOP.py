
# page = BasePage.LoginPage("dev02")
# page.login("twen101", "123qwe")
# while True:
#     for game in BasePage.GameNames:
#         page.dir_jump_to(game).bet_all()
# page.get_driver().close()

from page_objects.BasePages import *

new_user = LoginPage('dev02') \
    .login('twen101', '123qwe') \
    .dir_jump_to(LoginPage.CustomPages.register) \
    .random_register().user

print(new_user)
