import threading
import unittest
from time import sleep

import re
import redis
import json
import random
import requests
import time

from utils import Config, Logger
from utils.Config import LotteryData
from utils.Config import func_time

def get_rediskey(envs):  # env參數 決定是哪個環境
    redis_dict = {'ip': ['10.13.22.152', '10.6.1.82']}  # 0:dev,1:188
    global r
    pool = redis.ConnectionPool(host=redis_dict['ip'][envs], port=6379)
    r = redis.Redis(connection_pool=pool)

def get_token(envs, user):
    get_rediskey(envs)
    global redis_
    redis_ = r_keys = (r.keys('USER_TOKEN_%s*' % re.findall(r'[0-9]+|[a-z]+', user)[0]))
    for i in r_keys:
        if user in str(i):
            user_keys = (str(i).replace("'", '')[1:])

    user_dict = r.get(user_keys)
    timestap = str(user_dict).split('timeOut')[1].split('"token"')[0][2:-4]  #
    token_time = time.localtime(int(timestap))
    print('token到期時間: %s-%s-%s %s:%s:%s' % (token_time.tm_year, token_time.tm_mon, token_time.tm_mday,
                                            token_time.tm_hour, token_time.tm_min, token_time.tm_sec))

class ApiTestApp(unittest.TestCase):
    u'APP接口測試'
    envConfig = ""
    user_g = ""
    red_type = ""
    logger = ""

    def __init__(self, case, env, user, red_type):
        super().__init__(case)
        self.logger = Logger.create_logger(self.__class__.__name__)
        self.envConfig = env
        self.user_g = user
        self.red_type = red_type

    @func_time
    def test_AppLogin(self):
        u"APP登入測試"
        global userAgent
        userAgent = Config.UserAgent.PC.value
        account_ = {self.user_g: '輸入的用戶名'}
        global token_, userid_
        token_ = {}
        userid_ = {}
        global header
        header = {
            'User-Agent': userAgent,
            'Content-Type': 'application/json'
        }

        # 判斷用戶是dev或188,  uuid和loginpasssource為固定值
        global envs, env, domain_url  # envs : DB環境 用, env 環境 url ,request url 用, domin_url APP開戶 參數用

        env = self.envConfig.get_iapi()
        domain_url = self.envConfig.get_domain()
        envs = self.envConfig.get_env_id()
        uuid = self.envConfig.get_uuid()
        loginpasssource = self.envConfig.get_login_pass_source()
        jointVenture = self.envConfig.get_joint_venture()

        # 登入request的json
        for i in account_.keys():
            login_data = {
                "head": {
                    "sessionId": ''
                },
                "body": {
                    "param": {
                        "username": i + "|" + uuid,
                        "loginpassSource": loginpasssource,
                        "appCode": 1,
                        "uuid": uuid,
                        "loginIp": 2130706433,
                        "device": 2,
                        "app_id": 9,
                        "come_from": "3",
                        "appname": "1",
                        "jointVenture": jointVenture
                    }
                }
            }
            print("Joy188Test3 Start")
            print(login_data)
            try:
                r = requests.post(env + 'front/login', data=json.dumps(login_data), headers=header)
                # print(r.json())
                token = r.json()['body']['result']['token']
                userid = r.json()['body']['result']['userid']
                token_.setdefault(i, token)
                userid_.setdefault(i, userid)
                print(u'APP登入成功,登入帳號: %s' % (i))
                print("Token: %s" % token)
                print("Userid: %s" % userid)
            except ValueError as e:
                print(e)
                print(u"登入失敗")
                break
            # user_list.setdefault(userid,token)
        get_token(envs, self.user_g)

    @func_time
    def test_AppSubmit(self):
        u"APP投注"
        global user

        user = self.user_g  # 業面用戶登入
        t = time.strftime('%Y%m%d %H:%M:%S')
        print(u'投注帳號: %s, 現在時間: %s' % (user, t))
        try:
            for i in LotteryData.lottery_dict.keys():
                if i in ['slmmc', 'sl115', 'btcctp']:
                    '''
                    data_ = {"head":{"sessionId":token_[user]},
                    "body":{"param":{"data":{"version":"1.0.30",
                    "channel":"android","gameType":"slmmc_","amount":2,
                    "balls":[{"id":0,"ball":"-,-,9,3,3",
                    "type":"housan.zhixuan.fushi","num":1,"multiple":1,"moneyunit":1,"amount":2}],
                    "isTrace":0,"traceWinStop":0,"traceStopValue":-1,"activityType":0,"awardMode":1,
                    "orders":[{"number":"/","issueCode":1,"multiple":1}],"loginIp":168627247},
                    "app_id":10,"come_from":"4","appname":"1"}}}
                    '''
                    pass
                else:
                    lotteryid = LotteryData.lottery_dict[i][1]

                    self.select_issue(Config.get_conn(envs), lotteryid)  # 目前彩種的獎棋
                    # print(issue,issueName)
                    now = int(time.time() * 1000)  # 時間戳
                    ball_type_post = self.game_type(i)  # 玩法和內容,0為玩法名稱, 1為投注內容
                    methodid = ball_type_post[0].replace('.', '')  # ex: housan.zhuiam.fushi , 把.去掉

                    # 找出對應的玩法id
                    bet_type = self.select_betTypeCode(Config.get_conn(envs), lotteryid, methodid)

                    data_ = {"head":
                                 {"sessionId": token_[user]},
                             "body": {"param": {"CGISESSID": token_[user],  # 產生  kerr001的token
                                                "lotteryId": str(lotteryid), "chan_id": 1, "userid": 1373224,
                                                "money": 2 * mul, "issue": issue[0], "issueName": issueName[0],
                                                "isFirstSubmit": 0,
                                                "list": [
                                                    {"methodid": bet_type[0], "codes": ball_type_post[1], "nums": 1,
                                                     "fileMode": 0, "mode": 1, "times": mul, "money": 2 * mul}],
                                                # times是倍數
                                                "traceIssues": "", "traceTimes": "", "traceIstrace": 0,
                                                "saleTime": now,
                                                "userIp": 168627247, "channelId": 402, "traceStop": 0}}}
                    session = requests.session()

                    r = session.post(env + 'game/buy', data=json.dumps(data_), headers=header)

                    if r.json()['head']['status'] == 0:  # status0 為投注成功
                        print('{} 投注成功'.format(LotteryData.lottery_dict[i][0]))
                        print(bet_type[2])  # 投注完法 中文名稱
                        print("投注內容 : {}".format(ball_type_post[1]))
                        print("投注金額 : {}, 投注倍數: {}".format(2 * mul, mul))  # mul 為game_type方法對甕倍數
                        # print(r.json())
                        orderid = (r.json()['body']['result']['orderId'])
                        order_code = Config.get_order_code_iapi(Config.get_conn(envs), orderid)  # 找出對應ordercode
                        # print('orderid: %s'%orderid)
                        print(u'投注單號: {}'.format(order_code[-1]))
                        print('------------------------------')
                    else:
                        print('{} 投注失敗'.format(LotteryData.lottery_dict[i][0]))
                        pass
        except requests.exceptions.ConnectionError:
            print('please wait')
        except IndexError:
            pass

    def select_issue(self, conn, lotteryid):  # 查詢正在銷售的 期號
        # Joy188Test.date_time()
        # today_time = '2019-06-10'#for 預售中 ,抓當天時間來比對,會沒獎期
        try:
            with conn.cursor() as cursor:
                sql = "select web_issue_code,issue_code from game_issue where lotteryid = '%s' and sysdate between sale_start_time and sale_end_time" % (
                    lotteryid)

                cursor.execute(sql)
                rows = cursor.fetchall()

                global issueName
                global issue
                issueName = []
                issue = []
                if lotteryid in ['99112', '99306']:  # 順利秒彩,順利11選5  不需 講期. 隨便塞
                    issueName.append('1')
                    issue.append('1')
                else:
                    for i in rows:  # i 生成tuple
                        issueName.append(i[0])
                        issue.append(i[1])
            conn.close()
        except:
            pass

    def ball_type(self, test):  # 對應完法,產生對應最大倍數和 投注完法
        ball = []
        global mul
        if test == 'wuxing':

            ball = [str(Config.random_mul(9)) for i in range(5)]  # 五星都是數值
            mul = Config.random_mul(2)
        elif test == 'sixing':
            ball = ['-' if i == 0 else str(Config.random_mul(9)) for i in range(5)]  # 第一個為-
            mul = Config.random_mul(22)
        elif test == 'housan':
            ball = ['-' if i in [0, 1] else str(Config.random_mul(9)) for i in range(5)]  # 第1和2為-
            mul = Config.random_mul(222)
        elif test == 'qiansan':
            ball = ['-' if i in [3, 4] else str(Config.random_mul(9)) for i in range(5)]  # 第4和5為-
            mul = Config.random_mul(222)
        elif test == 'zhongsan':
            ball = ['-' if i in [0, 4] else str(Config.random_mul(9)) for i in range(5)]  # 第2,3,4為-
            mul = Config.random_mul(222)
        elif test == 'houer':
            ball = ['-' if i in [0, 1, 2] else str(Config.random_mul(9)) for i in range(5)]  # 第1,2,3為-
            mul = Config.random_mul(2222)
        elif test == 'qianer':
            ball = ['-' if i in [2, 3, 4] else str(Config.random_mul(9)) for i in range(5)]  # 第3,4,5為-
            mul = Config.random_mul(2222)
        elif test == 'yixing':  # 五個號碼,只有一個隨機數值
            ran = Config.random_mul(4)
            ball = ['-' if i != ran else str(Config.random_mul(9)) for i in range(5)]
            mul = Config.random_mul(2222)
        else:
            mul = Config.random_mul(1)
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
            0: ["%s.zhixuan.fushi" % (group_,), lottery_ball],
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
            play_ = u'玩法名稱: %s.%s.%s' % (game_group[group_], game_set['zhixuan'],
                                         game_method['fushi'])

        elif lottery in LotteryData.lottery_3d:
            num = 1
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['qianer'], game_set['zhixuan'],
                                         game_method['zhixuanfushi'])
        elif lottery in LotteryData.lottery_noRed:
            if lottery in ['p5', 'np3']:
                num = 9
                play_ = u'玩法名稱: %s.%s.%s' % (game_group['p3sanxing'], game_set['zhixuan'],
                                             game_method['fushi'])
            else:
                num = 1
                play_ = u'玩法名稱: %s.%s.%s' % (game_group['qianer'], game_set['zhixuan'],
                                             game_method['zhixuanfushi'])
        elif lottery in LotteryData.lottery_115:
            num = 2
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['xuanqi'], game_set['renxuanqizhongwu'],
                                         game_method['fushi'])
        elif lottery in LotteryData.lottery_k3:
            num = 3
            play_ = u'玩法名稱: %s.%s' % (game_group['sanbutonghao'], game_set['biaozhun'])
        elif lottery in LotteryData.lottery_sb:
            num = 4
            play_ = u'玩法名稱: %s' % (game_group['santonghaotongxuan'])
        elif lottery in LotteryData.lottery_fun:
            num = 5
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['guanya'], game_set['zhixuan'],
                                         game_method['fushi'])
        elif lottery == 'shssl':
            num = 6
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['qianer'], game_set['zuxuan'],
                                         game_method['fushi'])
        elif lottery == 'ssq':
            num = 7
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['biaozhuntouzhu'], game_set['biaozhun'],
                                         game_method['fushi'])
        elif lottery == 'lhc':
            num = 8
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['zhengma'], game_set['pingma'],
                                         game_method['zhixuanliuma'])
        elif lottery == 'p5':
            num = 9
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['p3sanxing'], game_set['zhixuan'],
                                         game_method['fushi'])
        elif lottery == 'bjkl8':
            num = 10
            play_ = u'玩法名稱: %s.%s.%s' % (game_group['renxuan'], game_set['putongwanfa'],
                                         game_method['renxuan7'])
        else:
            num = 11
            # play_ = u'玩法名稱: 沖天炮
        return test_dicts[num][0], test_dicts[num][1], play_

    def test_AppOpenLink(self):
        '''APP開戶/註冊'''
        user = self.user_g
        if envs == 1:  # 188 環境
            data_ = {"head": {"sowner": "", "rowner": "", "msn": "", "msnsn": "", "userId": "", "userAccount": "",
                              "sessionId": token_[user]}, "body": {"pager": {"startNo": "1", "endNo": "99999"},
                                                                   "param": {"CGISESSID": token_[user], "type": 1,
                                                                             "days": -1, "infos": [
                                                                           {"lotteryId": "77101",
                                                                            "lotterySeriesCode": 10,
                                                                            "lotterySeriesName": "\\u771f\\u4eba\\u5f69\\u7968",
                                                                            "awardGroupId": 77101,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99101",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 12,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99103",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 19,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99104",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 36,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99105",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 13,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99105",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 5,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41700",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99105",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 16,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41500",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99106",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 33,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99107",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 15,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99107",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 8,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41700",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99107",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 18,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41500",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99108",
                                                                                             "lotterySeriesCode": 2,
                                                                                             "lotterySeriesName": "3D\\u7cfb",
                                                                                             "awardGroupId": 101,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41700",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99109",
                                                                            "lotterySeriesCode": 2,
                                                                            "lotterySeriesName": "3D\\u7cfb",
                                                                            "awardGroupId": 102,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41700",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99111",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 41,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99112",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 56,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99113",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 205,
                                                                                             "awardName": "2000\\u5956\\u91d1\\u7ec4",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99114",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 208,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99115",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 219,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41000",
                                                                                             "directLimitRet": 4300,
                                                                                             "threeLimitRet": 4300,
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99116",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 231,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99117",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 248,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99118",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 249,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99119",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 253,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99120",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 254,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99121",
                                                                                             "lotterySeriesCode": 1,
                                                                                             "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 255,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99122",
                                                                            "lotterySeriesCode": 1,
                                                                            "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                                                                            "awardGroupId": 256,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99123",
                                                                                             "lotterySeriesCode": 2,
                                                                                             "lotterySeriesName": "3D\\u7cfb",
                                                                                             "awardGroupId": 258,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directLimitRet": 450,
                                                                                             "threeLimitRet": 450,
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99124",
                                                                            "lotterySeriesCode": 2,
                                                                            "lotterySeriesName": "3D\\u7cfb",
                                                                            "awardGroupId": 259,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directLimitRet": 450, "threeLimitRet": 450,
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99201",
                                                                                             "lotterySeriesCode": 4,
                                                                                             "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb",
                                                                                             "awardGroupId": 32,
                                                                                             "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99202",
                                                                            "lotterySeriesCode": 4,
                                                                            "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb",
                                                                            "awardGroupId": 206,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directLimitRet": 950, "directRet": 0,
                                                                            "threeoneRet": 0, "superRet": 0},
                                                                           {"lotteryId": "99203",
                                                                            "lotterySeriesCode": 4,
                                                                            "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb",
                                                                            "awardGroupId": 238,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41000",
                                                                            "directLimitRet": 5000, "directRet": 0,
                                                                            "threeoneRet": 0, "superRet": 0},
                                                                           {"lotteryId": "99301",
                                                                            "lotterySeriesCode": 3,
                                                                            "lotterySeriesName": "11\\u90095\\u7cfb",
                                                                            "awardGroupId": 24,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41782",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99302",
                                                                                             "lotterySeriesCode": 3,
                                                                                             "lotterySeriesName": "11\\u90095\\u7cfb",
                                                                                             "awardGroupId": 27,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41782",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99303",
                                                                            "lotterySeriesCode": 3,
                                                                            "lotterySeriesName": "11\\u90095\\u7cfb",
                                                                            "awardGroupId": 29,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41782",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99306",
                                                                                             "lotterySeriesCode": 3,
                                                                                             "lotterySeriesName": "11\\u90095\\u7cfb",
                                                                                             "awardGroupId": 192,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41782",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99401",
                                                                            "lotterySeriesCode": 5,
                                                                            "lotterySeriesName": "\\u53cc\\u8272\\u7403\\u7cfb",
                                                                            "awardGroupId": 107,
                                                                            "awardName": "\\u53cc\\u8272\\u7403\\u5956\\u91d1\\u7ec4",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99501",
                                                                                             "lotterySeriesCode": 6,
                                                                                             "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 188,
                                                                                             "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99502",
                                                                            "lotterySeriesCode": 6,
                                                                            "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                            "awardGroupId": 190,
                                                                            "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99601",
                                                                                             "lotterySeriesCode": 7,
                                                                                             "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 189,
                                                                                             "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99602",
                                                                            "lotterySeriesCode": 7,
                                                                            "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                            "awardGroupId": 203,
                                                                            "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99604",
                                                                                             "lotterySeriesCode": 7,
                                                                                             "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 213,
                                                                                             "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0},
                                                                           {"lotteryId": "99605",
                                                                            "lotterySeriesCode": 7,
                                                                            "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                            "awardGroupId": 207,
                                                                            "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99701",
                                                                                             "lotterySeriesCode": 9,
                                                                                             "lotterySeriesName": "\\u516d\\u5408\\u7cfb",
                                                                                             "awardGroupId": 202,
                                                                                             "awardName": "\\u516d\\u5408\\u5f69\\u5956\\u91d1\\u7ec4",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0,
                                                                                             "lhcYear": 0,
                                                                                             "lhcColor": 0,
                                                                                             "lhcFlatcode": 0,
                                                                                             "lhcHalfwave": 0,
                                                                                             "lhcOneyear": 0,
                                                                                             "lhcNotin": 0,
                                                                                             "lhcContinuein23": 0,
                                                                                             "lhcContinuein4": 0,
                                                                                             "lhcContinuein5": 0,
                                                                                             "lhcContinuenotin23": 0,
                                                                                             "lhcContinuenotin4": 0,
                                                                                             "lhcContinuenotin5": 0,
                                                                                             "lhcContinuecode": 0},
                                                                           {"lotteryId": "99801",
                                                                            "lotterySeriesCode": 2,
                                                                            "lotterySeriesName": "3D\\u7cfb",
                                                                            "awardGroupId": 223,
                                                                            "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                            "directLimitRet": 450, "threeLimitRet": 450,
                                                                            "directRet": 0, "threeoneRet": 0,
                                                                            "superRet": 0}, {"lotteryId": "99901",
                                                                                             "lotterySeriesCode": 11,
                                                                                             "lotterySeriesName": "\\u9ad8\\u9891\\u5f69\\u7cfb",
                                                                                             "awardGroupId": 243,
                                                                                             "awardName": "\\u5956\\u91d1\\u7ec41800",
                                                                                             "directRet": 0,
                                                                                             "threeoneRet": 0,
                                                                                             "superRet": 0}],
                                                                             "memo": "", "setUp": 1, "needContact": "N",
                                                                             "authenCellphone": "N",
                                                                             "showRegisterBtn": "Y", "app_id": "9",
                                                                             "come_from": "3", "appname": "1",
                                                                             "domain": "https:\\/\\/www2.joy188.com"}}}
        else:  # dev
            data_ = {"head": {"sessionId": token_[user]}, "body": {
                "param": {"CGISESSID": token_[user], "type": 1, "days": -1, "infos": [
                    {"lotteryId": "77101", "lotteryName": "\\u4e50\\u5229\\u771f\\u4eba\\u5f69",
                     "lotterySeriesCode": 10, "lotterySeriesName": "\\u771f\\u4eba\\u5f69\\u7968",
                     "awardGroupId": 77101, "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 480},
                    {"lotteryId": "99101", "lotteryName": "\\u6b22\\u4e50\\u751f\\u8096", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 12,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99103", "lotteryName": "\\u65b0\\u7586\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 19,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99104", "lotteryName": "\\u5929\\u6d25\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 36,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99105", "lotteryName": "\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 13,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99106", "lotteryName": "\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 33,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99107", "lotteryName": "\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 15,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99108", "lotteryName": "3D", "lotterySeriesCode": 2,
                     "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 101, "awardName": "\\u5956\\u91d1\\u7ec41700",
                     "directLimitRet": 1380, "threeLimitRet": 980},
                    {"lotteryId": "99109", "lotteryName": "P5", "lotterySeriesCode": 2,
                     "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 102, "awardName": "\\u5956\\u91d1\\u7ec41700",
                     "directLimitRet": 1380, "threeLimitRet": 980},
                    {"lotteryId": "99111", "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 41,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99112", "lotteryName": "\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 56,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99113", "lotteryName": "\\u8d85\\u7ea72000\\u79d2\\u79d2\\u5f69(APP\\u7248)",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb",
                     "awardGroupId": 11416083, "awardName": "2000\\u5956\\u91d1\\u7ec4", "superLimitRet": 80},
                    {"lotteryId": "99114", "lotteryName": "\\u817e\\u8baf\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 208,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99115", "lotteryName": "\\u51e4\\u51f0\\u6bd4\\u7279\\u5e01\\u5206\\u5206\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 214,
                     "awardName": "\\u5956\\u91d1\\u7ec41000", "directLimitRet": 4780, "threeLimitRet": 4780},
                    {"lotteryId": "99116", "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 228,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99117", "lotteryName": "\\u51e4\\u51f0\\u91cd\\u5e86\\u5168\\u7403\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 263,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99118", "lotteryName": "\\u51e4\\u51f0\\u65b0\\u7586\\u5168\\u7403\\u5f69",
                     "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 264,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99119", "lotteryName": "\\u6cb3\\u5185\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 268,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99120", "lotteryName": "\\u6cb3\\u5185\\u4e94\\u5206\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 273,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99121", "lotteryName": "360\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 274,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99122", "lotteryName": "360\\u4e94\\u5206\\u5f69", "lotterySeriesCode": 1,
                     "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 275,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99123", "lotteryName": "\\u8d8a\\u5357\\u798f\\u5f69", "lotterySeriesCode": 2,
                     "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 278, "awardName": "\\u5956\\u91d1\\u7ec41800",
                     "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99124", "lotteryName": "\\u8d8a\\u53573D\\u798f\\u5f69", "lotterySeriesCode": 2,
                     "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 279, "awardName": "\\u5956\\u91d1\\u7ec41800",
                     "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99201", "lotteryName": "\\u5317\\u4eac\\u5feb\\u4e508", "lotterySeriesCode": 4,
                     "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 32,
                     "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directLimitRet": 1980, "threeLimitRet": 1380},
                    {"lotteryId": "99202", "lotteryName": "PK10", "lotterySeriesCode": 4,
                     "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 206,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 980},
                    {"lotteryId": "99203", "lotteryName": "\\u98de\\u8247", "lotterySeriesCode": 4,
                     "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 233,
                     "awardName": "\\u5956\\u91d1\\u7ec41000", "directLimitRet": 4780},
                    {"lotteryId": "99301", "lotteryName": "\\u5c71\\u4e1c11\\u90095", "lotterySeriesCode": 3,
                     "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 24,
                     "awardName": "\\u5956\\u91d1\\u7ec41782", "directLimitRet": 980, "threeLimitRet": 980},
                    {"lotteryId": "99302", "lotteryName": "\\u6c5f\\u897f11\\u90095", "lotterySeriesCode": 3,
                     "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 27,
                     "awardName": "\\u5956\\u91d1\\u7ec41782", "directLimitRet": 980, "threeLimitRet": 980},
                    {"lotteryId": "99303", "lotteryName": "\\u5e7f\\u4e1c11\\u90095", "lotterySeriesCode": 3,
                     "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 29,
                     "awardName": "\\u5956\\u91d1\\u7ec41782", "directLimitRet": 980, "threeLimitRet": 980},
                    {"lotteryId": "99306", "lotteryName": "\\u51e4\\u51f0\\u987a\\u522911\\u90095",
                     "lotterySeriesCode": 3, "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 192,
                     "awardName": "\\u5956\\u91d1\\u7ec41782", "directLimitRet": 980, "threeLimitRet": 980},
                    {"lotteryId": "99401", "lotteryName": "\\u53cc\\u8272\\u7403", "lotterySeriesCode": 5,
                     "lotterySeriesName": "\\u53cc\\u8272\\u7403\\u7cfb", "awardGroupId": 107,
                     "awardName": "\\u53cc\\u8272\\u7403\\u5956\\u91d1\\u7ec4", "directLimitRet": 1480,
                     "threeLimitRet": 1480},
                    {"lotteryId": "99501", "lotteryName": "\\u6c5f\\u82cf\\u5feb\\u4e09", "lotterySeriesCode": 6,
                     "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 188,
                     "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directLimitRet": 1280},
                    {"lotteryId": "99502", "lotteryName": "\\u5b89\\u5fbd\\u5feb\\u4e09", "lotterySeriesCode": 6,
                     "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 190,
                     "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directLimitRet": 1280},
                    {"lotteryId": "99601", "lotteryName": "\\u6c5f\\u82cf\\u9ab0\\u5b9d", "lotterySeriesCode": 7,
                     "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 189,
                     "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directLimitRet": 880}, {"lotteryId": "99602",
                                                                                                  "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u5a31\\u4e50\\u5385)",
                                                                                                  "lotterySeriesCode": 7,
                                                                                                  "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb",
                                                                                                  "awardGroupId": 203,
                                                                                                  "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4",
                                                                                                  "directLimitRet": 880},
                    {"lotteryId": "99604", "lotteryName": "\\u5b89\\u5fbd\\u9ab0\\u5b9d", "lotterySeriesCode": 7,
                     "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 11416087,
                     "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directLimitRet": 880},
                    {"lotteryId": "99605", "lotteryName": "\\u51e4\\u51f0\\u987a\\u5229\\u9ab0\\u5b9d",
                     "lotterySeriesCode": 7, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 207,
                     "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directLimitRet": 880, "threeLimitRet": 130},
                    {"lotteryId": "99701", "lotteryName": "\\u516d\\u5408\\u5f69", "lotterySeriesCode": 9,
                     "lotterySeriesName": "\\u516d\\u5408\\u7cfb", "awardGroupId": 202,
                     "awardName": "\\u516d\\u5408\\u5f69\\u5956\\u91d1\\u7ec4", "directLimitRet": 1390,
                     "lhcYearLimit": 280, "lhcColorLimit": 280, "lhcFlatcodeLimit": 380, "lhcHalfwaveLimit": 280,
                     "lhcOneyearLimit": 180, "lhcNotinLimit": 280, "lhcContinuein23Limit": 280,
                     "lhcContinuein4Limit": 480, "lhcContinuein5Limit": 480, "lhcContinuenotin23Limit": 280,
                     "lhcContinuenotin4Limit": 480, "lhcContinuenotin5Limit": 480, "lhcContinuecodeLimit": 480},
                    {"lotteryId": "99801", "lotteryName": "\\u51e4\\u51f0\\u5409\\u52293D", "lotterySeriesCode": 2,
                     "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 223, "awardName": "\\u5956\\u91d1\\u7ec41800",
                     "directLimitRet": 880, "threeLimitRet": 980},
                    {"lotteryId": "99901", "lotteryName": "\\u5feb\\u5f00", "lotterySeriesCode": 11,
                     "lotterySeriesName": "\\u9ad8\\u9891\\u5f69\\u7cfb", "awardGroupId": 238,
                     "awardName": "\\u5956\\u91d1\\u7ec41800", "directLimitRet": 980}], "memo": "", "setUp": 1,
                          "needContact": "N", "authenCellphone": "N", "showRegisterBtn": "Y"}}}
        r = requests.post(env + 'information/doRetSetting', data=json.dumps(data_), headers=header)  # 儲存連結反點,生成連結
        # print(r.json())
        if r.json()['head']['status'] == 0:
            print('開戶連結創立成功')
            data_ = {"head": {"sowner": "", "rowner": "", "msn": "", "msnsn": "", "userId": "", "userAccount": "",
                              "sessionId": token_[user]},
                     "body": {"param": {"CGISESSID": token_[user], "app_id": "10", "come_from": "4",
                                        "appname": "1"}, "pager": {"startNo": "", "endNo": ""}}}

            r = requests.post(env + 'information/openLinkList', data=json.dumps(data_),
                              headers=header)  # 找出開戶連結后的註冊id,回傳註冊
            # print(r.json())
            result = r.json()['body']['result']['list'][0]
            global regCode, token, exp, pid
            regCode = result['regCode']  # 回傳開戶 的 id
            token = result['urlstring'].split('token=')[1]  # 回傳 開戶 的token
            # print(token)
            exp = result['urlstring'].split('exp=')[1].split('&')[0]
            pid = result['urlstring'].split('pid=')[1].split('&')[0]
            print('%s 的 開戶連結' % user)
            print("註冊連結: %s, \n註冊碼: %s, 建置於: %s" % (result['urlstring'], result['regCode'], result['start']))
        else:
            print('創立失敗')
        user_random = random.randint(1, 100000)  # 隨機生成 頁面輸入 用戶名 + 隨機數 的下級
        new_user = self.user_g + str(user_random)
        data_ = {"head": {"sowner": "", "rowner": "", "msn": "", "msnsn": "", "userId": "", "userAccount": ""},
                 # 開戶data
                 "body": {
                     "param": {"token": token, "accountName": new_user, "password": "3bf6add0828ee17c4603563954473c1e",
                               "cellphone": "", "qqAccount": "", "wechat": "", "id": int(regCode), "exp": exp,
                               "pid": int(pid), "qq": '',
                               "ip": "192.168.2.18", "app_id": "10", "come_from": "4", "appname": "1"},
                     "pager": {"startNo": "", "endNo": ""}}}
        if self.envConfig in ['dev02', 'joy188']:  # 一般 4.0  data 不用帶 joint_venture
            pass
        elif self.envConfig in ['fh82dev02', 'teny2020dev02', 'joy188.teny2020', 'joy188.195353']:  # 合營版
            data_['body']['param']['jointVenture'] = 1
        else:  # 歡樂棋牌
            data_['body']['param']['jointVenture'] = 2

        r = requests.post(env + 'user/register', data=json.dumps(data_), headers=header)
        if r.json()['head']['status'] == 0:
            print('%s 註冊成功' % new_user)
        else:
            print('註冊失敗')

    def amount_data(self, user):
        data = {"head": {"sowner": "", "rowner": "", "msn": "", "msnsn": "", "userId": "", "userAccount": "",
                         "sessionId": token_[user]},
                "body": {"param": {"amount": 10, "CGISESSID": token_[user], "app_id": "9",
                                   "come_from": "3", "appname": "1"}, "pager": {"startNo": "", "endNo": ""}}}
        return data

    def balance_data(self, user):
        data = {"head": {"sowner": "", "rowner": "", "msn": "", "msnsn": "", "userId": "",
                         "userAccount": "", "sessionId": token_[user]}, "body": {"param": {"CGISESSID": token_[user],
                                                                                           "loginIp": "61.220.138.45",
                                                                                           "app_id": "9",
                                                                                           "come_from": "3",
                                                                                           "appname": "1"},
                                                                                 "pager": {"startNo": "", "endNo": ""}}}
        return data

    def APP_SessionPost(self, third, url, post_data):  # 共用 session post方式 (Pc)
        header = {
            'User-Agent': userAgent,
            'Content-Type': 'application/json; charset=UTF-8',
        }
        try:
            session = requests.Session()
            # r = requests.post(env+'/%s/balance'%third,data=json.dumps(data_),headers=header)
            # print(env)
            r = session.post(env + '/%s/%s' % (third, url), headers=header, data=json.dumps(post_data))

            if 'balance' in url:
                balance = r.json()['body']['result']['balance']
                print('%s 的餘額為: %s' % (third, balance))
            elif 'getBalance' in url:
                balance = r.json()['body']['result']['balance']
                print('4.0餘額: %s' % balance)

        except requests.exceptions.ConnectionError:
            print(u'連線有問題,請稍等')

    def select_betTypeCode(self, conn, lotteryid, game_type):  # 從game_type 去對應玩法的數字,給app投注使用
        with conn.cursor() as cursor:
            sql = "select bet_type_code from game_bettype_status where lotteryid = '%s' and group_code_name||set_code_name||method_code_name = '%s'" % (
                lotteryid, game_type)

            cursor.execute(sql)
            rows = cursor.fetchall()

            bet_type = []
            for i in rows:  # i 生成tuple
                bet_type.append(i[0])
        conn.close()
        return bet_type

    @func_time
    def test_AppBalance(self):
        '''APP 4.0/第三方餘額'''
        threads = []
        user = self.user_g
        data_ = self.balance_data(user)
        third_list = ['gns', 'sb', 'im', 'ky', 'lc', 'city']
        print('帳號: %s' % user)
        for third in third_list:
            if third == 'shaba':
                third = 'sb'
            # r = requests.post(env+'/%s/balance'%third,data=json.dumps(data_),headers=header)
            t = threading.Thread(target=self.APP_SessionPost, args=(third, 'balance', data_))
            threads.append(t)
        t = threading.Thread(target=self.APP_SessionPost, args=('information', 'getBalance', data_))
        threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
            # print(r.json())
            # balance = r.json()['body']['result']['balance']
            # print('%s 的餘額為: %s'%(third,balance))
        '''
        r = requests.post(env+'/information/getBalance',data=json.dumps(data_),headers=header)
        balance =  r.json()['body']['result']['balance']
        print('4.0餘額: %s'%balance)
        '''

    @func_time
    def test_ApptransferIn(self):
        '''APP轉入'''
        user = self.user_g
        data_ = self.amount_data(user)
        print('帳號: %s' % user)
        third_list = ['gns', 'sb', 'im', 'ky', 'lc', 'city']
        for third in third_list:
            tran_url = 'Thirdly'  # gns規則不同
            if third == 'gns':
                tran_url = 'Gns'
            r = requests.post(env + '/%s/transferTo%s' % (third, tran_url), data=json.dumps(data_), headers=header)
            # print(r.json())#列印出來
            status = r.json()['body']['result']['status']
            if status == 'Y':
                print('轉入%s金額 10' % third)
            else:
                print('%s 轉入失敗' % third)
        for third in third_list:
            if third == 'sb':
                third = 'shaba'
            tran_result = Config.thirdly_tran(Config.my_con(evn=envs, third=third), tran_type=0, third=third,
                                              user=user)  # 先確認資料轉帳傳泰
            count = 0
            # print(status_list)
            while tran_result[1] != '2' and count != 16:  # 確認轉帳狀態,  2為成功 ,最多做10次
                tran_result = Config.thirdly_tran(Config.my_con(evn=envs, third=third), tran_type=0, third=third,
                                                  user=user)  #
                sleep(0.5)
                count += 1
                if count == 15:
                    print('轉帳狀態失敗')  # 如果跑道9次  需確認
                    # pass
            print('%s ,sn 單號: %s' % (third, tran_result[0]))
        self.test_AppBalance()

    @func_time
    def test_ApptransferOut(self):
        '''APP轉出'''
        user = self.user_g
        data_ = self.amount_data(user)
        print('帳號: %s' % user)
        third_list = ['gns', 'sb', 'im', 'ky', 'lc', 'city']
        for third in third_list:  # PC 沙巴 是 shaba , iapi 是 sb
            r = requests.post(env + '/%s/transferToFF' % third, data=json.dumps(data_), headers=header)
            # print(r.json())
            status = r.json()['body']['result']['status']
            if status == 'Y':
                print('%s轉出金額 10' % third)
            else:
                print('%s 轉出失敗' % third)
        for third in third_list:
            if third == 'sb':
                third = 'shaba'
            tran_result = Config.thirdly_tran(Config.my_con(evn=envs, third=third), tran_type=1, third=third,
                                              user=user)  # 先確認資料轉帳傳泰
            count = 0
            while tran_result[1] != '2' and count != 16:  # 確認轉帳狀態,  2為成功 ,最多做10次
                tran_result = Config.thirdly_tran(Config.my_con(evn=envs, third=third), tran_type=1, third=third,
                                                  user=user)  #
                sleep(1)
                count += 1
                if count == 15:
                    print('轉帳狀態失敗')  # 如果跑道9次  需確認

            print('%s, sn 單號: %s' % (third, tran_result[0]))
        self.test_AppBalance()