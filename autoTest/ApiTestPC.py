import threading
import unittest
from time import sleep

from bs4 import BeautifulSoup
import hashlib
import json
import requests
import time

from utils import Config, Logger, Connection
from utils.Config import LotteryData, func_time
from utils.Connection import select_issue, select_red_id, select_red_bal

logger = Logger.create_logger(r"\AutoTest", 'auto_test_pc')
COOKIE = None  # 以全域變數儲存，以利在各測試間共用
MUL = None
MUL_ = None


class ApiTestPC(unittest.TestCase):
    """PC接口測試"""
    envConfig = None
    user = None
    red_type = None
    money_unit = None
    user_agent = None
    header = {  # 預設Header格式
        'User-Agent': Config.UserAgent.PC.value,
        'Content-Type': 'application/json; charset=UTF-8'
    }
    post_url = None
    en_url = None
    SESSION = requests.Session()
    third_list = ['gns', 'shaba', 'im', 'ky', 'lc', 'city']

    def setUp(self):
        logger.info(f'ApiTestPC setUp : {self._testMethodName}')

    def __init__(self, case, _env, _user, _red_type, _money_unit):
        super().__init__(case)
        global COOKIE
        self.envConfig = _env
        self.user = _user
        self.red_type = _red_type
        self.money_unit = _money_unit
        self.post_url = self.envConfig.get_post_url()
        self.en_url = self.envConfig.get_em_url()
        logger.info('ApiTestPC __init__.')
        if COOKIE:  # 若已有Cookie則加入Header
            self.header['Cookie'] = f'ANVOID={COOKIE}'
        elif case != 'test_PcLogin':
            self.fail('Cookie為空，停止測試！')

    def web_issue_code(self, lottery):  # 頁面產生  獎期用法,  取代DB連線問題
        now_time = int(time.time())
        r = self.SESSION.get(self.en_url + f'/gameBet/{lottery}/lastNumber?_={now_time}', headers=self.header)
        try:
            return r.json()['issueCode']
        except:
            pass
        if lottery == 'lhc':
            pass

    def plan_num(self, evn, lottery, plan_len):  # 追號生成
        plan_ = []  # 存放 多少 長度追號的 list
        issue = select_issue(Connection.get_oracle_conn(evn), LotteryData.lottery_dict[lottery][1])
        for i in range(plan_len):
            plan_.append({"number": issue.get('issueName')[i], "issueCode": issue.get('issue')[i], "multiple": 1})
        return plan_

    def ball_type(self, test):  # 對應完法,產生對應最大倍數和 投注完法
        ball = []
        global MUL
        if test == 'wuxing':
            ball = [str(Config.random_mul(9)) for i in range(5)]  # 五星都是數值
            MUL = Config.random_mul(2)
        elif test == 'sixing':
            ball = ['-' if i == 0 else str(Config.random_mul(9)) for i in range(5)]  # 第一個為-
            MUL = Config.random_mul(22)
        elif test == 'housan':
            ball = ['-' if i in [0, 1] else str(Config.random_mul(9)) for i in range(5)]  # 第1和2為-
            MUL = Config.random_mul(222)
        elif test == 'qiansan':
            ball = ['-' if i in [3, 4] else str(Config.random_mul(9)) for i in range(5)]  # 第4和5為-
            MUL = Config.random_mul(222)
        elif test == 'zhongsan':
            ball = ['-' if i in [0, 4] else str(Config.random_mul(9)) for i in range(5)]  # 第2,3,4為-
            MUL = Config.random_mul(222)
        elif test == 'houer':
            ball = ['-' if i in [0, 1, 2] else str(Config.random_mul(9)) for i in range(5)]  # 第1,2,3為-
            MUL = Config.random_mul(2222)
        elif test == 'qianer':
            ball = ['-' if i in [2, 3, 4] else str(Config.random_mul(9)) for i in range(5)]  # 第3,4,5為-
            MUL = Config.random_mul(2222)
        elif test == 'yixing':  # 五個號碼,只有一個隨機數值
            ran = Config.random_mul(4)
            ball = ['-' if i != ran else str(Config.random_mul(9)) for i in range(5)]
            MUL = Config.random_mul(2222)
        else:
            MUL = Config.random_mul(1)
        a = (",".join(ball))
        return a

    def game_type(self, lottery):
        # test___ = play_type()

        game_group = {'wuxing': u'五星', 'sixing': u'四星', 'qiansan': u'前三', 'housan': u'後三',
                      'zhongsan': u'中三', 'qianer': u'前二', 'houer': u'後二', 'xuanqi': u'選ㄧ', 'sanbutonghao': u'三不同號',
                      'santonghaotongxuan': u'三同號通選', 'guanya': u'冠亞', 'biaozhuntouzhu': u'標準玩法', 'zhengma': u'正碼',
                      'p3sanxing': u'P3三星', 'renxuan': u'任選'}

        game_set = {
            'zhixuan': u'直選', 'renxuanqizhongwu': u'任選一中一', 'biaozhun': u'標準', 'zuxuan': u'組選'
            , 'pingma': u'平碼', 'putongwanfa': u'普通玩法'}
        game_method = {
            'fushi': u'複式', 'zhixuanfushi': u'直選複式', 'zhixuanliuma': u'直選六碼',
            'renxuan7': u'任選7'
        }

        group_ = Config.play_type()  # 建立 個隨機的goup玩法 ex: wuxing,目前先給時彩系列使用
        # set_ = game_set.keys()[0]#ex: zhixuan
        # method_ = game_method.keys()[0]# ex: fushi
        play_ = ''

        # play_ = ''#除了 不是 lottery_sh 裡的彩種

        lottery_ball = self.ball_type(group_)  # 組出什麼玩法 的 投注內容 ,目前只有給時彩系列用

        test_dicts = {
            0: [f"{group_}.zhixuan.fushi", lottery_ball],
            1: ["qianer.zhixuan.zhixuanfushi", '3,6,-'],
            2: ["xuanqi.renxuanqizhongwu.fushi", "01,02,05,06,08,09,10"],
            3: ["sanbutonghao.biaozhun.biaozhuntouzhu", "1,2,6"],
            4: ["santonghaotongxuan.santonghaotongxuan.santonghaotongxuan", "111 222 333 444 555 666"],
            5: ["guanya.zhixuan.fushi", "09 10,10,-,-,-,-,-,-,-,-"],
            6: ['qianer.zuxuan.fushi', '4,8'],
            7: ["biaozhuntouzhu.biaozhun.fushi", "04,08,13,19,24,27+09", ],
            8: ["zhengma.pingma.zhixuanliuma", "04"],
            9: ["p3sanxing.zhixuan.p3fushi", "9,1,0", ],
            10: ["renxuan.putongwanfa.renxuan7", "09,13,16,30,57,59,71"],
            11: ["chungtienpao.chungtienpao.chungtienpao", "1.01"]  # 快開
        }

        if lottery in LotteryData.lottery_sh:  # 時彩系列
            num = 0
            play_ = f'玩法名稱: {game_group[group_]}.{game_set["zhixuan"]}.{game_method["fushi"]}'

        elif lottery in LotteryData.lottery_3d:
            num = 1
            play_ = f'玩法名稱: {game_group["qianer"]}.{game_set["zhixuan"]}.{game_method["zhixuanfushi"]}'
        elif lottery in LotteryData.lottery_noRed:
            if lottery in ['p5', 'np3']:
                num = 9
                play_ = f'玩法名稱: {game_group["p3sanxing"]}.{game_set["zhixuan"]}.{game_method["fushi"]}'
            else:
                num = 1
                play_ = f'玩法名稱: {game_group["qianer"]}.{game_set["zhixuan"]}.{game_method["zhixuanfushi"]}'
        elif lottery in LotteryData.lottery_115:
            num = 2
            play_ = f'玩法名稱: {game_group["xuanqi"]}.{game_set["renxuanqizhongwu"]}.{game_method["fushi"]}'
        elif lottery in LotteryData.lottery_k3:
            num = 3
            play_ = f'玩法名稱: {game_group["sanbutonghao"]}.{game_set["biaozhun"]}'
        elif lottery in LotteryData.lottery_sb:
            num = 4
            play_ = f'玩法名稱: {game_group["santonghaotongxuan"]}'
        elif lottery in LotteryData.lottery_fun:
            num = 5
            play_ = f'玩法名稱: {game_group["guanya"]}.{game_set["zhixuan"]}.{game_method["fushi"]}'
        elif lottery == 'shssl':
            num = 6
            play_ = f'玩法名稱: {game_group["qianer"]}.{game_set["zuxuan"]}.{game_method["fushi"]}'
        elif lottery == 'ssq':
            num = 7
            play_ = f'玩法名稱: {game_group["biaozhuntouzhu"]}.{game_set["biaozhun"]}.{game_method["fushi"]}'
        elif lottery == 'lhc':
            num = 8
            play_ = f'玩法名稱: {game_group["zhengma"]}.{game_set["pingma"]}.{game_method["zhixuanliuma"]}'
        elif lottery == 'p5':
            num = 9
            play_ = f'玩法名稱: {game_group["p3sanxing"]}.{game_set["zhixuan"]}.{game_method["fushi"]}'
        elif lottery == 'bjkl8':
            num = 10
            play_ = f'玩法名稱: {game_group["renxuan"]}.{game_set["putongwanfa"]}.{game_method["renxuan7"]}'
        else:
            num = 11
            # play_ = u'玩法名稱: 沖天炮
        return test_dicts[num][0], test_dicts[num][1], play_

    def req_post_submit(self, account, lottery, data_, money_unit, award_mode, play_):
        logger.info(
            f'account: {account}, lottery: {lottery}, data_: {data_}, moneyunit: {money_unit}, awardmode: {award_mode}, '
            f'play_ {play_}')
        global MUL_

        award_mode_dict = {0: u"非一般模式", 1: u"非高獎金模式", 2: u"高獎金"}
        money_dict = {1: u"元模式", 0.1: u"分模式", 0.01: u"角模式"}
        r = self.SESSION.post(self.en_url + '/gameBet/' + lottery + '/submit',
                              data=json.dumps(data_), headers=self.header)
        try:
            msg = (r.json()['msg'])
            mode = money_dict[money_unit]
            mode1 = award_mode_dict[award_mode]
            project_id = (r.json()['data']['projectId'])  # 訂單號
            submit_amount = (r.json()['data']['totalprice'])  # 投注金額
            # submit_mul = f"投注倍數: {m}"  #隨機倍數
            lottery_name = f'投注彩種: {LotteryData.lottery_dict[lottery][0]}'

            if r.json()['isSuccess'] == 0:  #
                content_ = f'{lottery_name} \n {MUL_} "\n" {play_} "\n" {msg} "\n"'

                if r.json()['msg'] == u'存在封锁变价':  # 有可能封鎖變價,先跳過   ()
                    print(u'存在封锁变价')
                elif r.json()['msg'] == u'您的投注内容 超出倍数限制，请调整！':
                    print(u'倍數超出了唷,下次再來')
                elif r.json()['msg'] == u'方案提交失败，请检查网络并重新提交！':
                    print(r.json()['msg'])
                else:  # 系統內部錯誤
                    print(r.json()['msg'])
            else:  # 投注成功
                if self.red_type == 'yes':
                    content_ = f'{lottery_name} \n' \
                               f' 投注單號: {project_id} \n' \
                               f' {MUL_}\n' \
                               f' {play_}\n' \
                               f' 投注金額: {str(float(submit_amount * 0.0001))} \n' \
                               f' 紅包金額: 2 {mode}/{mode1} \n' \
                               f' {msg} \n'
                else:
                    content_ = f'{lottery_name}\n' \
                               f' 投注單號: {project_id}\n' \
                               f' {MUL_}\n' \
                               f' {play_}\n' \
                               f'投注金額: {str(float(submit_amount * 0.0001))} \n' \
                               f' {mode}/{mode1} \n' \
                               f' {msg}\n'
        except ValueError:
            content_ = (f'{lottery} 投注失敗' + "\n")
        print(content_)

    def test_PCLotterySubmit(self, plan=1):  # 彩種投注
        """投注測試"""
        _money_unit = 1  # 初始元模式

        if self.red_type == 'yes':
            print('使用紅包投注')
        else:
            print('不使用紅包投注')
        while True:
            try:
                for i in LotteryData.lottery_dict.keys():
                    global MUL_  # 傳回 投注出去的組合訊息 req_post_submit 的 content裡
                    global MUL
                    ball_type_post = self.game_type(i)  # 找尋彩種後, 找到Mapping後的 玩法後內容

                    award_mode = 1

                    if self.money_unit == '1':  # 使用元模式
                        _money_unit = 1
                    elif self.money_unit == '2':  # 使用角模式
                        _money_unit = 0.1

                    if i == 'btcctp':
                        award_mode = 2
                        MUL = Config.random_mul(1)  # 不支援倍數,所以random參數為1
                    elif i == 'bjkl8':
                        MUL = Config.random_mul(5)  # 北京快樂8
                    elif i == 'p5':
                        MUL = Config.random_mul(5)

                    elif i in ['btcffc', 'xyft']:
                        award_mode = 2
                    elif i in LotteryData.lottery_sb:  # 骰寶只支援  元模式
                        _money_unit = 1

                    MUL_ = f'選擇倍數: {MUL}'
                    amount = 2 * MUL * _money_unit

                    # 從DB抓取最新獎期.[1]為 99101類型select_issueselect_issue

                    if plan == 1:  # 一般投住

                        # Joy188Test.select_issue(Joy188Test.get_conn(1),lottery_dict[i][1])
                        # 從DB抓取最新獎期.[1]為 99101類型
                        # print(issueName,issue)
                        issuecode = self.web_issue_code(i)
                        plan_ = [{"number": '123', "issueCode": issuecode, "multiple": 1}]
                        print(u'一般投住')
                        isTrace = 0
                        traceWinStop = 0
                        traceStopValue = -1
                    else:  # 追號
                        plan_ = self.plan_num(self.envConfig.get_env_id(), i, Config.random_mul(30))  # 隨機生成 50期內的比數
                        print(f'追號, 期數:{len(plan_)}')
                        isTrace = 1
                        traceWinStop = 1
                        traceStopValue = 1

                    len_ = len(plan_)  # 一般投注, 長度為1, 追號長度為
                    # print(game_type)

                    post_data = {"gameType": i, "isTrace": isTrace, "traceWinStop": traceWinStop,
                                 "traceStopValue": traceWinStop,
                                 "balls": [{"id": 1, "ball": ball_type_post[1], "type": ball_type_post[0],
                                            "moneyunit": _money_unit, "multiple": MUL, "awardMode": award_mode,
                                            "num": 1}], "orders": plan_, "amount": len_ * amount}  # 不使用紅包

                    post_data_lhc = {"balls": [{"id": 1, "moneyunit": _money_unit, "multiple": 1, "num": 1,
                                                "type": ball_type_post[0], "amount": amount, "lotterys": "13",
                                                "ball": ball_type_post[1], "odds": "7.5"}],
                                     "isTrace": 0, "orders": plan_,
                                     "amount": amount, "awardGroupId": 202}

                    post_data_sb = {"gameType": i, "isTrace": 0, "multiple": 1, "trace": 1,
                                    "amount": amount,
                                    "balls": [{"ball": ball_type_post[1],
                                               "id": 11, "moneyunit": _money_unit, "multiple": 1, "amount": amount,
                                               "num": 1,
                                               "type": ball_type_post[0]}],
                                    "orders": plan_}

                    if i in 'lhc':
                        self.req_post_submit(self.user, 'lhc', post_data_lhc, _money_unit, award_mode,
                                             ball_type_post[2])

                    elif i in LotteryData.lottery_sb:
                        self.req_post_submit(self.user, i, post_data_sb, _money_unit, award_mode, ball_type_post[2])
                    else:
                        if self.red_type == 'yes':  # 紅包投注
                            post_data['redDiscountAmount'] = 2  # 增加紅包參數
                            self.req_post_submit(self.user, i, post_data, _money_unit, award_mode, ball_type_post[2])
                        else:
                            self.req_post_submit(self.user, i, post_data, _money_unit, award_mode, ball_type_post[2])
                red_bal = select_red_bal(Connection.get_oracle_conn(1), self.user)
                print(f'紅包餘額: {int(red_bal[0]) / 10000}')
                break
            except KeyError as e:
                print(u"輸入值有誤")
                break
            except IndexError as e:
                # print(e)
                break

    @func_time
    def test_PcLogin(self):
        """登入測試"""
        print("Enter test_PcLogin")
        global COOKIE
        self.en_url = self.envConfig.get_em_url()

        param = b'f4a30481422765de945833d10352ea18'

        self.header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        print("userAgent : " + self.user_agent)
        print("post_url : " + self.post_url)
        # while True:
        r = None
        try:
            postData = {
                "username": self.user,
                "password": self.md(str.encode(self.envConfig.get_password()), param),
                "param": param
            }
            logger.info(f'postData = {postData}')
            logger.Debug(f'header = {self.header.items()}')
            r = self.SESSION.post(self.post_url + '/login/login', data=postData, headers=self.header)
            logger.info(f'response = {r.json()}')
            COOKIE = r.cookies.get_dict()['ANVOID']  # 獲得登入的cookies 字典
            logger.Debug(f'r.cookies.get_dict() = {r.cookies.get_dict()}')
            self.header['Cookie'] = f'ANVOID={COOKIE}'
            t = time.strftime('%Y%m%d %H:%M:%S')
            # msg = (f'登錄帳號: {i},登入身分: {account_[i]}' + u',現在時間:' + t + r.text)
            print(f'登錄帳號: {self.user}' + u',現在時間:' + t)
            self.header['Content-Type'] = 'application/json; charset=UTF-8'  # 只有Login使用form, 改回Json
        except IOError:
            self.fail(f'測試結果：登入失敗.\n接口回傳：{r.json()}')

    def md(self, _password, _param):
        m = hashlib.md5()
        m.update(_password)
        sr = m.hexdigest()
        for i in range(3):
            sr = hashlib.md5(sr.encode()).hexdigest()
        rx = hashlib.md5(sr.encode() + _param).hexdigest()
        return rx

    def session_post(self, account, third, url, post_data):  # 共用 session post方式 (Pc)
        try:
            r = self.SESSION.post(self.post_url + url, headers=self.header, data=json.dumps(post_data))

            if 'Balance' in url:
                print(f'{third}, 餘額: {r.json()["balance"]}')
            elif 'transfer' in url:
                if r.json()['status']:
                    print(f'帳號 kerrthird001 轉入 {third} ,金額:1, 進行中')
                else:
                    print(f'{third} 轉帳失敗')
            elif 'getuserbal' in url:
                print(f'4.0 餘額: {r.json()["data"]}')
            # print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
            # print('result: '+statu_code+"\n"+'---------------------')

        except requests.exceptions.ConnectionError:
            print(u'連線有問題,請稍等')

    def session_get(self, user, url_, url):  # 共用 session get方式
        try:
            r = self.SESSION.get(url_ + url, headers=self.header)
            html = BeautifulSoup(r.text, 'lxml')  # type為 bs4類型
            title = str(html.title)
            statu_code = str(r.status_code)  # int 轉  str

            print(title)  # 強制便 unicode, 不燃顯示在html報告  會有誤
            print(url)
            print('result: ' + statu_code + "\n" + '---------------------')

        except requests.exceptions.ConnectionError:
            print(u'連線有問題,請稍等')

    @func_time
    def test_PcThirdHome(self):  # 登入第三方頁面,創立帳號
        """第三方頁面測試"""
        threads = []
        third_url = ['gns', 'ag', 'sport', 'shaba', 'lc', 'im', 'ky', 'fhx', 'bc', 'fhll', 'bc']

        for i in third_url:
            if i == 'shaba':  # 沙巴特立
                url = '/shaba/home?act=esports'
            elif i == 'fhll':  # 真人特例
                fhll_dict = {'77104': u'樂利時彩', '77101': u'樂利1.5分彩',
                             '77103': u'樂利六合彩', '77102': u'樂利快3'}
                for i in fhll_dict.keys():
                    url = f'/fhll/home/{i}'
                    # print(url)
                    # print(fhll_dict[i])#列印 中文(因為fhll的title都是一樣)
                    t = threading.Thread(target=self.session_get, args=(self.user, self.post_url, url))
                    threads.append(t)
                    # Joy188Test.session_get(user,post_url,url)# get方法
                break  # 不再跑到 下面 session_get 的func
            elif i == 'fhx':
                url = '/fhx/index'
            else:
                url = f'/{i}/home'
            # print(url)
            t = threading.Thread(target=self.session_get, args=(self.user, self.post_url, url))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()

    @func_time
    def test_PcFFHome(self):
        """4.0頁面測試"""
        threads = []
        url_188 = ['/fund', '/bet/fuddetail', '/withdraw', '/transfer', '/index/activityMall',
                   '/ad/noticeList?noticeLevel=2', '/frontCheckIn/checkInIndex', '/frontScoreMall/pointsMall']
        em_188 = ['/gameUserCenter/queryOrdersEnter', '/gameUserCenter/queryPlans']
        for i in url_188:
            if i in ['/frontCheckIn/checkInIndex', '/frontScoreMall/pointsMall']:
                self.session_get(self.user, self.post_url, i)
            else:
                t = threading.Thread(target=self.session_get, args=(self.user, self.post_url, i))
                threads.append(t)
            # Joy188Test.session_get(user,post_url,i)
        for i in em_188:
            # Joy188Test.session_get(user,em_url,i)
            t = threading.Thread(target=self.session_get, args=(self.user, self.en_url, i))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()

    @func_time
    def test_PcChart(self):
        """走勢圖測試"""
        ssh_url = ['cqssc', 'hljssc', 'tjssc', 'xjssc', 'llssc', 'txffc', 'btcffc', 'fhjlssc',
                   'jlffc', 'slmmc', 'sd115', 'll115', 'gd115', 'jx115']
        k3_url = ['jsk3', 'ahk3', 'jsdice', 'jldice1', 'jldice2']
        low_url = ['d3', 'v3d']
        fun_url = ['xyft', 'pk10']
        for i in ssh_url:
            self.session_get(self.user, self.en_url, f'/game/chart/{i}/Wuxing')
        for i in k3_url:
            self.session_get(self.user, self.en_url, f'/game/chart/{i}/chart')
        for i in low_url:
            self.session_get(self.user, self.en_url, f'/game/chart/{i}/Qiansan')
        for i in fun_url:
            self.session_get(self.user, self.en_url, f'/game/chart/{i}/CaipaiweiQianfushi')
        self.session_get(self.user, self.en_url, '/game/chart/p5/p5chart')
        self.session_get(self.user, self.en_url, '/game/chart/ssq/ssq_basic')
        self.session_get(self.user, self.en_url, '/game/chart/kl8/Quwei')

    @func_time
    def test_PcThirdBalance(self):
        """4.0/第三方餘額"""
        threads = []

        print(f'帳號: {self.user}')
        for third in self.third_list:
            if third == 'gns':
                third_url = '/gns/gnsBalance'
            else:
                third_url = f'/{third}/thirdlyBalance'
                # r = session.post(post_url+third_url,headers=self.header)
            # print(f'{third}, 餘額: {r.json()["balance"]}')
            t = threading.Thread(target=self.session_post, args=(self.user, third, third_url, ''))
            threads.append(t)
        t = threading.Thread(target=self.session_post, args=(self.user, '', '/index/getuserbal', ''))
        threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        '''
        r = session.post(post_url+'/index/getuserbal',headers=self.header)
        print('4.0 餘額: %s'%r.json()['data'])
        '''

    @func_time
    def test_PcTransferin(self):  # 第三方轉入
        """第三方轉入"""
        post_data = {"amount": 1}
        status_dict = {}  # 存放 轉帳的 狀態
        errors = {}
        for third in self.third_list:
            if third == 'gns':
                third_url = '/gns/transferToGns'
            else:
                third_url = f'/{third}/transferToThirdly'
            logger.info(f'header = {self.header.items()}')
            r = self.SESSION.post(self.post_url + third_url, data=json.dumps(post_data), headers=self.header)
            logger.info(f'r.json() = {r.json()}')

            # 判斷轉帳的 狀態
            if r.json()['status']:
                print(f'帳號 {self.user} 轉入 {third} ,金額:1, 進行中')
            else:
                print(f'{third} 轉帳失敗')  # 列出錯誤訊息 ,
            status_dict[third] = r.json()['status']  # 存放 各第三方的轉帳狀態

        for third in status_dict.keys():
            if status_dict[third]:  # 判斷轉帳的狀態, 才去要 單號
                tran_result = Connection.thirdly_tran(
                    Connection.get_mysql_conn(evn=self.envConfig.get_env_id(), third=third), tran_type=0,
                    third=third,
                    user=self.user)  # tran_type 0為轉轉入
                count = 0
                while tran_result[1] != '2' and count != 10:  # 確認轉帳狀態,  2為成功 ,最多做10次
                    tran_result = Connection.thirdly_tran(
                        Connection.get_mysql_conn(evn=self.envConfig.get_env_id(), third=third),
                        tran_type=0,
                        third=third,
                        user=self.user)  #
                    sleep(1.5)
                    count += 1
                    if count == 15:
                        errors[third] = tran_result
                        print('轉帳狀態失敗')  # 如果跑道9次  需確認
                        break
                else:
                    pass
        for key, value in errors.items():
            print(f'三方: {key} 轉帳失敗. 接口返回: {value}')
        self.test_PcThirdBalance()

    @func_time
    def test_PcTransferout(self):  # 第三方轉回
        """第三方轉出"""
        status_dict = {}  # 存放 第三方狀態
        post_data = {"amount": 1}
        errors = {}
        for third in self.third_list:
            url = f'/{third}/transferToFF'

            r = self.SESSION.post(self.post_url + url, data=json.dumps(post_data), headers=self.header)
            if r.json()['status']:
                print(f'帳號 {self.user}, {third} 轉回4.0 ,金額:1, 進行中')
            else:
                print(third + r.json()['errorMsg'])
                print('轉帳接口失敗')
            status_dict[third] = r.json()['status']

        for third in status_dict.keys():
            if status_dict[third]:
                tran_result = Connection.thirdly_tran(
                    Connection.get_mysql_conn(evn=self.envConfig.get_env_id(), third=third), tran_type=1,
                    third=third,
                    user=self.user)  # tran_type 1 是 轉出
                count = 0
                while tran_result[1] != '2' and count != 10:  # 確認轉帳狀態,  2為成功 ,最多做10次
                    tran_result = Connection.thirdly_tran(
                        Connection.get_mysql_conn(evn=self.envConfig.get_env_id(), third=third),
                        tran_type=0,
                        third=third,
                        user=self.user)
                    sleep(1)
                    count += 1
                    if tran_result[1] == '2':
                        print(f'狀態成功. {third} ,sn 單號: {tran_result[0]}')
                        break
                    if count == 9:
                        errors[third] = tran_result
                        print('轉帳狀態失敗')  # 如果跑道9次  需確認
                        break
            else:
                pass
        for key, value in errors.items():
            print(f'三方: {key} 轉帳失敗. 接口返回: {value}')
        self.test_PcThirdBalance()

    @staticmethod
    def admin_login(env_config):
        global ADMIN_COOKIE, ADMIN_URL, HEADER, COOKIES
        ADMIN_COOKIE = {}
        HEADER = {
            'User-Agent': Config.UserAgent.PC.value,
            'Content-Type': 'application/x-www-form-urlencoded'}
        admin_data = env_config.get_admin_data()
        ADMIN_URL = env_config.get_admin_url()
        session = requests.Session()
        r = session.post(ADMIN_URL + '/admin/login/login', data=admin_data, headers=HEADER)
        COOKIES = r.cookies.get_dict()  # 獲得登入的cookies 字典
        ADMIN_COOKIE['admin_cookie'] = COOKIES['ANVOAID']
        print(ADMIN_COOKIE)
        print(f'登入後台 , 環境: {ADMIN_URL}')
        print(r.text)
        return COOKIES

    def test_redEnvelope(self):  # 紅包加壁,審核用
        user = self.user
        print(f'用戶: {user}')
        red_list = []  # 放交易訂單號id

        try:
            red_bal = select_red_bal(Connection.get_oracle_conn(self.envConfig.get_env_id()), user)
            print(f'紅包餘額: {int(red_bal[0]) / 10000}')
        except IndexError:
            print('紅包餘額為0')
        self.admin_login(env_config=self.envConfig)  # 登入後台
        data = {"receives": user, "blockType": "2", "lotteryType": "1", "lotteryCodes": "",
                "amount": "100", "note": "test"}
        HEADER['Cookie'] = 'ANVOAID=' + ADMIN_COOKIE['admin_cookie']  # 存放後台cookie
        HEADER['Content-Type'] = 'application/json'
        r = self.SESSION.post(ADMIN_URL + '/redAdmin/redEnvelopeApply',  # 後台加紅包街口
                              data=json.dumps(data), headers=HEADER)
        if r.json()['status'] == 0:
            print('紅包加幣100')
        else:
            print('失敗')
        red_id = select_red_id(Connection.get_oracle_conn(self.envConfig.get_env_id()), user)  # 查詢教地訂單號,回傳審核data
        # print(red_id)
        red_list.append(f'{red_id[0]}')
        # print(red_list)
        data = {"ids": red_list, "status": 2}
        r = self.SESSION.post(ADMIN_URL + '/redAdmin/redEnvelopeConfirm',  # 後台審核街口
                              data=json.dumps(data), headers=HEADER)
        try:
            logger.info(f'r.json() : {r.json()}')
            if r.json()['status'] == 0:
                print('審核通過')
        except Exception as e:
            print(r.json()['errorMsg'])
            logger.error(e)
        red_bal = select_red_bal(Connection.get_oracle_conn(self.envConfig.get_env_id()), user)
        print(f'紅包餘額: {int(red_bal[0] / 10000)}')

    def tearDown(self) -> None:
        pass


class ApiTestYFT(unittest.TestCase):
    """
    YFT API測試
    """

    def __init__(self, case):
        super().__init__(case)
        pass
