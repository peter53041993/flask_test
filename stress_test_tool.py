from json import loads
from math import ceil
from random import randint
from re import split
from sys import exit
from time import sleep

import requests
from utils.Config import EnvConfig, UserAgent
from utils.FF4GameContentGenerator import FF4GameContentGenerator


class ApiStressTestTool:
    """
    最小的壓測模型，依照各環境與需求不同繼承後補足功能。
    """

    def __init__(self):
        self.session = requests.Session()

    def stress_test(self, index):
        """
        壓測實體，壓測實際運行的內容，需繼承後改寫
        :param index: 壓測流水號
        """
        pass

    def start_stress_test(self, run_times: int = 10000):
        from tornado import concurrent
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_index = [executor.submit(self.stress_test, index) for index in range(run_times)]
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    data = future.result()
                    print(data)
                except Exception as e:
                    print(e)

    def output_request_result(self, data):
        """
        輸出資料至.csv檔
        :param data: 需輸出的內容，為 Array
        :return: None
        """
        import csv
        # 使用 append 模式，逐行增加內容
        from datetime import datetime
        data.append(datetime.now())
        with open('request_result.csv', 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data)


class FF4LiteTool(ApiStressTestTool):

    def __init__(self, env: str, use_proxy=False):
        """
        FF4.0 簡易壓測工具
        :param env: 環境名稱. ex: dev02 / joy188
        """
        super().__init__()
        if use_proxy:
            self.session.proxies = {"http": "http://127.0.0.1:8888", "https": "http://127.0.0.1:8888"}
        self.env_data = EnvConfig(env)
        self.header = {  # 預設Header格式
            'User-Agent': UserAgent.PC.value
        }
        self.target_api = None  # 初始化，stress_test壓測時使用
        self.content = None  # 初始化，stress_test壓測時使用
        self.is_bet_test = None  # 初始化，stress_test壓測時使用
        self.target_lottery = None

    def login(self, user_name: str, password: str, param: str = b'e83267bddfd226525e69275b9ff8c436') -> None:
        """
        登入並取得Cookie
        :param user_name: 使用者名稱
        :param password: 密碼
        :param param: 網頁隨機認證碼, 可用預設值
        """
        self.header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        _content = {
            "username": user_name,
            "password": self.__md(str.encode(password), param),
            "param": param
        }
        r = self.session.post(self.env_data.get_post_url() + '/login/login', headers=self.header, data=_content)
        try:
            cookie = r.cookies.get_dict()['ANVOID']
            self.header['Cookie'] = f'ANVOID={cookie}'
            self.header['Content-Type'] = 'application/json; charset=UTF-8'
        except Exception as e:
            print(e)
            exit("登入失敗")

    def start_bet_stress_test(self, run_times: int = 10000, lottery=None) -> None:
        """
        執行投注壓力測式
        :param run_times: 重複運行次數
        :param lottery: 彩種名稱
        """
        self.target_api = self.env_data.get_em_url() + f'/gameBet/{lottery}/submit'
        self.is_bet_test = True
        self.target_lottery = lottery
        self.__get_newest_issue()
        super(FF4LiteTool, self).start_stress_test(run_times)

    def start_api_stress_test(self, run_times: int = 10000, api=None, api_content=None) -> None:
        """
        執行接口壓力測試
        :param run_times: 重複運行次數
        :param api: api接口網址
        :param api_content: api請求內容
        """
        self.target_api = api
        self.content = api_content
        self.is_bet_test = False
        super(FF4LiteTool, self).start_stress_test(run_times)

    def stress_test(self, index):
        """
        壓力測試本體，以index來針對每一次請求變更請求內容
        :param index: 1~run_times
        """
        import timeit
        timer = timeit.default_timer()

        if self.is_bet_test is None:  # 若測試方式尚未定義
            import sys
            sys.exit('壓測時未知測試方式')
        if self.is_bet_test:  # 若為投注接口測試
            self.__check_issue_time()
            self.content = self.__get_bet_content(index)
            r = self.session.post(self.target_api, headers=self.header, json=self.content, verify=False)
        else:  # 若為其他接口測試
            r = self.session.post(self.target_api, headers=self.header, data=self.content, verify=False)
        self.output_request_result([r.status_code, r.elapsed.total_seconds()])
        # print(f'index: {index}, cost time: {timeit.default_timer() - timer}')
        return None  # r.content

    def start_auto_bet_tool_trace(self, _lottery_code: str, _generator: 'FF4GameContentGenerator',
                                  _max_bet_one_issue: int, _min_bet_per_day: int, _target_amount: float):
        """
        依照指定條件進行投注功能
        :param _lottery_code: 彩種代號
        :param _generator: class FF4GameContentGenerator 物件
        :param _max_bet_one_issue: 單期最大注數
        :param _min_bet_per_day: 一日最小注單數量
        :param _target_amount: 總投注金額
        :return: None
        """
        bet_amount = 0
        bet_times = 0
        trace_times = ceil(_min_bet_per_day / _max_bet_one_issue)  # 計算最低需投注期數
        self.__get_newest_issue(lottery_code=_lottery_code, trace_times=trace_times)  # 取得當前最新的獎期
        methods = _generator.methods
        while 0 <= bet_amount < _target_amount:
            rand_method = methods[randint(0, len(methods) - 1)]
            full_game_name = f'{rand_method.group_name}.{rand_method.set_name}.{rand_method.method_name}'
            max_mul = self.__is_method_enable(lottery_code=_lottery_code, method_name=full_game_name)
            if not max_mul:
                continue
            bet_content = _generator.get_bet_content(method=rand_method, issues=self.newest_issue)
            if bet_content is not None:
                print(f'開始投注: {rand_method.title}')
                # 若預期的投注小於  (目標投注金額 - 已投注金額) / 剩餘的單期投注注單數量
                average_bet_amount = (_target_amount - bet_amount) / (_max_bet_one_issue - bet_times)
                if bet_content['amount'] < average_bet_amount:
                    multiple = ceil(average_bet_amount / bet_content['amount'])
                    multiple = multiple if multiple < max_mul else max_mul  # 倍數不可大於玩法限制
                    for index in range(0, len(bet_content['orders'])):  # 修改投注內容內每一期的倍數
                        bet_content['orders'][index]['multiple'] = multiple
                    bet_content['amount'] *= multiple  # 投注金額調整
                    print(f'因預期投注最低金額為{_target_amount}，本期最多投注{_max_bet_one_issue}筆\n'
                          f'已提升追號倍數至{multiple}倍，總投注金額為{bet_content["amount"]}')
                self.__check_issue_time()
                print(f'生成注單內容: {bet_content}')
                r = self.session.post(self.env_data.get_em_url() + f'/gameBet/{_lottery_code}/submit',
                                      headers=self.header, json=bet_content, verify=False)
                bet_amount += bet_content['amount']
                bet_times += 1
                try:  # 如果順利
                    print(f'投注結果:{loads(r.content)["msg"]}\n'
                          f'當前已投注{bet_times}注，總金額為{bet_amount}')
                except:  # 如果不順利
                    print(f'投注失敗')
                    print(f'詳細問題請見封包返還內容：\n{r.content}')

    def start_auto_bet_tool_single(self, _lottery_code: str, _generator: 'FF4GameContentGenerator',
                                   _max_bet_one_issue: int, _min_bet_per_day: int, _target_amount: float):
        """
        依照指定條件進行投注功能
        :param _lottery_code: 彩種代號
        :param _generator: class FF4GameContentGenerator 物件
        :param _max_bet_one_issue: 單期最大注數
        :param _min_bet_per_day: 一日最小注單數量
        :param _target_amount: 總投注金額
        :return: None
        """
        total_amount = 0
        total_issue_times = 0
        current_bet_times = 0

        self.__get_newest_issue(lottery_code=_lottery_code)  # 取得當前最新的獎期 (1期)
        methods = _generator.methods
        while 0 <= total_amount < _target_amount or total_issue_times < _min_bet_per_day:  # 當尚未達到投注金額或次數
            rand_method = methods[randint(0, len(methods) - 1)]
            current_issue = self.newest_issue
            full_game_name = f'{rand_method.group_name}.{rand_method.set_name}.{rand_method.method_name}'
            max_mul = self.__is_method_enable(lottery_code=_lottery_code, method_name=full_game_name)
            if not max_mul:  # 若彩種未開放
                continue
            bet_content = _generator.get_bet_content(method=rand_method, issues=self.newest_issue)
            print(f'methods:{list(methods)}, bet_content: {bet_content}')
            if bet_content is not None:
                print(f'當前期數：{current_issue[0]["number"]}, 開始投注: {rand_method.title}')
                # 若預期的投注小於  (目標投注金額 - 已投注金額) / 剩餘的單期投注注單數量
                average_bet_amount = (_target_amount - total_amount) / (_min_bet_per_day - total_issue_times)
                if bet_content['amount'] < average_bet_amount:
                    multiple = ceil(average_bet_amount / bet_content['amount'])
                    multiple = multiple if multiple < max_mul else max_mul  # 倍數不可大於玩法限制
                    for index in range(0, len(bet_content['orders'])):  # 修改投注內容內每一個玩法的倍數
                        bet_content['balls'][index]['multiple'] = multiple
                    bet_content['amount'] *= multiple  # 投注金額調整

                    print(f'因預期投注最低金額為{_target_amount}，本日預計再投注{_min_bet_per_day - total_issue_times}筆\n'
                          f'已提升倍數至{multiple}倍，總投注金額為{bet_content["amount"]}')

                print(f'生成注單內容: {bet_content}')
                r = self.session.post(self.env_data.get_em_url() + f'/gameBet/{_lottery_code}/submit',
                                      headers=self.header, json=bet_content, verify=False)
                total_amount += bet_content['amount']
                total_issue_times += 1
                try:  # 如果順利
                    print(f'投注結果:{loads(r.content)["msg"]}\n'
                          f'當前已投注{total_issue_times}注，總金額為{total_amount}')
                except:  # 如果不順利
                    print(f'投注失敗')
                    print(f'詳細問題請見封包返還內容：\n{r.content}')
                current_bet_times += 1

            while current_issue == self.newest_issue and current_bet_times == _max_bet_one_issue:
                sleep(20)
                self.__get_newest_issue(lottery_code=_lottery_code)
                if current_issue != self.newest_issue:
                    current_bet_times = 0

    def __is_method_enable(self, lottery_code: str, method_name: str):
        """
        驗證當前玩法是否可用
        :param lottery_code: 彩種代號
        :param method_name: 玩法名稱
        :return: 該玩法最大投注倍數，若不可用則返還 False
        """
        r = self.session.get(self.env_data.get_em_url() + f'/gameBet/{lottery_code}/dynamicConfig',
                             headers=self.header, verify=False)
        try:
            return loads(r.content)['data']['gamelimit'][0][method_name]['maxmultiple']
        except:
            return False

    def __get_newest_issue(self, lottery_code: str = 'cqssc', trace_times: int = 1) -> None:
        """
        投注壓測用，取得當前玩法最新期號與期號過期時間
        """
        self.content = ''
        target_api = self.env_data.get_em_url() + f'/gameBet/{lottery_code}/dynamicConfig'
        response = self.session.post(target_api, headers=self.header, data=self.content, verify=False)
        try:
            self.newest_issue = response.json()['data']['gamenumbers'][:trace_times:]
            self.now_stop_time = response.json()['data']['nowstoptime']
        except:
            print(f'取得獎期失敗，詳細見封包返還數據\n{response.content}')

    def __check_issue_time(self):
        """
        投注壓測用，驗證當前獎期是否已過期，若過期則重新取得
        """
        from datetime import datetime
        _format = '%Y/%m/%d %H:%M:%S'
        _issue_end_time = datetime.strptime(self.now_stop_time, _format)
        while datetime.now() > _issue_end_time:
            self.__get_newest_issue()
            sleep(3)

    def __get_bet_content(self, ball_num: int = 0):
        """
        投注壓測用，取得投注內容
        :param ball_num: 取得投注號，因使用在壓測中因此傳入index避免單一號碼重複投注
        :return: 投注內容
        """
        ball_num %= 100000  # ball_num 需小於100000
        return {"gameType": self.target_lottery, "isTrace": 0, "traceWinStop": 0, "traceStopValue": -1,
                "balls": [
                    {"id": 1, "ball": str(ball_num).zfill(5), "type": "wuxing.zhixuan.danshi", "moneyunit": "1",
                     "multiple": 1,
                     "awardMode": 1, "num": 1}
                ],
                "orders": [
                    {"number": self.newest_issue['number'], "issueCode": self.newest_issue['issueCode'], "multiple": 1}
                ],
                "redDiscountAmount": 0, "amount": '2.00'
                }

    def __md(self, _password, _param):
        import hashlib
        m = hashlib.md5()
        m.update(_password)
        sr = m.hexdigest()
        for i in range(3):
            sr = hashlib.md5(sr.encode()).hexdigest()
        rx = hashlib.md5(sr.encode() + _param).hexdigest()
        return rx


lottery = {
    99111: 'jlffc',
    99101: 'cqssc',
    99105: 'hljssc'
}

while True:
    try:
        input_env = input('投注環境:\n>> 1(Joy188)\n>> 2(Joy188 合營)\n>> 3(Dev02)\n>> 4(Dev02 合營)\n')
        if input_env == '1':
            env = 'joy188'
            break
        elif input_env == '2':
            env = 'joy188.195353'
            break
        elif input_env == '3':
            env = 'dev02'
            break
        elif input_env == '4':
            env = 'fh82dev02'
            break
    except:
        print('環境輸入錯誤，請重新輸入\n')

while True:
    try:
        input_tip = ''
        for k, v in lottery.items():
            input_tip += f'>> {k}({v})\n'
        lottery_id = int(input(f'投注ID:\n{input_tip}'))
        if lottery_id not in lottery.keys():
            print('不支援的彩種，請重新輸入')
        else:
            break
    except:
        pass

while True:
    try:
        max_bet_one_issue = int(input('每期最多投注注數:\n'))
        break
    except ValueError:
        print('參數錯誤，請輸入正整數')

while True:
    try:
        min_bet_per_day = int(input('最低每日投注注數: \n'))
        break
    except:
        print('參數有誤，請重新輸入')

while True:
    try:
        target_amount = int(input('輸入目標投注金額: (整數)\n'))
        break
    except:
        print('輸入金額有誤，請重新輸入')

while True:
    try:
        tip = '是否追號？\n' \
              '>> 0 （不追號，程式會持續運行並於跨期後持續投注到目標注數與金額　※：每期隨機投注號）\n' \
              '>> 1 （追號，計算可達需求的追號單並一次性投注　※：每期固定投注號）'
        is_trace = int(input(tip))
        if is_trace in [0, 1]:
            is_trace = True if is_trace == 1 else False
            break
        min_trace = ceil(min_bet_per_day / max_bet_one_issue)
        print(f'單期投注{max_bet_one_issue}筆注單，單日投注{min_bet_per_day}注，將追號{min_trace}期')
    except:
        print('參數有誤，請重新輸入')

while True:
    try:
        user_names = split(',|_| |,', input('輸入投注帳號，多帳號以 , 或空格區隔:\n'))
        break
    except:
        print('輸入用戶名有誤，請重新輸入')

while True:
    try:
        custom_password = input('輸入密碼:\n※：輸入空值則用預設密碼（Dev02:123qwe, Joy188:amberrd）\n')
        break
    except:
        print('輸入密碼有誤，請重新輸入')

ff = FF4LiteTool(env, use_proxy=False)

for user in user_names:
    generator = FF4GameContentGenerator(_lottery_id=lottery_id, target_method=['baozi'],
                                        env_id=ff.env_data.get_env_id(), _user=user)
    if env in ['dev02', 'fh82dev02']:
        ff.login(user, custom_password if custom_password != '' else '123qwe')
    else:
        ff.login(user, custom_password if custom_password != '' else 'amberrd')
    # ff.start_auto_bet_tool_trace(_lottery_code=lottery[int(input_lottery)], _generator=generator,
    #                              _max_bet_one_issue=max_bet_one_issue, _min_bet_per_day=min_bet_per_day,
    #                              _target_amount=target_amount)
    ff.start_auto_bet_tool_single(_lottery_code=lottery[int(lottery_id)], _generator=generator,
                                  _max_bet_one_issue=max_bet_one_issue, _min_bet_per_day=min_bet_per_day,
                                  _target_amount=target_amount)

input('自動投注結束')

# ff.start_bet_stress_test(run_times=5, lottery='cqssc')  # 單一彩種單式連續投注
# ff.start_api_stress_test(run_times=100, api=ff.env_data.get_em_url() + '/gameUserCenter/queryOrders', api_content='')

# ffgcg = FF4GameContentGenerator(99111)
# print(ffgcg.get_bet_content(ffgcg.get_method('后二组选组选单式'), [{'number': '123', 'issueCode': '4123'}]))
