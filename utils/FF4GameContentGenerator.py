from itertools import combinations
from json import load
from math import pow
from random import randint


class Method:
    def __init__(self, lottery_id: int, group_name: str, set_name: str, method_name: str, title: str):
        self.lottery_id = lottery_id
        self.group_name = group_name
        self.set_name = set_name
        self.method_name = method_name
        self.title = title
        if group_name in ['yixing', 'yixing_2000']:  # 一星
            self.offset = 4
        elif group_name in ['houer', 'houer_2000']:  # 後二
            self.offset = 3
        elif group_name in ['housan', 'housan_2000']:  # 後三
            self.offset = 2
        elif group_name in ['sixing', 'zhongsan', 'sixing_2000', 'zhongsan_2000']:  # 四星 中三
            self.offset = 1
        elif group_name in ['wuxing', 'qianer', 'qiansan', 'qiansi']:  # 五星 前二 前三
            self.offset = 0
        else:
            self.offset = None

        if group_name in ['qianwu', 'qiansi', 'guanya', 'guanyaji', 'caipaiwei']:
            self.digit = 10
        elif group_name in ['wuxing']:
            self.digit = 5
        elif group_name in ['sixing', 'sixing_2000']:
            self.digit = 4
        elif group_name in ['qiansan', 'zhongsan', 'zhongsan_2000', 'housan', 'housan_2000'] or method_name in [
            'houyi']:
            self.digit = 3
        elif group_name in ['qianer', 'houer', 'houer_2000'] or method_name in ['qianer', 'houer']:
            self.digit = 2
        elif group_name in ['yixing', 'yixing_2000'] or method_name in ['qianyi', 'houyi', 'zonghe']:
            self.digit = 1
        else:
            self.digit = None

    def output_detail(self):
        print(f'lottery: {self.lottery_id}')
        print(f'title: {self.title}')
        print(f'name: {self.group_name}.{self.set_name}.{self.method_name}')

    @staticmethod
    def get_all_games(lottery_id: int = None, target_group: list = None, target_set: list = None,
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
                if lottery_id is None:
                    if target_group:
                        if method['GROUP_CODE_NAME'] not in target_group:
                            continue
                    if target_set:
                        if method['SET_CODE_NAME'] not in target_set:
                            continue
                    if target_method:
                        if method['METHOD_CODE_NAME'] not in target_method:
                            continue
                    result.append(Method(method['LOTTERYID'], method['GROUP_CODE_NAME'], method['SET_CODE_NAME'],
                                         method['METHOD_CODE_NAME'], method['TITLE']))
                elif method['LOTTERYID'] == lottery_id:
                    if target_group:
                        if method['GROUP_CODE_NAME'] not in target_group:
                            continue
                    if target_set:
                        if method['SET_CODE_NAME'] not in target_set:
                            continue
                    if target_method:
                        if method['METHOD_CODE_NAME'] not in target_method:
                            continue
                    result.append(Method(method['LOTTERYID'], method['GROUP_CODE_NAME'], method['SET_CODE_NAME'],
                                         method['METHOD_CODE_NAME'], method['TITLE']))
        return result


class FF4GameContentGenerator:
    def __init__(self, lottery_id: int, env_id: int, user_name: str,
                 target_group: list = None, target_set: list = None, target_method: list = None):
        """
        :param lottery_id: 玩法ID, 為空時返還全部
        :param target_group: 指定玩法群, 為空時返還全部
        :param target_set: 指定玩法組, 為空時返還全部
        :param target_method: 指定方法, 為空時返還全部
        :param env_id: 雙面盤用，用來抓取用戶返點並計算遊戲獎金
        :param user_name:  雙面盤用，用來抓取用戶返點並計算遊戲獎金
            """
        self.lottery_id = lottery_id
        self.env_id = env_id
        self._user = user_name
        self.methods = Method.get_all_games(lottery_id=self.lottery_id, target_group=target_group,
                                            target_set=target_set, target_method=target_method)

    def get_bet_content(self, method: Method, issues: list, multiple: int = 1):
        random_ball = self.__get_random_method_ball(method)
        print(f'get_bet_content: {random_ball}')
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
            "gameType": method.lottery_id,
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

    def get_all_ignore_games(self):
        index = 1
        for method in self.methods:
            try:
                random_ball = self.__get_random_method_ball(method)
            except Exception as e:
                error_class = e.__class__.__name__  # 取得錯誤類型
                detail = e.args[0]  # 取得詳細內容
                import sys
                cl, exc, tb = sys.exc_info()  # 取得Call Stack
                import traceback
                lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
                fileName = lastCallStack[0]  # 取得發生的檔案名稱
                lineNum = lastCallStack[1]  # 取得發生的行號
                funcName = lastCallStack[2]  # 取得發生的函數名稱
                errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
                print(errMsg)
                method.output_detail()
            if random_ball is None:
                print(f'\nindex: {index}')
                method.output_detail()
                index += 1

    def __get_random_method_ball(self, method: Method) -> [str, int]:
        """
        回傳當前玩法的隨機投注內容與注數
        :param method:
        :return:
        """
        if method.lottery_id in [99301, 99302, 99303, 99304, 99305, 99306]:
            content = self.__random_115_series(method)
        elif method.group_name == 'daxiaodanshuang':  # 大小單雙
            content = self.__random_daxiaodanshuang(method)
        elif method.group_name == 'longhu':  # 龍虎
            content = self.__random_longhu(method)
        elif method.group_name == 'shuangmienpan':  # 雙面盤
            content = self.__random_shuangmienpan(method)
        elif method.set_name in ['putongwanfa', 'panmian']:  # 快樂彩系列
            content = self.__random_klc_series(method)
        elif method.method_name in ["fushi"]:
            content = self.__random_fushi(method)
        elif method.method_name in ['danshi', 'zuliudanshi', 'zusandanshi', 'hunhezuxuan']:
            content = self.__random_danshi(method)
        elif method.method_name in ['zusan', 'zuliu']:
            content = self.__random_zusanzuliu(method)
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
        elif method.method_name in ['qianwu', 'qiansi', 'guanya', 'guanyaji', 'caipaiwei']:
            content = self.__random_pk10(method)
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
            return [','.join(balls), bet_amount]

    def __random_shuangmienpan(self, method: Method) -> [str, int]:
        """
        雙面盤投注內容產出，需取得用戶返點與玩法理論獎金換算平台高獎金
        :param method:
        :return:
        """
        num_pool = ['龙', '虎', '和', '大', '小', '单', '双']
        from utils.Connection import OracleConnection
        # conn = OracleConnection(self.env_id)
        # bonus = conn.select_bonus(self.lottery_id, '', self._user)  # 需取得用戶返點等資訊
        if method.set_name == 'zonghe':
            random_num = num_pool[randint(0, len(num_pool) - 1)]
            # return [random_num, 1]
            return None
        elif method.set_name == 'shiuanma':
            ball_pool = ['第一球', '第二球', '第三球', '第四球', '第五球']
            random_ball = ball_pool[randint(0, len(ball_pool) - 1)]
            for digit in range(0, 9):
                num_pool.append(str(digit))
            random_num = num_pool[randint(0, len(num_pool) - 1)]
            # return [random_ball + random_num, 1]
            return None
        else:
            ball_pool = ['豹子', '顺子', '对子', '半顺', '杂六']
            random_ball = ball_pool[randint(0, len(ball_pool) - 1)]
            # return [random_ball, 1]
            return None

    def __random_pk10(self, method: Method) -> [str, int]:
        if method.group_name == 'guanya':
            return None
        elif method.group_name == 'guanyaji':
            return None
        elif method.group_name == 'qianwu':
            return None
        elif method.group_name == 'qiansi':
            return None
        else:  # method.group_name == 'caipaiwei':
            return None

    def __random_zusanzuliu(self, method: Method) -> [str, int]:
        ball = ''
        if method.method_name == 'zusan':
            length = randint(2, 10)
            while len(ball) < length:
                random_num = str(randint(0, 9))
                if random_num not in ball:
                    ball += random_num
            return [','.join(ball), len(ball) * (len(ball) - 1)]
        elif method.method_name == 'zuliu':
            length = randint(3, 10)
            while len(ball) < length:
                random_num = str(randint(0, 9))
                if random_num not in ball:
                    ball += random_num
            return [','.join(ball), len(list(combinations(ball, 3)))]

    def __random_115_series(self, method: Method) -> [str, int]:
        min_length_pool = {'xuanyi': 1, 'xuaner': 2, 'xuansan': 3, 'xuansi': 4, 'xuanwu': 5,
                           'xuanliu': 6, 'xuanqi': 7, 'xuanba': 8, 'quwei': 1}
        min_length = min_length_pool[method.group_name]
        ball_pool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # 通用的號碼池
        balls = []  # 最後的投注內容
        delimiter = ','  # 通用分隔符

        if method.set_name == 'dingweidan':  # 定位膽單獨處理
            bet_amount = 0
            selected = []
            for _ in range(0, 5):  # 運行N次
                ball = []
                if _ == 4 and bet_amount == 0:  # 連續4次0的狀況
                    target_length = randint(1, len(ball_pool))
                else:
                    target_length = randint(0, len(ball_pool))
                if target_length == 0:
                    balls.append('-')
                    continue
                while len(ball) < target_length:
                    random_num = str(ball_pool[randint(0, len(ball_pool) - 1)]).zfill(2)
                    ball.append(random_num)
                balls.append(' '.join(ball))
                bet_amount += len(ball)
            return [','.join(balls), bet_amount]

        elif method.method_name == 'zhixuanfushi':  # 直選複式
            if method.method_name == 'dantuo' or method.set_name == 'qianerzhixuan':  # 膽拖 / 前二組選
                digits = 2  # 位數數量 (01,02)
            else:
                digits = 3  # 位數數量 (01,02,03)
            bet_amount = 1
            selected = []
            for index in range(1, digits + 1):  # 運行N次
                ball = []
                target_length = randint(1, len(ball_pool) - len(selected) - digits + index)
                while len(ball) < target_length:
                    random_num = str(ball_pool[randint(0, len(ball_pool) - 1)]).zfill(2)
                    if random_num not in selected:
                        selected.append(random_num)
                        ball.append(random_num)
                balls.append(' '.join(ball))
                bet_amount *= len(ball)
            final_ball = ','.join(balls)
            for _ in range(0, 5 - min_length):
                final_ball += ',-'
            return [final_ball, bet_amount]

        elif method.method_name in ['dantuo', 'renxuandantuo', 'zuxuandantuo']:  # 處理擔拖
            bet_amount = 1
            selected = []
            for index in range(0, 2):  # 運行2次
                ball = []
                if index == 0:
                    target_length = randint(1, min_length - 1)
                else:
                    target_length = randint(min_length - len(balls[0]), len(ball_pool) - len(selected))
                while len(ball) < target_length:
                    random_num = str(ball_pool[randint(0, len(ball_pool) - 1)]).zfill(2)
                    if random_num not in selected:
                        selected.append(random_num)
                        ball.append(random_num)
                balls.append(ball)  # balls = [['01','02','03'], ['05','06','07']]
                bet_amount *= len(ball)
            # 擔碼必選, 因此組合數為: "第二碼"中挑選(最小選號數 - 擔碼數量)個號碼的"組合數"
            bet_amount = len(list(combinations(balls[1], min_length - len(balls[0]))))
            # 為了符合擔拖格式調整balls[0]內容
            balls[0] = '[胆' + ','.join(balls[0]) + ']'
            balls[1] = ','.join(balls[1])
            return ['  '.join(balls), bet_amount]  # 處理擔拖

        elif method.set_name == 'normal':  # 趣味 猜中位 定單雙
            if method.method_name == 'caizhongwei':
                ball_pool = [3, 4, 5, 6, 7, 8, 9]  # 趣味用的號碼池
            else:  # method.method_name =   = 'dingdanshuang':
                ball_pool = ['5单0双', '4单1双', '3单2双', '2单3双', '1单4双', '0单5双']  # 定單雙用的號碼池
                delimiter = '|'  # 定單雙用分隔符
        elif method.set_name == 'normal' or method.method_name in ['caizhongwei', 'fushi']:  # 前三一碼/前一不定
            length = randint(min_length, len(ball_pool) - 1)
            while len(balls) < length:
                random_num = str(ball_pool[randint(0, len(ball_pool) - 1)]).zfill(2)
                if random_num not in balls:
                    balls.append(random_num)
            return [delimiter.join(balls), len(list(combinations(balls, min_length)))]

        elif method.method_name in ['danshi', 'renxuandanshi', 'zhixuandanshi', 'zuxuandanshi']:  # 處理單式
            total_comb = len(list(combinations(ball_pool, min_length)))
            target_amount = randint(1, total_comb)  # 單式長度範圍1~全餐
            while len(balls) < target_amount:
                ball = []
                while len(ball) < min_length:
                    random_num = str(ball_pool[randint(0, len(ball_pool) - 1)]).zfill(2)
                    if random_num not in ball:
                        ball.append(random_num)
                ball = ' '.join(sorted(ball))
                if ball not in balls:
                    balls.append(ball)
            return [','.join(balls), len(balls)]
        print(f'{method.title} not done yet.')
        return None

    def __random_klc_series(self, method: Method) -> [str, int]:
        return None

# ff = FF4GameContentGenerator(lottery_id=None, env_id=None, user_name=None)
#
# ff.get_all_ignore_games()
