import os
import unittest
import HTMLTestRunner
import time

from autoTest.ApiTestApp import ApiTestApp
from autoTest.ApiTestPC import ApiTestPC
from autoTest.IntegrationTestWeb import IntegrationTestWeb
from utils import Config
from utils.Logger import create_logger
from utils.TestTool import trace_log

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'  # 避免抓出oracle中文 為問號


def suite_test(test_cases, user_name, test_env, is_use_red):
    """
    autoTest 初始化
    :param test_cases: Array[][]; 測試項目，為二維矩陣。第一維區分測試類型（PC_API、APP_API、PC整合），二維紀錄測試method名稱
    :param user_name: String; 就是個用戶名
    :param test_env: String; 網域名稱，用於Config.encConfig初始化
    :param is_use_red: String; yse or no; 目前未使用
    :return: 
    """
    global logger
    global today_time
    logger = create_logger(r'\AutoTest')
    logger.info("Auto Test 初始化")
    today_time = Config.date_time()
    env_config = Config.EnvConfig(test_env)
    env_config_app = Config.EnvConfigApp(test_env)
    _env_app_config = Config.EnvConfigApp(test_env)
    # pc = []
    # app =[]test_PcLogin
    # driver =[]
    suite_list = []
    # threads =[]
    lottery_list = ['cqssc', 'hljssc', 'xjssc', 'fhcqc', 'fhxjc', 'btcffc', 'txffc', 'jlffc', 'bjkl8', 'jsdice', 'ahk3',
                    'pk10', 'xyft', 'v3d', 'fc3d', 'p5', 'ssq', 'slmmc', 'sl115']
    test_list = ['xjssc']
    logger.debug('autoTest test_cases : {}'.format(test_cases))
    try:
        suite = unittest.TestSuite()
        # suite_pc = unittest.TestSuite()
        # suite_app = unittest.TestSuite()
        now = time.strftime('%Y_%m_%d %H-%M-%S')
        # print(len(testcase))
        for case in test_cases[0]:
            if case in ['test_PcLogin', 'test_PcLotterySubmit', 'test_PcThirdHome', 'test_PcFFHome',
                        'test_PcChart', 'test_PcThirdBalance', 'test_PcTransferin', 'test_PcTransferout',
                        'test_PCLotterySubmit',
                        'test_redEnvelope']:  # PC 案例
                suite_list.append(ApiTestPC(case=case, env=env_config, user=user_name, red_type=is_use_red))

        for case in test_cases[1]:
            if case in ['test_AppLogin', 'test_AppSubmit', 'test_AppOpenLink', 'test_AppBalance', 'test_ApptransferIn',
                        'test_ApptransferOut']:  # APP案例
                suite_list.append(ApiTestApp(case=case, env=env_config_app, user=user_name, red_type=is_use_red))

        for case in test_cases[2]:
            if case in ['test_safepersonal', 'test_applycenter', 'test_plan']:  # 瀏覽器案例
                if case == 'test_plan':
                    for lottery in test_list:
                        suite_list.append(
                            IntegrationTestWeb(case='test_{}'.format(lottery), env=env_config, user=user_name,
                                               red_type=is_use_red))
                else:
                    suite_list.append(
                        IntegrationTestWeb(case=case, env=env_config, user=user_name, red_type=is_use_red))

        logger.debug("測試內容 suite_list : {}".format(suite_list))

        suite.addTests(suite_list)
        print(suite)

        filename = Config.reportHtml_Path  # now + u'自動化測試' + '.html'
        fp = open(filename, 'wb')
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title=u'測試報告',
            description='環境: {env},帳號: {user}'.format(env=env_config, user=user_name),
        )
        logger.debug(">>>>>>>>Test Start.<<<<<<<<")
        runner.run(suite)
        logger.debug(">>>>>>>>Test End.<<<<<<<<")
        fp.close()
    except Exception as e:
        trace_log(e)
