from itertools import combinations
from json import loads, load
from math import ceil, pow
from random import randint
from re import split
from sys import exit
from time import sleep

import requests
from utils.Config import EnvConfig, UserAgent


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


class Method:
    def __init__(self, lottery: int, group_name: str, set_name: str, method_name: str, title: str):
        self.lottery = lottery
        self.group_name = group_name
        self.set_name = set_name
        self.method_name = method_name
        self.title = title
        if group_name in ['yixing']:  # 一星
            self.offset = 4
        elif group_name in ['houer']:  # 後二
            self.offset = 3
        elif group_name in ['housan']:  # 後三
            self.offset = 2
        elif group_name in ['sixing', 'zhongsan']:  # 四星 中三
            self.offset = 1
        elif group_name in ['wuxing', 'qianer', 'qiansan']:  # 五星 前二 前三
            self.offset = 0
        else:
            self.offset = None

        if group_name in ['wuxing']:
            self.digit = 5
        elif group_name in ['sixing']:
            self.digit = 4
        elif group_name in ['qiansan', 'zhongsan', 'housan'] or method_name in ['houyi']:
            self.digit = 3
        elif group_name in ['qianer', 'houer'] or method_name in ['qianer', 'houer']:
            self.digit = 2
        elif group_name in ['yixing'] or method_name in ['qianyi', 'houyi', 'zonghe']:
            self.digit = 1
        else:
            self.digit = None

    @staticmethod
    def get_all_games(lottery_id: int, target_group: list = None, target_set: list = None,
                      target_method: list = None) -> list:
        """
        自FF4GameAwards.json取得所有對應採種玩法，並以Array<GameAward>回傳
        :param target_group: 目標玩法群
        :param target_set: 目標玩法組
        :param target_method: 目標玩法
        :param lottery_id: 彩種ID
        :return: Array<GameAward>
        """
        result = []
        with open('FF4GameAwards.json', encoding='utf8', errors='ignore') as json_file:
            method_json = load(json_file)
            for method in method_json['data']:
                if method['LOTTERYID'] == lottery_id:
                    if target_group:
                        if method['GROUP_CODE_NAME'] not in target_group:
                            continue
                    if target_set:
                        if method['SET_CODE_NAME'] not in target_set:
                            continue
                    if target_method:
                        if method['METHOD_CODE_NAME'] not in target_method:
                            continue
                    result.append(Method(lottery_id, method['GROUP_CODE_NAME'], method['SET_CODE_NAME'],
                                         method['METHOD_CODE_NAME'], method['TITLE']))
        return result


class FF4GameContentGenerator:
    def __init__(self, _lottery_id: int, env_id: int, _user: str,
                 target_group: list = None, target_set: list = None, target_method: list = None):
        """

        :param _lottery_id:
        :param target_group:
        :param target_set:
        :param target_method:
        :param env_id:
        """
        self.lottery_id = _lottery_id
        self.env_id = env_id
        self._user = _user
        self.methods = Method.get_all_games(lottery_id=self.lottery_id, target_group=target_group,
                                            target_set=target_set, target_method=target_method)

    def get_bet_content(self, method: Method, issues: list, multiple: int = 1):
        random_ball = self.__get_random_method_ball(method)
        if random_ball is None:
            return None
        orders = []
        for issue in issues:
            orders.append(
                {"number": issue['number'],
                 "issueCode": issue['issueCode'],
                 "multiple": multiple}
            )
        return {
            "gameType": method.lottery,
            "isTrace": 0 if len(issues) == 1 else 1,
            "traceWinStop": 0,
            "traceStopValue": -1,
            "balls": [
                {
                    "id": 1,
                    "ball": random_ball[0],
                    "type": f'{method.group_name}.{method.set_name}.{method.method_name}',
                    "moneyunit": "1",
                    "multiple": 1,
                    "awardMode": 1,
                    "num": random_ball[1]
                }
            ],
            "orders": orders,
            "redDiscountAmount": 0,
            "amount": random_ball[1] * 2 * len(orders) * multiple
        }

    def get_method(self, title):
        for method in self.methods:
            if method.title == title:
                return method
        return None

    def __get_random_method_ball(self, method: Method) -> [str, int]:
        """
        回傳當前玩法的隨機投注內容與注數
        :param method:
        :return:
        """
        if method.group_name == 'daxiaodanshuang':
            content = self.__random_daxiaodanshuang(method)
        elif method.group_name == 'longhu':
            content = self.__random_longhu(method)
        elif method.group_name == 'shuangmienpan':
            content = self.__random_shuangmienpan(method)
        elif method.method_name in ["fushi"]:
            content = self.__random_fushi(method)
        elif method.method_name in ['danshi', 'zuliudanshi', 'zusandanshi', 'hunhezuxuan']:
            content = self.__random_danshi(method)
        elif 'zuxuan' in method.method_name:
            content = self.__random_zuxuan_n(method)
        elif method.set_name == 'budingwei':
            content = self.__random_budingwei(method)
        elif method.method_name == 'baodan':
            content = self.__random_baodan(method)
        elif method.method_name == 'hezhi':
            content = self.__random_hezhi(method)
        elif method.set_name == 'quwei':
            content = self.__random_quwei()
        elif method.method_name == 'kuadu':
            content = self.__random_kuadu(method)
        else:
            content = None
        return content

    def __random_fushi(self, method: Method) -> [str, int]:
        balls = []
        num = 1
        if method.set_name == 'zhixuan':
            for digit in range(method.digit):  # 運行(投注號長度)次
                ball = ""
                _len = randint(1, 9)  # 單一位數的投注數量
                while len(ball) < _len:
                    r_int = randint(0, 9)
                    if str(r_int) not in ball:
                        ball += str(r_int)
                balls.append(''.join(sorted(ball)))
            for _ball in balls:
                num *= len(_ball)
            for _ in range(method.offset):  # 前方省略號碼補 '-'
                balls.insert(0, '-')
            for _ in range(5 - method.offset - method.digit):  # 剩餘後方補 '-'
                balls.append('-')
            return [','.join(balls), num]
        elif method.set_name == 'zuxuan':
            ball = ""
            _len = randint(2, 9)  # 隨機投注數量
            while len(ball) < _len:
                r_int = randint(0, 9)  # 隨機不重複數字
                if str(r_int) not in ball:
                    ball += str(r_int)
            num = len(list(combinations(ball, 2)))  # 組選取組合數
            return [','.join(sorted(ball)), num]
        elif method.set_name == 'dingweidan':
            num = 0
            balls = []
            for _digit in range(0, 5):  # 萬~個獨立判斷
                _amount = randint(0, 10)  # 隨機0~10位數
                if _amount == 0:
                    balls.append('-')
                else:
                    ball = ""
                    while len(ball) < _amount:
                        r_int = randint(0, 9)
                        if str(r_int) not in ball:
                            ball += str(r_int)
                    num += _amount
                    balls.append(''.join(sorted(ball)))
            return [','.join(balls), num]
        return None

    def __random_danshi(self, method: Method) -> [str, int]:
        balls = []
        if method.method_name == 'danshi':  # 5/4/3/2星單式
            amount = randint(1, int(pow(10, method.digit) / 3))  # 投注位數取隨機注數，配合組選限制，只取1/3號
            while len(balls) < amount:
                if method.set_name == 'zhixuan':  # 直選單式
                    num = str(randint(0, int(pow(10, method.digit) - 1))).zfill(
                        method.digit)  # 取隨機號，若開頭為0則須補0至足夠位數
                    if num not in balls:
                        balls.append(num)
                elif method.set_name == 'zuxuan':  # 組選單式
                    ball = ''
                    for _ in range(0, method.digit):  # 依照單式的號碼長度運行N次
                        num = str(randint(0, 9))
                        while ball.count(num) + 1 == method.digit:  # 若加入新數字後形成豹子號
                            num = str(randint(0, 9))
                        ball += num
                    ball = ''.join(sorted(ball))
                    if ball not in balls:
                        balls.append(ball)
            return [' '.join(balls), len(balls)]
        elif method.method_name in ['zuliudanshi', 'hunhezuxuan']:  # 組六邏輯
            amount = randint(1, 100)  # 投注位數取隨機注數，配合組選限制，至多只取100號
            while len(balls) < amount:
                ball = ''
                while len(ball) < 3:
                    num = str(randint(0, 9))
                    if num not in ball:
                        ball += num
                ball = ''.join(sorted(ball))
                if ball not in balls:
                    balls.append(ball)
            return [' '.join(balls), amount]
        elif method.method_name == 'zusandanshi':  # 組三邏輯
            amount = randint(1, 80)  # 投注位數取隨機注數，配合組選限制，至多只取80號
            while len(balls) < amount:
                ball = ''
                num = str(randint(0, 9))  # 00/11/22...
                num2 = str(randint(0, 9))
                while num == num2:
                    num2 = str(randint(0, 9))
                ball += num + num + num2
                ball = ''.join(sorted(ball))
                if ball not in balls:
                    balls.append(ball)
            return [' '.join(balls), amount]
        return None

    def __random_zuxuan_n(self, method: Method) -> [str, int]:
        if method.method_name in ['zuxuan120', 'zuxuan24', 'zuxuan6']:  # 組120 / 24 / 6 單獨處理
            if method.method_name == 'zuxuan120':
                pick_num = 5
            elif method.method_name == 'zuxuan24':
                pick_num = 4
            else:
                pick_num = 2
            length = randint(pick_num, 10)  # 隨機選n~10號
            ball = ''
            while len(ball) < length:
                num = str(randint(0, 9))
                if num not in ball:
                    ball += num
            return [','.join(sorted(ball)), len(list(combinations(ball, pick_num)))]
        if method.method_name == 'zuxuan60':  # 二重號*1 + 單號*3
            pick_first = 1  # 首號取數
            pick_second = 3  # 第二號取數
        elif method.method_name == 'zuxuan30':  # 二重號*2 + 單號*1
            pick_first = 2
            pick_second = 1
        elif method.method_name == 'zuxuan20':  # 三重號*1 + 單號*2
            pick_first = 1
            pick_second = 2
        elif method.method_name == 'zuxuan10':  # 三重號*1 + 二重號*1
            pick_first = 1
            pick_second = 1
        elif method.method_name == 'zuxuan5':  # 四重號*1 + 單號*1
            pick_first = 1
            pick_second = 1
        elif method.method_name == 'zuxuan12':
            pick_first = 1
            pick_second = 2
        else:  # method.method_name == 'zuxuan4':
            pick_first = 1
            pick_second = 1

        length_first = randint(pick_first, 10 - pick_second)  # 第一號取數範圍
        length_second = randint(pick_second, 10 - length_first)  # 第二號取數範圍 (第一號取剩的)
        ball = ['', '']
        while len(ball[0]) < length_first:
            num = str(randint(0, 9))
            if num not in ball[0]:
                ball[0] += num
        ball[0] = ''.join(sorted(ball[0]))
        while len(ball[1]) < length_second:
            num = str(randint(0, 9))
            if num not in ball[0] and num not in ball[1]:  # **為簡化計算注數，二重號與單號數字不重複
                ball[1] += num
        ball[1] = ''.join(sorted(ball[1]))
        comb_first = len(list(combinations(ball[0], pick_first)))  # 單號組合數
        comb_second = len(list(combinations(ball[1], pick_second)))  # 單號組合數
        return [','.join(ball), comb_first * comb_second]

    def __random_budingwei(self, method: Method) -> [str, int]:
        if method.method_name == 'yimabudingwei':
            pick_len = 1
        elif method.method_name == 'ermabudingwei':
            pick_len = 2
        else:
            pick_len = 3
        length = randint(pick_len, 10)
        ball = ''
        while len(ball) < length:
            num = str(randint(0, 9))
            if num not in ball:
                ball += num
        return [','.join(ball), len(list(combinations(ball, pick_len)))]

    def __random_baodan(self, method: Method) -> [str, int]:
        if method.digit == 3:
            return [str(randint(0, 9)), 54]
        else:
            return [str(randint(0, 9)), 9]

    def __random_hezhi(self, method: Method) -> [str, int]:
        hezhi_table = {
            3: {
                'zhixuan': {
                    0: 1, 1: 3, 2: 6, 3: 10, 4: 15, 5: 21, 6: 28, 7: 36, 8: 45, 9: 55, 10: 63, 11: 69, 12: 73, 13: 75,
                    14: 75, 15: 73, 16: 69, 17: 63, 18: 55, 19: 45, 20: 36, 21: 28, 22: 21, 23: 15, 24: 10, 25: 6,
                    26: 3, 27: 1
                },
                'zuxuan': {
                    1: 1, 2: 2, 3: 2, 4: 4, 5: 5, 6: 6, 7: 8, 8: 10, 9: 11, 10: 13, 11: 14, 12: 14, 13: 15,
                    14: 15, 15: 14, 16: 14, 17: 13, 18: 11, 19: 10, 20: 8, 21: 6, 22: 5, 23: 4, 24: 2, 25: 2, 26: 1
                }
            },
            2: {
                'zhixuan': {
                    0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10,
                    10: 9, 11: 8, 12: 7, 13: 6, 14: 5, 15: 4, 16: 3, 17: 2, 18: 1
                },
                'zuxuan': {
                    1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5,
                    10: 4, 11: 4, 12: 3, 13: 3, 14: 2, 15: 2, 16: 1, 17: 1
                }
            }
        }
        hezhi_list = hezhi_table[method.digit][method.set_name]
        length = randint(1, len(hezhi_list))
        balls = []
        amount = 0
        while len(balls) < length:
            rand_hezhi = randint(0, len(hezhi_list) - 1)
            if str(list(hezhi_list.keys())[rand_hezhi]) not in balls:
                balls.append(str(list(hezhi_list.keys())[rand_hezhi]))
                amount += list(hezhi_list.values())[rand_hezhi]
        return [','.join(sorted(balls)), amount]

    def __random_quwei(self) -> [str, int]:
        length = randint(1, 10)
        ball = ''
        while len(ball) < length:
            rand_num = str(randint(0, 9))
            if rand_num not in ball:
                ball += rand_num
        return [','.join(ball), len(ball)]

    def __random_kuadu(self, method: Method) -> [str, int]:
        kuadu_table = {
            3: {
                0: 10, 1: 54, 2: 96, 3: 126, 4: 144, 5: 150, 6: 144, 7: 126, 8: 96, 9: 54
            },
            2: {
                0: 10, 1: 18, 2: 16, 3: 14, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2
            }
        }
        kuadu_list = kuadu_table[method.digit]
        length = randint(1, len(kuadu_list))
        balls = []
        amount = 0
        while len(balls) < length:
            rand_kuadu = randint(0, len(kuadu_list) - 1)
            if str(list(kuadu_list.keys())[rand_kuadu]) not in balls:
                balls.append(str(list(kuadu_list.keys())[rand_kuadu]))
                amount += list(kuadu_list.values())[rand_kuadu]
        return [','.join(sorted(balls)), amount]

    def __random_daxiaodanshuang(self, method: Method) -> [str, int]:
        daxiao_pool = ['大', '小', '单', '双']
        if method.method_name == 'fushi':  # for PK10系列
            pk10_pool = ['冠军', '亚军', '季军', '第四名', '第五名', '第六名', '第七名', '第八名', '第九名', '第十名']
            random_fushi = randint(0, len(pk10_pool) - 1)
            random_daxiao = randint(0, len(daxiao_pool) - 1)
            return [random_fushi + random_daxiao, 1]
        else:
            bet_amount = 1  # 投注注數
            balls = []
            for index in range(0, method.digit):
                ball = ''
                length = randint(1, 4)
                bet_amount *= length  # 注數計算
                while len(ball) < length:
                    random_daxiao = daxiao_pool[randint(0, 3)]
                    if random_daxiao not in ball:
                        ball += random_daxiao
                balls.append('|'.join(ball))
            return [','.join(balls), bet_amount]

    def __random_longhu(self, method: Method) -> [str, int]:
        print(f'method: {method}')
        longhu_pool = ['龙', '虎', '和']
        bet_amount = 0
        if method.set_name == 'lh':
            pk10_pool = ['冠军', '亚军', '季军', '第四名', '第五名', '第六名', '第七名', '第八名', '第九名', '第十名']
            pk10_pool = ['冠军', '亚军', '季军', '第四名', '第五名', '第六名', '第七名', '第八名', '第九名', '第十名']
            random_fushi = randint(0, len(pk10_pool) - 1)
            random_daxiao = randint(0, len(longhu_pool) - 1)
            return [random_fushi + random_daxiao, 1]
        else:  # method.st_name == 'longhu'
            balls = []
            for _ in range(0, 10):
                ball = ''
                length = randint(0, 3)
                while len(ball) < length:
                    random_longhu = longhu_pool[randint(0, 2)]
                    if random_longhu not in ball:
                        ball += random_longhu
                if length == 0:
                    ball = '-'
                balls.append('|'.join(ball))
                bet_amount += length
            print(f'balls: {list(balls)}')
            return [','.join(balls), bet_amount]

    def __random_shuangmienpan(self, method: Method) -> [str, int]:
        num_pool = ['龙', '虎', '和', '大', '小', '单', '双']
        if method.set_name == 'zonghe':
            random_num = num_pool[randint(0, len(num_pool) - 1)]
            return [random_num, 1]
        elif method.set_name == 'shiuanma':
            ball_pool = ['第一球', '第二球', '第三球', '第四球', '第五球']
            random_ball = ball_pool[randint(0, len(ball_pool) - 1)]
            for digit in range(0, 9):
                num_pool.append(str(digit))
            random_num = num_pool[randint(0, len(num_pool) - 1)]
            return [random_ball + random_num, 1]
        else:
            ball_pool = ['豹子', '顺子', '对子', '半顺', '杂六']
            random_ball = ball_pool[randint(0, len(ball_pool) - 1)]
            from utils.Connection import OracleConnection
            conn = OracleConnection(self.env_id)
            bonus = conn.select_bonus(lottery_id, '', self._user)
            print(bonus)
            return [random_ball, 1]

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
