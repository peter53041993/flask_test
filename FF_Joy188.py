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
        # self.session.proxies = {"http": "http://127.0.0.1:8888"}
        self.lottery_dict = LotteryData.lottery_dict  # 吃config ,後續只需增加一邊

    def session_post(self, request_url, request_func, postData, header,q):
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
        q.put(response)
        return response

    def session_get(self, request_url, request_func, getData, header,q):
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
        q.put(response)

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

    def submit_json(self, em_url: str, account: str, lottery: str, award_mode: int, trace_issue_num: int,
                    is_trace_win_stop: bool, envs: int, header: dict, money_unit: float = 1.0) -> list:
        """
        各彩種對應的投注格式, 受pc_submit呼叫
        :param money_unit: 單位模式
        :param em_url: 投注接口
        :param account: 用戶帳號
        :param lottery: 投注彩種
        :param award_mode: 獎金模式
        :param trace_issue_num: 追號與否
        :param is_trace_win_stop: 追中即停與否
        :param envs: 環境代號 (0, 1, 2)
        :param header: 封包header
        :return: None
        """

        logger.info(f'em_url = {em_url}, account = {account}, lottery = {lottery}, award_mode = {award_mode},'
                    f' trace_issue_num = {trace_issue_num}, is_trace_win_stop = {is_trace_win_stop}, envs = {envs}, header = {header}')
        if lottery in ['ahsb', 'slsb']:
            print("App專屬彩種跳過測試")
            return []

        print(f'開始投注彩種: {lottery}')

        trace_stop_value = 1 if trace_issue_num > 1 and is_trace_win_stop else -1
        trace_value = 1 if trace_issue_num else 0
        is_trace_win_stop = 1 if is_trace_win_stop else 0

        """
        自 dynamicConfig 取得當前彩種開放的玩法列表，
        並傳遞至 requestContent_FF，組出 balls 參數，
        投注金額也由 requestContent_FF 提供。
        
        若需判斷元角分模式，則在 requestContent_FF 內添加判斷調整即可。
        """
        from utils.requestContent_FF import get_game_dict, get_game_dict_smp
        game_methods = []
        r = self.session.get(em_url + f'/gameBet/{lottery}/dynamicConfig?_={int(time.time())}', headers=header)
        logger.info(f'submit_json<<<<<<<<<<')
        logger.info(f'r = {r.text}')

        while lottery == 'btcctp' and not self.is_btcctp_betable(lottery, r, em_url, header):  # 若當期沖天炮已過可投注時間則重新獲取
            time.sleep(2)

        issue_list = r.json()['data']['gamenumbers']  # 取代web_plan_issue()呼叫
        for games in r.json()["data"]["gamelimit"]:
            for key in games:
                game_methods.append(key)
        logger.debug(f'web_plan_issue: keys = {game_methods}')
        logger.debug(f'submit_json: award_mode = {award_mode}')
        game_dict = get_game_dict(lottery, game_methods, award_mode, money_unit)  # 取得一般投注內容
        conn = OracleConnection(env_id=envs)
        bonus_methods = conn.select_bonus(self.lottery_dict[lottery][1], '', account)  # 取得雙面盤 / 蛋蛋玩法代號與對應獎金和理論獎金
        lottery_point = conn.select_lottery_point(self.lottery_dict[lottery][1], account)
        # logger.info(f'lottery_point = {lottery_point}')
        user_point = lottery_point[0][2] / 10000  # 取得用戶返點，供蛋蛋與雙面盤玩法計算高獎金模式
        game_dict_extra = get_game_dict_smp(lottery=lottery, _award_mode=award_mode, bonus_list=bonus_methods,
                                            user_point=user_point)  # 取得當前彩種的雙面盤/整合(蛋蛋)玩法
        logger.info(f'game_dict_extra = {game_dict_extra}')
        if trace_issue_num > 1:  # 追號
            order_plan = []
            logger.info(f'開始追號投注: trace_issue_num={trace_issue_num}')
            for i in range(trace_value):  # 生成 order 的投注奖期列表
                order_plan.append(
                    {"number": issue_list[i]['number'], "issueCode": issue_list[i]['issueCode'], "multiple": 1})

            len_order = len(order_plan)
            print('追號期數:%s' % len_order)
        else:  # 一般投注
            if len(issue_list) > 0:
                order_plan = [{"number": str(issue_list[0]['number']), "issueCode": issue_list[0]['issueCode'],
                               "multiple": 1}]  # 一般投注
            else:
                order_plan = [{"number": r.json()['data']['number'], "issueCode": r.json()['data']['issueCode'],
                               "multiple": 1}]  # 一般投注
            len_order = 1

        if lottery == 'pcdd':  # PC蛋蛋Ball格式不同另外處理，只處理整合玩法部分
            # 需查出用戶反點, 如果是高獎金的話, odds 需用 平台獎金 * 用戶反點
            assert award_mode in [1, 2]  # 確保award_mode正確性
            return [{'balls': game_dict_extra[0], 'orders': order_plan,
                     'redDiscountAmount': 0, 'amount': game_dict_extra[1] * len_order, 'isTrace': trace_value,
                     'traceWinStop': is_trace_win_stop, 'traceStopValue': trace_stop_value}]
        elif lottery in LotteryData.lottery_sb:  # 骰寶類型投注格式不同另外處理
            return [{'gameType': lottery, 'isTrace': trace_value, 'multiple': 1, 'trace': 1,
                     'amount': game_dict[1] * len_order, 'balls': game_dict[0], 'orders': order_plan}]
        else:  # 其他所有彩種通用，部分彩種有標準玩法與雙面盤之分
            if len(game_dict_extra[0]) > 0:  # 若有雙面盤玩法，同時回傳標準內容與雙面盤內容
                return [{'gameType': lottery, 'isTrace': trace_value, 'traceWinStop': is_trace_win_stop,
                         'traceStopValue': trace_stop_value, 'balls': game_dict[0], 'orders': order_plan,
                         'amount': game_dict[1] * len_order},
                        {'gameType': lottery, 'isTrace': trace_value, 'traceWinStop': is_trace_win_stop,
                         'traceStopValue': trace_stop_value, 'balls': game_dict_extra[0], 'orders': order_plan,
                         'awardGroupId': lottery_point[0][4], 'amount': game_dict_extra[1] * len_order}]
            return [{'gameType': lottery, 'isTrace': trace_value, 'traceWinStop': is_trace_win_stop,
                     'traceStopValue': trace_stop_value, 'balls': game_dict[0], 'orders': order_plan,
                     'amount': game_dict[1] * len_order}]

    def is_btcctp_betable(self, lottery, r, em_url, header):
        import datetime
        r = self.session.get(em_url + f'/gameBet/{lottery}/dynamicConfig?_={int(time.time())}', headers=header)
        btcctp_time = time.mktime(
            datetime.datetime.strptime(r.json()['data']['nowstoptime'], '%Y/%m/%d %H:%M:%S').timetuple())
        logger.debug(f'當前時間: {time.time()}, 沖天炮截止投注時間: {btcctp_time}')
        return btcctp_time > time.time()  # 判斷當前是否可投注

    def pc_submit(self, account: str, envs: int, em_url: str, header: dict, lottery: str, award_mode: int,
                  trace_issue_num: int, win_stop: bool = True, red_mode: bool = False, money_unit: float = 1.0):
        """
        PC投注/追號共用功能.
        首先判斷當前彩種是否有紅包模式、獎金模式、元角模式限制並調整。
        後續透過 FF_().submit_json 取得投注注單內容。
        於發送投注後回傳投注結果。
        :param red_mode: 紅包模式，預設為關
        :param money_unit: 單位模式，預設為元
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
        if lottery in LotteryData.lottery_force_bonus:  # 強制高獎金
            award_mode = 2
        elif lottery in LotteryData.lottery_no_bonus:  # 無高獎金
            award_mode = 1
        if lottery in LotteryData.lottery_no_trace:  # 不支援追號彩種
            trace_issue_num = 0
        if lottery in LotteryData.lottery_no_red:  # 不支援紅包彩種
            red_mode = False
        if lottery in LotteryData.lottery_dollar:  # 強制元模式
            money_unit = 1
        elif money_unit == 0.01 and lottery in LotteryData.lottery_dime:
            money_unit = 0.1
        if trace_issue_num <= 1:  # 若非追號單，追中即停更改為False
            win_stop = False

        logger.info(f'pc_submit: account={account}, envs={envs}, em_url={em_url}, header={header}, lottery={lottery},'
                    f'award_mode={award_mode}, trace_issue_num={trace_issue_num}, win_stop={win_stop}')

        postData = FF_().submit_json(em_url=em_url, account=account, lottery=lottery, award_mode=award_mode,
                                     trace_issue_num=trace_issue_num, is_trace_win_stop=win_stop, envs=envs,
                                     header=header, money_unit=money_unit)
        assert len(postData) > 0  # 確保彩種有成功取得投注內容
        logger.info(f'postData = {postData}')

        for data in postData:
            if red_mode:  # 取得投注內容後，若為紅包投注則添加紅包參數
                data['redDiscountAmount'] = data['amount']
            # 呼叫各彩種 投注data api
            r = FF_().session_post(em_url, f'/gameBet/{lottery}/submit', json.dumps(data), header)
            print(f'{account}投注, 彩種: {self.lottery_dict[lottery][0]}\n')
            try:
                print(r.json()['msg'] + '\n')
                if r.json()['isSuccess'] == 0:  # 若投注結果為失敗
                    return [self.lottery_dict[lottery][0], r.json()['msg']]
                print(f'投注方案: {r.json()["data"]["projectId"]}\n')
            except KeyError as k:
                print(r.text)
                print(k)
                return [self.lottery_dict[lottery][0], r.text]
            except Exception as e:
                from utils.TestTool import trace_log
                trace_log(e)
                return [self.lottery_dict[lottery][0], r.text]
        return None
