import itertools
import json
import math
import random

import requests
from utils import Config


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
        self.env_data = Config.EnvConfig(env)
        self.header = {  # 預設Header格式
            'User-Agent': Config.UserAgent.PC.value
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
            import sys
            sys.exit("登入失敗")

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
        print(f'index: {index}, cost time: {timeit.default_timer() - timer}')
        return None  # r.content

    def bet_orderd_times(self, lottery_code: str, lottery_id: int, trace_times: int = 1, target_amount: float = 5000):
        self.game_content_generator = FF4GameContentGenerator(lottery_id)
        self.lottery_code = lottery_code
        bet_amount = 0
        self.__get_newest_issue(lottery_code=lottery_code, trace_times=trace_times)
        for method in self.game_content_generator.methods:
            print(f'Start bet method: {method.title}')
            self.__check_issue_time()
            if target_amount > 0 and bet_amount > target_amount:
                break
            bet_content = self.game_content_generator.get_bet_content(method=method, issues=self.newest_issue)
            print(f'bet_content={bet_content}')
            if bet_content is not None:
                bet_amount += bet_content['amount']
                r = self.session.post(self.env_data.get_em_url() + f'/gameBet/{lottery_code}/submit',
                                      headers=self.header, json=bet_content, verify=False)
            print(f'Done.')

    def __get_newest_issue(self, lottery_code: str = 'cqssc', trace_times: int = 1) -> None:
        """
        投注壓測用，取得當前玩法最新期號與期號過期時間
        """
        self.content = ''
        target_api = self.env_data.get_em_url() + f'/gameBet/{lottery_code}/dynamicConfig'
        response = self.session.post(target_api, headers=self.header, data=self.content, verify=False)
        self.newest_issue = response.json()['data']['gamenumbers'][:trace_times:]
        self.now_stop_time = response.json()['data']['nowstoptime']

    def __check_issue_time(self):
        """
        投注壓測用，驗證當前獎期是否已過期，若過期則重新取得
        """
        from datetime import datetime
        import time
        _format = '%Y/%m/%d %H:%M:%S'
        _issue_end_time = datetime.strptime(self.now_stop_time, _format)
        while datetime.now() > _issue_end_time:
            self.__get_newest_issue()
            time.sleep(3)

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
    def __init__(self, lottery: int, code_name: str, set_name: str, method_name: str, title: str):
        self.lottery = lottery
        self.code_name = code_name
        self.set_name = set_name
        self.method_name = method_name
        self.title = title
        if code_name in ['yixing']:  # 一星
            self.offset = 4
        elif code_name in ['houer']:  # 後二
            self.offset = 3
        elif code_name in ['housan']:  # 後三
            self.offset = 2
        elif code_name in ['sixing', 'zhongsan']:  # 四星 中三
            self.offset = 1
        elif code_name in ['wuxing', 'qianer', 'qiansan']:  # 五星 前二 前三
            self.offset = 0
        else:
            self.offset = None

        if code_name in ['wuxing']:
            self.digit = 5
        elif code_name in ['sixing']:
            self.digit = 4
        elif code_name in ['qiansan', 'zhongsan', 'housan']:
            self.digit = 3
        elif code_name in ['qianer', 'houer']:
            self.digit = 2
        elif code_name in ['yixing']:
            self.digit = 1
        else:
            self.digit = None

    @staticmethod
    def get_all_games(lotteryID: int) -> list:
        """
        自FF4GameAwards.json取得所有對應採種玩法，並以Array<GameAward>回傳
        :param lotteryID: 彩種ID
        :return: Array<GameAward>
        """
        result = []
        with open('FF4GameAwards.json', encoding='utf8', errors='ignore') as json_file:
            method_json = json.load(json_file)
            for method in method_json['data']:
                if method['LOTTERYID'] == lotteryID:
                    result.append(Method(lotteryID, method['GROUP_CODE_NAME'], method['SET_CODE_NAME'],
                                         method['METHOD_CODE_NAME'], method['TITLE']))
        return result


class FF4GameContentGenerator:
    def __init__(self, lotteryID: int):
        self.lotteryID = lotteryID
        self.methods = Method.get_all_games(self.lotteryID)

    def get_bet_content(self, method: Method, issues: list):
        random_ball = self.__get_random_method_ball(method)
        if random_ball is None:
            return None
        orders = []
        for issue in issues:
            orders.append(
                {"number": issue['number'],
                 "issueCode": issue['issueCode'],
                 "multiple": 1}
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
                    "type": f'{method.code_name}.{method.set_name}.{method.method_name}',
                    "moneyunit": "1",
                    "multiple": 1,
                    "awardMode": 1,
                    "num": random_ball[1]
                }
            ],
            "orders": orders,
            "redDiscountAmount": 0,
            "amount": random_ball[1] * 2 * len(orders)
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
        if method.method_name in ["fushi"]:
            content = self.__random_fushi(method)
        elif method.method_name in ['danshi', 'zuliudanshi', 'zusandanshi']:
            content = self.__random_danshi(method)
        else:
            content = None
        return content

    def __random_fushi(self, method: Method) -> [str, int]:
        balls = []
        num = 1
        if method.set_name == 'zhixuan':
            for digit in range(method.digit):  # 運行(投注號長度)次
                ball = ""
                _len = random.randint(1, 9)  # 單一位數的投注數量
                while len(ball) < _len:
                    r_int = random.randint(0, 9)
                    if str(r_int) not in ball:
                        ball += str(r_int)
                balls.append(''.join(sorted(ball)))
            for _ball in balls:
                num *= len(_ball)
            for _ in range(method.offset):  # 前方省略號碼補 '-'
                balls.insert(0, '-')
            for _ in range(5 - method.offset - method.digit):  # 剩餘後方補 '-'
                balls.append('-')
            print(','.join(balls))
            return [','.join(balls), num]
        elif method.set_name == 'zuxuan':
            ball = ""
            _len = random.randint(2, 9)  # 隨機投注數量
            while len(ball) < _len:
                r_int = random.randint(0, 9)  # 隨機不重複數字
                if str(r_int) not in ball:
                    ball += str(r_int)
            num = len(list(itertools.combinations(ball, 2)))  # 組選取組合數
            return [','.join(sorted(ball)), num]
        elif method.set_name == 'dingweidan':
            num = 0
            balls = []
            for _digit in range(0, 5):  # 萬~個獨立判斷
                _amount = random.randint(0, 10)  # 隨機0~10位數
                if _amount == 0:
                    balls.append('-')
                else:
                    ball = ""
                    while len(ball) < _amount:
                        r_int = random.randint(0, 9)
                        if str(r_int) not in ball:
                            ball += str(r_int)
                    num += _amount
                    balls.append(''.join(sorted(ball)))
            return [','.join(balls), num]
        return None

    def __random_danshi(self, method: Method) -> [str, int]:
        balls = []
        if method.method_name == 'danshi':  # 5/4/3/2星單式
            # amount = random.randint(1, int(math.pow(10, method.digit)))  # 投注位數取隨機注數
            amount = random.randint(1, 80)  # 投注位數取隨機注數
            while len(balls) < amount:
                if method.set_name == 'zhixuan':  # 直選單式
                    num = str(random.randint(0, int(math.pow(10, method.digit) - 1))).zfill(method.digit)  # 取隨機號，若開頭為0則須補0至足夠位數
                    if num not in balls:
                        balls.append(num)
                elif method.set_name == 'zuxuan':  # 組選單式
                    ball = ''
                    for _ in range(0, method.digit):  # 依照單式的號碼長度運行N次
                        num = str(random.randint(0, 9))
                        while ball.count(num) + 1 == method.digit:  # 若加入新數字後形成豹子號
                            num = str(random.randint(0, 9))
                        ball += num
                    ball = ''.join(sorted(ball))
                    if ball not in balls:
                        balls.append(ball)
            return [' '.join(balls), len(balls)]
        elif method.method_name == 'zuliudanshi':  # 組六邏輯
            amount = random.randint(1, 100)  # 組三組六上限需計算，先行固定100
            while len(balls) < amount:
                ball = ''
                while len(ball) < 3:
                    num = str(random.randint(0, 9))
                    if num not in ball:
                        ball += num
                ball = ''.join(sorted(ball))
                if ball not in balls:
                    balls.append(ball)
            return [' '.join(balls), amount]
        elif method.method_name == 'zusandanshi':  # 組三邏輯
            amount = random.randint(1, 100)  # 組三組六上限需計算，先行固定100
            while len(balls) < amount:
                ball = ''
                num = str(random.randint(0, 9))  # 00/11/22...
                num2 = str(random.randint(0, 9))
                while num == num2:
                    num2 = str(random.randint(0, 9))
                ball += num + num + num2
                ball = ''.join(sorted(ball))
                print(ball)
                if ball not in balls:
                    balls.append(ball)
            return [' '.join(balls), amount]
        return None


ff = FF4LiteTool('joy188', use_proxy=True)
for user in ['twen101']:
    ff.login(user, 'amberrd')
    ff.bet_orderd_times(lottery_code='jlffc', lottery_id=99111, trace_times=3, target_amount=-1)

# ff.start_bet_stress_test(run_times=5, lottery='cqssc')  # 單一彩種單式連續投注
# ff.start_api_stress_test(run_times=100, api=ff.env_data.get_em_url() + '/gameUserCenter/queryOrders', api_content='')

# ffgcg = FF4GameContentGenerator(99111)
# print(ffgcg.get_bet_content(ffgcg.get_method('前三直选单式'), [{'number': '123', 'issueCode': '4123'}]))
