#!/usr/bin/env python
# coding: utf-8
import math
import traceback
from http.client import HTTPException
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, abort
import datetime
import requests
import json
import os
from autoTest import AutoTest
from autoTest import ApiTestPC
from time import sleep
import threading
import test_benefit
import calendar
import test_lotteryRecord
import logging
from flask import current_app
import urllib3
from bs4 import BeautifulSoup
# import twstock, stock
import pandas as pd
import re
from utils import Config
from utils.Connection import PostgresqlConnection, OracleConnection, RedisConnection
import FF_Joy188
from urllib.parse import urlsplit
from functools import reduce
import itertools 

app = Flask(__name__)  # name 為模塊名稱
logger = logging.getLogger('flask_test')



def iapi_login(envir):  # iapi 抓取沙巴token
    session = requests.Session()
    global HEADERSB
    global ENVSB
    ENVSB = Config.EnvConfigApp(envir)
    HEADERSB = {
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
                "username": user + "|" + ENVSB.get_uuid(),
                "loginpassSource": ENVSB.get_login_pass_source(),
                "appCode": 1,
                "uuid": ENVSB.get_uuid(),
                "loginIp": 2130706433,
                "device": 2,
                "app_id": 9,
                "come_from": "3",
                "appname": "1"
            }
        }
    }
    r = session.post(ENVSB.get_iapi() + '/front/login', data=json.dumps(login_data), headers=HEADERSB)
    # print(r.text)
    global TOKEN
    TOKEN = r.json()['body']['result']['token']
    # print(token)


def sb_game():  # iapi沙巴頁面
    session = requests.Session()

    data = {"head": {"sessionId": TOKEN}, "body": {"param": {"CGISESSID": TOKEN,
                                                             "loginIp": "10.13.20.57", "types": "1,0,t", "app_id": 9,
                                                             "come_from": "3", "appname": "1"}}}

    r = session.post(ENVSB.get_iapi() + '/sb/mobile', data=json.dumps(data), headers=HEADERSB)
    # print(r.text)
    global SB_URL
    SB_URL = r.json()['body']['result']['loginUrl']
    cookies = r.cookies.get_dict()


def get_sb():  # 沙巴體育
    session = requests.Session()
    iapi_login('dev02')
    sb_game()
    # 抓取沙巴,token成功的方式, 先get 在post
    r = session.get(SB_URL + '/', headers=HEADERSB)
    cookies = r.cookies.get_dict()
    r = session.post(SB_URL + '/', headers=HEADERSB)

    HEADERSB['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    session = requests.Session()

    data = {
        'GameId': 1,
        'DateType': 't',
        'BetTypeClass': 'WhatsHot',
        # 'Matchid':''
    }
    url = 'http://smartsbtest.thirdlytest.st402019.com'
    # /Odds/ShowAllOdds ,   /Odds/GetMarket
    r = session.post(url + '/Odds/ShowAllOdds', headers=HEADERSB, data=data, cookies=cookies)

    global SB_LIST
    SB_LIST = []
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
            game_dict['Etm'] = (d).strftime('%Y-%m-%d %H:%M:%S')  # 加12小時
        SB_LIST.append(game_dict)
    SB_LIST.sort(key=lambda k: (k.get('Etm', 0)))  # 列表裡包字典, 時間排序

    for i in SB_LIST:  # list取出各個字點
        # print(i['MatchId'])#抓出mathch id ,去對應 賠率
        data['Matchid'] = i['MatchId']
        r = session.post(url + '/Odds/GetMarket', headers=HEADERSB, data=data, cookies=cookies)
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
    global TODAY_TIME

    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    format_month = f'{month:02d}'
    format_day = f"{day:02d}"
    TODAY_TIME = f'{year}-{format_month}-{format_day}'


def test_sport(type_keys='全部'):  # 企鵝網
    header = {
        'User-Agent': Config.UserAgent.PC.value
    }
    type_ = {'全部': 0, "英超": 1}
    date_time()
    session = requests.Session()

    r = session.get('http://live.qq.com' +
                    f'/api/calendar/game_list/{type_[type_keys]}/{TODAY_TIME}/{TODAY_TIME}',
                    headers=header)
    # print(r.json())
    # print(r.json())
    global SPORT_LIST
    SPORT_LIST = []  # 存放請求
    len_game = len(r.json()[TODAY_TIME])  # 當天遊戲列表長度
    # print(r.json()[today_time])

    for game in range(len_game):  # 取出長度
        game_dict = r.json()[TODAY_TIME][game]
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
        SPORT_LIST.append(game_new)
        # else:
        # pass
    # print(game_new)
    # print(sport_list)


@app.route('/form', methods=['POST', 'GET'])
def test_form():  # 輸入/form 頁面, 呼叫render_template的html
    if request.method == "POST":
        username = request.form['username']  # 在頁面上填的資料
        email = request.form['email']
        hobbies = request.form['hobbies']
        return redirect(url_for('showbio',  # 提交
                                username=username,  # 前面為參數,後面為資料
                                email=email,
                                hobbies=hobbies))  # redirect 重新定向
    return render_template('bio_form.html')


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
    return render_template('sport.html', sport_list=SPORT_LIST, today_time=TODAY_TIME)


@app.route('/sportApi', methods=['GET'])
def sport_api():  # 體育api
    test_sport()
    return jsonify(SPORT_LIST)


@app.route('/sb', methods=['GET'])
def sb_():
    get_sb()
    date_time()
    return render_template('sb.html', sb_list=SB_LIST, today_time=TODAY_TIME)


@app.route('/sbApi', methods=['GET'])
def sb_api():  # 體育api
    get_sb()
    return jsonify(SB_LIST)

'''
@app.route('/image', methods=['GET'])
def image_():  # 調整圖片大小
    img_path = (os.path.join(os.path.expanduser("~"), 'Desktop'))
    return render_template('image.html', img_path=img_path)
@app.route('/imageAdj', methods=["POST"])
def image_adj():
    testInfo = {}  # 存放 圖名,長,寬 的資料
    image_name = request.form.get('image_name')
    height = request.form.get('height')
    width = request.form.get('width')
    testInfo['image_name'] = image_name
    testInfo['height'] = height
    testInfo['width'] = width
    testInfo['msg'] = image_test.image_resize(image_name, height, width)  # 將圖名, 長,寬 回傳給 image_test檔案下 image_的 func使用
    return json.dumps(testInfo['msg'])
'''

@app.route('/autoTest', methods=["GET"])  # 自動化測試 頁面
def auto_test():
    lottery_dict = FF_Joy188.FF_().lottery_dict
    try:
        lottery_dict.__delitem__('ahsb')
        lottery_dict.__delitem__('slsb')
    except Exception as e:
        from utils.TestTool import trace_log
        trace_log(e)
    return render_template('autoTest.html', lottery_dict=lottery_dict)


@app.route('/autoTest', methods=['POST'])
def auto_test_post():
    lottery_selected = None

    try:
        logger.info('logged by app.module')
        current_app.logger.info('logged by current_app.logger')
        # response_status ='start_progress'
        # return redirect("/progress")
        test_cases = []
        user_name = request.form.get('user_name')
        api_test_pc = request.form.getlist('api_test_pc')  # 回傳 測試案例data內容
        api_test_app = request.form.getlist('api_test_app')  # 回傳 測試案例data內容
        integration_test_pc = request.form.getlist('integration_test_pc')  # 回傳 測試案例data內容
        env_config = Config.EnvConfig(request.form.get('env_type'))  # 環境選擇
        red = True if int(request.form.get('red_type')) == 1 else False  # 紅包選擇
        award_mode = int(request.form.get('awardmode'))  # 獎金組設置
        money_unit = float(request.form.get('moneymode'))  # 金額模式
        ignore_name_check = request.form.get('ignore_user_check')
        domain_url = env_config.get_post_url().split('://')[1]  # 後台全局 url 需把 http做切割
        logger.info(f'ignore_name_check = {ignore_name_check}')

        if env_config.get_env_id() in (0, 1):  # FF4.0 用戶驗證
            lottery_selected = request.form.get('lottery_selected')  # 4.0選擇採種名稱
            conn = OracleConnection(env_config.get_env_id())
            domain_type = env_config.get_joint_venture(domain_url)  # 查詢 後台是否有設置 該url
            logger.debug(f"env_config.id: {env_config.get_env_id()},  red: {red}")
            user_id = conn.select_user_id(user_name, domain_type)
            logger.info(f'user_id : {user_id}')
            conn.close_conn()
        elif ignore_name_check:
            user_id = ["ignore"]
        else:  # yft用戶名驗證
            conn = PostgresqlConnection()
            user_id = conn.get_user_id_yft(user_name=user_name)

        test_cases.append(api_test_pc)
        test_cases.append(api_test_app)
        test_cases.append(integration_test_pc)

        logger.info(f'user_name : {user_name}')
        logger.info(f"test_cases : {test_cases}")
        if user_id is None:
            return '此環境沒有該用戶'
        elif type(user_id) == str:
            return user_id
        if len(user_id) > 0:  # user_id 值為空, 代表該DB環境沒有此用戶名, 就不用做接下來的事
            logger.info(
                f"AutoTest.suite_test(test_cases={test_cases}, user_name={user_name}, "
                f"env_config.get_domain()={env_config.get_domain()}, red={red}), "
                f"money_unit={money_unit}, award_mode={award_mode}")
            Config.test_cases_init(sum(len(cases) for cases in test_cases))  # 初始化測試案例數目，後續供進度條讀取百分比
            AutoTest.suite_test(test_cases, user_name, env_config.get_domain(),
                                red, money_unit, award_mode, lottery_selected)  # 呼叫autoTest檔 的測試方法, 將頁面參數回傳到autoTest.py
            return redirect('report')
        else:
            return '此環境沒有該用戶'
    except Exception as e:
        from utils.TestTool import trace_log
        print(trace_log(e))


@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')


@app.route('/progress')
def progress():  # 執行測試案例時, 目前 還位判斷 request街口狀態,  需 日後補上
    def generate():
        percent = 0
        while percent <= 100:
            if Config.CASE_AMOUNT:
                percent = Config.CASE_AMOUNT[0] / Config.CASE_AMOUNT[1] * 100
            yield "data:" + str(math.floor(percent)) + "\n\n"  # data內容, 換行
            sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/benefit', methods=["GET", "POST"])  # 日工資頁面  按鈕提交後, 在導往  benefit_日工資/分紅頁面
def benefit():
    if request.method == "POST":
        testInfo = {}  # 存放資廖
        cookies_dict = {}  # 存放cookie
        global RESULT  # 日工資 data資料

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
        env_ = Config.EnvConfig(env)
        conn = OracleConnection(env_id=env_.get_env_id())
        userid = conn.select_user_id(username)
        if len(userid) == 0:
            return '沒有該用戶'
        print(testInfo)  # 方便看資料
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
            RESULT = test_benefit.result_data
            print(RESULT)
            if RESULT['msg'] == '你輸入的日期或姓名不符,請再確認':  # 有cookie, 但cookie失效, 需再重新做
                test_benefit.admin_Login(env)
                admin_cookie = test_benefit.admin_cookie  # 呼叫  此function ,
                cookies_dict[env] = admin_cookie['admin_cookie']
                cookies = admin_cookie['admin_cookie']
                test_benefit.game_report_day(user=username, month=int(month), day=int(day), cookies=cookies, env=env)
                RESULT = test_benefit.result_data
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
            RESULT = test_benefit.result_data
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
    return render_template('benefit_day.html', result=RESULT)


@app.route('/benefit_month', methods=["GET"])
def benefit_month():
    return render_template('benefit_month.html', result=RESULT)


@app.route('/report_APP', methods=["GET", "POST"])  # APP戰報
def report_APP():
    global RESULT
    if request.method == 'POST':
        envtype = request.form.get('env_type')
        print(envtype)
        if envtype == 'dev':
            env = 0
        else:  # 188
            env = 1
        test_lotteryRecord.all_lottery(env)
        RESULT = test_lotteryRecord.result

        return redirect('report_AppData')

    return render_template('report_APP.html')


@app.route('/report_AppData', methods=["GET"])  # APP戰報資料顯示
def report_AppData():
    return render_template('report_AppData.html', result=RESULT)


@app.route('/domain_list', methods=["GET"])  # 域名列表測試,抓取 http://172.16.210.101/domain_list  提供的 網域
def domain_list():
    return render_template('domain_list.html')

    # print(url_dict)


def domain_get(url):  # domain_list , url 訪問後  ,回傳 url_dict
    urllib3.disable_warnings()  # 解決 會跳出 request InsecureRequestWarning問題
    header = {
        'User-Agent': FF_Joy188.FF_().user_agent['Pc']
    }
    global r, URL_DICT
    try:
        r = requests.get(url + '/', headers=header, verify=False, timeout=5)
    except:
        pass
    URL_DICT[url] = r.status_code


@app.route('/domain_status', methods=["GET"])
def domain_status():  # 查詢domain_list 所有網域的  url 接口狀態
    global URL_DICT
    urllib3.disable_warnings()  # 解決 會跳出 request InsecureRequestWarning問題
    print(request.url)  # "http://3eeb8f01ffe7.ngrok.io/domain_status"
    url_split = urlsplit(request.url)
    request_url = "%s://%s" % (url_split.scheme, url_split.netloc)  # 動態切割 當前url
    header = {
        'User-Agent': FF_Joy188.FF_().user_agent['Pc']
    }
    r = requests.get(request_url + '/domain_list', headers=header)
    # print(r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    URL_DICT = {}  # 存放url 和 皆口狀態
    try:  # 過濾 從頁面上抓取的url, 有些沒帶http
        for i in soup.find_all('table', {'class': 'domain_table'}):
            for a in i.find_all('a'):
                if 'http' not in a.text:
                    url = 'http://' + a.text
                    URL_DICT[url] = ''  # 先存訪到url_dict
                else:  # 這邊提供的  頁面 不用做額外處理, 就是 a.text
                    URL_DICT[a.text] = ''
        threads = []
        for url_key in URL_DICT:
            threads.append(threading.Thread(target=domain_get, args=(url_key,)))
        for i in threads:
            i.start()
        for i in threads:
            i.join()
    except requests.Timeout as e:
        pass
    except urllib3.exceptions.NewConnectionError as e:
        print(e)
    print(URL_DICT)
    return URL_DICT
    # return render_template('domain_status.html',url_dict=url_dict)


@app.route('/stock_search', methods=["GET", "POST"])
def stock_search():
    stock_detail = {}
    try:
        if request.method == "POST":
            stock_num = request.form.get('stock_search')
            stock_name = request.form.get('stock_search2')
            print(stock_num, stock_name)  # 股票號碼,股票名稱
            if stock_name not in [None, '']:  # 代表頁面 輸入名稱 , 先從DB 找 有沒有該名稱,在去yahoo找
                stock.stock_selectname(stock.kerr_conn(), stock_name)  # 找出相關資訊
                stock_detail2 = stock.stock_detail2
                if len(stock_detail2) == 0:  # 名稱營收db為空的, 就不列印營收資訊
                    raise Exception(f'沒有該股票名稱: {stock_name}')
                else:  # DB有找到該名稱 ,
                    stock_deatil2 = stock.stock_detail2
                    print(stock_deatil2)
                    stock_num = str(list(stock_deatil2.values())[0][1])  # 號碼
                    stock.df_test(stock_num)
                    stock.df_test2(stock_num)
                    now = stock.now  # 查詢時間
                    latest_close = stock.latest_close  # 最新收盤
                    latest_open = stock.latest_open
                    latest_high = stock.latest_high
                    latest_low = stock.latest_low
                    latest_volume = stock.latest_volume
            else:  # 輸入號碼 ,和頁面輸入名稱流程不同,  有號碼 先從yahoo直接去找
                try:
                    stock_name = twstock.codes[stock_num][2]
                    stock.df_test(stock_num)
                    stock.df_test2(stock_num)
                    now = stock.now  # 查詢時間
                    latest_close = stock.latest_close  # 最新收盤
                    latest_open = stock.latest_open
                    latest_high = stock.latest_high
                    latest_low = stock.latest_low
                    latest_volume = stock.latest_volume
                except KeyError:
                    raise Exception(f'沒有該股票號碼: {stock_num}')  # yahoo沒有,DB正常就不會有
                stock.stock_selectnum(stock.kerr_conn(), int(stock_num))  # 有股號後, 從mysql 抓出更多資訊
                stock_detail2 = stock.stock_detail2
                if len(stock_detail2) == 0:  # 營收db為空的,但 yahoo查詢是有該股的, 就不列印營收資訊 ,
                    data = {"股票名稱": stock_name, '股票號碼': stock_num, "目前股價": latest_close,
                            '開盤': latest_open, '高點': latest_high, '低點': latest_low, '成交量': latest_volume,
                            "查詢時間": now
                            }
                    frame = pd.DataFrame(data, index=[0])
                    print(frame)
                    return (frame.to_html())
                else:  # yahoo有, DB也有, 就是多列印 營收
                    pass  # 走到下面  和輸入 名稱  共用  營收邏輯

            # 有營收, 輸入號碼 和輸入 名稱 共用
            stock_curMonRev = list(stock_detail2.values())[0][4]
            stock_lastMonRev = list(stock_detail2.values())[0][5]
            stock_lastYearMonRev = list(stock_detail2.values())[0][6]
            stock_lastMonRate = list(stock_detail2.values())[0][7]
            stock_lastYearMonRate = list(stock_detail2.values())[0][8]
            stock_curYearRev = list(stock_detail2.values())[0][9]
            stock_lastYearRev = list(stock_detail2.values())[0][10]
            stock_lastYearRate = list(stock_detail2.values())[0][11]
            stock_memo = list(stock_detail2.values())[0][12]
            data = {"股票名稱": stock_name, '股票號碼': stock_num, "目前股價": latest_close,
                    '開盤': latest_open, '高點': latest_high, '低點': latest_low, '成交量': latest_volume,
                    "當月營收": stock_curMonRev, '上月營收': stock_lastMonRev, '去年當月': stock_lastYearMonRev,
                    "上月營收增": stock_lastMonRate,
                    '去年同月營收增減': stock_lastYearMonRate, '今年營收': stock_curYearRev, '去年營收': stock_lastYearRev,
                    '去年營收增減': stock_lastYearRate, '股票備注': stock_memo, "查詢時間": now
                    }
            now_hour = datetime.datetime.now().hour  # 現在時間 :時
            weekday = datetime.date.today().weekday() + 1  # 現在時間 :周, 需加1 , 禮拜一為0
            print(f'現在時數: {now_hour},禮拜:{weekday}')
            if now_hour > 14 or weekday in [6, 7]:
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
    stock.stock_select2(stock.kerr_conn(), stock_type)  # select 出來
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


def number_map(number_record):  # 開獎號使用
    if number_record == '':
        return ''
    play_dict = {}
    print(number_record)
    if lottery_name == 'PC蛋蛋':
        sum_ = 0
        try:
            for i in number_record:
                sum_ = sum_ + int(i)
        except ValueError as e:
            print(e)
        for i in range(27):  # PC蛋蛋個號碼mapping 顏色
            if i in [0, 13, 14, 27]:
                number_color = '灰'
            elif i in [1, 4, 7, 10, 16, 19, 22, 25]:
                number_color = '綠'
            elif i in [2, 5, 8, 1, 11, 17, 20, 23, 26]:
                number_color = '藍'
            else:
                number_color = '紅'
            play_dict[i] = number_color
        record = number_record + "#總和:%s, 顏色:%s" % (sum_, play_dict[sum_])
        return record
    else:
        return number_record


def game_map(type_=''):  # 玩法 和 說明 mapping,type_ 預設  '' ,為玩法說明,  不是 '' ,走其他邏輯
    global game_theory, bonus, data  # 說明, 玩法
    if lottery_name in ['凤凰顺利秒秒彩']:
        print(game_play_type)
        if '五星' in game_play_type:
            if any(s in game_play_type for s in ['复式', '单式']):
                # if game_play_type in ['复式', '单式']:
                game_explan = '#五個號碼順續需全相同'
            elif '组选120' in game_play_type:
                game_explan = '#五個號碼相同,順續無需相同(開獎號無重覆號碼)'
        else:
            game_explan = '#test'
    elif lottery_name == '凤凰比特币冲天炮':
        game_theory = round(float(game_submit) / 0.9, 2)  # 快開  理論將金 另外算
        game_cal = '%s*%s=%s' % (game_amount, game_submit, float(game_submit) * game_amount)
        # '%s*(%s+%s*%s)'%(game_amount,game_submit,game_theory,game_point)# 獎金計算  原本公式 ,現在變成 直皆投注高度*金額
        game_explan = game_cal + '/獎金計算: 投注金額*投注內容#快開改後不帶返點'  # '獎金計算: 投注金額*(投注內容+理論獎金*反點)'
        bonus = (float(game_submit) + game_theory * game_point)
        data['中獎率'] = '0.95/投注內容%s=%s' % (game_submit, round(0.95 / float(game_submit), 4))
        data['理論獎金'] = str(game_theory) + "(投注內容/0.9)#快開改後不適用"
        data['獎金模式'] = "快開改前: %s" % bonus
        data['中獎獎金'] = '改前: %s/改後: %s' % (game_amount * bonus, game_award)
        del data['反點獎金']  # 快開沒參考價值
        del data['平台獎金']
    elif lottery_name == 'PC蛋蛋':
        if type_ == '':
            theory_data = data['理論獎金']  # ex : [1,2,3,4,5]
            theory_data[0] = str(theory_data[0]) + "#理論賠率"  # 只取列表第一個值 +  說明
            data['理論獎金'] = theory_data

            game_explan = '賠率=獎金#一注1元'
        else:
            pcdd_sum = {}
            if bet_type_code == '66_28_71':  # PC蛋蛋  和值玩法, 要錯特殊處理
                for i in range(28):  # 0-28 和值
                    if i < 13:
                        a = i + 72
                    elif i in (13, 14):
                        a = 85
                    else:
                        a = 99 - i
                    pcdd_sum[str(i)] = str(a)  # a 是傳回 個和值 數值 的 獎金
            elif bet_type_code == '66_13_84':  # 色波
                pcdd_sum['RED'] = '88'
                pcdd_sum['GREEN'] = '89'
                pcdd_sum['BLUE'] = '90'
            elif bet_type_code == '66_74_107':  # 大單,大雙 系列
                pcdd_sum['DADAN'] = '47'
                pcdd_sum['DASHUNG'] = '48'
                pcdd_sum['XIAODAN'] = '49'
                pcdd_sum['XIAOSHUNG'] = '50'
            return pcdd_sum
    elif lottery_name in ['北京快乐8', '快乐8全球彩', '福彩快乐8']:  # 後續再增加
        game_explan = "上盘(01-40),下盘(41-80)/ #合值>810(大)"
        theory_data = data['理論獎金']
        theory_data[0] = str(theory_data[0]) + "#多獎金,理論/平台獎金 有誤"  # 只取列表第一個值 +  說明
        data['理論獎金'] = theory_data
    else:
        game_explan = '#未補上'
        theory_data = data['理論獎金']  # ex : [1,2,3,4,5]
        theory_data[0] = str(theory_data[0]) + "#未補上"  # 只取列表第一個值 +  說明
        data['理論獎金'] = theory_data
    # data['獎金計算'] = game_cal
    data['遊戲說明'] = game_explan


@app.route('/stock_search3', methods=["POST"])
def stock_search3():
    stock.stock_search3(stock.kerr_conn())
    stock_detail = stock.stock_detail3


def status_style(val):  # 判斷狀態,來顯示顏色屬性 , 給 game_order 裡的order_status用
    color = None
    if val == '中獎':
        color = 'blue'
    elif val == '未中獎':
        color = 'red'
    else:
        raise Exception('參數錯誤')
    return (f'color:{color}')


@app.route('/get_cookie', methods=["GET"])
def get_cookie():  # 存放cookie皆口
    return cookie


@app.route('/game_result', methods=["GET", "POST"])  # 查詢方案紀錄定單號
def game_result():
    global game_play_type, game_amount, game_submit, game_point, lottery_name, game_theory, bonus, data, game_award, bet_type_code, len_game

    if request.method == "POST":
        game_code = request.form.get('game_code')  # 訂單號
        game_type = request.form.get('game_type')  # 玩法
        envConfig = Config.EnvConfig(request.form.get('env_type'))
        cookies_ = request.cookies  # 瀏覽器上的cookie
        conn = OracleConnection(env_id=envConfig.get_env_id())
        print(cookies_, envConfig.get_admin_url())
        if game_code != '':  # game_code 不為空,代表前台 是輸入 訂單號
            game_detail = conn.select_game_result(game_code)  # 將 取得 game_detail 宣告變數 遊戲訂單的 內容
            len_game = len(game_detail)
            print(game_detail)
            if len_game == 0:
                return "此環境沒有此訂單號"
            else:
                index_list, game_code_list, game_time_list, game_status_list, game_play_list, game_awardname_list = [], [], [], [], [], []
                lottery_id_list, game_submit_list, theory_bonus_list, ff_bonus_list, game_point_list, bonus_list = [], [], [], [], [], []
                game_amount_list, game_retaward_list, game_moneymode_list, game_mul_list, game_award_list = [], [], [], [], []
                game_awardmode_list = []
                issue_code = game_detail[0][19]  # 旗號
                lottery_id = game_detail[0][14]  # 彩種id
                number_record = conn.select_number_record(lottery_id, issue_code)[0]  # 開獎號
                for key in game_detail.keys():
                    print(key)
                    index_list.append(key)
                    game_code_list.append(game_code)  # 訂單號
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
                    game_play_type = game_detail[key][4] + game_detail[key][5] + game_detail[key][6]
                    game_play_list.append(lottery_name + "/" + game_play_type)
                    game_awardname_list.append(game_detail[key][8])
                    bet_type_code = game_detail[key][15]  # 玩法
                    theory_bonus = float(game_detail[key][16])  # 理論獎金

                    game_submit = game_detail[key][7]  # 投注內容
                    game_submit_list.append(game_submit)
                    if lottery_name == 'PC蛋蛋':
                        if bet_type_code not in ['66_28_71', '66_13_84', '66_74_107']:  # 同個玩法只有單一賠率
                            bonus = conn.select_bonus(lottery_id=lottery_id, bet_type_code=bet_type_code)
                        else:
                            game_map_ = game_map(type_=1)  # 呼叫玩法說明/遊戲mapping
                            print(game_map_)
                            if bet_type_code == '66_13_84':  # 色波
                                color_dict = {
                                    "红": "RED",
                                    "绿": "GREEN",
                                    "蓝": "BLUE"
                                }
                                game_submit = color_dict[game_submit]  # 換成 英文 , 因為要再去select_bonus  找  獎金
                            elif bet_type_code == '66_74_107':  # 大單,大雙,,,,,,
                                color_dict = {
                                    "大双": "DASHUNG",
                                    "小双": "XIAOSHUNG",
                                    "大单": "DADAN",
                                    "小单": "XIAODAN"
                                }
                                game_submit = color_dict[game_submit]  # 換成 英文 , 因為要再去select_bonus  找  獎金
                            else:  # 和值

                                pass  # 和值 0 -27 ,投注內容 keys不用做Mapping
                            # print(game_submit)
                            point_id = bet_type_code + "_" + game_map_[game_submit]  # 前面bet_type_code一致, _後面 動態

                            # 相同賠率 有不同完髮的(ex: 投注內容 0和27, 賠率都是 900 ), 需再把 投注內容game_submit 進去 找
                            bonus = conn.select_bonus(lottery_id=lottery_id, bet_type_code=point_id, detail=game_submit)
                        theory_bonus = bonus[0][1] / 10000
                        # print(theory_bonus,FF_bonus)
                    else:  # 其他大眾彩種
                        theory_bonus = theory_bonus / 10000  # 理論將金
                        point_id = bet_type_code + "_" + str(
                            theory_bonus)  # 由bet_type_code + theory_bonus 串在一起(投注方式+理論獎金])
                        # for i in soup.find_all('span', id=re.compile("^(%s)" % point_id)):  # {'id':point_id}):
                        # FF_bonus = float(i.text)
                        award_group_id = game_detail[key][17]  # 用來查詢 用戶 獎金組 屬於哪種
                        bonus = conn.select_bonus(lottery_id, bet_type_code, award_group_id)  # 使用bet_type_code like
                    pc_dd_bonus = bonus
                    FF_bonus = pc_dd_bonus[0][0] / 10000
                    theory_bonus_list.append(theory_bonus)
                    ff_bonus_list.append(FF_bonus)
                    game_point = float(float(game_detail[key][18]) / 10000)
                    game_point_list.append(game_point)
                    game_retaward = float(float(game_detail[key][10]) / 10000)  # 反點獎金 需除1萬
                    game_retaward_list.append(game_retaward)
                    game_award_mode = game_detail[key][9]  # 是否為高獎金
                    if game_award_mode == 1:
                        game_award_mode = '否'
                        bonus = f'{FF_bonus} - {game_point}'
                    else:
                        game_award_mode = '是'
                        bonus = game_retaward + FF_bonus  # 高獎金的話, 獎金 模式 + 反點獎金
                    game_awardmode_list.append(game_award_mode)
                    bonus_list.append(bonus)
                    game_amount = float(float(game_detail[key][2]) / 10000)  # 投注金額  需在除 1萬
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
                    game_award = float(float(game_detail[key][13]) / 10000)  # 中獎獎金
                    game_award_list.append(game_award)
                if number_record is None:
                    number_record = ''
                record_mapping = number_map(number_record)
                number_record = record_mapping
                # print(number_record)
                data = {"遊戲訂單號": game_code_list, "訂單時間": game_time_list, "中獎狀態": game_status_list,
                        "投注彩種/投注玩法": game_play_list,
                        "獎金組": game_awardname_list, "獎金模式狀態": game_awardmode_list,
                        '理論獎金': theory_bonus_list, "平台獎金": ff_bonus_list, "投注金額": game_amount_list,
                        "投注倍數": game_mul_list, "元角分模式": game_moneymode_list,
                        "投注內容": game_submit_list, '用戶反點': game_point_list, "獎金模式": bonus_list,
                        "反點獎金": game_retaward_list, "中獎獎金": game_award_list, "開獎號": number_record
                        }
                game_map()  # 呼叫玩法說明,更新data 
                frame = pd.DataFrame(data, index=index_list)
                return frame.to_html()
        elif game_type != '':  # game_type 不為空, 代表前台輸入 指定玩法
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
            order = conn.select_game_order(game_type)
            game_order = order[0]
            len_order = order[1]
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
            order_award_mode = []  # 獎金模式
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
                    award_mode = "一般獎金"
                else:
                    award_mode = '高獎金'
                order_award_mode.append(award_mode)
            # print(order_list)
            data = {"訂單號": order_list, "用戶名": order_user, "投注時間": order_time, "投注彩種": order_lottery, "投注玩法": order_type,
                    "投注內容": order_detail, "獎金模式": order_award_mode, "開獎號碼": order_record, "中獎狀態": order_status}
            frame = pd.DataFrame(data)
            # test = frame.style.applymap(status_style)#增加狀態顏色 ,這是for jupyter_notebook可以直接使用
            print(frame)
            return frame.to_html()

    return render_template('game_result.html')


@app.route('/user_active', methods=["POST", "GET"])
def user_acitve():  # 驗證第三方有校用戶
    if request.method == "POST":
        user = request.form.get('user')
        env = Config.EnvConfig(request.form.get('env_type'))
        conn = OracleConnection(env_id=env.get_env_id())
        joint_type = request.form.get('joint_type')

        userid = conn.select_user_id(user)
        # 查詢用戶 userid
        print(user, env)
        if len(userid) == 0:
            return ("此環境沒有該用戶")
        else:
            active_app = conn.select_active_app(user)
            # 查詢APP有效用戶 是否有值  ,沒值 代表 沒投注

            # print(active_user)
            bind_card = []  # 綁卡列表.可能超過多張
            card_number = []  # 該綁卡,有被多少張數綁定,但段 是否為有效性
            # print(active_app)

            user_fund = conn.select_active_fund(user)  # 當月充值
            print(user_fund)

            card_num = conn.select_active_card(user, env.get_env_id())  # 查詢綁卡數量

            if len(active_app) == 0:  # 非有效用戶,也代表 APP 有效用戶表沒資料(舊式沒投注)
                print(f"{user}用戶 為非有效用戶")

                active_submit = 0  # 有效投注
                is_active = "否"  # 有效用戶值

                if user_fund[0] is None:  # 確認沒充值
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

                # bind_card.append("test")
            else:  # 這邊長度非0, 是select_activeAPP 這方法,有值, 需判斷 is_active 是否為1
                if active_app[2] == 0:  # 列表[1] = is_active,  值 0 非有效
                    is_active = "否"  # active_user[0][1]
                    print(f"{user}用戶 為非有效用戶")
                else:
                    is_active = "是"  # active_user[0][1]
                    print(f"{user}用戶 為有效用戶")
                active_submit = active_app[3]

                # autoTest.Joy188Test.select_activeFund(autoTest.Joy188Test.get_conn(envs),user)#當月充值

                if user_fund[0] is None:  # 確認沒充值
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
            conn.close_conn()
            return frame.to_html()

    return render_template('user_active.html')


@app.route('/app_bet', methods=["POST"])
def app_bet():  # user_active, 第三方 銷量計算 接口
    user = request.form.get('user')
    env = Config.EnvConfig(request.form.get('env_type'))
    conn = OracleConnection(env_id=env.get_env_id())
    joint = request.form.get('joint_type')

    app_bet = conn.select_app_bet(user)  # APP代理中心,銷量/盈虧
    third_list = []  # 存放第三方列表
    active_bet = []  # 第三方有效投注
    third_prize = []  # 第三方獎金
    third_report = []  # 第三方盈虧
    third_memo = []  # 第三方memo
    for third_ in app_bet.keys():
        third = app_bet[third_][3]  # 第三方名稱
        third_list.append(third)
        active_bet.append(app_bet[third_][0])  # 有效銷量 為列表 1
        third_prize.append(app_bet[third_][1])
        third_report.append(app_bet[third_][2])
        if third == 'CITY':
            third_memo.append("#後台投注紀錄盈虧值 為用戶角度")
        elif third == 'BBIN':
            third_memo.append('#獎金不會小於0')
        elif third == 'LC':
            third_memo.append('#前台獎金=後台盈利額,前台投注金額=總投注,後台代理盈虧的遊戲獎金=有效投注額+投注紀錄的盈虧值')
        else:  # 待後續確認每個第三方 規則
            third_memo.append('')
    third_memo.append("用戶盈虧: 總獎金-有效銷量")
    third_list.append('ALL')
    active_bet.append(reduce(lambda x, y: x + y, active_bet))  # reduce 方法 為 可以計算列表總合, 再加到陣列裡
    third_prize.append(reduce(lambda x, y: x + y, third_prize))
    third_report.append(reduce(lambda x, y: x + y, third_report))

    # print(user_list,active_bet,third_prize,third_report)

    data = {"有效銷量": active_bet, "總獎金": third_prize, "用戶盈虧": third_report,
            "備註": third_memo}
    print(data)
    frame = pd.DataFrame(data, index=third_list)
    print(frame)
    conn.close_conn()
    return frame.to_html()


@app.route('/url_token', methods=["POST", "GET"])
def url_token():
    domain_keys = {  # url 為 keys,values 0 為預設連結, 1為 DB環境參數 , 2 為預設註冊按紐顯示
        'www.dev02.com': ['id=18408686&exp=1867031785352&pid=13438191&token=5705', 0, '否', '一般'],
        'www.fh82dev02.com': ['id=18416115&exp=1898836925873&pid=13518151&token=674d', 0, '是', '合營'],
        'www.teny2020dev02.com': ['id=18416115&exp=1898836925873&pid=13518151&token=674d', 0, '是', '合營'],
        'www.88hlqpdev02.com': ['id=18416447&exp=1900243129901&pid=13520850&token=c46d', 0, '是', '歡樂棋排'],
        'www2.joy188.com': ['id=23629565&exp=1870143471538&pid=14055451&token=e609', 1, '否', '一般'],
        'www2.joy188.195353.com': ['id=30402641&exp=1899103987027&pid=14083381&token=f2ae', 1, '是', '合營'],
        'www2.joy188.maike2020.com': ['id=30402641&exp=1899103987027&pid=14083381&token=f2ae', 1, '是', '合營'],
        'www2.joy188.teny2020.com': ['id=30402641&exp=1899103987027&pid=14083381&token=f2ae', 1, '是', '合營'],
        'www2.joy188.88hlqp.com': ['id=30402801&exp=1900315909746&pid=14084670&token=296f', 1, '是', '歡樂棋排'],
        'www.88hlqp.com': ['id=12724515&exp=1900124358942&pid=23143290&token=60f9', 2, '是', '歡樂棋排'],
        'www.maike2020.com': ['id=12569709&exp=1900396646000&pid=23075061&token=f943', 2, '是', '合營'],
        'www.maike2021.com': ['id=12569709&exp=1900396646000&pid=23075061&token=f943', 2, '是', '合營'],
        'www.maike2022.com': ['id=12569709&exp=1900396646000&pid=23075061&token=f943', 2, '是', '合營'],
        'www.maike2023.com': ['id=12569709&exp=1900396646000&pid=23075061&token=f943', 2, '是', '合營'],
        'www.teny2020.com': ['id=12727731&exp=1900585598288&pid=23119541&token=60ac&qq=7769700', 2, '是', '合營'],
        'www.fh82.com': ['id=12464874&exp=1883450993237&pid=2163831&token=b12f&qq=1055108800', 1, '是', '一般'],
        'www.fhhy2020.com': ['', 2, '待確認', '合營'],
        'www.fh888.bet': ['', 2, '待確認', '合營'],
        'www.fh666.bet': ['', 2, '待確認', '合營']
    }
    if request.method == "POST":
        token = request.form.get('token')
        id_ = request.form.get('id')
        user = request.form.get('user')
        env = request.form.get('env_type')
        joint_type = request.form.get('joint_type')
        conn = OracleConnection(env_id=int(env))
        # print(env)
        if env == '0':
            env_type = '02'
        elif env == '1':
            env_type = '188'
        else:
            env_type = '生產'

        # print(token,env,id_,joint_type,domain)
        if token not in ['', None]:  # token 直不為空, 代表頁面輸入的是token
            print('頁面輸入token')
            token_url = conn.select_url_token(token, joint_type)
            print(token_url)
            if len(token_url) == 0:
                return (f'{env_type}沒有該註冊碼: {token}')
            user = []
            url_created = []
            url = []
            day_list = []  # 用註冊碼查, 長度可能會有多個
            register_list = []
            len_data = []
            for i in token_url.keys():
                user.append(token_url[i][0])
                url_created.append(token_url[i][1])
                url.append(token_url[i][2])
                days = token_url[i][3]
                register = token_url[i][4]
                if days == -1:
                    days = '無窮'
                elif days == 0:
                    days = '失效'
                else:
                    days = '有效性時間: %s天' % days
                day_list.append(days)
                if register is None:
                    register = '無'
                register_list.append(register)
                len_data.append(i)
            data = {'用戶名': user, '創立時間': url_created, '開戶連結': url, '失效性': day_list, '註冊數': register_list}
        elif id_ not in ['', None]:
            print('頁面輸入id')
            token_url = conn.select_url_token(id_, joint_type)
            print(token_url)
            if len(token_url) == 0:
                return (f'{env_type}沒有該id: {id_}')
            # id是唯一值 , key 值接待0 即可
            user = token_url[0][0]
            url_created = token_url[0][1]
            url = token_url[0][2]
            days = token_url[0][3]
            register = token_url[0][4]
            if days == '-1':
                days = '無窮'
            else:
                days = '失效,有效性時間: %s' % days
            if register is None:
                register = '無'
            data = {'用戶名': user, '創立時間': url_created, '開戶連結': url, '失效性': days, '註冊數': register}
            len_data = [0]  # 輸入ID 查 連結, ID 為唯一直
        elif user not in ['', None]:  # 頁面輸入 用戶名 查詢用戶從哪開出
            print('頁面輸入用戶名')
            user_id = conn.select_user_id(user)  # 查詢頁面上 該環境是否有這用戶
            if len(user_id) == 0:
                return (f'{env_type}環境沒有該用戶: {user}')
            user_url = conn.select_user_url(user, 2, joint_type)  # 查詢用戶 被開出的連結 , 2 為type_
            if len(user_url) == 0:  # user_url 為空 ,被刪除
                data = {'用戶名': user, '用戶從此連結開出': '被刪除'}
                frame = pd.DataFrame(data, index=[0])
                print(frame)
                return frame.to_html()
            else:  # 這邊代表  user_url 是有值,  在去從days 判斷是否失效
                if user_url[0][4] == -1:
                    days = '否'
                else:  # 不等於 -1 為失效
                    days = '是'
            data = {'用戶名': user, '用戶從此連結開出': user_url[0][1], '連結是否失效': days,
                    '用戶代理線': user_url[0][2], '裝置': user_url[0][3]}
            len_data = [0]
        else:  # 輸入domain 查尋 預設連結
            try:  # 對頁面輸入的domain, 做格式化處理
                domain = request.form.get('domain').strip()  # 頁面網域名稱 . strip 避免有空格問題
                print(domain)
                # env = domain_keys[domain][1]#  1 為環境 ,0 為預設連結
            except KeyError:  #
                raise KeyError('連結格式有誤')
            domain_url = conn.select_domain_default_url(domain)
            print(domain_url)
            if len(domain_url) != 0:  # 代表該預名 在後台全局管理有做設置
                domain_admin = '是'  # 後台是否有設定 該domain
                register_display = domain_url[0][3]  # 前台註冊按紐 是否隱藏
                if register_display == 0:
                    register_display = '關閉'
                else:
                    register_display = '開啟'
                app_display = domain_url[0][4]  # 前台掃碼 是否隱藏
                if app_display == 0:
                    app_display = '關閉'
                else:
                    app_display = '開啟'
                admin_url = domain_url[0][2]  # url 是預設連結,或者後台的設置 代理聯結
                agent = domain_url[0][1]
                domain_type = domain_url[0][5]  # 後台設置 環境組 的欄位
                if domain_type == 0:  # 0:一般,1:合營,2:歡樂期排
                    domain_type = '一般'
                elif domain_type == 1:
                    domain_type = '合營'
                else:
                    domain_type = '歡樂期排'
                env_type = domain_type + "/" + env_type  # 還台有設置 ,不能用damain_keys來看, 有可能 業務後台增加, damain_keys沒有
                status = domain_url[0][6]
                if status == 0:
                    status = '上架'
                else:
                    status = '下架/導往百度'

                data = {"網域名": domain, '環境': env_type, '後台是否有設置該網域': domain_admin, '後台設定連結': admin_url,
                        '後台設定待理': agent, '後台註冊開關': register_display, '後台掃碼開關': app_display, '後台設定狀態': status}
            else:  # 就走預設的設定
                try:
                    if domain_keys[domain][1] != int(env):
                        return ("該環境沒有此domain")
                    domain_admin = '否'
                    admin_url = '無'  # 後台沒設置
                    url = domain_keys[domain][0]  # 沒設定 ,為空, 走預設連結
                    register_status = domain_keys[domain][2]
                    env_type = domain_keys[domain][3] + "/" + env_type  # 後台沒設置, 就從domain_keys 原本 預設的規則走
                except KeyError:
                    return "網域名稱有誤"

                data = {"網域名": domain, '環境': env_type, '後台是否有設置該網域': domain_admin, '預設連結': url,
                        '預設註冊按紐': register_status}
            len_data = [0]  # 查詢網域名 ,長度只會為 1
        try:
            frame = pd.DataFrame(data, index=len_data)
            print(frame)
            conn.close_conn()
            return frame.to_html()
        except ValueError:
            conn.close_conn()
            raise ValueError('DATA有錯誤')
    return render_template('url_token.html')


@app.route('/sun_user2', methods=["POST"])
def sun_user2():  # 查詢太陽成 指定domain
    if request.method == 'POST':
        env = request.form.get('env_type')
        conn = OracleConnection(env_id=int(env))
        domain = request.form.get('domain_type')
        print(env, domain)
        sun_user = conn.select_sun_user('', 2, domain)
        print(sun_user)

        data = {'域名': [sun_user[i][0] for i in sun_user.keys()],
                '代理': [sun_user[i][1] for i in sun_user.keys()],
                '連結': [sun_user[i][2] for i in sun_user.keys()],
                '註冊顯示': ['是' if sun_user[i][3] == 1 else "否" for i in sun_user.keys()],
                '狀態': ['下架' if sun_user[i][4] == 1 else '正常' for i in sun_user.keys()],
                '備註': [sun_user[i][5] for i in sun_user.keys()],
                '連結失效性': ['失效' if sun_user[i][6] != -1 else '正常' for i in sun_user.keys()],
                '註冊數量': ['0' if sun_user[i][7] is None else int(sun_user[i][7]) for i in sun_user.keys()]
                }
        frame = pd.DataFrame(data, index=[i for i in sun_user.keys()])
        print(frame)
        conn.close_conn()
        return frame.to_html()
    else:
        raise Exception('錯誤')


@app.route('/sun_user', methods=["POST", "GET"])
def sun_user():  # 太陽成用����� 找尋
    if request.method == "POST":
        user = request.form.get('user')
        env = request.form.get('env_type')
        domain = request.form.get('domain_type')
        conn = OracleConnection(env_id=int(env))
        print(user, env, domain)
        if env == '0':
            env_name = 'dev'
        elif env == '1':
            env_name = '188'
        else:
            print(env)
            env_name = '生產'
        if domain == '0':
            domain_type = '太陽城'
        else:
            domain_type = '申博'  # domain  = "1"
        if user in [None, '']:
            type_ = 1  # 頁面查詢 轉移成功用戶,
        else:
            type_ = ''  # 查詢 指定用戶
        print(type_)
        sun_user = conn.select_sun_user(user, type_, domain)  # 太陽/申博用戶
        print(sun_user)
        if len(sun_user) == 0:
            if type_ == 1:
                raise Exception('目前還沒有成功轉移用戶')
            raise Exception(f'{env_name + domain_type}沒有該用戶 : {user}')
        if type_ != 1:  # 指定用戶
            user = sun_user[0][0]
            phone = sun_user[0][1]
            tran_status = sun_user[0][4]
            if tran_status == 1:
                tran_status = '成功'
            else:
                tran_status = '未完成'
            tran_time = sun_user[0][5]
            index_len = [0]
            user_id = conn.select_user_id(user, int(domain))  # 4.0 資料庫
            '''
            if len(userid) == 0:# 代表該4.0環境沒有該用戶
                FF_memo = '無'
            else:
                FF_memo = '有'
            '''
            data = {'環境/類型': env_name + domain_type, '用戶名': user, '電話號碼': phone, '轉移狀態': tran_status, '轉移時間': tran_time,
                    # '4.0資料庫':FF_memo
                    }
        else:  # 找尋以轉移用戶, 資料會很多筆
            user = []
            phone = []
            tran_status = []
            tran_time = []
            index_len = []
            for num in sun_user.keys():
                user.append(sun_user[num][0])
                phone.append(sun_user[num][1])
                if sun_user[num][2] == 1:
                    status = '成功'
                else:
                    status = '失敗'
                tran_status.append(status)
                tran_time.append(sun_user[num][3])
                index_len.append(num)
            data = {'環境/類型': env_name + domain_type, '用戶名': user, '電話號碼': phone, '轉移狀態': tran_status, '轉移時間': tran_time}
        frame = pd.DataFrame(data, index=index_len)
        print(frame)
        conn.close_conn()
        return frame.to_html()
    return render_template('sun_user.html')


@app.route('/fund_activity', methods=["POST", "GEt"])
def fund_activity():  # 充值紅包 查詢
    if request.method == "POST":
        user = request.form.get('user')
        env = request.form.get('env_type')
        conn = OracleConnection(env_id=int(env))
        print(user, env)
        user_id = conn.select_user_id(user)  # 查詢頁面上 該環境是否有這用戶
        if len(user_id) == 0:
            raise Exception('該環境沒有此用戶')
        red_able = conn.select_red_fund(user)  # 先確認 是否領取過紅包
        print(red_able)

        fund_list = []  # 存放各充值表的 紀錄 ,總共四個表
        for i in range(4):
            red_able = conn.select_red_fund(user, i)
            fund_list.append(red_able)
        # begin_mission = AutoTest.fund_# 新守任務表
        print(fund_list)
        data = {}
        fund_log = 0  # 紀錄 是否 四個表都沒有資料
        for _index, fund_data in enumerate(fund_list):
            if _index == 0:
                msg = '新手任務：/BEGIN_MISSION'
            elif _index == 1:
                msg = '活動：/ACTIVITY_FUND_OPEN_RECORD'
            elif _index == 2:
                msg = '資金明細：/fund_change_log'
            elif _index == 3:
                msg = '資金明細搬動：/fund_change_log_hist'
            else:
                raise Exception('fund_activity -> index out of range.')

            if len(fund_data) == 0:
                msg2 = '無紀錄'
            else:
                msg2 = f'{fund_data[0]}'
                fund_log = fund_log + 1  #
            logger.info('fund_activity -> msg = {}, msg2 = {}'.format(msg, msg2))
            data[msg] = msg2

        logger.warning(f'fund_activity ->red_able = {red_able}')
        logger.warning(f'fund_activity ->fund_list = {fund_list}')
        if len(red_able) == 0:  # 紅包還沒領取
            red_able = '否'
            if fund_log == 0:  # 代表沒成功
                activity_able = '符合資格'
            else:
                activity_able = "不符合資格"
        else:  # 代表已經領取過 紅包
            red_able = float(red_able[0][0] / 10000)
            activity_able = "符合資格"
        data['紅包是否領取'] = '紅包金 : {}'.format(red_able)
        data['充直紅包活動'] = activity_able
        logger.info(f'fund_activity -> data = {data}')
        frame = pd.DataFrame(data, index=[0])
        logger.info(f'fund_activity -> frame = {frame}')

        conn.close_conn()
        return frame.to_html()
    return render_template('fund_activity.html')


@app.route('/api_test', methods=["GET", "POST"])
def api_test():
    import FF_Joy188
    if request.method == "POST":
        print(request.cookies)
        request_type = request.form.get('request_type')
        content_type = request.form.get('Content_type')  # header
        from urllib.parse import urlsplit
        url = urlsplit(request.form.get('url'))  # url 要切割
        url_domain = url.scheme + '://' + url.netloc  # 為網域名
        url_path = url.path  # .com/ 後面url路徑
        url_query = url.query  # url 把參數加在面url的
        if url_query != '':  # url有這段的化, 需加? 參數
            url_query = '?%s' % url_query
        data = request.form.get('request_data')
        login_cookie = request.form.get('login_cookie')
        check_type = request.form.get('check_type')
        header_key = request.form.getlist('header_key')
        header_value = request.form.getlist('header_value')
        print(check_type, login_cookie, header_key, header_value)
        header = {
            "Content-Type": content_type,
            'User-Agent': FF_Joy188.FF_().user_agent['Pc'],  # 這邊先寫死給一個
        }
        for key, value in zip(header_key, header_value):  # header_key/ header_value  為列表
            if key == "":  # 如果為空 就不增加到 header裡
                pass
            else:
                header[key] = value
        if login_cookie != '':
            header['Cookie'] = login_cookie
        print(header)
        print(request_type, content_type, url_domain, url_path, url_query, data)
        threads, status, content, req_time = [], [], [], []
        if request_type == 'post':
            thread_func = FF_Joy188.FF_().session_post
        else:
            thread_func = FF_Joy188.FF_().session_get
        if check_type == 'thread_check':  # 併發
            num = 2
        else:
            num = 1
        for i in range(num):
            t = threading.Thread(target=thread_func, args=(url_domain, url_path + url_query, data, header))
            threads.append(t)
        # print(len(threads))
        for i in threads:
            i.start()
        for i in threads:
            i.join()
            print(FF_Joy188.content)
            status.append(FF_Joy188.status)
            content.append(FF_Joy188.content)
            req_time.append(FF_Joy188.req_time)
        # print(FF_Joy188.content)
        result = {}
        result['status'] = '連線狀態: %s' % status[-1]
        result['data'] = content[-1]
        result['time'] = req_time[-1]
        return result
    return render_template('api_test.html')


@app.route('/gameBox', methods=["POST", "GET"])
def gameBox():
    admin_items, user_items = {}, {}  # 管理/客戶端
    import GameBox
    for key in GameBox.GameBox().data_type.keys():
        # print(key)
        # 中文名稱為key, 英文參數唯value,用意 顯示在頁面上中文
        if key == 'getClientInfo':  # 管理端 用  獲得client信息即可,其它 不需動
            admin_items[GameBox.GameBox().data_type[key][0]] = key
        elif key in ['token', 'createApp', 'updateIpWhitelist', 'updateSupplierAccount']:  # 管理端
            pass
        else:
            user_items[GameBox.GameBox().data_type[key][0]] = key
    if request.method == "POST":
        client_type = {
            "api_key": ["1566e8efbdb444dfb670cd515ab99fda", "XT", "9RJ0PYLC5Ko4O4vGsqd", "",
                        "a93f661cb1fcc76f87cfe9bd96a3623f", "BgRWofgSb0CsXgyY", "b86fc6b051f63d73de262d4c34e3a0a9",
                        "8153503006031672EF300005E5EF6AEF"]
            , "api_url": ["https://api.dg99web.com", "http://tsa.l0044.xtu168.com",
                          "https://testapi.onlinegames22.com", "http://api.cqgame.games",
                          "http://gsmd.336699bet.com", "https://testapi.onlinegames22.com",
                          "http://ab.test.gf-gaming.com", "http://am.bgvip55.com/open-cloud/api/"]
            , "supplier_type": ["dream_game", "sa_ba_sports", "ae_sexy", "cq_9", "gpi", "ya_bo_live", "pg_game",
                                "bg_game"]
            , "supplier_user": ["DGTE01011T", "6yayl95mkn", "fhlmag", "cq9_test", "xo8v", "ZSCH5",
                                "aba4d198602ba6f2a3a604edcebd08f1", "am00"]
            , "game_type": ["DG", "沙巴", "Sexy", "Cq9", 'GPI', "YB", "PG", "BG"]
        }
        cq_9Key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiI1ZjU5OWU3NTc4MDdhYTAwMDFlYTFjMjYiLCJhY2NvdW50IjoiYW1iZXJ1YXQiLCJvd25lciI6IjVkYzExN2JjM2ViM2IzMDAwMTA4ZTQ4NyIsInBhcmVudCI6IjVkYzExN2JjM2ViM2IzMDAwMTA4ZTQ4NyIsImN1cnJlbmN5IjoiVk5EIiwianRpIjoiNzkyMjU1MDIzIiwiaWF0IjoxNTk5NzA4Nzg5LCJpc3MiOiJDeXByZXNzIiwic3ViIjoiU1NUb2tlbiJ9.cyvPJaWFGwhX4dZV7fwcwgUhGM9d5dVv8sgyctlRijc"
        url_dict = {0: ['http://43.240.38.15:21080', '測試區'], 1: ['http://54.248.18.149:8203', '灰度']}  # 測試 / 灰度
        env_type = request.form.get('env_type')
        game_type = request.form.get('game_type')  # 0 : DG , 1: 沙巴
        user = request.form.get('user')
        check_type = request.form.get('check_type')  # 0 為管理端/ 1 : 客戶端
        print(env_type, game_type, user, check_type)
        game_list = []  # 存放前台選擇的 測試項目
        if check_type == '0':
            game_list.append('token')  # 管理端 先獲得 token
            game_list.append(request.form.get('admin_name'))
        else:
            game_list.append(request.form.get('user_name'))
        print(game_list)

        api_key = client_type["api_key"][int(game_type)]
        api_url = client_type["api_url"][int(game_type)]
        supplier_type = client_type["supplier_type"][int(game_type)]
        supplier_user = client_type["supplier_user"][int(game_type)]
        clientId = client_type["supplier_user"][int(game_type)]
        client_detail = GameBox.GameBox.GameBox_Con(client_id=clientId, env=int(env_type))
        url = url_dict[int(env_type)][0]
        url_type = '%s, ' % url + client_type['game_type'][int(game_type)] + url_dict[int(env_type)][1]
        GameBox.suite_test(game_type=int(game_type), url_type=url_type, clientId=clientId, user=user,
                           client_detail=client_detail,
                           api_key=api_key, api_url=api_url, supplier_type=supplier_type, url=url,
                           game_list=game_list, user_items=user_items, admin_items=admin_items, cq_9Key=cq_9Key)

        return 'ok'
    print(admin_items, user_items)
    return render_template('gameBox.html', user_items=user_items, admin_items=admin_items)


@app.route('/fund_fee', methods=["POST", "GET"])  # 充值/提線 手續費查詢
def fund_fee():
    if request.method == "POST":
        select_type = request.form.get('type')
        env_type = request.form.get('env_type')
        user = request.form.get('user')
        print(select_type, user)
        # 總代: 因為parent_id  為 -1.需用 user_iD查
        conn = OracleConnection(env_id=int(env_type))
        fund_fee = conn.select_fee(select_type, user)
        # fund_fee = AutoTest.fund_fee
        print(fund_fee)
        if select_type == "fund":  # 充值
            type_msg = "充值"
            if len(fund_fee) == 0:  # 總代線沒設定
                rule_msg = "總代線沒設定,走平台設定"
            else:  # 總代線有設定手續費
                FF_list = []  # 存放平台的 充值
                for key in fund_fee:
                    if fund_fee[key][0] in [i for i in range(1, 16)]:  # [0] 是bank_id  , [1-15] 是 PC銀行卡
                        ff_name = "PC銀行卡"
                    elif fund_fee[key][2] == 1:  # APP
                        ff_name = "APP%s" % fund_fee[key][3]
                    elif fund_fee[key][2] == 0:  # PC
                        ff_name = "PC%s" % fund_fee[key][3]
                    FF_list.append(ff_name)
                rule_msg = '走總代線設定%s' % set(FF_list)

            data = {"手續費類型": type_msg, "手續費規則": rule_msg, "備註": "總代線有設定走平台/不管用戶身分"}
        else:  # 提線
            user_lvl = conn.select_user_lvl(user)
            type_msg = "提現"
            if len(fund_fee) == 0:  # 總代線沒設定
                rule_msg = "總代線沒設定,走平台設定"
            elif fund_fee[0][0] == 0:  # 手續費有設定,開關
                rule_msg = "總代線开設定關閉,走平台"
            elif user_lvl[0][1] == 0:  # 非星級
                rule_msg = "一般用戶"
                if user_lvl[0][0] >= 1:  # 柏金 vip
                    rule_msg = rule_msg + ",vip/走平台"
                else:
                    rule_msg = rule_msg + ",非vip/走總代線設定"
            elif user_lvl[0][1] == 1:  # 星級
                rule_msg = "星級用戶"
                if user_lvl[0][0] >= 3:  # 星級 3 等以上 vip
                    rule_msg = rule_msg + ",vip/走平台"
                else:
                    rule_msg = rule_msg + ",非vip/走總代線設定"
            data = {"手續費類型": type_msg, "手續費規則": rule_msg}
        frame = pd.DataFrame(data, index=[0])
        print(frame)
        return frame.to_html()
    return render_template('FundFee.html')


@app.route('/FundCharge', methods=["POST", "GET"])
def FundCharge():  # 充值成功金額 查詢
    if request.method == "POST":
        env_type = request.form.get('env_type')
        check_type = request.form.get('check_type')  # '0'使用日期 , '1'使用月份
        # AutoTest.get_rediskey(2)  # 連到本地 redis
        if check_type == '0':  # 單日
            day = request.form.get('day_day')
            month = request.form.get('day_month')
            year = request.form.get('day_year')
            date = "%s/%s/%s" % (year, month, day)  # 格式化日期 傳到  select_FundCharge
            key_name = 'FundCharge: %s/%s/%s' % (check_type, env_type, date)  # 0/環境:日期
            result = RedisConnection.get_key(2, key_name)
            # result = AutoTest.get_key(key_name)
            print(result)
            if result != 'not exist':  # 代表 已經存 到redis過
                return result
            conn = OracleConnection(env_id=int(env_type))
            data_fund = conn.select_fund_charge(date)
            # data_fund = AutoTest.data_fund  # key 為0 , value 0 為發起金額 總合, 1為 手續費總和 , 2 為充值個數
            # print(data_fund)
            if len(data_fund) == 0:
                sum_fund = 0
                len_fund = 0
                len_Allfund = 0
            else:
                if data_fund[0][1] is None:  # 有手續費 是none
                    fund_fee = 0
                else:
                    fund_fee = int(data_fund[0][1]) / 10000
                if data_fund[0][0] is None:  # 有充值金額 是none
                    fund_apply = 0
                else:
                    fund_apply = int(data_fund[0][0]) / 10000
                len_fund = data_fund[0][2]
                sum_fund = fund_apply - fund_fee  # 發起充值金額 - 手續費 , 兩者相減
                len_Allfund = conn.select_fund_charge(date, '1')[0][0]  # 總個數
                # len_Allfund = AutoTest.data_fund[0][0]
                try:
                    fund_per = int(int(len_fund) / int(len_Allfund) * 10000) / 100
                except ZeroDivisionError:
                    fund_per = 0
                # fund_list =  reduce(lambda x,y: x+y,fund_list)#計算列表裡數值總合
            data_ = {"date": date, "sum_fund": sum_fund, "len_fund": len_fund, "len_Allfund": len_Allfund,
                     'fund_per': fund_per}
            RedisConnection.set_key(key_name, data_)
            # AutoTest.set_key(key_name, data_)
        else:  # 月份
            now = datetime.datetime.now()
            now_day = now.day  # 今天日期
            now_month = now.month  # 這個月
            month = request.form.get('month_month')
            year = request.form.get('month_year')
            date = "%s/%s" % (year, month)  # 格式化日期 傳到  select_FundCharge
            # print(month,now_month)
            if month == str(now_month):  # 頁面選擇的 月份 等於這個月, 需把 當下日期 一起加進去 , 因為 這個月每天進來 都會 有新的一天數據
                key_name = 'FundCharge: %s/%s/%s-%s' % (check_type, env_type, date, now_day)  # 1/環境:日期 , 多增加今天日期為key
            else:
                key_name = 'FundCharge: %s/%s/%s' % (check_type, env_type, date)  # 不是這個月, 不用管今天日期
            result = RedisConnection.get_key(2, key_name)
            # result = AutoTest.get_key(key_name)
            print(result)
            if result != 'not exist':  # result是 not exist, 代表 redis 沒值 ,不等於 就是 redis有值
                return result
            # print(date)
            conn = OracleConnection(env_id=int(env_type))
            data_fund = conn.select_fund_charge(date, 'month')
            # AutoTest.Joy188Test.select_FundCharge(AutoTest.Joy188Test.get_conn(int(env_type)), date, 'month')
            # data_fund = AutoTest.data_fund  # key 為日期 , value 0 為發起金額 總合, 1為 手續費總和 , 2 為充值個數
            # print(data_fund)
            date_list, sum_fund_list, len_fund_list, fund_per_list, len_Allfund_list = [], [], [], [], []
            for key, value in data_fund.items():
                date_list.append(key)
                if value[0] is None:  # 發起金額
                    fun_apply = 0
                else:
                    fun_apply = value[0] / 10000
                if value[1] is None:  # 手續費
                    len_fund = 0
                else:
                    len_fund = value[1] / 10000
                sum_fund = fun_apply - len_fund  # 充直總發起金額
                sum_fund_list.append(int(sum_fund * 100) / 100)
                len_fund = value[2]  # 充值成功個數
                len_fund_list.append(len_fund)
                len_Allfund = value[3]  # 充值 總個數
                len_Allfund_list.append(len_Allfund)
                try:
                    fund_per = int(int(len_fund) / int(len_Allfund) * 10000) / 100
                except ZeroDivisionError:  # 0/0 報的錯
                    fund_per = 0
                fund_per_list.append(fund_per)  # 充值 成功率
            data_ = {"date": date_list, "sum_fund": sum_fund_list, "len_fund": len_fund_list,
                     "len_Allfund": len_Allfund_list,
                     'fund_per': fund_per_list}
            RedisConnection.set_key(key_name, data_)
        # print(data_)
        return data_
        # frame = pd.DataFrame(data,index=date_list)
        # return frame.to_html()
    return render_template('FundCharge.html')


@app.route('/newAgent', methods=["POST", "GET"])
def new_Agent():  # 新代理中心
    reson_dict = {
        'Turnover': [{'GM,DVCB,null,2': "投注扣款", 'GM,DVCN,null,2': "追号投注扣款", 'GM,PDXX,null,3': "奖金派送",
                      'GM,BDRX,null,1': "撤销派奖", 'OT,RBAP,null,3': "加币-补发奖金", 'OT,BDBA,null,3': "扣币-中奖减项",
                      'HB,DHBS,null,2': "红包抵扣"}, "4.0輸贏"],
        "Activities": [{'PM,PGXX,null,3': "活动礼金-加幣/舊代理也用", 'PM,IPXX,null,3': "平台奖励/舊代理也用",
                        'PM,PMXX,null,3': '加币-积分商城', 'GM,FBRX,null,1': '首投返利', 'OT,ADBA,null,3': '扣币-活动减项',
                        'PM,PGXX,null,4': '活动礼金-自动/舊代理也用', 'PM,PGXX,null,5': '活动礼金-代活动系统派发/舊代理也用',
                        'PM,PGPT,null,1': 'PT活动奖金', 'PM,PGAP,null,1': 'PT活动礼金', 'PM,PGFX,null,1': 'FHX活动礼金',
                        'PM,EGPR,null,1': "凤凰体育体验金活动", 'PM,PGSP,null,1': "凤凰体育活动奖金",
                        'PM,PGNS,null,1': "GNS活动礼金", 'PM,PGNP,null,1': "GNS活动奖金", 'PM,PGLC,null,1': "凤凰棋牌活动礼金",
                        'PM,PLCP,null,1': "凤凰棋牌活动奖金", 'PM,PGSB,null,1': "沙巴活动礼金", 'PM,PSBP,null,1': "沙巴活动奖金",
                        'PM,PGAG,null,1': "AG活动礼金", 'PM,PAGP,null,1': "AG活动奖金", 'PM,PGKY,null,1': "开元活动礼金",
                        'PM,PKYP,null,1': "开元活动奖金", 'PM,PGIM,null,1': "IM活动礼金", 'PM,PIMP,null,1': "IM活动奖金",
                        'PM,PBCP,null,1': "BC体育活动奖金", 'PM,PGCT,null,1': "爱棋牌活动礼金", 'PM,PGBB,null,1': "BBIN活动礼金",
                        'PM,PBBP,null,1': "BBIN活动奖金", 'PM,PGBG,null,1': "BG真人活动礼金", 'PM,PGPG,null,1': "PG电子活动礼金",
                        'PM,PGPL,null,1': "凤凰真人活动礼金", 'PM,TAAM,null,3': "三方活动奖金"}, "活動獎金總計"],
        "Rebates": [{'OT,RDBA,null,3': "反點扣項", 'GM,RHAX,null,2': "上级投注返点", 'GM,RSXX,null,1': "本人投注返点",
                     'GM,RRSX,null,1': "撤销本人投注返点", 'GM,RRHA,null,2': "撤销上级投注返点"}, "彩票反點"],
        "NewVipReward": [{'PM,SVUR,null,1': "晋级礼金", 'PM,RHYB,null,6': "彩票返水", 'PM,RHYB,null,3': "体育返水",
                          'PM,RHYB,null,4': "电竞返水", 'PM,RHYB,null,5': "真人返水", 'PM,RHYB,null,7': "加幣-星级返水",
                          'OT,SVWD,null,3': "扣币-星级返水", 'OT,SVWF,null,3': "扣币-星级三方返水"}, "星級獎勵"],
        'Red': [{'HB,AHBC,null,1': "红包收入", '': ''}, '紅包'],
        'Depoist': [{'FD,ADAL,null,3': "一般充值", 'OT,AAXX,null,3': "人工加幣", 'FD,ADML,null,8': "人工干预",
                     'FD,MDAX,null,5': "加币-人工充值"}, '充直'],
        "DepoistFee": [{"FD,ADAC,null,1": "充值手續費", "": ""}, "充直手續費"],
        'Withdraw': [{'FD,CWTS,null,5': "发起提现成功", 'FD,CWTS,null,6': "打款部分成功 ",
                      'FD,CWCS,null,4': "打款-人工提现", 'FD,CWCS,null,6': "?"}, '提現'],
        "WithdrawFee": [{"FD,ADAC,null,1": "充值手續費", "": ""}, "提現手續費"],
        'DailyWage': [{'TF,DLSY,null,1': "转入日工资-系統(新舊)", 'PM,AADS,null,3': "日工资派发-人工(新)",
                       'OT,WDBA,null,3': "扣币-日工资减项(新)", "TF,DABR,null,1": '轉入下級日工資/系統(新舊)'}, '日工資'],
        'MonthWage': [{'TF,MLDD,null,1': '转入月分红-系統(新舊)', 'PM,AAMD,null,3': '月分红派发-人工(新)', 'GM,DDAX,null,1': '彩票分红(新舊)',
                       'OT,DDBA,null,3': '扣币-分红减项(新)'}, '月分紅'],  # 轉入下級分紅  暫時沒扣除
        'ThirdRebates': [{'GM,SFFS,null,1': "三方返水/後台加幣(新舊)", 'OT,TDBA,null,3': "扣币-返水减项(新)",
                          "TF,TADS,null,1": "轉入反水/系統(新舊)", "TF,DTWR,null,1": "下級反水/系統(新舊)"}, '反水'],
        'ThirdShares': [{'GM,SFYJ,null,1': "三方佣金/後台加幣", 'OT,TDDA,null,3': "扣币-佣金减项"}, '佣金'],
        # "Compensation": [{'OT,CEXX,null,3':"客户理赔/人工-加币-投诉理赔",'OT,PCXX,null,3':"平台理赔"},'理賠'] 理賠移除 淨數贏
    }
    if request.method == "POST":
        env_type = request.form.get('env_type')
        joint_type = request.form.get('joint_type')
        user = request.form.get('user')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        check_type = request.form.get('check_type')  # 判斷頁面是點了哪個查詢

        print(check_type, start_time, end_time)
        conn = OracleConnection(env_id=int(env_type))
        user_id = conn.select_user_id(user, joint_type)
        print(user_id)
        if len(user_id) == 0:
            return '無該用戶'
        now_hour = datetime.datetime.now().hour  # 當下 小時
        now_day = datetime.datetime.now().day  # 當下 日期
        print(now_day)
        if str(now_day) == start_time[-1] and str(now_day) == end_time[
            -1]:  # 開始/結束時間 是今天的話, 需要待now_hour 進去key , 因為當天的 每個小時牌成 都有可能變動
            print('查詢今天日期')
            key_name = 'NewAgent: %s/%s/%s-%s:%s' % (check_type, user, start_time, end_time, now_hour)
        else:
            key_name = 'NewAgent: %s/%s/%s-%s' % (check_type, user, start_time, end_time)  # 0/環境:日期
        result = RedisConnection.get_key(2, key_name)
        if result != 'not exist':  # result是 not exist, 代表 redis 沒值 ,不等於 就是 redis有值
            return result
        if check_type == "ThirdBet":  # 第三方 抓 COLLECT_THIRDLY_BET_RECORD 表
            data = conn.select_NewAgent_ThirdBet(user, joint_type, start_time, end_time)
        elif check_type == 'GP':  # 淨輸贏 需把所有reason 做出來,  但只抓sum  和 三方
            data_third = conn.select_NewAgent_ThirdBet(user, joint_type, start_time, end_time, 'sum')
            # 移除淨輸贏 沒計算 的項目
            del reson_dict['Depoist']
            del reson_dict['Withdraw']
            del reson_dict['MonthWage']
            del reson_dict['ThirdShares']
            data_fund = conn.select_NewAgent(user, joint_type, start_time, end_time, reson_dict, check_type)
            # print(data_third,data_fund)
            data = data_third.copy()
            data.update(data_fund)
        else:  # 其他 fund_change_log ,需帶不同reson
            reson_key = tuple(reson_dict[check_type][0].keys())  # reson名稱 ,tuple 格式
            data = conn.select_NewAgent(user, joint_type, start_time, end_time, reson_key, check_type)
        print(data)
        if len(data) == 0:
            return "無資料"
        items = []  # 存放 reson中文名稱
        if check_type in ['ThirdBet', 'GP']:  # 需做處理,不然items都叫 銷量/中獎
            pass
        else:
            for i in range(len(data['用戶名'])):
                reson_name = reson_dict[check_type][0][data['帳變摘要'][i]]  # data['帳變摘要'][i] 取出  reson的英文名稱
                items.append(reson_name)
            data["備註"] = items
        RedisConnection.set_key(key_name, data)
        return data
    return render_template('newAgent.html', items=reson_dict)


@app.route('/Single', methods=["GET", "POST"])
def Single():  # 單挑
    if request.method == "POST":
        env_type = request.form.get('env_type')
        order_code = request.form.get('order_code')
        day = request.form.get('day_day')
        month = request.form.get('day_month')
        year = request.form.get('day_year')
        date = "%s/%s/%s" % (year, month, day)
        lotteryid = request.form.get('lottery')

        conn = OracleConnection(env_id=int(env_type))
        order_ = conn.select_game_order_data(order_code, lotteryid, date)  # 用來確認 該環境有沒有 該order_code
        if len(order_) == 0:
            return '無該單號'
        elif order_[0]["STATUS"] == 3:  # 該game_order 未中獎 一定不會進單挑:
            return '該單沒中獎, 不會進單挑'
        elif order_[0]["STATUS"] == 1:  # 該game_order 等待開獎 一定不會進單挑:
            return '該單未開獎, 不會進單挑'
        elif order_[0]["STATUS"] == 4:  # 該game_order 等待開獎 一定不會進單挑:
            return '該單撤銷, 不會進單挑'

        key_name = "Single:%s_%s_%s_%s" % (env_type, order_code, lotteryid, order_[0]["STATUS"])  # redis key存入
        result = RedisConnection.get_key(2, key_name)
        if result != 'not exist':  # result是 not exist, 代表 redis 沒值 ,不等於 就是 redis有值
            return result

        slip_ = conn.select_game_slip(order_[0]['ID'])
        userid = slip_[0]['USERID']
        issue_code = slip_[0]['ISSUE_CODE']
        orderid = slip_[0]['ORDERID']
        print(slip_)
        BetTypeCode_list, Totbets_list, Status_list, Amount_list,Bet_list = [], [], [], [],[]
        for index in range(len(slip_)):  # 一張訂單 可能要很多個detail
            BetTypeCode_list.append(slip_[index]['BET_TYPE_CODE'])
            Totbets_list.append(slip_[index]['TOTBETS'])
            Status_list.append(slip_[index]['STATUS'])  # 一張單 的各個玩法 是否中獎  3 沒中獎
            Amount_list.append(slip_[index]['TOTAMOUNT'] / 10000)  # 該完法 投注金額 ,看驗證  投中比
            Bet_list.append(slip_[index]['BET_DETAIL'])
        # print(BetTypeCode_list)
        if len(BetTypeCode_list) == 1:  # 轉tuple 需處理, 否則帶到sql 會有問題
            BetTypeCode_tuple = "('%s')" % BetTypeCode_list[0]
        else:
            BetTypeCode_tuple = tuple(BetTypeCode_list)

        slipNum = conn.select_SingleSum(userid, BetTypeCode_tuple, lotteryid, issue_code)  # 找出該單號 該期 的總 投注總數
        bet_type_name = conn.select_SingleGame(lotteryid, BetTypeCode_tuple)  # 用 bet_type 數值 對應 找出 中文
        soloNum = conn.select_SingleSolo(lotteryid, BetTypeCode_tuple)  # 查詢該玩法後台設定的 單挑設定
        
        slipBet = conn.select_SingleBet(orderid)# 查詢 投注內容, 需去重用
        print(slipBet)
        
        bet_dict = {}# 存放 key bet_type_code value 為 去重後的投注組合
        for bet_type_code in slipBet.keys():
            new_list = return_Deduplica(BetDetailList=slipBet[bet_type_code],bet_type_code=bet_type_code)
            new_detail = return_NewCount(new_list)
            bet_dict[bet_type_code] = new_detail
        #print(bet_dict)
        
        # print(slipNum,bet_type_name,soloNum)
        bet_type_list = []  # 存放中文名稱
        slipNum_list = []  # 存放總注數
        soloNum_list = []  # 存放後台單挑設置
        soloOpen_list = []  # 存放後台單挑開關
        solo_status = []  # 存放是否進入單挑
        Deduplica_list = []# 去重後注數
        # print(bet_type_name,slipNum,soloNum)
        for index, bet_code in enumerate(BetTypeCode_list):
            try:
                bet_type_list.append(bet_type_name[bet_code])
                slipNum_list.append(slipNum[bet_code][0])
                soloNum_list.append(soloNum[bet_code][0])
                soloOpen_list.append(soloNum[bet_code][1])
                #Deduplica_list.append(bet_dict[bet_code][0])

                if Status_list[index] == 3:  # 該完法沒中獎 ,不會進單挑
                    solo_status.append("否")
                    Deduplica_list.append('無需去重')
                elif soloNum[bet_code][1] == 0:  # 後台該玩法 關閉單挑, 也不進
                    solo_status.append("否")
                    Deduplica_list.append('無需去重')
                else:# 這邊是有中獎, 後台也有開放,  差別就是和後台 比較 單條設定值
                    if bet_dict[bet_code][0] <= soloNum[bet_code][0]:  # 當期該玩法 的總注注和slipNUm 小於等於 後台 設定值 就會進單挑
                        solo_status.append("是")
                    else:
                        solo_status.append("否")
                    Deduplica_list.append(bet_dict[bet_code][0])    
            except IndexError:  # 有可能注單理的玩法,是 後台單挑值沒有的玩法
                soloNum_list.append('無')
                soloOpen_list.append('')
                solo_status.append("玩法沒開放")
                Deduplica_list.append('無需去重')

        data = {}
        data["當期玩法'原本'總投注數"] = slipNum_list
        data["當期玩法'去重後'新總投注數"] = Deduplica_list
        data["投注玩法名稱"] = bet_type_list
        data['投注玩法內容'] = Bet_list
        data["投注玩法bet_type_code"] = BetTypeCode_list
        data["該玩法注數"] = Totbets_list
        data["當期玩法後台單挑值"] = soloNum_list
        data["該單後台單挑開關"] = ["開" if i == 1 else "無" if i == "" else "關閉" for i in soloOpen_list]
        data["是否進入單挑"] = solo_status
        data["玩法是否中獎"] = ["未中獎" if i == 3 else "中獎" for i in Status_list]
        data["該玩法投注金額"] = Amount_list
        
        RedisConnection.set_key(key_name, data)
        key_name2 =  "Deduplica: %s" % (order_code)#去重的號碼次數
        RedisConnection.set_key(key_name2, bet_dict )
        
        return data
    lottery_dict = FF_Joy188.FF_().lottery_dict
    return render_template('Single.html', lottery_dict=lottery_dict)
def return_NewCount(list_):# list_ 為所有的組合list  ,該方法 產生新的去重組和
    from collections import Counter
    if bet_type in ['43']: # 組選系列 用另外種方式 判斷
        rep_dict = {}
        fir_elen = list_[0]# 先用sort 長度 最長為第一原素 ,後面 元素判斷是否友包含在裡面
        print(fir_elen)
        og_len = ["".join(tuple_) for tuple_ in [i for i in 
        itertools.combinations(fir_elen,len_play)] ]
        if len(list_) > 1: # 超過長度 2的列表 ,需再將原本list 長度 減1, 減1 因為先從 fir_elen 取出一個
            og_list = len(og_len) +(len(list_)-1)
        print('原總注數: %s'%og_list)
        exist_list = []
        for index,ele in enumerate(list_):
            if index == 0:
                pass
            else:
                if ele in fir_elen:
                    print('%s 元素已經存在'%ele)
                    exist_list.append(ele)
        print('重複號碼: %s'%exist_list)
        for i in exist_list:
            rep_dict[i] = exist_list.count(i)
        need_cal =  len(exist_list)
        new_len = og_list - need_cal
    else:
        og_list = len(list_)
        print('原總注數: %s'%og_list)
        b = dict(Counter(list_))
        rep_dict = ({key:value for key,value in b.items()if value > 1})
        if len(rep_dict) == 0:
            rep_dict[''] = 0
        rep_con = 0
        for key,value in rep_dict.items():
            rep_con += value
        need_cal = rep_con-len(rep_dict)
        if need_cal <0: 
            need_cal = 0

        print ("重複號碼:次數  %s"% rep_dict ) 
    new_len = og_list - need_cal
    print('需被減去的長度: %s'%need_cal)
    print('去重後的注數: %s'%new_len)
    return new_len,rep_dict
def return_FuziP(list_,len_list):# 計算 複試 的排列組合
    len_ = len(list_)
    if len_ == 5:
        arrange_list = [q+w+e+r+t for i in range(len_list[0])  for q in list_[0][i] 
            for i in range(len_list[1]) for w in list_[1][i] 
            for i in range(len_list[2]) for e in list_[2][i] 
            for i in range(len_list[3]) for r in list_[3][i]
            for i in range(len_list[4]) for t in list_[4][i] ]
    elif len_ == 4:
        arrange_list = [q+w+e+r for i in range(len_list[0])  for q in list_[0][i] 
            for i in range(len_list[1]) for w in list_[1][i] 
            for i in range(len_list[2]) for e in list_[2][i] 
            for i in range(len_list[3]) for r in list_[3][i] ]
    elif len_ == 3:
        arrange_list = [q+w+e for i in range(len_list[0])  for q in list_[0][i] 
            for i in range(len_list[1]) for w in list_[1][i] 
            for i in range(len_list[2]) for e in list_[2][i]  ]
    elif len_ == 2:
        arrange_list = [q+w for i in range(len_list[0])  for q in list_[0][i] 
            for i in range(len_list[1]) for w in list_[1][i]  ]
    elif len_ == 1:
        arrange_list = [q for i in range(len_list[0])  for q in list_[0][i] ]
    else:
        print('列表長度需確認')
        arrange_list = ['']
    return arrange_list
def return_SumP(str_,cal_,play_type,game_type,bet_type):# 和值的 排列組合
    new_list = []
    if play_type in ['15','14']: #15 前二 14後二
        len_play = 2
    elif play_type in ['12','13','33']:# 12 前三. 13 後三 ,33 中三
        len_play = 3
    elif play_type == '10':#五星
        len_play = 5
    elif play_type == '11':#四星
        len_play = 4
    else:
        return  '投注類型確認'
    
    #和值key號碼組合為 tuple , 需轉str  存redis才不會有問題
    if game_type == "11":# 11 組選 
        #combinations_with_replacement   有AB 就不會有 BA元素 可重复 
        a = ["".join(tuple_) for tuple_ in [i for i in 
        itertools.combinations_with_replacement(str_,len_play)] ]
        #存redis才不會有問題
    elif game_type == '10':# 10 直選  
        a = [ "".join(tuple_) for tuple_ in[i for i in 
        itertools.product(str_,repeat=len_play)] ]#所有總類, AB BA 是包含的
    else:
        return '投注玩法確認'
    for i in a:# 和值玩法 才做這段
        sum_ = 0
        for b in i:# 取出 i, ex i: 123 ,
            sum_ += int(b)
            if game_type == '11': # 組選 ,  需排除三個相同字原
                if i.count(b) ==  len_play:
                    sum_ = 0# 故意給的 不會 等於的直, 就不會append到 new_list
        #print(sum_)
        if sum_ == cal_:
            new_list.append(i)# 加起來為指定數值
    print(new_list)
    print('共 %s 注'%len(new_list))# 
    return new_list

def return_Deduplica(BetDetailList,bet_type_code):# bet_type_code 傳  ex: 33_10_33
    global bet_type # return_NewCount 方法會拿來判斷 玩法 
    new_list = []
    bet_list = bet_type_code.split('_')# 切割為list[x,x,x] , 
    play_type = bet_list[0]# 0 為玩法類型(ex:五星)...
    game_type = bet_list[1]#1 為直選/組選...
    bet_type = bet_list[2]#2 為複試/單式/和值...
    if bet_type == '33':# 33 式和值 ,但還需判斷 是 組選還是直選
        if len(BetDetailList) == 1:# 列表 指有一個元素
            BetDetailList = "".join(BetDetailList).split(',')# ['10,11'] 需轉換成 ['10','11']
        else:
            BetDetailList  = ",".join(BetDetailList).split(',')#['10,11,12','10']
        print(BetDetailList)
        for index,num in  enumerate(BetDetailList):
            print('%s 的組合: '%num)# 取出來 轉乘Int ,傳給 return_p 第三個參數,
            int_num = int(num)
            if int_num >= 9:# 9 以上直接就是 0123456789
                bet_str = '0123456789'
            else:
                bet_str = "".join([str(i) for i in range(int(BetDetailList[index])+1)])
            new_list += return_SumP(str_=bet_str, cal_= int_num,play_type=play_type,game_type=game_type,bet_type=bet_type)
    
    elif bet_type in ['43']: # 組選120系列
        global len_play
        len_play = 5
        new_list = [i.replace(',','') for i in BetDetailList]# 原本: ['5,6,7','5,6,7,8']轉乘 ['567', '5678']
        new_list.sort(key=lambda i :len(i),reverse=True)# 長度長在前,用來 後面 用第一元素來判斷 後面元素是否包含
    else :
        if bet_type == '10':# 复式
            print('複試系列')
        else:
            print('其他玩法還沒做')
        for bet_detail in BetDetailList:
            len_detail = []#存放葛長
            bet_detail = bet_detail.split(',')# 將字串分割 陣列
            bet_detail = [x for x in bet_detail if x!= '-']# 去掉 -
            print(bet_detail)
            all_len = len(bet_detail)# 該列表 的長度,用來下面算出每個元素的長度
            for len_ in range(all_len):
                len_detail.append(len(bet_detail[len_]))
            print(len_detail)# 每個元素的 分別長度
            new_list += return_FuziP(bet_detail,len_detail)
    return new_list

@app.route('/Single/bet',methods=["POST"])
def Single_OrderBEt():
    order_code = request.form.get('order_code')
    a = RedisConnection.get_key(2, "Deduplica: %s"%order_code)
    print(a)
    return a

@app.route('/login_cookie', methods=["POST"])  # 傳回登入cookie, 在api_test頁面.  取得登入cookie的方式
def login_cookie():
    import FF_Joy188
    env_url = request.form.get('env_type')
    envConfig = Config.EnvConfig(env_url)
    joint = envConfig.get_joint_venture(envConfig.get_env_id())
    user = request.form.get('username')
    conn = OracleConnection(env_id=int(envConfig.get_env_id()))
    userid = conn.select_user_id(user, joint)
    print(userid)
    if len(userid) == 0:
        return ('該環境沒有此用戶')
    password = str.encode(envConfig.get_password())
    param = FF_Joy188.FF_().param[0]
    postData = {
        "username": user,
        "password": ApiTestPC.ApiTestPC.md(_password=password, _param=param),
        "param": param
    }
    header = {
        'User-Agent': FF_Joy188.FF_().user_agent['Pc']  # 從FF_joy188.py 取
    }
    print(user, envConfig.get_post_url())
    FF_Joy188.FF_().session_post(envConfig.get_post_url(), '/login/login', postData, header)
    cookies = FF_Joy188.r.cookies.get_dict()['ANVOID']
    print(cookies)
    return cookies


@app.route('/remote_IP', methods=['POST'])  # 從瀏覽器 獲得本地 ip,方便 好記錄 查證使用
def remote_IP():
    ip = request.form
    print(ip)
    return 'ok'


@app.route('/game_prize_cal', methods=["GET"])
def game_prize_cal():
    return render_template('game_prize_calculator.html')


@app.route('/api/game_prize_cal', methods=["POST"])
def get_prize_cal_result():
    conn = OracleConnection(env_id=1)
    lottery = request.form.get('lottery')
    method = request.form.get('method')
    bonus_prize = float(request.form.get('bonus_prize'))
    print(f'lottery = {lottery}, method = {method}, bonus_prize = {bonus_prize}')
    issue_nums = conn.select_lottery_issue_number(lottery.upper())
    conn.close_conn()

    total_prize = 0  # 總獎金初始化
    total_bonus_prize = 0  # 總返點獎金初始化
    total_bet_prize = 0  # 總投注金額初始化
    result = []  # 回傳結果. [開獎號, 中獎注數, 獎金, 返點獎金, 累計獎金, 累計投注金額, 總盈利]
    for issue_num in issue_nums:
        if method == 'g1':  # 快三猜一個號
            bet_nums = [1, 2, 3, 4, 5, 6]
            prize = 4  # 平台獎金
            matched_nums = 0  # 計入單期開獎號總中獎注數. 初始化
            total_bet_prize += 12  # 每期全餐投注金額

            for bet_num in bet_nums:
                matched_times = 0  # 紀錄單投注號是否中獎
                for issue_digit in str(issue_num):
                    if bet_num == int(issue_digit):  # 若投注號對應到開獎號, 中多號不影響獎金
                        matched_times += 1
                if matched_times > 0:  # 若相同次數大於0
                    matched_nums += 1
            total_prize += math.floor(prize * matched_nums * 10000) / 10000
            total_bonus_prize += math.floor(bonus_prize * matched_nums * 10000) / 10000
            # 回傳結果. [開獎號, 中獎注數, 獎金, 返點獎金, 累計獎金, 累計投注金額, 總盈利]
            result.append([issue_num,
                           matched_nums,
                           prize * matched_nums,
                           bonus_prize * matched_nums,
                           math.floor((total_prize + total_bonus_prize) * 10000) / 10000,
                           total_bet_prize,
                           math.floor((total_bet_prize - total_prize - total_bonus_prize) * 10000) / 10000])
        if method in ('pair_1', 'pair_2', 'pair_3'):  # 對子
            prize = 2.88  # 平台獎金
            total_bet_prize += 1  # 每期全餐投注金額

            history_nums = []
            if method == 'pair_1':
                history_nums = [issue_num[0], issue_num[1], issue_num[2]]
            if method == 'pair_2':
                history_nums = [issue_num[1], issue_num[2], issue_num[3]]
            if method == 'pair_3':
                history_nums = [issue_num[2], issue_num[3], issue_num[4]]
            history_nums.sort()
            if (history_nums[0] == history_nums[1] or history_nums[1] == history_nums[2]) and history_nums[0] != \
                    history_nums[2]:
                matched_nums = 1
                total_prize += math.floor(prize * 10000) / 10000
                total_bonus_prize += bonus_prize
            else:
                matched_nums = 0
            result.append([history_nums,
                           matched_nums,
                           prize * matched_nums,
                           bonus_prize * matched_nums,
                           math.floor((total_prize + total_bonus_prize) * 10000) / 10000,
                           total_bet_prize,
                           math.floor((total_bet_prize - total_prize - total_bonus_prize) * 10000) / 10000])
            pass
        if method == 'straight':
            pass
        if method == 'dice3':
            pass
        if method == 'straight_0.5':
            pass
        if method == 'diff6':
            pass

    for data in result:
        print(data)
    return jsonify({'success': 200, "msg": "ok", "content": result})


@app.route('/qrcode_checker', methods=["GET"])
def qrcode_checker():
    return render_template('qrcode_check.html')


@app.route('/api/qrcode_checker', methods=["POST"])
def get_qrcode_result():
    def decode_base64(img_base64: str):
        try:
            img_path = Config.project_path + "/temp.png"
            from base64 import b64decode

            with open(img_path, "wb") as fh:
                fh.write(b64decode(img_base64))
                fh.close()
            print(f'base64 image saved.')
            return decode_img(img_path=img_path)
        except Exception as e:
            print(e)

    def decode_img(img_path: str):
        from pyzbar.pyzbar import decode
        from PIL import Image
        img = Image.open(img_path)
        img = img.resize((5000, 5000), Image.ANTIALIAS)
        decoded_img = decode(img)
        import os
        os.remove(img_path)
        print(f'Image decoded. data = {decoded_img}')
        if not decoded_img:
            return '解析失敗'
        print(f"Image decoded. link = {str(decoded_img[0].data, 'utf-8')}")
        return str(decoded_img[0].data, 'utf-8')

    data = []

    from utils.Config import EnvConfig
    env_config = EnvConfig(request.form.get('env_type'))
    user = request.form.get('user')
    print(
        f"request.form.get('env') = {request.form.get('env_type')}, env_config={env_config.get_domain()}, user={user}")

    """
        登入頁App下載QRCode
    """
    print('>>>>>>>>>>>>>>>>>>>> 登入頁')
    from page_objects.BasePages import LoginPage
    page = LoginPage(env_config=env_config)  # 頁面初始化
    driver = page.get_driver()
    Config.test_cases_init(19)

    page.mouse_action(element=LoginPage.elements.id_j_dl_apple)
    canvas = driver.find_element_by_xpath('//div[@id="J-download-qrcode"]/canvas')
    canvas_url = str(driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['登入頁_Apple下載', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    page.mouse_action(element=LoginPage.elements.id_j_dl_android)
    canvas = driver.find_element_by_xpath('//div[@id="J-download-qrcode"]/canvas')
    canvas_url = str(driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['登入頁_Android下載', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    page.mouse_action(LoginPage.elements.xpath_fhlm_logo)
    fhlm_qrcode = driver.find_element_by_id('qr-image')
    data.append(
        ['登入頁_鳳凰聯盟驗證', decode_base64(fhlm_qrcode.get_attribute('src').split(',')[1]), fhlm_qrcode.get_attribute('src')])
    Config.test_cases_update(1)

    """
        安全登入頁下載QRCode
    """
    print('>>>>>>>>>>>>>>>>>>>> 安全登入頁')
    page = page.jump_to(LoginPage.elements.id_safeLogin)  # 跳轉安全登入頁

    canvas = driver.find_element_by_xpath('//div[@id="J-download-qrcode"]/canvas')
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['安全登入頁_Apple下載', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    page.mouse_action(element=LoginPage.elements.id_j_dl_android)
    canvas = driver.find_element_by_xpath('//div[@id="J-download-qrcode"]/canvas')
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['安全登入頁_Android下載', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    from page_objects.BasePages import ShowSecLoginPage
    page.mouse_action(ShowSecLoginPage.elements.xpath_fhlm_logo)
    fhlm_qrcode = driver.find_element_by_id('qr-image')
    data.append(
        ['安全登入頁_鳳凰聯盟驗證', decode_base64(fhlm_qrcode.get_attribute('src').split(',')[1]),
         fhlm_qrcode.get_attribute('src')])
    Config.test_cases_update(1)

    page = page.jump_to(ShowSecLoginPage.elements.id_return_normal)  # 返回登入頁

    """
        首頁導航欄QRCode
    """
    print('>>>>>>>>>>>>>>>>>>>> 導航欄')
    page = page.login(user, env_config.get_password())
    sleep(2)
    qr_codes = driver.find_elements_by_xpath("//img[@alt='Scan me!']")
    data.extend(
        [['導航欄_體育', decode_base64(qr_codes[0].get_attribute('src').split(',')[1]), qr_codes[0].get_attribute('src')],
         ['導航欄_電競', decode_base64(qr_codes[1].get_attribute('src').split(',')[1]), qr_codes[1].get_attribute('src')],
         ['導航欄_棋牌', decode_base64(qr_codes[2].get_attribute('src').split(',')[1]), qr_codes[2].get_attribute('src')],
         ['導航欄_下載', decode_base64(qr_codes[3].get_attribute('src').split(',')[1]), qr_codes[3].get_attribute('src')],
         ['首頁_彩票', decode_base64(qr_codes[4].get_attribute('src').split(',')[1]), qr_codes[4].get_attribute('src')]])
    Config.test_cases_update(5)

    app_download_url = driver.find_element_by_xpath('//div[@class="down-app-text"]/a').get_attribute('href')
    driver.get(app_download_url)
    qr_codes = driver.find_elements_by_xpath('//li[@class="code-img"]/canvas')
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', qr_codes[0]))
    data.append(['App下載頁QRCode1', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', qr_codes[1]))
    data.append(['App下載頁QRCode2', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    """
        比特幣分分彩投注頁 / 專題頁 / 代理模板預覽
    """
    print('>>>>>>>>>>>>>>>>>>>> 比特幣')
    from page_objects.BetPages import BetPage_Btcffc
    page = BetPage_Btcffc(page)
    page.go_to()
    try:
        qr_code = driver.find_element_by_xpath('//div[@class="qrcode-img"]/img')
        data.append(
            ['比特幣分分彩_掃碼下載', decode_base64(qr_code.get_attribute('src').split(',')[1]), qr_code.get_attribute('src')])
    except:
        data.append(['比特幣分分彩_掃碼下載', 'QRCode取得失敗', '無圖片'])
    Config.test_cases_update(1)

    driver.get(page.env_config.get_post_url() + '/activity/btchome')
    canvas = driver.find_element_by_xpath("//div[@class='qrcode-content']/canvas")
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['比特幣專題頁_首頁', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    driver.get(page.env_config.get_post_url() + '/activity/introduce')
    canvas = driver.find_element_by_xpath("//div[@class='qrcode-content']/canvas")
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['比特幣專題頁_彩種介紹', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    driver.get(page.env_config.get_post_url() + '/proxy/promotepreview?target=btc')
    canvas = driver.find_element_by_xpath("//div[@class='qrcode-content']/canvas")
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['比特幣推廣模板_首頁', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    driver.get(page.env_config.get_post_url() + '/promote/btcintroduce?target=btc')
    canvas = driver.find_element_by_xpath("//div[@class='qrcode-content']/canvas")
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['比特幣推廣模板_彩種介紹', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    """推廣頁推廣面"""
    driver.get(page.env_config.get_post_url() + '/proxy/promotepreview?target=shaibao')
    canvas = driver.find_element_by_xpath("//canvas")
    canvas_url = str(
        driver.execute_script('return arguments[0].toDataURL("image/png").substring(22);', canvas))
    data.append(['安徽骰寶推廣模板_彩種介紹', decode_base64(canvas_url), 'data:image/png;base64,' + canvas_url])
    Config.test_cases_update(1)

    driver.close()
    print(f'data = {data}')
    return jsonify({'success': 200, "msg": "ok", "content": data})


@app.route('/monitor', methods=["GET"])
def monitor():
    return render_template('monitor.html')


@app.route('/api/monitorAddDomain/<domain>', methods=["POST"])
def monitor_add_domain(domain: str):
    data = {domain: True}
    print(domain)
    # if request.method == 'POST':
    #     data = request.form
    return jsonify({'success': 200, "msg": "ok", "content": data})


@app.route('/api/monitor_update/<domain>', methods=["GET"])
def monitor_update(domain: str):
    def update():
        print(f'update start. domain:{domain}')
        web, wap = 0, 0
        while web == 0 or wap == 0:
            web = curl_test(f'https://www.{domain}.com')
            wap = curl_test(f'https://m.{domain}.com')
            yield f'data: {{"web":{web}, "wap": {wap}}}\n\n'
            print(f'domain: {domain}, web={web}, wap={wap}, pass:{web == 0 and wap == 0}')
            sleep(3)

    def curl_test(host):
        response = os.system(f'{Config.curl_path} -k {host}')
        return 1 if response.numerator == 0 else 0

    return Response(update(), mimetype='text/event-stream')


@app.route('/otpauth', methods=["GET"])
def otpauth():
    return render_template('otpauth.html')


@app.route('/error')  # 錯誤處理
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
    log_msg = f"HTTPException {error_dict['code']}, Description: {error_dict['description']}, Stack trace: {error_dict['stack_trace']}"
    logger.log(msg=log_msg)
    response = jsonify(error_dict)
    response.status_code = error.code
    return response


# @app.route('/favicon.ico')
# def favicon():
#     from flask import send_from_directory
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')


'''
@celery.task()
def test_fun():
    for _ in range(10000):
        for j in range(50000):
            i = 1
    print('hello')
'''

if __name__ == "__main__":
    '''
    handler = logging.FileHandler('flask.log')
    app.logger.addHandler(handler)
    '''
    app.config['TESTING'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(host="0.0.0.0", debug=True, port=4444, threaded=True)

    # app.config.from_object(DevConfig)
