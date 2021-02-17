import threading
import unittest
from time import sleep

from bs4 import BeautifulSoup
import hashlib
import json
import requests
import time
import FF_Joy188

from utils import Config, Logger
from utils.Config import LotteryData, func_time

logger = Logger.create_logger(r"\AutoTest", 'auto_test_pc')
COOKIE = None  # 以全域變數儲存，以利在各測試間共用
MUL = None
MUL_ = None


class ApiTestPC(unittest.TestCase):
    """PC接口測試"""
    __slots__ = '_env_config', '_user', '_red_type', '_money_unit', '_award_mode', \
                '_header', '_post_url', '_en_url', '_third_list'
    SESSION = requests.Session()

    def setUp(self):
        global COOKIE
        logger.info(f'ApiTestPC setUp : {self._testMethodName}')
        if COOKIE:  # 若已有Cookie則加入Header
            logger.info('已有Cookie')
            self._header['Cookie'] = f'ANVOID={COOKIE}'

    def __init__(self, case, env_config, _user, red_type: bool, money_unit: float, award_mode: int, oracle, mysql, lottery_name):
        """
        PC測試初始化
        :param case: 測試案例
        :param env_config:
        :param _user: 用戶名
        :param red_type: 紅包使用與否
        :param money_unit: 投注單位
        :param award_mode: 獎金模式
        :param oracle: 已創建的oracle連線
        :param mysql: 已創建的mysql連線
        :param lottery_name: 彩種名稱
        """

        super().__init__(case)
        global COOKIE
        self._env_config = env_config
        self._user = _user
        self._red_type = red_type
        self._money_unit = money_unit
        self._award_mode = 1 if award_mode == 0 else award_mode
        self._post_url = self._env_config.get_post_url()
        self._en_url = self._env_config.get_em_url()
        self._header = {  # 預設Header格式
            'User-Agent': Config.UserAgent.PC.value,
            'Content-Type': 'application/json; charset=UTF-8'
        }
        self._admin_header = {  # 預設Header格式
            'User-Agent': Config.UserAgent.PC.value,
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ANVOAID=' + env_config.get_admin_cookie()
        }
        self._third_list = ['gns', 'shaba', 'im', 'ky', 'lc', 'city']
        self._conn_mysql = mysql
        self._conn_oracle = oracle
        self.SESSION.proxies = {"http": "http://127.0.0.1:8888"}
        if COOKIE:  # 若已有Cookie則加入Header
            logger.info('已有Cookie')
            self._header['Cookie'] = f'ANVOID={COOKIE}'
        self.lottery_name = lottery_name

    def web_issue_code(self, lottery):  # 頁面產生  獎期用法,  取代DB連線問題
        now_time = int(time.time())
        r = self.SESSION.get(self._en_url + f'/gameBet/{lottery}/dynamicConfig?_={now_time}', headers=self._header)
        return r.json()['data']['issueCode']

    def plan_num(self, evn, lottery, plan_len):  # 追號生成
        plan_ = []  # 存放 多少 長度追號的 list
        issue = self._conn_oracle.select_issue(LotteryData.lottery_dict[lottery][1])
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
        elif lottery in LotteryData.lottery_no_red:
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


    def test_PcPlan(self):
        """
        追號測試
        :return: None
        """
        failed_test = []
        for lottery in self.lottery_name:
            trace_issue_num = 10  # 預設追號期數
            if lottery == 'btcctp':  # 若彩種不支援追號，提前跳出
                print(f'彩種: {LotteryData.lottery_dict[lottery][0]} 不支援追號，跳過測試')
                continue

            error_message = FF_Joy188.FF_().pc_submit(lottery=lottery, envs=self._env_config.get_env_id(),
                                                      account=self._user, em_url=self._env_config.get_em_url(),
                                                      header=self._header, award_mode=self._award_mode,
                                                      trace_issue_num=trace_issue_num, win_stop=True,
                                                      red_mode=self._red_type, money_unit=self._money_unit)
            if error_message: failed_test.append(error_message)
        if failed_test:
            is_error = False
            for error in failed_test:
                if error[0] != '六合彩':  # 六合彩無法投注避免拋錯
                    print(error)
                    is_error = True
            if is_error:
                self.fail('部分彩種投注失敗')

    def test_PCLotterySubmit(self):  # 彩種投注
        failed_test = []
        for lottery in self.lottery_name:
            trace_issue_num = 0  # 投注一期
            error_message = FF_Joy188.FF_().pc_submit(lottery=lottery, envs=self._env_config.get_env_id(),
                                                      account=self._user, em_url=self._env_config.get_em_url(),
                                                      header=self._header, award_mode=self._award_mode,
                                                      trace_issue_num=trace_issue_num, win_stop=False,
                                                      red_mode=self._red_type, money_unit=self._money_unit)
            if error_message:
                failed_test.append(error_message)
        if failed_test:
            is_error = False
            for error in failed_test:
                if error[0] != '六合彩':  # 六合彩無法投注避免拋錯
                    print(error)
                    is_error = True
            if is_error:
                self.fail('部分彩種投注失敗')

    @func_time
    def test_PcLogin(self):
        """登入測試"""
        print("Enter test_PcLogin")
        global COOKIE
        self._en_url = self._env_config.get_em_url()

        param = b'f4a30481422765de945833d10352ea18'

        self._header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        print("post_url : " + self._post_url)
        # while True:
        r = None
        try:
            postData = {
                "username": self._user,
                "password": self.md(str.encode(self._env_config.get_password()), param),
                "param": param
            }
            logger.info(f'postData = {postData}')
            r = self.SESSION.post(self._post_url + '/login/login', data=postData, headers=self._header)
            if r.json()["errors"]:  # 失敗時應報錯
                self.fail(f'登入失敗.\n接口回傳：{r.json()}')
            COOKIE = r.cookies.get_dict()['ANVOID']  # 獲得登入的cookies 字典
            logger.info(f'Get login cookie : {COOKIE}')
            self._header['Cookie'] = f'ANVOID={COOKIE}'
            t = time.strftime('%Y%m%d %H:%M:%S')
            print(f'登錄帳號: {self._user}' + u',現在時間:' + t)
            self._header['Content-Type'] = 'application/json; charset=UTF-8'  # 只有Login使用form, 改回Json
            logger.info(f'登入成功.\n _header = {self._header}')
        except KeyError:
            self.fail(f'測試結果：登入失敗，無法解析回傳結果.\n接口回傳: {r.json()}')
        except Exception as e:
            self.fail(f'無法預期的錯誤.\n{e}')

    @staticmethod
    def md(_password, _param):
        m = hashlib.md5()
        m.update(_password)
        sr = m.hexdigest()
        for i in range(3):
            sr = hashlib.md5(sr.encode()).hexdigest()
        rx = hashlib.md5(sr.encode() + _param).hexdigest()
        return rx

    def session_post(self, account, third, url, post_data):  # 共用 session post方式 (Pc)
        try:
            r = self.SESSION.post(self._post_url + url, headers=self._header, data=json.dumps(post_data))

            if 'Balance' in url:
                print(f'{third}, 餘額: {r.json()["balance"]}')
            elif 'transfer' in url:
                if r.json()['status']:
                    print(f'帳號 kerrthird001 轉入 {third} ,金額:1, 狀態碼:{r.json()["status"]}')
                else:
                    print(f'{third} 轉帳失敗')
            elif 'getuserbal' in url:
                print(f'4.0 餘額: {r.json()["data"]}')
            # print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
            # print('result: '+statu_code+"\n"+'---------------------')

        except requests.exceptions.ConnectionError:
            print(f'{third} 轉帳失敗')
            print(u'連線有問題,請稍等')
        except Exception as e:
            print(f'{third} 轉帳失敗')
            from utils.TestTool import trace_log
            trace_log(e)

    def session_get(self, user, url_, url):  # 共用 session get方式
        try:
            r = self.SESSION.get(url_ + url, headers=self._header)
            html = BeautifulSoup(r.text, 'lxml')  # type為 bs4類型
            title = str(html.title)
            status_code = str(r.status_code)  # int 轉  str

            print(title)  # 強制便 unicode, 不燃顯示在html報告  會有誤
            print(url)
            print('result: ' + status_code + "\n" + '---------------------')

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
                    t = threading.Thread(target=self.session_get, args=(self._user, self._post_url, url))
                    threads.append(t)
                    # Joy188Test.session_get(user,post_url,url)# get方法
                break  # 不再跑到 下面 session_get 的func
            elif i == 'fhx':
                url = '/fhx/index'
            else:
                url = f'/{i}/home'
            # print(url)
            t = threading.Thread(target=self.session_get, args=(self._user, self._post_url, url))
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
                self.session_get(self._user, self._post_url, i)
            else:
                t = threading.Thread(target=self.session_get, args=(self._user, self._post_url, i))
                threads.append(t)
            # Joy188Test.session_get(user,post_url,i)
        for i in em_188:
            # Joy188Test.session_get(user,em_url,i)
            t = threading.Thread(target=self.session_get, args=(self._user, self._en_url, i))
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
            self.session_get(self._user, self._en_url, f'/game/chart/{i}/Wuxing')
        for i in k3_url:
            self.session_get(self._user, self._en_url, f'/game/chart/{i}/chart')
        for i in low_url:
            self.session_get(self._user, self._en_url, f'/game/chart/{i}/Qiansan')
        for i in fun_url:
            self.session_get(self._user, self._en_url, f'/game/chart/{i}/CaipaiweiQianfushi')
        self.session_get(self._user, self._en_url, '/game/chart/p5/p5chart')
        self.session_get(self._user, self._en_url, '/game/chart/ssq/ssq_basic')
        self.session_get(self._user, self._en_url, '/game/chart/kl8/Quwei')

    @func_time
    def test_PcThirdBalance(self):
        """4.0/第三方餘額"""
        threads = []
        print('------------------------------------------------------------------------')
        print(f'開始確認帳號: {self._user} 三方餘額')
        for third in self._third_list:
            if third == 'gns':
                third_url = '/gns/gnsBalance'
            else:
                third_url = f'/{third}/thirdlyBalance'
                # r = session.post(post_url+third_url,headers=self.header)
            # print(f'{third}, 餘額: {r.json()["balance"]}')
            t = threading.Thread(target=self.session_post, args=(self._user, third, third_url, ''))
            threads.append(t)
        t = threading.Thread(target=self.session_post, args=(self._user, '', '/index/getuserbal', ''))
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
        for third in self._third_list:
            if third == 'gns':
                third_url = '/gns/transferToGns'
            else:
                third_url = f'/{third}/transferToThirdly'
            r = self.SESSION.post(self._post_url + third_url, data=json.dumps(post_data), headers=self._header)
            logger.info(f'r.json() = {r.json()}')

            # 判斷轉帳的 狀態
            if r.json()['status']:
                print(f'帳號 {self._user} 轉入 {third} ,金額:1, 狀態碼:{r.json()["status"]}')
            else:
                errors[third] = r.json()
                print(f'{third} 轉帳失敗')  # 列出錯誤訊息 ,
            status_dict[third] = r.json()['status']  # 存放 各第三方的轉帳狀態

        logger.debug(f'status_dict = {status_dict.items()}')
        for third in status_dict.keys():
            if status_dict[third]:  # 判斷轉帳的狀態, 才去要 單號
                tran_result = ["", 0]  # 初始化
                count = 0
                while tran_result[1] != '2':  # 確認轉帳狀態,  2為成功 ,最多做10次
                    tran_result = self._conn_mysql.thirdly_tran(
                        tran_type=0,
                        third=third,
                        user=self._user
                    )
                    sleep(1.5)
                    count += 1
                    # print(f'驗證{third}中 : tran_result = {tran_result}')
                    if tran_result[1] == '2':
                        print(f'{third}: 轉帳成功 ,sn 單號: {tran_result[0]}')
                        break
                    if count == 15:
                        errors[third] = tran_result
                        # print(f'{third} : 轉帳狀態失敗')  # 如果跑道9次  需確認
                        break
            else:
                pass
        for key, value in errors.items():
            print(f'三方: {key} 轉帳失敗. 接口返回: {value}')

        self.test_PcThirdBalance()

        if errors:
            self.fail('部分轉帳失敗')

    @func_time
    def test_PcTransferout(self):  # 第三方轉回
        """第三方轉出"""
        status_dict = {}  # 存放 第三方狀態
        post_data = {"amount": 1}
        errors = {}
        for third in self._third_list:
            url = f'/{third}/transferToFF'
            try:
                r = self.SESSION.post(self._post_url + url, data=json.dumps(post_data), headers=self._header)
                if r.json()['status']:
                    print(f'帳號 {self._user}, {third} 轉回4.0 ,金額:1, 狀態碼:{r.json()["status"]}')
                else:
                    logger.error(f'轉帳接口失敗 : errors[{third}] = {r.json()}')
                    errors[third] = r.json()
                    print(f'{third} 轉帳接口失敗')
                status_dict[third] = r.json()['status']
            except Exception as e:
                print(f'{third} 轉帳接口失敗')
                from utils.TestTool import trace_log
                trace_log(e)
        logger.debug(f'status_dict = {status_dict.items()}')
        for third in status_dict.keys():
            if status_dict[third]:
                logger.debug(f'status_dict[{third}]:  # 判斷轉帳的狀態, 才去要 單號 = {status_dict[third]}')
                tran_result = ["", 0]
                count = 0
                while tran_result[1] != '2':  # 確認轉帳狀態,  2為成功 ,最多做10次
                    tran_result = self._conn_mysql.thirdly_tran(
                        tran_type=1,
                        third=third,
                        user=self._user)
                    sleep(2)
                    count += 1
                    # print(f'驗證{third}中 : tran_result = {tran_result}')
                    if tran_result[1] == '2':
                        logger.info(f'轉帳狀態成功 : [{third}] = {tran_result}')
                        print(f'狀態成功. {third} ,sn 單號: {tran_result[0]}')
                        break
                    if count == 15:
                        logger.error(f'轉帳狀態失敗 : errors[{third}] = {tran_result}')
                        errors[third] = tran_result
                        # print(f'{third} : 轉帳狀態失敗')  # 如果跑道9次  需確認
                        break
            else:
                pass
        for key, value in errors.items():
            print(f'三方: {key} 轉帳失敗. 接口返回: {value}')
        self.test_PcThirdBalance()
        if errors:
            self.fail('部分轉帳失敗')

    def test_redEnvelope(self):  # 紅包加壁,審核用
        user = self._user
        print(f'用戶: {user}')
        red_list = []  # 放交易訂單號id

        try:
            red_bal = self._conn_oracle.select_red_bal(user)
            print(f'紅包餘額: {int(red_bal[0]) / 10000}')
        except IndexError:
            print('紅包餘額為0')
        data = {"receives": user, "blockType": "2", "lotteryType": "1", "lotteryCodes": "",
                "amount": "100", "note": "test"}
        self._admin_header['Content-Type'] = 'application/json'
        r = self.SESSION.post(self._env_config.get_admin_url() + '/redAdmin/redEnvelopeApply',  # 後台加紅包街口
                              data=json.dumps(data), headers=self._admin_header)
        if r.json()['status'] == 0:
            print('紅包加幣100')
        else:
            print('失敗')
        red_id = self._conn_oracle.select_red_id(user)  # 查詢教地訂單號,回傳審核data
        # print(red_id)
        red_list.append(f'{red_id[0]}')
        # print(red_list)
        data = {"ids": red_list, "status": 2}
        r = self.SESSION.post(self._env_config.get_admin_url() + '/redAdmin/redEnvelopeConfirm',  # 後台審核街口
                              data=json.dumps(data), headers=self._admin_header)
        try:
            logger.info(f'r.json() : {r.json()}')
            if r.json()['status'] == 0:
                print('審核通過')
        except Exception as e:
            print(r.json()['errorMsg'])
            logger.error(e)
        red_bal = self._conn_oracle.select_red_bal(user)
        print(f'紅包餘額: {int(red_bal[0] / 10000)}')

    def tearDown(self) -> None:
        Config.test_cases_update(1)


class ApiTestPC_YFT(unittest.TestCase):
    """
    YFT API測試
    """
    _session = None
    _env_config = None
    _user = None
    _money_unit = None
    _award_mode = None
    _conn = None
    _header = {'User-Agent': Config.UserAgent.PC.value,
               'Content-Type': 'application/json;charset=UTF-8'}

    def setUp(self):
        logger.info(f'ApiTestPC setUp : {self._testMethodName}')
        self.login()
        logger.info(f'After login. header = {self._header}')

    def __init__(self, case, env_config, user, conn, money_unit=1, _award_mode=0):
        """
        YFT初始化
        :param case: List
        :param env_config: EnvConfig
        :param user: Str
        :param money_unit: 1 / 0.1 / 0.01
        :param _award_mode: 0=預設 / 1=一般 / 2=高獎金
        """
        super().__init__(case)
        logger.info(
            f'ApiTestPC_YFT __init__ : _env={env_config}, _user={user}, _money_unit={money_unit}, _award_mode={_award_mode}')
        self._env_config = env_config
        self._user = user
        self._money_unit = money_unit
        self._award_mode = _award_mode
        self._conn = conn
        if self._session is None:
            self._session = requests.Session()

    """Tools"""

    def login(self):
        _post_url = '/a/login/login'
        md = hashlib.md5()
        md.update(self._env_config.get_password().encode('utf-8'))
        request = f'{{"account": "{self._user}", "passwd": "{md.hexdigest()}", "timeZone": "GMT+8", "isWap": false, "online": false}} '
        logger.debug(f'request_body = {request}')
        response = self._session.post(url=self._env_config.get_post_url() + _post_url, data=request,
                                      headers=self._header)
        logger.debug(f'login_url = {self._env_config.get_post_url() + _post_url}')
        logger.debug(f'Login response = {response.content}')
        if response.cookies['JSESSIONID']:
            logger.info(f'Cookies = {response.cookies["JSESSIONID"]}')
            self._header['JSESSIONID'] = response.cookies['JSESSIONID']  # setCookie into header
        else:
            self.fail('登入失敗.')

    def admin_login(self):
        _cookies = self._session.get(url=self._env_config.get_admin_url(), headers=self._header).cookies.get_dict()
        logger.info(f'_loginPage={_cookies["sid"]}')
        _post_url = f'/leona/login;JSESSIONID={_cookies["sid"]}'
        _admin_user = ['admin', '1234qwer']
        md = hashlib.md5()
        md.update(_admin_user[1].encode('utf-8'))
        _content = f'username={_admin_user[0]}&password={md.hexdigest()}'
        self._session.post(url=self._env_config.get_admin_url() + _post_url, data=_content, header=self._header)

    def get_lottery_info(self, lottery_name):
        """
        取得彩種資訊（獎期等）
        :param lottery_name: 彩種英文ID
        :return: 返還獎期資訊內容
        """
        content = f'{{"lotteryType":"{lottery_name}","timeZone":"GMT+8","isWap":false,"online":false}}'
        logger.debug(f'get_lottery_info -----> {content}')

        response = self._session.post(url=self._env_config.get_post_url() + '/a/lottery/init', data=content,
                                      headers=self._header)
        logger.debug(f'get_lottery_info <----- {response.json()}')
        return response.json()['content']

    def bet_yft(self, lottery_name, games, is_trace=False, stop_on_win=True):
        """
        YFT發起投注
        :param games: 投注玩法清單，可取自BetContent_yft.py
        :param lottery_name: 彩種英文ID
        :param is_trace: 追號與否，影響投注內容需替換的參數
        :param stop_on_win: 追中即停
        :return: 投注結果
        """
        post_url = '/a/lottery/betV2'
        lottery_info = self.get_lottery_info(lottery_name)

        from utils.requestContent_YFT import game_default
        import json
        default = json.loads(game_default)
        logger.debug(f'default json = {default}')
        from utils.requestContent_YFT import game_dict
        totalAmount = 0
        schemeList = []
        for game in games:
            if game_dict.get(game) and game not in ('pt333bt02', 'pt137bt02'):  # 排除牛牛
                schemeList.append(game_dict.get(game)[0])
                totalAmount += game_dict.get(game)[1]
        default['currIssueNo'] = lottery_info["chaseableIssueNoList"][0]
        default['stopOnWon'] = 'null'
        default['schemeList'] = schemeList
        default['lotteryType'] = lottery_name
        default['issueList'] = [1]
        default['isWap'] = False

        if is_trace:
            default['issueList'] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            totalAmount *= 10
            if stop_on_win:
                default['stopOnWon'] = 'yes'
            else:
                default['stopOnWon'] = 'no'
        if self._money_unit == '0.1':
            totalAmount *= 0.1
        elif self._money_unit == '0.01':
            totalAmount *= 0.01

        default['totalAmount'] = totalAmount

        data = json.dumps(default)
        data.replace('\'null\'', 'null')
        data.replace('True', 'true')
        data.replace('False', 'false')

        logger.debug(f"self.money_unit == '0.1' = {self._money_unit == '0.1'}\n"
                     f"self.money_unit == '0.01' = {self._money_unit == '0.01'}\n"
                     f"self.award_mode == '2' = {self._award_mode == '2'}")
        if self._money_unit == '0.1':
            logger.debug("self.money_unit == '0.1'")
            data = data.replace('"potType": "Y"', '"potType": "J"')
        elif self._money_unit == '0.01':
            logger.debug("self.money_unit == '0.01'")
            data = data.replace('"potType": "Y"', '"potType": "F"')
        if self._award_mode == '2':
            logger.debug("self.award_mode == '2'")
            data = data.replace('"doRebate": "yes"', '"doRebate": "no"')

        logger.info(f'Bet content = {data}')
        bet_response = self._session.post(url=self._env_config.get_post_url() + post_url, data=data,
                                          headers=self._header)
        logger.info(f'Bet response = {bet_response.json()}\n')
        return bet_response.json()

    def bet_trace(self, game_name, stop_on_win):
        games = self._conn.get_lottery_games(game_name[0])
        expected = 'ok'
        bet_response = self.bet_yft(lottery_name=game_name[0], stop_on_win=stop_on_win, games=games,
                                    is_trace=False)
        if bet_response['status'] == expected:
            print(f'{game_name[1]}投注追號成功。\n用戶餘額：{bet_response["content"]["_balUsable"]} ; '
                  f'投注金額：{bet_response["content"]["_balWdl"]}')
        else:
            self.fail(f'投注失敗，接口返回：{bet_response}')

        bet_response = self.bet_yft(lottery_name=game_name[0], stop_on_win=stop_on_win, games=games,
                                    is_trace=True)
        if bet_response['status'] == expected:
            print(f'{game_name[1]}追號全彩種成功。\n用戶餘額：{bet_response["content"]["_balUsable"]} ; '
                  f'投注金額：{bet_response["content"]["_balWdl"]}')
        else:
            self.fail(f'投注失敗，接口返回：{bet_response}')

    def test_create_user(self):
        from datetime import datetime
        from utils.requestContent_YFT import link_default
        m = hashlib.md5()
        m.update("123123".encode("utf-8"))
        """直接新增用戶"""
        link = "/a/agent/createNewUser"
        data = eval(link_default.replace('r_percent', '0.001').replace('false', 'False').replace('true', 'True'))
        extra = {
            "type": "a",
            "username": "autoreg" + str(round(datetime.now().timestamp())),
            "password": m.hexdigest(),
            "passwordConfirm": m.hexdigest(),
            "timeZone": "GMT+8",
            "isWap": False,
            "online": True
        }
        data.update(extra)
        logger.info(f'Dir create user. data = {json.dumps(data)}')
        response = self._session.post(url=self._env_config.get_post_url() + link, data=json.dumps(data),
                                      headers=self._header)
        logger.info(f'response.text = {response.text}')
        if response.status_code == 200:
            if response.json()["status"] == 'failed':
                self.fail(f'開戶結果 : response = {response.json()}')
            else:
                print(f'直接開戶成功\n返回數據：{response.json()["content"]}\n')

        """新增開戶連結"""
        link = '/a/agent/createAgentLink'
        from utils.requestContent_YFT import link_default
        link_contant = link_default.replace('r_percent', '0.001')
        logger.warning(f'link_contant = {link_contant}')
        response = self._session.post(url=self._env_config.get_post_url() + link, data=link_contant,
                                      headers=self._header)
        logger.info(f'response.text = {response.text}')

        if response.json()['status'] == 'ok':
            link_id = response.json()["content"]["id"]
            print(f'連結創立成功！\n連結ID = {link_id}\n')

            """用連結新增用戶"""
            link = "/a/register/register"
            data = {
                "account": "autoreg" + str(round(datetime.now().timestamp())),
                "passwd": m.hexdigest(),
                "id": link_id,
                "timeZone": "GMT+8",
                "isWap": False,
                "online": False
            }
            logger.info(f'json.dumps(data) = {json.dumps(data)}')
            response = self._session.post(self._env_config.get_post_url() + link, headers=self._header,
                                          data=json.dumps(data))
            logger.info(f'response.text = {response.text}')
            if response.status_code == 200:
                print('開戶連結開戶成功')
                print(f'回傳資料：{response.json()["content"]}')
            else:
                raise Exception(f'用戶創建失敗{response.json()["msg"]}')
        else:
            raise Exception(f'連結創立失敗{response.json()["msg"]}')

    """時時彩系列"""

    def test_bet_qqffc(self, stop_on_win=True):
        """
        QQ分分彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['qqffc', 'QQ分分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_hjcqssc(self, stop_on_win=True):
        """
        懷舊重慶時時彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['hjcqssc', '懷舊重慶時時彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_ynffc(self, stop_on_win=True):
        """
        印尼分分彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['ynffc', '印尼分分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_tcffc(self, stop_on_win=True):
        """
        騰訊分分彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['tcffc', '騰訊分分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_se15fc(self, stop_on_win=True):
        """
        首爾1.5分彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['se15fc', '首爾1.5分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_yn2fc(self, stop_on_win=True):
        """
        印尼2分彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['yn2fc', '印尼2分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_xjssc(self, stop_on_win=True):
        """
        新疆時時彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['xjssc', '新疆時時彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_tjssc(self, stop_on_win=True):
        """
        天津時時彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['tjssc', '天津時時彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_tcdffc(self, stop_on_win=True):
        """
        騰訊兩分彩投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['tcdffc', '騰訊兩分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_cqssc(self, stop_on_win=True):
        """
        重慶時時彩生肖
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['cqssc', '重慶時時彩生肖']
        self.bet_trace(game_name, stop_on_win)

    """賽車／飛艇系列"""

    def test_bet_fhxyft(self, stop_on_win=True):
        """
        幸運飛艇投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['fhxyft', '鳳凰幸運飛艇']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_bjpk10(self, stop_on_win=True):
        """
        PK10投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['bjpk10', '北京PK10']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_djpk10(self, stop_on_win=True):
        """
        東京賽車投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['djpk10', '東京賽車']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_xyftpk10(self, stop_on_win=True):
        """
        皇家幸運飛艇投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['xyftpk10', '皇家幸運飛艇']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_metftpk10(self, stop_on_win=True):
        """
        馬爾他飛艇投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['metftpk10', '馬爾他飛艇']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_xnpk10(self, stop_on_win=True):
        """
        悉尼PK10投注
        牛牛不可高獎金，另外投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['xnpk10', '悉尼PK10']
        self.bet_trace(game_name, stop_on_win)

    """快三系列"""

    def test_bet_ahk3(self, stop_on_win=True):
        """
        安徽快三投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['ahk3', '安徽快三']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_hbk3(self, stop_on_win=True):
        """
        湖北快三
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['hbk3', '湖北快三']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_jsk3(self, stop_on_win=True):
        """
        江蘇快三投注。
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['jsk3', '江蘇快三']
        self.bet_trace(game_name, stop_on_win)

    """11選5系列"""

    def test_bet_sd11x5(self, stop_on_win=True):
        """
        山東11選5投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['sd11x5', '山東11選5']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_jx11x5(self, stop_on_win=True):
        """
        江西11選5投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['jx11x5', '江西11選5']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_sh11x5(self, stop_on_win=True):
        """
        上海11選5投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['sh11x5', '上海11選5']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_js11x5(self, stop_on_win=True):
        """
        江蘇11選5投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['js11x5', '江蘇11選5']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_gd11x5(self, stop_on_win=True):
        """
        廣東11選5投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['gd11x5', '廣東蘇11選5']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_hn60(self, stop_on_win=True):
        """
        多彩河内分分彩投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['hn60', '多彩河内分分彩']
        self.bet_trace(game_name, stop_on_win)

    def test_bet_xyft168(self, stop_on_win=True):
        """
        168幸運飛艇投注
        :param stop_on_win: 追號與否
        :return: None
        """

        game_name = ['xyft168', '168幸运飞艇']
        self.bet_trace(game_name, stop_on_win)

    def tearDown(self) -> None:
        Config.test_cases_update(1)
