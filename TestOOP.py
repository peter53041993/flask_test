from page_objects.BasePages import *
from page_objects.BetPages import *

page = LoginPage("dev02")
page.login("twen103", "123qwe")
page = BetPage_V3d(page)
page.go_to()
page.add_all_random()
page.submit_trace()
# page = BetPage_Slmmc(page)
# page.go_to()
# page.add_all_random()

#
# new_user = LoginPage('dev02') \
#     .login('twen101', '123qwe') \
#     .dir_jump_to(LoginPage.CustomPages.register) \
#     .random_register().user
#
# print(new_user)
