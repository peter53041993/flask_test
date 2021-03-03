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

    def __get_newest_issue(self, lottery: str = 'cqssc') -> None:
        """
        投注壓測用，取得當前玩法最新期號與期號過期時間
        """
        self.content = ''
        target_api = self.env_data.get_em_url() + f'/gameBet/{lottery}/dynamicConfig'
        response = self.session.post(target_api, headers=self.header, data=self.content, verify=False)
        self.newest_issue = response.json()['data']['gamenumbers'][0]
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


ff = FF4LiteTool('dev02', use_proxy=True)
ff.login('twen101', '123qwe')
ff.start_bet_stress_test(run_times=5, lottery='cqssc')  # 單一彩種單式連續投注
# ff.start_api_stress_test(run_times=100, api=ff.env_data.get_em_url() + '/gameUserCenter/queryOrders', api_content='')
