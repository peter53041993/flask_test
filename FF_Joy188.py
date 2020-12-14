from bs4 import BeautifulSoup
import json, cx_Oracle, requests, hashlib, time, urllib3, time
from fake_useragent import UserAgent

from utils import Logger
from utils.Config import LotteryData, EnvConfig
from utils.Connection import OracleConnection

logger = Logger.create_logger(r"\AutoTest", 'FF_')


class FF_:  # 4.0專案

    def __init__(self):
        self.dev_url = ['dev02', 'dev03', 'fh82dev02', '88hlqpdev02', 'teny2020dev02']
        self.uat_url = ['joy188', 'joy188.195353']
        self.user_agent = {
            'Pc': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/68.0.3440.100 Safari/537.36",
            'Ios': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 \
        (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            'Andorid': "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36",
            'Fake': UserAgent(verify_ssl=False).random
        }

        self.param = b'ba359dddc3c5dfd979169d056de72638',  # 固定寫死即可
        self.session = requests.Session()
        self.session.proxies = {"http": "http://127.0.0.1:8888"}
        self.lottery_dict = LotteryData.lottery_dict  # 吃config ,後續只需增加一邊

    def session_post(self, request_url, request_func, postData, header):
        """
        共用 request.post方式 ,url 為動態 請求url ,source預設走PC
        :param request_url:
        :param request_func:
        :param postData:
        :param header:
        :return:
        """
        logger.info(
            f'session_post: request_url = {request_url}, request_func={request_func}, getData={postData}, header={header}')
        urllib3.disable_warnings()
        response = self.session.post(request_url + request_func, data=postData, headers=header, verify=False)
        logger.info(f'session_post : response = {response.text}')
        return response

    def session_get(self, request_url, request_func, getData, header):
        """
        共用 request.get方法 ,url 為動態 請求url ,source預設走PC
        :param request_url:
        :param request_func:
        :param getData:
        :param header:
        :return:
        """
        logger.info(
            f'session_get: request_url = {request_url}, request_func={request_func}, getData={getData}, header={header}')
        urllib3.disable_warnings()
        response = self.session.get(request_url + request_func, data=getData, headers=header, verify=False)
        # logger.info(f'session_get : response = {response.text}')
        return response

    def get_conn(self, env):  # 連結數據庫 env 0: dev02 , 1:188 ,2: 生產
        if env == 2:
            username = 'rdquery'
            service_name = 'gamenxsXDB'
        else:
            username = 'firefog'
            service_name = ''
        oracle_ = {'password': ['LF64qad32gfecxPOJ603', 'JKoijh785gfrqaX67854', 'eMxX8B#wktFZ8V'],
                   'ip': ['10.13.22.161', '10.6.1.41', '10.6.1.31'],
                   'sid': ['firefog', 'game', '']}
        conn = cx_Oracle.connect(username, oracle_['password'][env], oracle_['ip'][env] + ':1521/' +
                                 oracle_['sid'][env] + service_name)
        return conn

    def plan_return(self, trace_value, issue_list):  # 根據 type_ 判斷是不是追號, 生成動態的 動態order
        plan_ = []
        try:
            for i in range(trace_value):
                plan_.append({"number": 'test', "issueCode": issue_list[i]['issueCode'], "multiple": 1})
            return plan_
        except IndexError as e:
            print(e)

    @staticmethod
    def web_plan_issue(lottery, em_url, header):  # 從頁面  dynamicConfig 皆口去獲得
        """
        取得彩種獎期
        :param lottery: 彩種名稱
        :param em_url: em網域
        :param header: request header
        :return: 回傳['data']['gamenumbers']
        """
        logger.info(f'web_plan_issue: lottery={lottery}, em_url={em_url}, header={header}')
        now_time = int(time.time())
        response = FF_().session_get(em_url, '/gameBet/%s/dynamicConfig?_=%s' % (lottery, now_time), '',
                                     header)  # dynamicConfig 有歷史獎其資訊
        try:
            return response.json()['data']['gamenumbers']
        except KeyError:
            print(response.text)
            return None
        except Exception as e:
            print(e)
            return None

    def submit_json(self, em_url, account, lottery, award_mode, trace_issue_num: int, is_trace_win_stop: bool, envs,
                    header):
        """
        各彩種對應的投注格式, 受pc_submit呼叫
        :param em_url: 投注接口
        :param account: 用戶帳號
        :param lottery: 投注彩種
        :param award_mode: 獎金模式
        :param trace_issue_num: 追號與否
        :param is_trace_win_stop: 追中即停與否
        :param envs: 環境
        :param header: 封包header
        :return: None
        """
        logger.info(f'em_url = {em_url}, account = {account}, lottery = {lottery}, award_mode = {award_mode},'
                    f' trace_issue_num = {trace_issue_num}, is_trace_win_stop = {is_trace_win_stop}, envs = {envs}, header = {header}')
        if lottery in ['ahsb', 'slsb']:
            return None

        issue_list = FF_().web_plan_issue(lottery, em_url, header)  # 追號獎期
        print(f'彩種: {lottery}')
        trace_stop_value = 1 if trace_issue_num > 1 and is_trace_win_stop else -1
        trace_value = 1 if trace_issue_num else 0
        is_trace_win_stop = 1 if is_trace_win_stop else 0

        """
        自 dynamicConfig 取得當前彩種開放的玩法列表，
        並傳遞至 requestContent_FF，組出 balls 參數，
        投注金額也由 requestContent_FF 提供。
        
        若需判斷元角分模式，則在 requestContent_FF 內添加判斷調整即可。
        """
        from utils.requestContent_FF import get_game_dict
        now_time = int(time.time())
        keys = []
        r = self.session.get(em_url + f'/gameBet/{lottery}/dynamicConfig?_={now_time}', headers=header)
        for games in r.json()["data"]["gamelimit"]:
            for key in games:
                keys.append(key)
        logger.info(f'web_plan_issue: keys = {keys}')
        logger.info(f'submit_json: award_mode = {award_mode}')
        game_dict = get_game_dict(lottery, keys, award_mode)

        if trace_issue_num > 1:  # 追號
            order_plan = FF_().plan_return(trace_issue_num, issue_list)  # 生成 order 的投注奖期列表

            len_order = len(order_plan)
            print('追號期數:%s' % len_order)
        else:  # 一般投注
            if issue_list:
                order_plan = [
                    {"number": str(issue_list), "issueCode": issue_list[0]['issueCode'], "multiple": 1}]  # 一般投注
            else:
                order_plan = [{"number": str(issue_list), "issueCode": 1, "multiple": 1}]  # 一般投注
            len_order = 1
        if lottery == 'pcdd':
            # 需查出用戶反點, 如果是高獎金的話, odds 需用 平台獎金 * 用戶反點
            conn = OracleConnection(env_id=envs)
            lottery_point = conn.select_lottery_point(self.lottery_dict[lottery][1], account)
            logger.info(
                lottery_point)  # {0: ('autotest101', datetime.datetime(2020, 12, 2, 17, 11, 54, 328000), 450, '奖金组1800')}
            user_point = lottery_point[0][2] / 10000
            bonus = conn.select_bonus(self.lottery_dict[lottery][1], '', 'FF_bonus')
            # print(bonus)
            assert award_mode in [1, 2]  # 確保award_mode正確性

            if award_mode == 1:  # 一般玩法, odds 就直接用 bonus 的key
                list_keys = list(bonus.keys())
            else:
                list_keys = [int((bonus_[0] + bonus_[1] * user_point) * 100) / 100 for bonus_ in
                             bonus.items()]  # 高獎金抓出來, 需呈上自己返點
            # print(list_keys)
            return {"balls": [
                {"id": 1, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "0",
                 "odds": list_keys[0], "awardMode": award_mode},
                {"id": 2, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "1", "odds": list_keys[1], "awardMode": award_mode},
                {"id": 3, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "2", "odds": list_keys[2], "awardMode": award_mode},
                {"id": 4, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "3", "odds": list_keys[3], "awardMode": award_mode},
                {"id": 5, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "5", "odds": list_keys[5], "awardMode": award_mode},
                {"id": 6, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "4", "odds": list_keys[4], "awardMode": award_mode},
                {"id": 7, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "6", "odds": list_keys[6], "awardMode": award_mode},
                {"id": 8, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "13", "odds": list_keys[13], "awardMode": award_mode},
                {"id": 9, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "12", "odds": list_keys[12], "awardMode": award_mode},
                {"id": 10, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "11", "odds": list_keys[11], "awardMode": award_mode},
                {"id": 11, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "10", "odds": list_keys[10], "awardMode": award_mode},
                {"id": 12, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "9", "odds": list_keys[9], "awardMode": award_mode},
                {"id": 13, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "8", "odds": list_keys[8], "awardMode": award_mode},
                {"id": 14, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "7", "odds": list_keys[7], "awardMode": award_mode},
                {"id": 15, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "14", "odds": list_keys[13], "awardMode": award_mode},
                {"id": 16, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "15", "odds": list_keys[12], "awardMode": award_mode},
                {"id": 17, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "16", "odds": list_keys[11], "awardMode": award_mode},
                {"id": 18, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "17", "odds": list_keys[10], "awardMode": award_mode},
                {"id": 19, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "18", "odds": list_keys[9], "awardMode": award_mode},
                {"id": 20, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "19", "odds": list_keys[8], "awardMode": award_mode},
                {"id": 21, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "20", "odds": list_keys[7], "awardMode": award_mode},
                {"id": 22, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "27", "odds": list_keys[0], "awardMode": award_mode},
                {"id": 23, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "26", "odds": list_keys[1], "awardMode": award_mode},
                {"id": 24, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "25", "odds": list_keys[2], "awardMode": award_mode},
                {"id": 25, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "24", "odds": list_keys[3], "awardMode": award_mode},
                {"id": 26, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "23", "odds": list_keys[4], "awardMode": award_mode},
                {"id": 27, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "22", "odds": list_keys[5], "awardMode": award_mode},
                {"id": 28, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.hezhi.hezhi", "amount": 1,
                 "ball": "21", "odds": list_keys[6], "awardMode": award_mode},
                {"id": 29, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.quwei.baosan", "amount": 1,
                 "ball": "0,1,2", "odds": list_keys[20], "awardMode": award_mode},
                {"id": 30, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.quwei.saibo", "amount": 1,
                 "ball": "红", "odds": list_keys[18], "awardMode": award_mode},
                {"id": 31, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.quwei.saibo", "amount": 1,
                 "ball": "绿", "odds": list_keys[19], "awardMode": award_mode},
                {"id": 32, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.quwei.baozi", "amount": 1,
                 "ball": "豹子", "odds": list_keys[3], "awardMode": award_mode},
                {"id": 33, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.quwei.saibo", "amount": 1,
                 "ball": "蓝", "odds": list_keys[19], "awardMode": award_mode},
                {"id": 34, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.jizhi", "amount": 1,
                 "ball": "极小", "odds": list_keys[17], "awardMode": award_mode},
                {"id": 35, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.zuhedaxiaodanshuang",
                 "amount": 1, "ball": "大单", "odds": list_keys[16], "awardMode": award_mode},
                {"id": 36, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.zuhedaxiaodanshuang",
                 "amount": 1, "ball": "大双", "odds": list_keys[15], "awardMode": award_mode},
                {"id": 37, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.jizhi", "amount": 1,
                 "ball": "极大", "odds": list_keys[17], "awardMode": award_mode},
                {"id": 38, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.zuhedaxiaodanshuang",
                 "amount": 1, "ball": "小单", "odds": list_keys[15], "awardMode": award_mode},
                {"id": 39, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.zuhedaxiaodanshuang",
                 "amount": 1, "ball": "小双", "odds": list_keys[16], "awardMode": award_mode},
                {"id": 40, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.daxiaodanshuang",
                 "amount": 1, "ball": "双", "odds": list_keys[14], "awardMode": award_mode},
                {"id": 41, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.daxiaodanshuang",
                 "amount": 1, "ball": "单", "odds": list_keys[14], "awardMode": award_mode},
                {"id": 42, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.daxiaodanshuang",
                 "amount": 1, "ball": "小", "odds": list_keys[14], "awardMode": award_mode},
                {"id": 43, "moneyunit": 1, "multiple": 1, "num": 1, "type": "zhenghe.shuangmian.daxiaodanshuang",
                 "amount": 1, "ball": "大", "odds": list_keys[14], "awardMode": award_mode}], "orders": order_plan,
                "redDiscountAmount": 0, "amount": 43 * len_order, "isTrace": trace_value,
                "traceWinStop": is_trace_win_stop,
                "traceStopValue": trace_stop_value}
        elif lottery in ['jsdice', 'jldice1', 'jldice2']:
            return {"gameType": lottery, "isTrace": trace_value, "multiple": 1, "trace": 1,
                    "amount": game_dict[1] * len_order, "balls": game_dict[0], "orders": order_plan}
        else:
            # logger.info(f'game_dict = {game_dict}')
            return {"gameType": lottery, "isTrace": trace_value, "traceWinStop": is_trace_win_stop,
                    "traceStopValue": trace_stop_value, "balls": game_dict[0], "orders": order_plan,
                    "amount": game_dict[1] * len_order}

    def pc_submit(self, account, envs: EnvConfig, em_url, header, lottery, award_mode, trace_issue_num: int,
                  win_stop: bool = True):
        """
        PC投注
        :param account: 用戶帳號
        :param envs: 環境物件
        :param em_url: 投注網域
        :param header: header內容
        :param lottery: 彩種名稱
        :param award_mode: 獎金組模式
        :param trace_issue_num: 追號期數，>2則判定為追號，否則為一般投注
        :param win_stop: 是否追中即停
        :return: 若投置請求成功，回傳None。若請求報錯，回傳 [彩種名稱, 錯誤訊息]
        """
        logger.info(f'pc_submit: account={account}, envs={envs}, em_url={em_url}, header={header}, lottery={lottery},'
                    f' award_mode={award_mode}, trace_issue_num={trace_issue_num},win_stop={win_stop}')
        if trace_issue_num <= 1:  # 若非追號單，追中即停更改為False
            win_stop = False
        postData = FF_().submit_json(em_url=em_url, account=account, lottery=lottery, award_mode=award_mode,
                                     trace_issue_num=trace_issue_num, is_trace_win_stop=win_stop, envs=envs,
                                     header=header)
        # 呼叫各彩種 投注data api
        r = FF_().session_post(em_url, '/gameBet/%s/submit' % lottery, json.dumps(postData), header)
        print('%s投注,彩種: %s' % (account, self.lottery_dict[lottery][0]))
        try:
            print(r.json()['msg'])
            if r.json()['isSuccess'] == 0:  # 若投注結果為失敗
                print('\n')
                return [self.lottery_dict[lottery][0], r.json()['msg']]
            print(f'投注方案: {r.json()["data"]["projectId"]}\n')
            return None
        except KeyError as k:
            print(r.text)
            print(k)
            return [self.lottery_dict[lottery][0], r.text]
        except Exception as e:
            from utils.TestTool import trace_log
            trace_log(e)
            return [self.lottery_dict[lottery][0], r.text]
