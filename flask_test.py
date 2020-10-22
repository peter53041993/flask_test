#!/usr/bin/env python
# coding: utf-8
import traceback,datetime,requests,json,os,random,threading,time,calendar,logging,urllib3,twstock, stock,re
from http.client import HTTPException
from flask import Flask, render_template, request, jsonify, redirect, make_response, url_for, Response, abort
from dateutil.relativedelta import relativedelta
import image_test,AutoTest,test_benefit,test_lotteryRecord,FF_Joy188,GameBox
from Utils import Config
from time import sleep
from flask import current_app
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.parse import urlsplit

app = Flask(__name__)  # name 為模塊名稱
logger = logging.getLogger('flask_test')
url_dict = {}  # 存放url 和街口狀態 , 給domain_ 用

class Flask():
    def iapi_login(envir):  # iapi 抓取沙巴token
        session = requests.Session()
        global headerSb
        global envSb
        envSb = Config.EnvConfigApp(envir)
        headerSb = {
            'User-Agent': Config.UserAgent.PC.value,
            'Content-Type': 'application/json'
        }

        if envir == 'dev02':
            user = 'hsieh100'
        elif envir == '188':
            user = 'kerr001'
        else:
            raise Exception('envir 參數錯誤')

        login_data = {
            "head": {
                "sessionId": ''},
            "body": {
                "param": {
                    "username": user + "|" + envSb.get_uuid(),
                    "loginpassSource": envSb.get_login_pass_source(),
                    "appCode": 1,
                    "uuid": envSb.get_uuid(),
                    "loginIp": 2130706433,
                    "device": 2,
                    "app_id": 9,
                    "come_from": "3",
                    "appname": "1"
                }
            }
        }
        r = session.post(envSb.get_iapi() + '/front/login', data=json.dumps(login_data), headers=headerSb)
        # print(r.text)
        global token
        token = r.json()['body']['result']['token']
        # print(token)


    def sb_game():  # iapi沙巴頁面
        session = requests.Session()

        data = {"head": {"sessionId": token}, "body": {"param": {"CGISESSID": token,
                                                                "loginIp": "10.13.20.57", "types": "1,0,t", "app_id": 9,
                                                                "come_from": "3", "appname": "1"}}}

        r = session.post(envSb.get_iapi() + '/sb/mobile', data=json.dumps(data), headers=headerSb)
        # print(r.text)
        global sb_url
        sb_url = r.json()['body']['result']['loginUrl']
        cookies = r.cookies.get_dict()


    def get_sb():  # 沙巴體育
        session = requests.Session()
        iapi_login('dev02')
        sb_game()
        # 抓取沙巴,token成功的方式, 先get 在post
        r = session.get(sb_url + '/', headers=headerSb)
        cookies = r.cookies.get_dict()
        r = session.post(sb_url + '/', headers=headerSb)

        headerSb['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        session = requests.Session()

        data = {
            'GameId': 1,
            'DateType': 't',
            'BetTypeClass': 'WhatsHot',
            # 'Matchid':''
        }
        url = 'http://smartsbtest.thirdlytest.st402019.com'
        # /Odds/ShowAllOdds ,   /Odds/GetMarket
        r = session.post(url + '/Odds/ShowAllOdds', headers=headerSb, data=data, cookies=cookies)

        global sb_list
        sb_list = []
        # print(r.json())
        game = r.json()['Data']['NewMatch']
        game_map = r.json()['Data']['TeamN']
        for dict_ in game:
            team1 = game_map[str(dict_['TeamId1'])]
            # team1 = game['TeamId1']
            team2 = game_map[str(dict_['TeamId2'])]
            # print(team1,team2,score1,score2)
            game_dict = {}
            for k in dict_:  # 字典的keys 找出來
                if k in ['MatchId', 'MarketId', 'T1V', 'T2V', 'TeamId1', 'TeamId2', 'Etm']:
                    game_dict[k] = dict_[k]
                game_dict['team1name'] = team1
                game_dict['team2name'] = team2
                date_day = dict_['Etm'].split('T')  # 將str 分割成 日棋 和時間
                d = datetime.datetime.strptime(date_day[0] + ' ' + date_day[1], '%Y-%m-%d %H:%M:%S')  # date_day 0為年月日, 1為時間
                # print(d)
                game_dict['Etm'] = (d + relativedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')  # 加12小時
            sb_list.append(game_dict)
        sb_list.sort(key=lambda k: (k.get('Etm', 0)))  # 列表裡包字典, 時間排序

        for i in sb_list:  # list取出各個字點
            # print(i['MatchId'])#抓出mathch id ,去對應 賠率
            data['Matchid'] = i['MatchId']
            r = session.post(url + '/Odds/GetMarket', headers=headerSb, data=data, cookies=cookies)
            # print(r.text)
            game_Odd = (r.json()['Data']['NewOdds'])
            # print(game_Odd)
            for odd in game_Odd:
                if odd['BetTypeId'] == 5:  # 抓 特定玩法
                    i['price1'] = odd['Selections']['1']['Price']  # 多增加賠率欄位
                    i['price2'] = odd['Selections']['2']['Price']
                    # game_list.append(i)
                else:
                    pass


    def date_time():  # 給查詢 獎期to_date時間用, 今天時間
        global today_time

        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        format_month = '{:02d}'.format(month)
        format_day = '{:02d}'.format(day)
        today_time = '%s-%s-%s' % (year, format_month, format_day)


    def test_sport(type_keys='全部'):  # 企鵝網
        header = {
            'User-Agent': Config.UserAgent.PC.value
        }
        type_ = {'全部': 0, "英超": 1}
        date_time()
        session = requests.Session()

        r = session.get('http://live.qq.com' +
                        '/api/calendar/game_list/%s/%s/%s' % (type_[type_keys], today_time, today_time),
                        headers=header)
        # print(r.json())
        # print(r.json())
        global sport_list
        sport_list = []  # 存放請求
        len_game = len(r.json()[today_time])  # 當天遊戲列表長度
        # print(r.json()[today_time])

        for game in range(len_game):  # 取出長度
            game_dict = r.json()[today_time][game]
            # print(game_dict)
            play_status = game_dict['play_status']
            # if play_status != '1':#1: 正在 ,2:比完, 3: 還未開打
            '''
            team1_name =game_dict['team1_name']
            team2_name = game_dict['team2_name']
            team1_score = game_dict['team1_score']
            team2_score = game_dict['team2_score']
            '''
            game_new = {}  # 把需要抓取的欄位 存放近來,  在把所有當天比賽放到game_list
            for i in game_dict.keys():
                if i in ['id', 'team1_id', 'team2_id', 'team1_name',
                        'team2_name', 'team1_score', 'team2_score', 'play_status', 'team1_icon',
                        'team2_icon', 'category_name']:
                    game_new[i] = game_dict[i]  # key = value
                else:
                    pass
            # print(game_new)
            sport_list.append(game_new)
            # else:
            # pass
        # print(game_new)
        # print(sport_list)


    # test_sport('全部')

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')


    @app.route('/showbio', methods=["GET"])
    def showbio():  # 提交submit後的頁面顯示
        username = request.args.get('username')
        email = request.args.get('email')
        hobbies = request.args.get('hobbies')
        return render_template("show_bio.html",
                            username=username,  # 前面username 傳回html的 ,後面username 是用戶填寫
                            email=email,
                            hobbies=hobbies)


    @app.route('/sport', methods=["GET"])
    def sport_():  # 體育比分
        test_sport()
        # return jsonify(game_list)
        return render_template('sport.html', sport_list=sport_list, today_time=today_time)


    @app.route('/sportApi', methods=['GET'])
    def sport_api():  # 體育api
        test_sport()
        return jsonify(sport_list)


    @app.route('/sb', methods=['GET'])
    def sb_():
        get_sb()
        date_time()
        return render_template('sb.html', sb_list=sb_list, today_time=today_time)


    @app.route('/sbApi', methods=['GET'])
    def sb_api():  # 體育api
        get_sb()
        return jsonify(sb_list)


    @app.route('/image', methods=['GET'])
    def image_():  # 調整圖片大小
        img_path = (os.path.join(os.path.expanduser("~"), 'Desktop'))
        return render_template('image.html', img_path=img_path)


    @app.route('/imageAdj', methods=["POST"])
    def imageAdj():
        testInfo = {}  # 存放 圖名,長,寬 的資料
        image_name = request.form.get('image_name')
        height = request.form.get('height')
        width = request.form.get('width')
        testInfo['image_name'] = image_name
        testInfo['height'] = height
        testInfo['width'] = width
        image_test.image_(image_name, height, width)  # 將圖名, 長,寬 回傳給 image_test檔案下 image_的 func使用
        msg = image_test.msg  # 宣告image_test方法裡 global msg變數
        testInfo['msg'] = msg

        return json.dumps(testInfo['msg'])

    @app.route('/autoTest', methods=["GET", "POST"])  # 自動化測試 頁面
    def autoTest():
        global lottery_name
        try:
            if request.method == "POST":
                logger.info('logged by app.module')
                current_app.logger.info('logged by current_app.logger')
                # response_status ='start_progress'
                # return redirect("/progress")
                testcase = []
                username = request.form.get('username')
                test_case = request.form.getlist('test_Suite')  # 回傳 測試案例data內容
                envConfig = Config.EnvConfig(request.form.get('env_type'))  # 初始化
                awardmode = request.form.get('awardmode')# 頁面獎金玩法選擇
                red = request.form.get('red_type')#紅包選擇
                money = request.form.get('moneymode')#金額模式
                submit_cancel = request.form.get('submit_cancel')# 投注完是否撤銷 , 0為否 , 1為是
                submit_plan =  request.form.get('test_PcPlan')# 追號使用
                lottery_name = request.form.get('lottery_name')#彩種選擇
                domain_url = envConfig.get_post_url().split('http://')[1]# 後台全局 url 需把 http做切割
                domain_type = envConfig.get_joint_venture(envConfig.get_env_id(),domain_url)# 查詢 後台是否有設置 該url 
                print(red,awardmode,lottery_name,type(awardmode))
                print(envConfig.get_post_url())# url
                AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(envConfig.get_env_id()),username,domain_type)  # 查詢用戶 userid
                userid = AutoTest.userid
                for test in test_case:
                    testcase.append(test)
                print(testcase)
                if len(userid) > 0:  # userid 值為空,　代表該ＤＢ　環境　沒有此用戶名　，　就不用做接下來的事
                    AutoTest.suite_test(testcase,username,envConfig.get_domain(),red,awardmode,money,submit_cancel,lottery_name)# 呼叫autoTest檔 的測試方法, 將頁面參數回傳到autoTest.py
                    return redirect('report')
                else:
                    # print(response_status)
                    return('此環境沒有該用戶')# 強制return 讓頁面location.reload
            else:
                lottery_dict = FF_Joy188.FF_().lottery_dict

            # return redirect("/report")
        except Exception as e:
            from Utils.TestTool import traceLog
            traceLog(e)
            abort(500)
        
        return render_template('autoTest.html',test=lottery_dict)


    @app.route("/report", methods=['GET'])
    def report():
        return render_template('report.html')


    @app.route('/progress')
    def progress():  # 執行測試案例時, 目前 還位判斷 request街口狀態,  需 日後補上
        def generate():
            x = 0
            # global response_status
            # print(response_status)
            while x <= 100:
                # print(response_status)
                yield "data:" + str(x) + "\n\n"  # data內容, 換行
                x = x + 1
                sleep(0.5)
            # yield "data:"+ str(100)

        return Response(generate(), mimetype='text/event-stream')


    @app.route('/benefit', methods=["GET", "POST"])  # 日工資頁面  按鈕提交後, 在導往  benefit_日工資/分紅頁面
    def benefit():
        if request.method == "POST":
            testInfo = {}  # 存放資廖
            cookies_dict = {}  # 存放cookie
            global result  # 日工資 data資料

            cookies_ = request.cookies  # 目前的改瀏覽器上的cookie
            print(cookies_)

            benefit_type = request.form.get('benefit_type')
            username = request.form.get('username')
            month = request.form.get('month')
            day = request.form.get('day')
            env = request.form.get('env')
            testInfo['benefit_type'] = benefit_type
            testInfo['username'] = username
            testInfo['month'] = month
            testInfo['day'] = day
            testInfo['env'] = env
            envConfig = Config.EnvConfig(request.form.get('env'))
            AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(envConfig.get_env_id()),username,'')
            if len(AutoTest.userid) == 0:
                return '此環境沒有該用戶'
            print(testInfo)  # 方便看資料用

            if env not in cookies_.keys():  # 請求裡面 沒有 這些環境cookie,就再登入各環境後台
                test_benefit.admin_Login(env)  # 登入生產環境 後台
                admin_cookie = test_benefit.admin_cookie  # 呼叫  此function ,

                cookies_dict[env] = admin_cookie['admin_cookie']
                cookies = admin_cookie['admin_cookie']
                # print(cookies_dict)
            else:
                cookies = cookies_[env]  # cookies_已經有了, 就直接使用

            if benefit_type == 'day':
                test_benefit.game_report_day(user=username, month=int(month), day=int(day), cookies=cookies, env=env)
                result = test_benefit.result_data
                print(result)
                if result['msg'] == '你輸入的日期或姓名不符,請再確認':  # 有cookie, 但cookie失效, 需再重新做
                    test_benefit.admin_Login(env)
                    admin_cookie = test_benefit.admin_cookie  # 呼叫  此function ,
                    cookies_dict[env] = admin_cookie['admin_cookie']
                    cookies = admin_cookie['admin_cookie']
                    test_benefit.game_report_day(user=username, month=int(month), day=int(day), cookies=cookies, env=env)
                    result = test_benefit.result_data
                    res = redirect('benefit_day')
                else:
                    res = redirect('benefit_day')
                if cookies_dict == {}:  # 會為空 代表,瀏覽器 有存在的cookie. 不用再額外在set
                    pass
                else:
                    res.set_cookie(env, cookies_dict[env])
                return res
            elif benefit_type == 'month':  # 需將 頁面獲得的 0或1  轉帳 日期 上半月: 15 ,下半月: 當月最後一天
                # print(type(day))
                print(type(day), day)
                if day == '0':
                    day = 15
                elif day == '1':
                    now = datetime.datetime.now()
                    day = calendar.monthrange(now.year, int(month))[1]  # 獲取當月 最後一天
                test_benefit.game_report_month(user=username, month=int(month), day=int(day), cookies=cookies, env=env)
                result = test_benefit.result_data
                res = redirect('benefit_month')
                if cookies_dict == {}:
                    pass
                else:
                    res.set_cookie(env, cookies_dict[env])
                return res
            else:
                print('福利中心 類型錯誤')
        return render_template('benefit.html')  # 這邊是 單存get,表單填寫頁面


    @app.route('/benefit_day', methods=["GET"])
    def benefit_day():
        return render_template('benefit_day.html', result=result)


    @app.route('/benefit_month', methods=["GET"])
    def benefit_month():
        return render_template('benefit_month.html', result=result)


    @app.route('/report_APP', methods=["GET", "POST"])  # APP戰報
    def report_APP():
        global result
        if request.method == 'POST':
            envtype = request.form.get('env_type')
            print(envtype)
            if envtype == 'dev':
                env = 0
            else:  # 188
                env = 1
            test_lotteryRecord.all_lottery(env)
            result = test_lotteryRecord.result

            return redirect('report_AppData')

        return render_template('report_APP.html')


    @app.route('/report_AppData', methods=["GET"])  # APP戰報資料顯示
    def report_AppData():
        return render_template('report_AppData.html', result=result)


    @app.route('/domain_list', methods=["GET"])  # 域名列表測試,抓取 http://172.16.210.101/domain_list  提供的 網域
    def domain_list():
        return render_template('domain_list.html')


    def domain_get(self,url):# domain_list , url 訪問後  ,回傳 url_dict
        urllib3.disable_warnings()  # 解決 會跳出 request InsecureRequestWarning問題
        header = {
            'User-Agent': FF_Joy188.FF_().user_agent['Pc']
        }
        global r, url_dict
        try:
            r = requests.get(url + '/', headers=header, verify=False, timeout=5)
        except:
            pass
        url_dict[url] = r.status_code
        # print(url_dict)


    @app.route('/domain_status', methods=["GET"])
    def domain_status():  # 查詢domain_list 所有網域的  url 接口狀態
        global url_dict
        urllib3.disable_warnings()  # 解決 會跳出 request InsecureRequestWarning問題
        print(request.url)#"http://3eeb8f01ffe7.ngrok.io/domain_status"
        url_split = urlsplit(request.url)
        request_url = "%s://%s"%(url_split.scheme,url_split.netloc)# 動態切割 當前url
        header = {
            'User-Agent': FF_Joy188.FF_().user_agent['Pc']
        }
        r = requests.get(request_url + '/domain_list', headers=header)
        # print(r.text)
        soup = BeautifulSoup(r.text, 'lxml')
        url_dict = {}  # 存放url 和 皆口狀態
        try:  # 過濾 從頁面上抓取的url, 有些沒帶http
            for i in soup.find_all('table', {'class': 'domain_table'}):
                for a in i.find_all('a'):
                    if 'http' not in a.text:
                        url = 'http://' + a.text
                        url_dict[url] = ''  # 先存訪到url_dict
                    else:  # 這邊提供的  頁面 不用做額外處理, 就是 a.text
                        url_dict[a.text] = ''
            threads = []
            for url_key in url_dict:
                threads.append(threading.Thread(target= Flask().domain_get, args=(url_key,)))
            for i in threads:
                i.start()
            for i in threads:
                i.join()
        except requests.Timeout as e:
            pass
        except urllib3.exceptions.NewConnectionError as e:
            print(e)
        print(url_dict)
        return url_dict
        # return render_template('domain_status.html',url_dict=url_dict)


    @app.route('/stock_search', methods=["GET", "POST"])
    def stock_search():
        stock_detail = {}
        try:
            if request.method == "POST":
                stock_num = request.form.get('stock_search')
                stock_name = request.form.get('stock_search2')
                print(stock_num,stock_name)#股票號碼,股票名稱
                if stock_name not in  [None,'']:# 代表頁面 輸入名稱 , 先從DB 找 有沒有該名稱,在去yahoo找
                    stock.stock_selectname(stock.kerr_conn(),stock_name)#找出相關資訊
                    stock_detail2 = stock.stock_detail2
                    if len(stock_detail2) == 0:# 名稱營收db為空的, 就不列印營收資訊
                        return('沒有該股票名稱: %s'%stock_name)
                    else:# DB有找到該名稱 ,
                        stock_deatil2 = stock.stock_detail2
                        print(stock_deatil2)
                        stock_num = str(list(stock_deatil2.values())[0][1])#號碼
                        stock.df_test(stock_num)
                        stock.df_test2(stock_num)
                        now = stock.now#查詢時間
                        latest_close = stock.latest_close#最新收盤
                        latest_open = stock.latest_open
                        latest_high = stock.latest_high
                        latest_low = stock.latest_low
                        latest_volume = stock.latest_volume
                else:# 輸入號碼 ,和頁面輸入名稱流程不同,  有號碼 先從yahoo直接去找
                    try:
                        stock_name = twstock.codes[stock_num][2]
                        stock.df_test(stock_num)
                        stock.df_test2(stock_num)
                        now = stock.now#查詢時間
                        latest_close = stock.latest_close#最新收盤
                        latest_open = stock.latest_open
                        latest_high = stock.latest_high
                        latest_low = stock.latest_low
                        latest_volume = stock.latest_volume
                    except KeyError:
                        return('沒有該股票號碼: %s'%stock_num)#yahoo沒有,DB正常就不會有
                    stock.stock_selectnum(stock.kerr_conn(),int(stock_num))# 有股號後, 從mysql 抓出更多資訊
                    stock_detail2 = stock.stock_detail2
                    if len(stock_detail2) == 0:# 營收db為空的,但 yahoo查詢是有該股的, 就不列印營收資訊 ,
                        data ={"股票名稱":stock_name,'股票號碼':stock_num,"目前股價":latest_close,
                        '開盤':latest_open,'高點': latest_high,'低點': latest_low,'成交量':latest_volume,
                        "查詢時間":now
                        }
                        frame = pd.DataFrame(data,index=[0])
                        print(frame)
                        return(frame.to_html())
                    else:# yahoo有, DB也有, 就是多列印 營收
                        pass# 走到下面  和輸入 名稱  共用  營收邏輯
                    
                # 有營收, 輸入號碼 和輸入 名稱 共用
                stock_curMonRev = list(stock_detail2.values())[0][4]
                stock_lastMonRev = list(stock_detail2.values())[0][5]
                stock_lastYearMonRev=list(stock_detail2.values())[0][6]
                stock_lastMonRate=list(stock_detail2.values())[0][7]
                stock_lastYearMonRate=list(stock_detail2.values())[0][8]
                stock_curYearRev=list(stock_detail2.values())[0][9]
                stock_lastYearRev=list(stock_detail2.values())[0][10]
                stock_lastYearRate=list(stock_detail2.values())[0][11]
                stock_memo=list(stock_detail2.values())[0][12]
                data ={"股票名稱":stock_name,'股票號碼':stock_num,"目前股價":latest_close,
                '開盤':latest_open,'高點': latest_high,'低點': latest_low,'成交量':latest_volume,
                "當月營收":stock_curMonRev,'上月營收':stock_lastMonRev,'去年當月': stock_lastYearMonRev,"上月營收增":stock_lastMonRate,
                '去年同月營收增減':stock_lastYearMonRate,'今年營收':stock_curYearRev,'去年營收':stock_lastYearRev,'去年營收增減': stock_lastYearRate,'股票備注':stock_memo, "查詢時間":now
                }
                now_hour = datetime.datetime.now().hour #現在時間 :時
                weekday = datetime.date.today().weekday()+1#現在時間 :周, 需加1 , 禮拜一為0
                print('現在時數: %s,禮拜:%s'%(now_hour,weekday))
                if now_hour > 14 or weekday in [6,7] :
                    print('大於最後成交時間或者六日,不再做更新股價')
                else:
                    print(stock.stock_detail2)  # mysql抓出來的 資訊
                    '''
                    stock_prize = (stock_detail['realtime']['latest_trade_price'])  # 股票 最新一筆成交價
                    print(stock_prize, type(stock_prize))  # 為一個 str ,需把 小數點  . 三和四 去除掉
                    if stock_prize == '-':  # 抓出來 是  "-"  就先不理會,給一個值0
                        stock_prize = 0
                    else:
                        stock_prize = stock_prize[0:-2]  # 後面兩個00不用,   到小數電第四位即可
                    # stock_prize = stock_prize[0:-2]# 後面兩個00不用,   到小數電第四位即可
                    print(stock_prize)
                    '''

                    stock.stock_update(stock.kerr_conn(), float(latest_close), int(stock_num))  # 將股價 Update進去 Mysql

                    '''
                    data = {"股票名稱": stock_detail['info']['name'], "目前股價": latest_close,
                            "開盤": latest_open,
                            "高點": stock_detail['realtime']['high'], "低點": stock_detail['realtime']['low'],
                            "查詢時間": stock_detail['info']['time']}
                    '''
                frame = pd.DataFrame(data, index=[0])
                print(frame)
                # print(frame.to_html())
                return frame.to_html()
            return render_template('stock.html')
        except requests.exceptions.Timeout as e:
            print(e)


    @app.route('/stock_search2', methods=["POST"])
    def stock_search2():
        stock_type = request.form.getlist('Revenue')
        print(stock_type)
        stock.stock_select2(stock.kerr_conn(),stock_type)  # select 出來
        stock_detail3 = stock.stock_detail3
        stock_num, stock_name, stock_prize, stock_curMonRev, stock_lastMonRev, stock_lastYearMonRev, stock_lastMonRate, stock_lastYearMonRate, stock_curYearRev, stock_lastYearRev, stock_lastYearRate, stock_memo = [], [], [], [], [], [], [], [], [], [], [], []

        for num in stock_detail3.keys():
            stock_num.append(stock_detail3[num][1])
            stock_name.append(stock_detail3[num][2])
            try:
                if stock_detail3[num][3] == 0:  # 股價是0,代表還沒有Update 股價過

                    stock_detail = twstock.realtime.get(str(stock_detail3[num][1]))
                    print(stock_detail)
                    prize = (stock_detail['realtime']['latest_trade_price'])  # 股票 最新一筆成交價
                    if prize == '-':  # 抓出來 是  "-"  就先不理會,給一個值0
                        prize = 0
                    else:
                        prize = prize[0:-2]  # 後面兩個00不用,   到小數電第四位即可
                    print(prize, type(prize))
                    stock_prize.append(prize)
                    stock.stock_update(stock.kerr_conn(), float(prize),
                                    int(stock_detail3[num][1]))  # 將股價 Update進去 Mysql
                else:
                    stock_prize.append(stock_detail3[num][3])
            except requests.exceptions.ConnectionError:
                print('連線失敗')
                stock_prize.append(stock_detail3[num][3])
            stock_curMonRev.append(stock_detail3[num][4])
            stock_lastMonRev.append(stock_detail3[num][5])
            stock_lastYearMonRev.append(stock_detail3[num][6])
            stock_lastMonRate.append(stock_detail3[num][7])
            stock_lastYearMonRate.append(stock_detail3[num][8])
            stock_curYearRev.append(stock_detail3[num][9])
            stock_lastYearRev.append(stock_detail3[num][10])
            stock_lastYearRate.append(stock_detail3[num][11])
            stock_memo.append(stock_detail3[num][12])

        # print(stock_num,stock_name,stock_prize,stock_curMonRev,stock_lastMonRev,stock_lastYearMonRev,stock_lastMonRate,stock_lastYearMonRate,stock_curYearRev,stock_lastYearRev,stock_lastYearRate,stock_memo)
        print(stock_prize)

        data = {'股票號碼': stock_num, "股票名稱": stock_name, "股價": stock_prize, "當月營收": stock_curMonRev,
                "上月營收增減": stock_lastMonRate,
                '去年同月營收增減': stock_lastYearMonRate, '今年營收': stock_curYearRev, '去年營收': stock_lastYearRev,
                '去年營收增減': stock_lastYearRate, '股票備注': stock_memo}
        frame = pd.DataFrame(data)
        print(frame)
        # print(frame.to_html())
        return frame.to_html()
    def number_map(number_record):# 開獎號使用
        if number_record == '':
            return  ''
        play_dict = {}
        print(number_record)
        if lottery_name == 'PC蛋蛋':
            sum_ = 0
            try:
                for i in number_record:
                    sum_ = sum_ + int(i)
            except ValueError as e:
                print(e)
            for i in range(27):# PC蛋蛋個號碼mapping 顏色 
                if i in [0,13,14,27]:
                    number_color = '灰'
                elif i in [1,4,7,10,16,19,22,25]:
                    number_color = '綠'
                elif i in [2,5,8,1,11,17,20,23,26]:
                    number_color = '藍'
                else:
                    number_color = '紅'
                play_dict[i] = number_color
            record  =  number_record + "#總和:%s, 顏色:%s"%(sum_,play_dict[sum_])
            return record
        else:
            return number_record

    def game_map(type_=''):  # 玩法 和 說明 mapping,type_ 預設  '' ,為玩法說明,  不是 '' ,走其他邏輯
        global game_playtype,game_theory,bonus,data  # 說明, 玩法
        if lottery_name  in ['slmmc']:
            if '五星' in game_playtype:
                if game_playtype in ['复式', '单式']:
                    game_explan = '#五個號碼順續需全相同'
                elif '组选120' in game_playtype:
                    game_explan = '#五個號碼相同,順續無需相同(開獎號無重覆號碼)'
            game_cal = 'test'
        elif lottery_name == '凤凰比特币冲天炮':
            game_theory = round(float(game_submit)/0.9,2)#快開  理論將金 另外算
            game_cal = '%s*%s=%s'%(game_amount,game_submit,float(game_submit)*game_amount)
            #'%s*(%s+%s*%s)'%(game_amount,game_submit,game_theory,game_point)# 獎金計算  原本公式 ,現在變成 直皆投注高度*金額
            game_explan = game_cal+ '/獎金計算: 投注金額*投注內容#快開改後不帶返點' #'獎金計算: 投注金額*(投注內容+理論獎金*反點)'
            bonus = (float(game_submit)+game_theory*game_point)
            data['中獎率'] = '0.95/投注內容%s=%s'%(game_submit,round(0.95/float(game_submit),4))
            data['理論獎金'] = str(game_theory)+"(投注內容/0.9)#快開改後不適用"
            data['獎金模式'] = "快開改前: %s"%bonus
            data['中獎獎金'] = '改前: %s/改後: %s'%(game_amount*bonus,game_award)
            del data['反點獎金']# 快開沒參考價值
            del data['平台獎金']
        elif lottery_name  =='PC蛋蛋':
            if type_ =='':
                theory_data = data['理論獎金']# ex : [1,2,3,4,5] 
                theory_data[0] = str(theory_data[0]) + "#理論賠率"# 只取列表第一個值 +  說明
                data['理論獎金'] = theory_data

                game_explan = '賠率=獎金#一注1元'
            else:
                pcdd_sum = {}
                if bet_type_code == '66_28_71':#PC蛋蛋  和值玩法, 要錯特殊處理
                    for i in range(28):#0-28 和值
                        if i < 13: 
                            a = i + 72
                        elif i in (13,14):
                            a = 85
                        else:
                            a = 99 - i
                        pcdd_sum[str(i)] = str(a)# a 是傳回 個和值 數值 的 獎金
                elif bet_type_code == '66_13_84': #色波
                    pcdd_sum['RED'] =  '88'
                    pcdd_sum['GREEN'] = '89'
                    pcdd_sum['BLUE'] = '90'
                elif bet_type_code == '66_74_107':# 大單,大雙 系列
                    pcdd_sum['DADAN'] = '47'
                    pcdd_sum['DASHUNG'] = '48'
                    pcdd_sum['XIAODAN'] = '49'
                    pcdd_sum['XIAOSHUNG'] = '50'
                return pcdd_sum
        else:
            game_explan = '#未補上'
            theory_data = data['理論獎金']# ex : [1,2,3,4,5] 
            theory_data[0] = str(theory_data[0]) + "#未補上"# 只取列表第一個值 +  說明
            data['理論獎金'] = theory_data
        #data['獎金計算'] = game_cal
        data['遊戲說明'] = game_explan
    @app.route('/stock_search3',methods=["POST"])    
    def stock_search3():
        stock.stock_search3(stock.kerr_conn())
        stock_detail = stock.stock_detail3
    def status_style(val):  # 判斷狀態,來顯示顏色屬性 , 給 game_order 裡的order_status用
        if val == '中獎':
            color = 'blue'
        elif val == '未中獎':
            color = 'red'
        else:
            pass
        return ('color:%s' % color)
    @app.route('/get_cookie',methods=["GET"])
    def get_cookie():# 存放cookie皆口
        return cookie

    @app.route('/game_result', methods=["GET", "POST"])  # 查詢方案紀錄定單號
    def game_result():
        global game_playtype,game_amount,game_submit,game_point,lottery_name,game_theory,bonus,data,game_award,bet_type_code,len_game

        if request.method == "POST":
            game_code = request.form.get('game_code')  # 訂單號
            game_type = request.form.get('game_type')  # 玩法
            env = request.form.get('env_type')  # 環境
            envConfig = Config.EnvConfig(request.form.get('env_type'))
            cookies_ = request.cookies  # 瀏覽器上的cookie
            session = requests.Session()
            print(cookies_,envConfig.get_admin_url())
            if env == 'dev02':  # 傳給DB 環境 get_conn(env)用
                envs = 0
            else:
                envs = 1
            if game_code != '':  # game_code 不為空,代表前台 是輸入 訂單號
                AutoTest.Joy188Test.select_gameResult(AutoTest.Joy188Test.get_conn(envs), game_code)  # 傳回此方法.找出相關 訂單細節
                game_detail = AutoTest.game_detail  # 將 global  game_detail 宣告變數 遊戲訂單的 內容
                len_game = len(game_detail)
                print(game_detail)
                if len_game == 0:
                    return "此環境沒有此訂單號"
                else:
                    index_list,game_code_list,game_time_list,game_status_list,game_play_list,game_awardname_list = [],[],[],[],[],[]
                    lotteryid_list,game_submit_list,theory_bonus_list,ff_bonus_list,game_point_list,bonus_list  = [],[],[],[],[],[]
                    game_amount_list,game_retaward_list,game_moneymode_list,game_mul_list,game_award_list =[],[],[],[],[]
                    game_awardmode_list = []
                    issue_code = game_detail[0][19]#旗號
                    lotteryid = game_detail[0][14]#彩種id
                    AutoTest.Joy188Test.select_numberRecord(AutoTest.Joy188Test.get_conn(envs),lotteryid,issue_code)  
                    number_record = AutoTest.number_record[0]#開獎號
                    for key in game_detail.keys():
                        print(key)
                        index_list.append(key)
                        game_code_list.append(game_code)#訂單號
                        game_time_list.append(game_detail[key][0])
                        game_status = game_detail[key][1]  # 需判斷  訂單狀態
                        if game_status == 1:
                            game_status = '等待開獎'
                        elif game_status == 2:
                            game_status = '中獎'
                        elif game_status == 3:
                            game_status = '未中獎'
                        elif game_status == 4:
                            game_status = '撤銷'
                        else:
                            game_status = '待確認'
                        game_status_list.append(game_status)
                        lottery_name = game_detail[key][3]
                        game_playtype = game_detail[key][4] + game_detail[key][5] + game_detail[key][6]
                        game_play_list.append(lottery_name+"/"+game_playtype)
                        game_awardname_list.append(game_detail[key][8])
                        bet_type_code = game_detail[key][15]#玩法
                        theory_bonus = game_detail[key][16]#理論獎金
                        
                        game_submit = game_detail[key][7]#投注內容
                        game_submit_list.append(game_submit)
                        '''
                        if theory_bonus == 0:  # 理論獎金為0, 代表一個完髮有可能有不同獎金
                            bonus = []
                            print('有多獎金玩法'+bet_type_code)
                            for i in soup.find_all('span', id=re.compile("^(%s)" % bet_type_code)):
                                bonus.append(float(i.text))  # 有多個獎金
                            FF_bonus = " ".join([str(x) for x in bonus])  # 原本bonus裡面裝 float  .需list裡轉成字元,
                        
                        else:
                        '''    
                        if lottery_name == 'PC蛋蛋':
                            if bet_type_code not in ['66_28_71','66_13_84','66_74_107']:# 同個玩法只有單一賠率 
                                AutoTest.Joy188Test.select_bonus(AutoTest.Joy188Test.get_conn(envs),lotteryid,bet_type_code)# 使用bet_type_code like
                            else:
                                game_map = Flask.game_map(type_=1)  # 呼叫玩法說明/遊戲mapping 
                                print(game_map)
                                if bet_type_code  == '66_13_84': #色波
                                    color_dict = {
                                        "红": "RED",
                                        "绿": "GREEN",
                                        "蓝": "BLUE"
                                    }
                                    game_submit = color_dict[game_submit]# 換成 英文 , 因為要再去select_bonus  找  獎金
                                elif bet_type_code == '66_74_107': #大單,大雙,,,,,,
                                    color_dict = {
                                        "大双": "DASHUNG", 
                                        "小双": "XIAOSHUNG",
                                        "大单": "DADAN",
                                        "小单": "XIAODAN"                               
                                        }
                                    game_submit = color_dict[game_submit]# 換成 英文 , 因為要再去select_bonus  找  獎金
                                else: #和值
                                    
                                    pass# 和值 0 -27 ,投注內容 keys不用做Mapping
                                #print(game_submit)
                                point_id =  bet_type_code + "_"+ game_map[game_submit]# 前面bet_type_code一致, _後面 動態
                                
                                #相同賠率 有不同完髮的(ex: 投注內容 0和27, 賠率都是 900 ), 需再把 投注內容game_submit 進去 找  
                                AutoTest.Joy188Test.select_bonus(AutoTest.Joy188Test.get_conn(envs),lotteryid,point_id,game_submit)
                            pc_dd_bonus = AutoTest.bonus
                            theory_bonus = pc_dd_bonus[0][1]/10000
                            FF_bonus =  pc_dd_bonus[0][0]/10000
                            #print(theory_bonus,FF_bonus)
                        else:# 其他大眾彩種
                            theory_bonus = theory_bonus/10000# 理論將金
                            point_id = bet_type_code + "_" + str(theory_bonus)  # 由bet_type_code + theory_bonus 串在一起(投注方式+理論獎金])
                            #for i in soup.find_all('span', id=re.compile("^(%s)" % point_id)):  # {'id':point_id}):
                                #FF_bonus = float(i.text)
                            award_group_id = game_detail[key][17]#用來查詢 用戶 獎金組 屬於哪種
                            AutoTest.Joy188Test.select_bonus(AutoTest.Joy188Test.get_conn(envs),lotteryid,bet_type_code,award_group_id)# 使用bet_type_code like
                            pc_dd_bonus = AutoTest.bonus
                            FF_bonus =  pc_dd_bonus[0][0]/10000
                        theory_bonus_list.append(theory_bonus)
                        ff_bonus_list.append(FF_bonus)
                        game_point = float(game_detail[key][18]/10000)
                        game_point_list.append(game_point)
                        game_retaward = float(game_detail[key][10] / 10000)  # 反點獎金 需除1萬
                        game_retaward_list.append(game_retaward)
                        game_awardmode = game_detail[key][9]  # 是否為高獎金
                        if game_awardmode == 1:
                            game_awardmode = '否'
                            bonus = '%s - %s'%(FF_bonus,game_point)
                        else: 
                            game_awardmode = '是'
                            bonus = game_retaward + FF_bonus  # 高獎金的話, 獎金 模式 + 反點獎金
                        game_awardmode_list.append(game_awardmode)
                        bonus_list.append(bonus)
                        game_amount = float(game_detail[key][2] / 10000)  # 投注金額  需在除 1萬
                        game_amount_list.append(game_amount)
                        game_moneymode = game_detail[key][12]  # 元角分模式 , 1:元, 2: 角
                        if game_moneymode == 1:
                            game_moneymode = '元'
                        elif game_moneymode == 2:
                            game_moneymode = '角'
                        else:
                            game_moneymode = '分'
                        game_moneymode_list.append(game_moneymode)
                        game_mul_list.append(game_detail[key][11])
                        game_award = float(game_detail[key][13] / 10000)  # 中獎獎金
                        game_award_list.append(game_award)
                    if number_record is None:
                            number_record = ''
                    record_mapping = Flask.number_map(number_record)
                    number_record = record_mapping
                    print(number_record)
                    data = {"遊戲訂單號": game_code_list, "訂單時間": game_time_list, "中獎狀態": game_status_list,
                           "投注彩種/投注玩法":game_play_list,
                            "獎金組": game_awardname_list,"獎金模式狀態": game_awardmode_list,
                            '理論獎金': theory_bonus_list,"平台獎金": ff_bonus_list,"投注金額": game_amount_list,
                            "投注倍數": game_mul_list,"元角分模式": game_moneymode_list,
                            "投注內容": game_submit_list,'用戶反點':game_point_list, "獎金模式": bonus_list,
                            "反點獎金": game_retaward_list, "中獎獎金": game_award_list,"開獎號": number_record
                            }
                    game_map = Flask.game_map()  # 呼叫玩法說明
                    frame = pd.DataFrame(data, index=index_list)
                    return frame.to_html()
            elif game_type != '':  # game_type 不為空,拜表前台輸入 指定玩法
                if "_" in game_type:  # 把頁面輸入  _   去除
                    print('有_需移除')
                    if "2000" in game_type:  # 超級2000 在DB格式 前面 多帶 _ ,不能移除
                        test_list = []  # 存放 超級2000 後新的列表,並join 新的 game_type
                        for i in game_type.split('_'):
                            if "2000" in i:
                                i = i + "_"
                            test_list.append(i)  # 新的列表
                        game_type = "".join(test_list)  # 超級2000符合的 DB mapping
                    else:
                        game_type = game_type.replace("_", "")  # 不是超級2000, _ 就值皆去除
                elif game_type[-1] == " ":  # 判斷輸入後面多增加空格:
                    print('輸入玩法 有空格需去除掉')
                    game_type = game_type.replace(' ', '')
                print(game_type)
                AutoTest.Joy188Test.select_gameorder(AutoTest.Joy188Test.get_conn(envs), '%' + game_type + '%')
                game_order = AutoTest.game_order
                len_order = AutoTest.len_order
                if len_order == 0:
                    return '沒有該玩法'
                order_list = []  # 因為可能有好幾個訂單,  傳入 dataframe 需為列表 ,訂單
                order_time = []  # 時間
                order_lottery = []  # 採種
                order_type = []  # 玩法
                order_status = []  # 狀態
                order_user = []  # 用戶名
                order_detail = []  # 投注內容
                order_record = []  # 開獎號碼
                order_awardmode = []#獎金模式
                for len_ in range(len_order):  # 取出長度
                    order_list.append(game_order[len_][2])  # 2為訂單號.
                    order_time.append(game_order[len_][1])
                    order_lottery.append(game_order[len_][0])
                    order_type.append(game_order[len_][3] + game_order[len_][4] + game_order[len_][5])
                    if game_order[len_][6] == 1:
                        game_order[len_][6] = '等待開獎'
                    elif game_order[len_][6] == 2:
                        game_order[len_][6] = '中獎'
                    elif game_order[len_][6] == 3:
                        game_order[len_][6] = '未中獎'
                    elif game_order[len_][6] == 4:
                        game_order[len_][6] = '撤銷'
                    else:
                        game_order[len_][6] = '確認狀態'              
                    order_status.append(game_order[len_][6])
                    order_user.append(game_order[len_][7])
                    order_detail.append(game_order[len_][8])
                    order_record.append(game_order[len_][9])
                    if game_order[len_][10] == 1:
                        awardmode = "一般獎金"
                    else:
                        awardmode= '高獎金'
                    order_awardmode.append(awardmode)
                # print(order_list)
                data = {"訂單號": order_list, "用戶名": order_user, "投注時間": order_time, "投注彩種": order_lottery, "投注玩法": order_type,
                        "投注內容": order_detail, "獎金模式":order_awardmode,"開獎號碼": order_record, "中獎狀態": order_status}
                frame = pd.DataFrame(data)
                # test = frame.style.applymap(status_style)#增加狀態顏色 ,這是for jupyter_notebook可以直接使用
                print(frame)
                return frame.to_html()

        return render_template('game_result.html')


    @app.route('/user_active', methods=["POST", "GET"])
    def user_acitve():  # 驗證第三方有校用戶
        if request.method == "POST":
            user = request.form.get('user')
            env = request.form.get('env_type')
            joint_type = request.form.get('joint_type')
            if env == 'dev02':
                envs = 0
            elif env == 'joy188':
                envs = 1
            else:
                envs = 2
            AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(envs),user,int(joint_type))
            #查詢用戶 userid
            userid = AutoTest.userid
            print(user, env)
            if len(userid) == 0:
                return ("此環境沒有該用戶")
            else:
                AutoTest.Joy188Test.select_activeAPP(AutoTest.Joy188Test.get_conn(envs), user)
                # 查詢APP有效用戶 是否有值  ,沒值 代表 沒投注

                active_app = AutoTest.active_app  # 呼叫 此變數
                # print(active_user)
                bind_card = []  # 綁卡列表.可能超過多張
                card_number = []  # 該綁卡,有被多少張數綁定,但段 是否為有效性
    

                AutoTest.Joy188Test.select_activeFund(AutoTest.Joy188Test.get_conn(envs), user)  # 當月充值
                user_fund = AutoTest.user_fund
                print(user_fund)
                AutoTest.Joy188Test.select_activeCard(AutoTest.Joy188Test.get_conn(envs), user, envs)  # 查詢綁卡數量
                card_num = AutoTest.card_num  # 綁卡 和 該卡榜定幾張
                if len(active_app) == 0:  # 非有效用戶,也代表 APP 有效用戶表沒資料(舊式沒投注)
                    print("%s用戶 為非有效用戶" % user)
                    active_submit = 0  # 有效投注
                    is_active = "否"  # 有效用戶值
                    # AutoTest.Joy188Test.select_activeFund(AutoTest.Joy188Test.get_conn(envs),user)#當月充值
                    if user_fund[0] == None:  # 確認沒充值
                        real_charge = 0
                    else:
                        real_charge = float(user_fund[0]) / 10000  # 抓充值表, 顯示充值金額
                    if len(card_num) == 0:
                        print("綁卡數量為0")
                        bind_card = "沒有綁卡"
                        card_number = ""
                    else:
                        for card_ in card_num.keys():
                            print(card_)
                            print(bind_card)
                            bind_card.append(str(card_num[card_][0]))
                            card_number.append(str(card_num[card_][1]))
                        bind_card = " ,".join(bind_card)
                        card_number = " ,".join(card_number)
                    print(bind_card, card_number)
                else:  # 這邊長度非0, 是select_activeAPP 這方法,有值, 需判斷 is_active 是否為1
                    if active_app[2] == 0:  # 列表[1] = is_active,  值 0 非有效
                        is_active = "否"  # active_user[0][1]
                        print("%s用戶 為非有效用戶" % user)
                    else:
                        is_active = "是"  # active_user[0][1]
                        print("%s用戶 為有效用戶" % user)
                    active_submit = active_app[3]
                    if user_fund[0] == None:  # 確認沒充值
                        real_charge = 0
                    else:
                        real_charge = float(user_fund[0]) / 10000  # 抓充值表, 顯示充值金額

                    if len(card_num) == 0:
                        print("綁卡數量為0")
                        bind_card = "沒有綁卡"
                        card_number = ""
                    else:
                        for card_ in card_num.keys():
                            bind_card.append(str(card_num[card_][0]))
                            card_number.append(str(card_num[card_][1]))
                        bind_card = " ,".join(bind_card)
                        card_number = " ,".join(card_number)
                    print(bind_card, card_number)
                data = {"用戶名": user, "是否為有效用戶": is_active, "當月有效投注": active_submit,
                        "當月有效充值": real_charge, "銀行卡號": bind_card, "該卡號綁訂張數": card_number
                        }
                frame = pd.DataFrame(data, index=['是否為有效用戶'])
                print(frame)
                return frame.to_html()
        return render_template('user_active.html')


    @app.route('/app_bet', methods=["POST"])# 第三方 銷量計算
    def app_bet():
        user = request.form.get('user')
        env = request.form.get('env_type')
        joint = request.form.get('joint_type')
        if env == 'dev02':
            envs = 0
        elif env == 'joy188':
            envs = 1
        else:
            envs = 2
        AutoTest.Joy188Test.select_AppBet(AutoTest.Joy188Test.get_conn(envs), user)  # APP代理中心,銷量/盈虧
        AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(envs),user,int(joint))#查詢用戶 userid
        userid = AutoTest.userid
        print(userid)
        if len(userid) == 0:
            return('此環境沒有該用戶')
        app_bet = AutoTest.app_bet  # 銷量/盈虧
        third_list = []  # 存放第三方列表
        active_bet = []  # 第三方有效投注
        third_prize = []  # 第三方獎金
        third_report = []  # 第三方盈虧
        third_memo = []  # 第三方memo
        user_list = []
        for third in app_bet.keys():
            third_list.append(third)
            active_bet.append(app_bet[third][0])  # 有效銷量 為列表 1
            third_prize.append(app_bet[third][1])
            third_report.append(app_bet[third][2])
            if third == "ALL":
                user_list.append(user)
            else:
                user_list.append("")
            if third == "ALL":
                third_memo.append("用戶盈虧: 總獎金-有效銷量")
            elif third == 'CITY':
                third_memo.append("#後台投注紀錄盈虧值 為用戶角度")
            elif third == 'BBIN':
                third_memo.append('#獎金不會小於0')
            else:  # 待後續確認每個第三方 規則
                third_memo.append('')
        # print(user_list,active_bet,third_prize,third_report)

        data = {"用戶名": user_list,"有效銷量": active_bet, "總獎金": third_prize, "用戶盈虧": third_report,
                "備註": third_memo}
        frame = pd.DataFrame(data, index=third_list)
        print(frame)
        return frame.to_html()
    @app.route('/url_token',methods=["POST","GET"])    
    def url_token():
        domain_keys ={ # url 為 keys,values 0 為預設連結, 1為 DB環境參數 , 2 為預設註冊按紐顯示 
            'www.dev02.com': ['id=18408686&exp=1867031785352&pid=13438191&token=5705',0,'否','一般'],
            'www.fh82dev02.com': ['id=18416115&exp=1898836925873&pid=13518151&token=674d',0,'是','合營'],
            'www.teny2020dev02.com': ['id=18416115&exp=1898836925873&pid=13518151&token=674d',0,'是','合營'],
            'www.88hlqpdev02.com': ['id=18416447&exp=1900243129901&pid=13520850&token=c46d',0,'是','歡樂棋排'],
            'www2.joy188.com':['id=23629565&exp=1870143471538&pid=14055451&token=e609',1,'否','一般'],
            'www2.joy188.195353.com':['id=30402641&exp=1899103987027&pid=14083381&token=f2ae',1,'是','合營'],
            'www2.joy188.maike2020.com':['id=30402641&exp=1899103987027&pid=14083381&token=f2ae',1,'是','合營'],
            'www2.joy188.teny2020.com':['id=30402641&exp=1899103987027&pid=14083381&token=f2ae',1,'是','合營'],
            'www2.joy188.88hlqp.com':['id=30402801&exp=1900315909746&pid=14084670&token=296f',1,'是','歡樂棋排'],
            'www.88hlqp.com': ['id=12724515&exp=1900124358942&pid=23143290&token=60f9',2,'是','歡樂棋排'],
            'www.maike2020.com':['id=12569709&exp=1900396646000&pid=23075061&token=f943',2,'是','合營'],
            'www.maike2021.com':['id=12569709&exp=1900396646000&pid=23075061&token=f943',2,'是','合營'],
            'www.maike2022.com':['id=12569709&exp=1900396646000&pid=23075061&token=f943',2,'是','合營'],
            'www.maike2023.com':['id=12569709&exp=1900396646000&pid=23075061&token=f943',2,'是','合營'],
            'www.teny2020.com':['id=12727731&exp=1900585598288&pid=23119541&token=60ac&qq=7769700',2,'是','合營'],
            'www.fh82.com':['id=12464874&exp=1883450993237&pid=2163831&token=b12f&qq=1055108800',1,'是','一般'],
            'www.fhhy2020.com':['',2,'待確認','合營'],
            'www.fh888.bet':['',2,'待確認','合營'],
            'www.fh666.bet':['',2,'待確認','合營']
        }
        if request.method == "POST":
            token = request.form.get('token')
            id_ = request.form.get('id')
            user = request.form.get('user')
            env = request.form.get('env_type')
            joint_type = request.form.get('joint_type')
            #print(env)
            if env == '0':
                env_type = '02'
            elif env == '1':
                env_type = '188'
            else:
                env_type = '生產'
            
            #print(token,env,id_,joint_type,domain)
            if token not in  ['',None] : #token 直不為空, 代表頁面輸入的是token
                print('頁面輸入token')
                AutoTest.Joy188Test.select_urltoken(AutoTest.Joy188Test.get_conn(int(env)),token,joint_type)
                token_url = AutoTest.token_url
                print(token_url)
                user =[]
                user_url = []
                len_data = [] # 用註冊碼查, 長度可能會有多個
                for i in token_url.keys():
                    user.append(token_url[i][0])
                    user_url.append(token_url[i][1])
                    len_data.append(i)
                data = {'用戶名':user,'開戶連結':user_url}        
            elif id_ not in ['',None]:
                print('頁面輸入id')
                AutoTest.Joy188Test.select_urltoken(AutoTest.Joy188Test.get_conn(int(env)),id_,joint_type)
                token_url = AutoTest.token_url
                print(token_url)
                user =[]
                user_url = []
                for i in token_url.keys():
                    user.append(token_url[i][0])
                    user_url.append(token_url[i][1])
                
                data = {'用戶名':user,'開戶連結':user_url}
                len_data = [0]#輸入ID 查 連結, ID 為唯一直
            elif user not in ['',None]:# 頁面輸入 用戶名 查詢用戶從哪開出
                print('頁面輸入用戶名')
                AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(int(env)),user,joint_type)# 檢查環境是否有這用戶
                if len(AutoTest.userid) == 0:
                    return('%s環境沒有該用戶: %s'%(env_type,user))
                print(AutoTest.userid)
                AutoTest.Joy188Test.select_userUrl(AutoTest.Joy188Test.get_conn(int(env)),user,2,joint_type)
                user_url =AutoTest.user_url
                print(user_url)
                if len(user_url) == 0:# user_url 有可能找不到 ,再從 user_customer 的refere去找
                    data = {'用戶名':user,'用戶從此連結開出':'被刪除','用戶id':AutoTest.userid[0]}
                    frame = pd.DataFrame(data,index=[0])
                    print(frame)
                    return frame.to_html()
                else:# 這邊代表  user_url 是有值,  在去從days 判斷是否失效
                    if user_url[0][4] == -1:
                        days= '否'
                    else:# 不等於 -1 為失效
                        days = '是'
                data = {'用戶名':user,'用戶Id':AutoTest.userid[0],'用戶從此連結開出':user_url[0][1],'連結是否失效':days,
                '用戶代理線':user_url[0][2],'裝置':user_url[0][3]}
                len_data = [0]
            else:# 輸入domain 查尋 預設連結
                try:# 對頁面輸入的domain, 做格式化處理
                    domain = request.form.get('domain').strip()# 頁面網域名稱 . strip 避免有空格問題
                    '''
                    if 'joy188' in domain:# joy188 前面為www2
                        if 'www2' in domain:
                            pass
                        else:
                            domain = 'www2.%s.com'%domain
                    elif any(s in domain for s in ['com','www']):# 網域名稱 有帶 www /com 不用額外更動
                        pass #  後續可以 對 開頭是否有 http ,尾不是 com  去做處理
                    else: # 沒有帶  www
                        
                        if any(s in domain for s in ['fh888','fh666']):
                            domain = 'www.%s.bet'%domain
                        else:
                            domain = 'www.%s.com'%domain
                    '''    
                    print(domain)
                    #env = domain_keys[domain][1]#  1 為環境 ,0 為預設連結
                except KeyError:# 
                    return('沒有該連結')
                AutoTest.Joy188Test.select_domainUrl(AutoTest.Joy188Test.get_conn(int(env)),domain)
                domain_url = AutoTest.domain_url
                print(domain_url)
                if len(domain_url) != 0:# 代表該預名 在後台全局管理有做設置
                    domain_admin = '是'# 後台是否有設定 該domain
                    register_display = domain_url[0][3]# 前台註冊按紐 是否隱藏
                    if register_display == 0:
                        register_display = '關閉'
                    else:
                        register_display = '開啟'
                    app_display = domain_url[0][4]# 前台掃碼 是否隱藏
                    if app_display == 0:
                        app_display = '關閉'
                    else:
                        app_display = '開啟'
                    admin_url = domain_url[0][2]#url 是預設連結,或者後台的設置 代理聯結
                    agent = domain_url[0][1]
                    domain_type = domain_url[0][5]# 後台設置 環境組 的欄位
                    if domain_type == 0:#  0:一般,1:合營,2:歡樂期排
                        domain_type = '一般'
                    elif domain_type == 1:
                        domain_type = '合營'
                    else:
                        domain_type = '歡樂期排'
                    env_type = domain_type+"/"+env_type#還台有設置 ,不能用damain_keys來看, 有可能 業務後台增加, damain_keys沒有

                    status = domain_url[0][6]
                    if status == 0:
                        status = '上架'
                    else:
                        status = '下架/導往百度'
                    
                    data = {"網域名":domain,'環境':env_type,'後台是否有設置該網域':domain_admin,'後台設定連結': admin_url,
                    '後台設定待理': agent,'後台註冊開關':register_display, '後台掃碼開關':app_display,'後台設定狀態':status}
                else:# 就走預設的設定
                    try:
                        if domain_keys[domain][1] != int(env):
                            return("該環境沒有此domain")
                        domain_admin = '否'
                        admin_url = '無'#後台沒設置
                        url = domain_keys[domain][0]# 沒設定 ,為空, 走預設連結
                        register_status = domain_keys[domain][2]
                        env_type = domain_keys[domain][3] +"/"+env_type#後台沒設置, 就從domain_keys 原本 預設的規則走
                    except KeyError:
                        return('沒有該連結')
                    
                    data = {"網域名":domain,'環境':env_type,'後台是否有設置該網域':domain_admin,'預設連結':url,
                    '預設註冊按紐':register_status}
                len_data = [0]# 查詢網域名 ,長度只會為 1
            try:
                frame = pd.DataFrame(data,index=len_data)
                print(frame)
                return frame.to_html()
            except ValueError:
                return('DATA有錯誤')
        return render_template('url_token.html')
    @app.route('/sun_user2',methods=["POST"])
    def sun_user2():# 查詢太陽成 指定domain
        if request.method == 'POST':
            env = request.form.get('env_type')
            domain = request.form.get('domain_type')
            print(env,domain)
            AutoTest.Joy188Test.select_sunuser(AutoTest.Joy188Test.get_conn(int(env)),'',2,domain)
            sun_user = AutoTest.sun_user
            print(sun_user)
            
            data = {'域名':[sun_user[i][0] for i in sun_user.keys()],
            '代理':[sun_user[i][1] for i in sun_user.keys()],
            '連結':[sun_user[i][2] for i in sun_user.keys()],
            '註冊顯示':['是' if sun_user[i][3] == 1 else "否" for i in sun_user.keys()],
            '狀態':['下架' if sun_user[i][4] == 1 else '正常' for i in sun_user.keys()],
            '備註':[sun_user[i][5] for i in sun_user.keys()],
            '連結失效性':['失效' if sun_user[i][6]!= -1 else '正常' for i in sun_user.keys()],
            '註冊數量':['0' if sun_user[i][7] == None else int(sun_user[i][7]) for i in sun_user.keys()]
            }
            frame = pd.DataFrame(data,index=[i for i in sun_user.keys()])
            print(frame)
            return frame.to_html()
        else:
            return('錯誤')
    @app.route('/sun_user',methods=["POST","GET"])
    def sun_user():# 太陽成用戶 找尋
        if request.method =="POST":
            user = request.form.get('user')
            env = request.form.get('env_type')
            domain = request.form.get('domain_type')
            print(user,env,domain)
            if env =='0' :
                env_name = 'dev'
            elif env == '1':
                env_name = '188'
            else:
                print(env)
                env_name = '生產'
            if domain == '0':
                domain_type = '太陽城'
            else:
                domain_type = '申博'# domain  = "1"
            if user in [None,'']:
                type_ = 1# 頁面查詢 轉移成功用戶, 
            else:
                type_ = ''# 查詢 指定用戶
            print(type_)
            AutoTest.Joy188Test.select_sunuser(AutoTest.Joy188Test.get_conn(int(env)),user,type_,domain)# 太陽/申博用戶 
            sun_user = AutoTest.sun_user
            print(sun_user)
            if len(sun_user) == 0:
                if type_ ==1:
                    return('目前還沒有成功轉移用戶')
                return('%s沒有該用戶:%s'%(env_name+domain_type,user))
            if type_!=1:# 指定用戶
                user = sun_user[0][0]
                phone = sun_user[0][1]
                tran_statu = sun_user[0][4]
                if tran_statu == 1:
                    tran_statu = '成功'
                else:
                    tran_statu = '未完成'
                tran_time = sun_user[0][5]
                index_len = [0]
                AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(int(env)),user,int(domain))# 4.0 資料庫
                userid = AutoTest.userid
                '''
                if len(userid) == 0:# 代表該4.0環境沒有該用戶
                    FF_memo = '無'
                else:
                    FF_memo = '有'
                '''
                data = {'環境/類型':env_name+domain_type,'用戶名':user,'電話號碼':phone,'轉移狀態':tran_statu,'轉移時間':tran_time,
                #'4.0資料庫':FF_memo
                }
            else:# 找尋以轉移用戶, 資料會很多筆
                user = []
                phone = []
                tran_statu = []
                tran_time = []
                index_len = []
                for num in sun_user.keys():
                    user.append(sun_user[num][0])
                    phone.append(sun_user[num][1])
                    if sun_user[num][2] == 1:
                        statu = '成功'
                    else: 
                        statu = '失敗'
                    tran_statu.append(statu)
                    tran_time.append(sun_user[num][3])
                    index_len.append(num)
                data = {'環境/類型':env_name+domain_type,'用戶名':user,'電話號碼':phone,'轉移狀態':tran_statu,'轉移時間':tran_time}
            frame = pd.DataFrame(data,index=index_len)
            print(frame)
            return frame.to_html()
        return render_template('sun_user.html')
    @app.route('/fund_activity',methods=["POST","GEt"])
    def fund_activity():# 充值紅包 查詢
        if request.method =="POST":
            user = request.form.get('user')
            env = request.form.get('env_type')
            print(user,env)
            AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(int(env)),user,'')# 查詢頁面上 該環境是否有這用戶
            if len(AutoTest.userid) == 0:
                return('該環境沒有此用戶')
            AutoTest.Joy188Test.select_FundRed(AutoTest.Joy188Test.get_conn(int(env)),user,'')# 先確認 是否領取過紅包
            red_able = AutoTest.fund_
            print(red_able)
            
            fund_list = []# 存放各充值表的 紀錄 ,總共四個表
            for i in range(4):
                AutoTest.Joy188Test.select_FundRed(AutoTest.Joy188Test.get_conn(int(env)),user,i)
                fund_list.append(AutoTest.fund_)
            #begin_mission = AutoTest.fund_# 新守任務表
            print(fund_list)
            data = {}
            fund_log = 0# 紀錄 是否 四個表都沒有資料
            for index,i in enumerate(fund_list):
                if index == 0:
                    msg = '新守任務/BEGIN_MISSION'
                elif index ==1:
                    msg = ('活動/ACTIVITY_FUND_OPEN_RECORD')
                elif index ==2:
                    msg = ('資金明細/fund_change_log')
                elif index==3:
                    msg = ('資金明細搬動/fund_change_log_hist')
                if len(i) ==0:
                    msg2 = ('無紀錄')
                else:
                    msg2 = ('%s'%i[0])
                    fund_log = fund_log+1#
                print(msg,msg2)
                data[msg] = msg2
            print(fund_log)
            if len(red_able) == 0:# 紅包還沒領取
                red_able = '否' 
                if fund_log == 0:# 代表沒成功
                    activity_able = '符合資格'
                else:
                    activity_able = "不符合資格"
            else:# 代表已經領取過 紅包
                red_able = float(red_able[0][0]/10000)
                activity_able = "符合資格"
            data['紅包是否領取'] = '紅包金:%s'%red_able
            data['充直紅包活動'] = activity_able
            print(data)
            frame = pd.DataFrame(data,index=[0])
            print(frame)
            return frame.to_html()
        return render_template('fund_activity.html')
    @app.route('/api_test',methods=["GET","POST"])
    def api_test():
        if request.method =="POST":
            print(request.cookies)
            request_type = request.form.get('request_type')
            content_type = request.form.get('Content_type')# header
            url = urlsplit(request.form.get('url'))# url 要切割
            url_domain = url.scheme+'://'+url.netloc# 為網域名
            url_path = url.path# .com/ 後面url路徑
            url_query = url.query# url 把參數加在面url的
            if url_query != '':# url有這段的化, 需加? 參數
                url_query = '?%s'%url_query
            data = request.form.get('request_data')
            login_cookie = request.form.get('login_cookie')
            check_type = request.form.get('check_type')
            header_key = request.form.getlist('header_key')
            header_value = request.form.getlist('header_value')
            print(check_type,login_cookie,header_key,header_value)
            header = { 
            "Content-Type": content_type,
            'User-Agent':FF_Joy188.FF_().user_agent['Pc'],# 這邊先寫死給一個
            }  
            for key,value in zip(header_key,header_value):# header_key/ header_value  為列表
                header[key] = value
            if login_cookie != '':
                header['Cookie'] = login_cookie
            print(request_type,content_type,url_domain,url_path,url_query,data)
            threads,status,content,req_time = [],[],[],[]
            if  request_type == 'post':
                thread_func = FF_Joy188.FF_().session_post
            else:
                thread_func = FF_Joy188.FF_().session_get
            if check_type == 'thread_check':# 併發
                num = 2
            else:
                num = 1
            for i in range(num):
                t = threading.Thread(target=thread_func,args=(url_domain,url_path+url_query,data,header))
                threads.append(t)
            #print(len(threads))
            for i in threads:
                i.start()
            for i in threads:
                i.join()
                print(FF_Joy188.content)
                status.append(FF_Joy188.status)
                content.append(FF_Joy188.content)
                req_time.append(FF_Joy188.req_time)
            #print(FF_Joy188.content)
            result = {}
            result['status'] = '連線狀態: %s'%status[-1]
            result['data'] = content[-1]
            result['time'] = req_time[-1]
            return result
        return render_template('api_test.html')
    @app.route('/gameBox',methods=["POST","GET"])
    def gameBox():
        admin_items,user_items = {},{}#管理/客戶端
        for key in GameBox.GameBox().data_type.keys():
            #print(key)
            # 中文名稱為key, 英文參數唯value,用意 顯示在頁面上中文
            if key == 'getClientInfo':# 管理端 用  獲得client信息即可,其它 不需動
                admin_items[GameBox.GameBox().data_type[key][0]] = key
            elif key in ['token','createApp','updateIpWhitelist','updateSupplierAccount']:# 管理端
                pass
            else:
                user_items[GameBox.GameBox().data_type[key][0]] = key
        if request.method == "POST":
            client_type = {
            "api_key":["1566e8efbdb444dfb670cd515ab99fda","XT","9RJ0PYLC5Ko4O4vGsqd","","a93f661cb1fcc76f87cfe9bd96a3623f","BgRWofgSb0CsXgyY"]
            ,"api_url":["https://api.dg99web.com","http://tsa.l0044.xtu168.com","https://testapi.onlinegames22.com","http://api.cqgame.games","http://gsmd.336699bet.com","https://testapi.onlinegames22.com"]
            ,"supplier_type":["dream_game","sa_ba_sports","ae_sexy","cq_9","gpi","ya_bo_live"]
            ,"supplier_user":["DGTE01011T","6yayl95mkn","fhlmag","cq9_test","xo8v","ZSCH5"]
            ,"game_type" :["DG","沙巴","Sexy","Cq9",'GPI',"YB"]
            }
            cq_9Key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiI1ZjU5OWU3NTc4MDdhYTAwMDFlYTFjMjYiLCJhY2NvdW50IjoiYW1iZXJ1YXQiLCJvd25lciI6IjVkYzExN2JjM2ViM2IzMDAwMTA4ZTQ4NyIsInBhcmVudCI6IjVkYzExN2JjM2ViM2IzMDAwMTA4ZTQ4NyIsImN1cnJlbmN5IjoiVk5EIiwianRpIjoiNzkyMjU1MDIzIiwiaWF0IjoxNTk5NzA4Nzg5LCJpc3MiOiJDeXByZXNzIiwic3ViIjoiU1NUb2tlbiJ9.cyvPJaWFGwhX4dZV7fwcwgUhGM9d5dVv8sgyctlRijc"
            url_dict = {0:['http://43.240.38.15:21080','測試區'],1:['http://54.248.18.149:8203','灰度']}# 測試 / 灰度
            env_type = request.form.get('env_type')
            game_type = request.form.get('game_type')#  0 : DG , 1: 沙巴
            user = request.form.get('user')
            check_type = request.form.get('check_type') # 0 為管理端/ 1 : 客戶端
            print(env_type,game_type,user,check_type)
            game_list = []# 存放前台選擇的 測試項目
            if check_type == '0':
                game_list.append('token')# 管理端 先獲得 token
                game_list.append(request.form.get('admin_name'))
            else:
                game_list.append(request.form.get('user_name'))
            print(game_list)

            api_key = client_type["api_key"][int(game_type)]
            api_url = client_type["api_url"][int(game_type)]
            supplier_type = client_type["supplier_type"][int(game_type)]
            supplier_user = client_type["supplier_user"][int(game_type)]
            clientId = client_type["supplier_user"][int(game_type)]
            client_detail = GameBox.GameBox.GameBox_Con(client_id=clientId,env=int(env_type))
            url = url_dict[int(env_type)][0]
            url_type = '%s, '%url+client_type['game_type'][int(game_type)]+url_dict[int(env_type)][1]
            GameBox.suite_test(game_type=int(game_type),url_type=url_type,clientId=clientId,user=user,client_detail=client_detail,
            api_key=api_key,api_url=api_url,supplier_type=supplier_type,url=url,game_list=game_list,user_items=user_items,admin_items=admin_items,cq_9Key=cq_9Key)

            return 'ok'
        print(admin_items,user_items)
        return render_template('gameBox.html',user_items=user_items,admin_items=admin_items)
        
    @app.route('/fund_fee',methods=["POST","GET"])# 充值/提線 手續費查詢
    def fund_fee():
        if request.method == "POST":
            select_type = request.form.get('type')
            env_type = request.form.get('env_type')
            user = request.form.get('user')
            print(select_type,user)
            #總代: 因為parent_id  為 -1.需用 user_iD查
            AutoTest.Joy188Test.select_Fee(AutoTest.Joy188Test.get_conn(int(env_type)),select_type,user)
            fund_fee = AutoTest.fund_fee
            print(fund_fee)
            if select_type == "fund":# 充值
                type_msg = "充值"
                if len(fund_fee) == 0:# 總代線沒設定
                    rule_msg = "總代線沒設定,走平台設定"
                else:# 總代線有設定手續費
                    FF_list = []# 存放平台的 充值
                    for key in fund_fee:
                        if fund_fee[key][0] in [i for i in range(1,16)]:# [0] 是bank_id  , [1-15] 是 PC銀行卡
                            ff_name =  "PC銀行卡"
                        elif fund_fee[key][2] == 1:#APP
                            ff_name = "APP%s"%fund_fee[key][3]
                        elif fund_fee[key][2] == 0:#PC
                            ff_name = "PC%s"%fund_fee[key][3]
                        FF_list.append(ff_name)
                    rule_msg = '走總代線設定%s'%set(FF_list)
                        
                data = {"手續費類型": type_msg,"手續費規則":rule_msg,"備註":"總代線有設定走平台/不管用戶身分"}
            else:# 提線
                AutoTest.Joy188Test.select_userLvl(AutoTest.Joy188Test.get_conn(int(env_type)),user)
                user_lvl = AutoTest.user_lvl
                type_msg = "提現"
                if len(fund_fee) == 0:# 總代線沒設定
                    rule_msg = "總代線沒設定,走平台設定"
                elif fund_fee[0][0] == 0:#手續費有設定,開關
                    rule_msg = "總代線开設定關閉,走平台"
                elif user_lvl[0][1] == 0:#非星級
                    rule_msg = "一般用戶"
                    if user_lvl[0][0] >= 1:#柏金 vip
                        rule_msg = rule_msg + ",vip/走平台"
                    else:
                         rule_msg = rule_msg + ",非vip/走總代線設定"
                elif user_lvl[0][1] == 1:#星級
                    rule_msg = "星級用戶"
                    if user_lvl[0][0] >= 3:#星級 3 等以上 vip
                        rule_msg = rule_msg + ",vip/走平台"
                    else:
                        rule_msg = rule_msg + ",非vip/走總代線設定"
                data = {"手續費類型": type_msg,"手續費規則":rule_msg}
            frame = pd.DataFrame(data,index=[0])
            print(frame)
            return frame.to_html()
        return render_template('FundFee.html')
    @app.route('/FundCharge',methods=["POST","GET"])
    def FundCharge():# 充值成功金額 查詢
        if request.method == "POST":
            env_type = request.form.get('env_type')
            check_type =request.form.get('check_type')# '0'使用日期 , '1'使用月份
            AutoTest.get_rediskey(2)# 連到本地 redis
            if check_type == '0': 
                day = request.form.get('day_day')
                month = request.form.get('day_month')
                year = request.form.get('day_year')
                date = "%s/%s/%s"%(year,month,day)# 格式化日期 傳到  select_FundCharge
                key_name = '%s/%s:%s'%(check_type,env_type,date)# 0/環境:日期
                result = AutoTest.get_key(key_name)
                print(result)
                if result != 'not exist':# 代表 已經存 到redis過
                    return result 
                AutoTest.Joy188Test.select_FundCharge(AutoTest.Joy188Test.get_conn(int(env_type)),date)
                data_fund = AutoTest.data_fund# key 為0 , value 0 為發起金額 總合, 1為 手續費總和 , 2 為充值個數
                #print(data_fund)
                if len(data_fund) == 0:
                    sum_fund= 0
                    len_fund = 0
                    len_Allfund = 0
                else: 
                    if data_fund[0][1] is None:# 有手續費 是none
                        fund_fee = 0
                    else:
                        fund_fee = int(data_fund[0][1])/10000
                    if data_fund[0][0] is None:# 有充值金額 是none
                        fund_apply = 0
                    else:
                        fund_apply = int(data_fund[0][0])/10000
                    len_fund = data_fund[0][2]
                    sum_fund = fund_apply- fund_fee# 發起充值金額 - 手續費 , 兩者相減
                    AutoTest.Joy188Test.select_FundCharge(AutoTest.Joy188Test.get_conn(int(env_type)),date,'1')# 總個數
                    len_Allfund = AutoTest.data_fund[0][0]
                    try:
                        fund_per = int(int(len_fund)/int(len_Allfund)*10000)/100
                    except ZeroDivisionError:
                        fund_per = 0
                    #fund_list =  reduce(lambda x,y: x+y,fund_list)#計算列表裡數值總合
                data_ = {"date":date,"sum_fund":sum_fund,"len_fund": len_fund,"len_Allfund":len_Allfund,'fund_per': fund_per }
                AutoTest.set_key(key_name,data_)
            else:#月份
                now = datetime.datetime.now()
                now_day = now.day# 今天日期
                now_month =  now.month#這個月
                month = request.form.get('month_month')
                year = request.form.get('month_year')
                date = "%s/%s"%(year,month)# 格式化日期 傳到  select_FundCharge
                #print(month,now_month)
                if month == str(now_month):# 頁面選擇的 月份 等於這個月, 需把 當下日期 一起加進去 , 因為 這個月每天進來 都會 有新的一天數據
                    key_name = '%s/%s:%s%s'%(check_type,env_type,date,now_day)# 1/環境:日期 , 多增加今天日期為key
                else:
                    key_name = '%s/%s:%s'%(check_type,env_type,date)# 不是這個月, 不用管今天日期
                result = AutoTest.get_key(key_name)
                print(result)
                if result != 'not exist':# result是 not exist, 代表 redis 沒值 ,不等於 就是 redis有值
                    return result
                #print(date)
                AutoTest.Joy188Test.select_FundCharge(AutoTest.Joy188Test.get_conn(int(env_type)),date,'month')
                data_fund = AutoTest.data_fund# key 為日期 , value 0 為發起金額 總合, 1為 手續費總和 , 2 為充值個數
                #print(data_fund)
                date_list,sum_fund_list,len_fund_list,fund_per_list,len_Allfund_list = [],[],[],[],[]
                for key,value in data_fund.items():
                    date_list.append(key)
                    if value[0] is None:# 發起金額
                        fun_apply = 0
                    else:
                        fun_apply = value[0]/10000
                    if value[1] is None:#手續費
                        len_fund = 0
                    else:
                        len_fund = value[1]/10000
                    sum_fund = fun_apply-len_fund# 充直總發起金額
                    sum_fund_list.append(int(sum_fund*100)/100)
                    len_fund = value[2]# 充值成功個數
                    len_fund_list.append(len_fund)
                    len_Allfund = value[3] # 充值 總個數
                    len_Allfund_list.append(len_Allfund)
                    try:
                        fund_per = int(int(len_fund)/int(len_Allfund)*10000)/100
                    except ZeroDivisionError:# 0/0 報的錯
                        fund_per = 0
                    fund_per_list.append(fund_per)# 充值 成功率
                data_ = {"date":date_list,"sum_fund":sum_fund_list,"len_fund": len_fund_list,"len_Allfund":len_Allfund_list,
                'fund_per': fund_per_list }
                AutoTest.set_key(key_name,data_)
            #print(data_)
            return data_
            #frame = pd.DataFrame(data,index=date_list)
            #return frame.to_html()
        return render_template('FundCharge.html')
    @app.route('/login_cookie',methods=["POST"])# 傳回登入cookie
    def login_cookie():
        env_url = request.form.get('env_type')
        envConfig = Config.EnvConfig(env_url)
        joint = envConfig.get_joint_venture(envConfig.get_env_id(),'www.%s.com'%env_url)
        user = request.form.get('username')
        AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(envConfig.get_env_id()),user,joint)  # 查詢用戶 userid
        userid = AutoTest.userid
        print(env_url)
        if len(AutoTest.userid) == 0:
                return('該環境沒有此用戶')
        password = str.encode(envConfig.get_password())
        param = FF_Joy188.FF_().param[0]
        postData = {
        "username": user,
        "password": AutoTest.Joy188Test.md(password, param),
        "param": param 
        }
        header = {
            'User-Agent': FF_Joy188.FF_().user_agent['Pc']#從FF_joy188.py 取
        }
        print(user,envConfig.get_post_url())
        FF_Joy188.FF_().session_post(envConfig.get_post_url(),'/login/login',postData,header)
        cookies = FF_Joy188.r.cookies.get_dict()['ANVOID']
        print(cookies)
        return cookies
    @app.route('/remote_IP',methods=['POST'])# 從瀏覽器 獲得本地 ip,方便 好記錄 查證使用
    def remote_IP():
        ip = request.form
        print(ip)
        return 'ok'
    @app.route('/error')#錯誤處理
    def error():
        abort(404)
    @app.errorhandler(404)
    def page_not_found(error):
        print(error)
        return render_template('404.html'), 404
    @app.errorhandler(500)
    def internal_error(error):
        print(error)
        return render_template('404.html'), 500
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        error_dict = {
            'code': error.code,
            'description': error.description,
            'stack_trace': traceback.format_exc()
        }
        log_msg = "HTTPException {error_dict.code}, Description: {error_dict.description}, Stack trace: {error_dict.stack_trace}"
        logger.log(msg=log_msg)
        response = jsonify(error_dict)
        response.status_code = error.code
        return response
    @app.route('/config',methods=["GET"])
    def config():
        print(request.url)#當前url
        Config.select_config(stock.kerr_conn())
        config_con = Config.config_con #config 內容
        print(config_con)
        config_data = json.loads(config_con[0][1])# str 轉json, config_con[0][1] : {"dev07": "close", "local": "open"}
        if 'dev07' not in request.url:# local url
            config_setting = config_data['local']
        else:
            config_setting = config_data['dev07']
        return config_setting

if __name__ == "__main__":
    '''
    handler = logging.FileHandler('flask.log')
    app.logger.addHandler(handler)
    '''
    app.config['TESTING'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(host="0.0.0.0", debug=True, port=4444, threaded=True)
    # app.config.from_object(DevConfig)
