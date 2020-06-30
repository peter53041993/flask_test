# from page_objects import BasePage
# from utils.TestTool import trace_log
#
# page = BasePage.LoginPage("dev02")
# page.login("twen101", "123qwe")
# while True:
#     for game in BasePage.GameNames:
#         page.jump_to(game).bet_all()
# # page.get_driver().close()
import unittest

import HTMLTestRunner


class test(unittest.TestCase):
    def setUpClass(self) -> None:
        print('setUpClass')

    def setUp(self) -> None:
        print('setUp')

    def __init__(self, a, b):
        super(test, self).__init__()
        print('__init__')
        print('{}, {}'.format(a, b))

    def tearDown(self) -> None:
        print('tearDown')

    def tearDownClass(cls) -> None:
        print('tearDownClass')


test_list = []
test_list.append(test(1, 2))

suite = unittest.TestSuite()
suite.addTests(test_list)
runner = unittest.TestRunner.run(suite)
