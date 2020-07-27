import datetime
import os
import pathlib
import unittest
import HTMLTestRunner
import time

from autoTest.ApiTestApp import ApiTestApp
from autoTest.ApiTestPC import ApiTestPC, ApiTestYFT
from autoTest.IntegrationTestWeb import IntegrationTestWeb
from utils import Config
from utils.Logger import create_logger
from utils.TestTool import trace_log

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'  # 避免抓出oracle中文 為問號


def date_time():  # 給查詢 獎期to_date時間用, 今天時間
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    format_day = f'{day:02d}'
    return f'{year}-{month}-{format_day}'


def suite_test(test_cases, user_name, test_env, is_use_red, money_unit, award_mode):
    """
    autoTest 初始化
    :param award_mode: 獎金模式 (0:預設 / 1:高獎金 / 2:高獎金)
    :param money_unit: 元角分模式 (1 / 0.1 / 0.01)
    :param test_cases: Array[][]; 測試項目，為二維矩陣。第一維區分測試類型（PC_API、APP_API、PC整合），二維紀錄測試method名稱
    :param user_name: String; 就是個用戶名
    :param test_env: String; 網域名稱，用於Config.encConfig初始化
    :param is_use_red: String; yse or no; 目前未使用
    :return: 
    """
    logger = create_logger(r'\AutoTest', 'auto_test')
    logger.info("suite_test 初始化")
    env_config = Config.EnvConfig(test_env)
    env_config_app = Config.EnvConfigApp(test_env)
    _env_app_config = Config.EnvConfigApp(test_env)
    suite_list = []
    test_list = ['cqssc', 'xjssc', 'hljssc', 'shssl', 'tjssc', 'txffc', 'fhjlssc', 'fhcqc', 'fhxjc', '3605fc', 'btcffc',
                 'llssc', '360ffc', 'jlffc', 'v3d']

    logger.debug(f'autoTest test_cases : {test_cases}')
    try:
        suite = unittest.TestSuite()

        logger.info(f"suite_test with test_cases : {test_cases}")

        if env_config.get_env_id() in (0,1):
            for case in test_cases[0]:
                logger.info(f'test_cases[0] : {test_cases[0]}')
                logger.info(f'For loop[0] : {case}')
                suite_list.append(ApiTestPC(case=case, _env=env_config, _user=user_name, _red_type=is_use_red,
                                            _money_unit=money_unit, _award_mode=award_mode))
            for case in test_cases[1]:
                logger.info(f'test_cases[1] : {test_cases[1]}')
                logger.info(f'For loop[1] : {case}')
                suite_list.append(ApiTestApp(case_=case, env_=env_config_app, user_=user_name, red_type_=is_use_red))
            for case in test_cases[2]:
                if case == 'test_plan':
                    for lottery in test_list:
                        logger.info(f'test_cases[2] : "test_{lottery}')
                        logger.info(f'For loop[2] : {case}')
                        suite_list.append(
                            IntegrationTestWeb(case=f'test_{lottery}', env_config=env_config, user=user_name,
                                               red_type=is_use_red))
                else:
                    logger.info(f'test_cases[2] : {test_cases[2]}')
                    logger.info(f'For loop[2] : {case}')
                    suite_list.append(
                        IntegrationTestWeb(case=case, env_config=env_config, user=user_name, red_type=is_use_red))
        elif env_config.get_env_id() == 11:  # 若為YFT測試案例
            for case in test_cases[0]:
                logger.info(f'test_cases[0] : {test_cases[0]}')
                logger.info(f'For loop[0] : {case}')
                suite_list.append(ApiTestYFT(case=case, _env=env_config, _user=user_name, _money_unit=money_unit))

        logger.info(f"測試內容 suite_list : {suite_list}")

        suite.addTests(suite_list)
        logger.info(f"測試內容Suite suite_api_pc : {suite}")

        filename = Config.reportHtml_Path  # now + u'自動化測試' + '.html'
        fp = open(filename, 'wb')
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title=u'測試報告',
            description=f'環境: {env_config},帳號: {user_name}',
        )
        logger.debug(">>>>>>>>Test Start.<<<<<<<<")
        runner.run(suite)
        logger.debug(">>>>>>>>Test End.<<<<<<<<")
        fp.close()
    except Exception as e:
        logger.error(trace_log(e))
