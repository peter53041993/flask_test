#!/usr/bin/env python
# coding: utf-8


from flask import Flask,render_template,request,jsonify,redirect,make_response,url_for,Response,abort
import datetime
from dateutil.relativedelta import relativedelta
import requests
import json
import image_test
import os
import AutoTest
from time import sleep
import random
import threading
import time
import test_benefit
import calendar
import celery
import test_lotteryRecord


app = Flask(__name__)# name 為模塊名稱

def iapi_login(envir):#iapi 抓取沙巴token
    session = requests.Session()
    global header
    global env
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36', 
    'Content-Type': 'application/json'
             }
    
    if envir == 'dev02':
        env = 'http://10.13.22.152:8199/'
        env_num = 0
        user = 'hsieh100'
        uuid = "2D424FA3-D7D9-4BB2-BFDA-4561F921B1D5"
        loginpasssource = "fa0c0fd599eaa397bd0daba5f47e7151"
    elif envir == '188':
        env = 'http://iphong.joy188.com/'
        env_num = 1
        user='kerr001'
        uuid = 'f009b92edc4333fd'
        loginpasssource = "3bf6add0828ee17c4603563954473c1e"
    else:
        pass
    login_data = {
    "head": {
    "sessionId": ''},
     "body": {
    "param": {
    "username": user+"|"+ uuid,
    "loginpassSource": loginpasssource,
    "appCode": 1,
    "uuid": uuid,
    "loginIp": 2130706433,
    "device": 2,
    "app_id": 9,
    "come_from": "3",
    "appname": "1"
    }
    }
    }
    r = session.post(env+'/front/login',data=json.dumps(login_data),headers=header)
    #print(r.text)
    global token
    token = r.json()['body']['result']['token']
    #print(token)

def sb_game():#iapi沙巴頁面
    session = requests.Session()

    data ={"head":{"sessionId":token},"body":{"param":{"CGISESSID":token,
    "loginIp":"10.13.20.57","types":"1,0,t","app_id":9,"come_from":"3","appname":"1"}}}
    
    r= session.post(env+'/sb/mobile',data=json.dumps(data),headers=header)
    #print(r.text)
    global sb_url
    sb_url = r.json()['body']['result']['loginUrl']
    cookies = r.cookies.get_dict()


def get_sb():# 沙巴體育
    session = requests.Session()
    iapi_login('dev02')
    sb_game()
    #抓取沙巴,token成功的方式, 先get 在post
    r =session.get(sb_url+'/',headers=header)
    cookies= r.cookies.get_dict()
    r =session.post(sb_url+'/',headers=header)
    
    
    header['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
    session = requests.Session()

    data = {
        'GameId':1,
        'DateType':'t',
        'BetTypeClass':'WhatsHot',
        #'Matchid':''
    }
    url = 'http://smartsbtest.thirdlytest.st402019.com'
    #/Odds/ShowAllOdds ,   /Odds/GetMarket
    r = session.post(url+'/Odds/ShowAllOdds',headers=header,data=data,cookies=cookies)

    global sb_list
    sb_list = []
    #print(r.json())
    game = r.json()['Data']['NewMatch']
    game_map = r.json()['Data']['TeamN']
    for dict_ in game:
        team1 = game_map[str(dict_['TeamId1'])]
        #team1 = game['TeamId1']
        team2 = game_map[str(dict_['TeamId2'])]
        #print(team1,team2,score1,score2)
        game_dict = {}
        for k in dict_:#字典的keys 找出來
            if k in ['MatchId','MarketId','T1V','T2V','TeamId1','TeamId2','Etm']:
                game_dict[k] = dict_[k]
            game_dict['team1name'] = team1
            game_dict['team2name'] = team2
            date_day = dict_['Etm'].split('T')#將str 分割成 日棋 和時間 
            d= datetime.datetime.strptime(date_day[0]+' '+date_day[1], '%Y-%m-%d %H:%M:%S')#date_day 0為年月日, 1為時間
            #print(d)
            game_dict['Etm'] =(d+relativedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')#加12小時
        sb_list.append(game_dict)   
    sb_list.sort(key=lambda k: (k.get('Etm', 0)))# 列表裡包字典, 時間排序
    
    for i in sb_list:#list取出各個字點
        #print(i['MatchId'])#抓出mathch id ,去對應 賠率
        data['Matchid'] = i['MatchId']
        r = session.post(url+'/Odds/GetMarket',headers=header,data=data,cookies=cookies)
        #print(r.text)
        game_Odd = (r.json()['Data']['NewOdds'])
        #print(game_Odd)
        for odd in game_Odd:
            if odd['BetTypeId']== 5:#抓 特定玩法
                i['price1'] = odd['Selections']['1']['Price']#多增加賠率欄位
                i['price2'] = odd['Selections']['2']['Price']
                #game_list.append(i)
            else:
                pass
def date_time():#給查詢 獎期to_date時間用, 今天時間
    global today_time

    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    format_month = '{:02d}'.format(month)
    format_day = '{:02d}'.format(day)
    today_time = '%s-%s-%s'%(year,format_month,format_day)
def test_sport(type_keys='全部'):#企鵝網
    userAgent =  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"     

    header = {
        'User-Agent':userAgent       
    }
    type_ = {'全部':0,"英超":1}
    date_time()
    session = requests.Session()
    
    r = session.get('http://live.qq.com'+
    '/api/calendar/game_list/%s/%s/%s'%(type_[type_keys],today_time,today_time),
    headers=header)
    #print(r.json())
    #print(r.json())
    global sport_list
    sport_list = []#存放請求
    len_game = len(r.json()[today_time])#當天遊戲列表長度
    #print(r.json()[today_time])

    for game in range(len_game):#取出長度
        game_dict = r.json()[today_time][game]
        #print(game_dict)
        play_status = game_dict['play_status']
        #if play_status != '1':#1: 正在 ,2:比完, 3: 還未開打
        '''
        team1_name =game_dict['team1_name']
        team2_name = game_dict['team2_name']
        team1_score = game_dict['team1_score']
        team2_score = game_dict['team2_score']
        '''
        game_new = {}#把需要抓取的欄位 存放近來,  在把所有當天比賽放到game_list
        for i in game_dict.keys():
            if i in ['id','team1_id','team2_id','team1_name',
            'team2_name','team1_score','team2_score','play_status','team1_icon',
            'team2_icon','category_name']:
                game_new[i] = game_dict[i]# key = value
            else:
                pass
        #print(game_new)
        sport_list.append(game_new)          
        #else:
            #pass
    #print(game_new)
    #print(sport_list)
#test_sport('全部')


def return_(status):
    global response_status
    response_status =status



@app.route('/form',methods=['POST','GET'])
def test_form():#輸入/form 頁面, 呼叫render_template的html
    if request.method == "POST":
        username = request.form['username']# 在頁面上填的資料
        email = request.form['email']
        hobbies = request.form['hobbies']
        return redirect(url_for('showbio',#提交
                                username = username,#前面為參數,後面為資料
                                email =email,
                                hobbies = hobbies))#redirect 重新定向
    return render_template('bio_form.html')


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/showbio',methods=["GET"])
def showbio():#提交submit後的頁面顯示
    username = request.args.get('username')
    email = request.args.get('email')    
    hobbies = request.args.get('hobbies')    
    return render_template("show_bio.html",
                           username=username, #前面username 傳回html的 ,後面username 是用戶填寫                                            
                           email=email,                         
                           hobbies=hobbies)

@app.route('/sport',methods=["GET"])
def sport_():#體育比分
    test_sport()
    #return jsonify(game_list)
    return render_template('sport.html',sport_list=sport_list,today_time=today_time)

@app.route('/sportApi',methods=['GET'])
def sport_api():#體育api
    test_sport()
    return jsonify(sport_list)
@app.route('/sb',methods=['GET'])
def sb_():
    get_sb()
    date_time()
    return render_template('sb.html',sb_list=sb_list,today_time=today_time)

@app.route('/sbApi',methods=['GET'])
def sb_api():#體育api
    get_sb()
    return jsonify(sb_list)

@app.route('/image',methods=['GET'])
def image_():#調整圖片大小
    img_path = (os.path.join(os.path.expanduser("~"), 'Desktop'))
    return render_template('image.html',img_path=img_path)

@app.route('/imageAdj',methods=["POST"])
def imageAdj():
    testInfo = {}#存放 圖名,長,寬 的資料
    image_name = request.form.get('image_name')
    height = request.form.get('height')
    width = request.form.get('width')
    testInfo['image_name'] = image_name
    testInfo['height'] = height
    testInfo['width'] = width
    image_test.image_(image_name,height,width)#將圖名, 長,寬 回傳給 image_test檔案下 image_的 func使用
    msg = image_test.msg#宣告image_test方法裡 global msg變數
    testInfo['msg'] = msg
    
    return json.dumps(testInfo['msg'])

@app.route('/autoTest',methods=["GET","POST"])#自動化測試 頁面
def autoTest():
    global response_status
    if request.method == "POST":
        
        #response_status ='start_progress'
        #return redirect("/progress")
        testcase = []
        username = request.form.get('username')
        test_case = request.form.getlist('test_Suite')#回傳 測試案例data內容
        env = request.form.get('env_type')#環境選擇
        red = request.form.get('red_type')#紅包選擇
        print(env,red)
        if env in ['dev02','fh82dev02','88hlqpdev02','teny2020dev02']:# 多判斷合營,歡樂棋牌
            env_ = 0# env_ 查詢 頁面上  該環境 是否真的有  此用戶名 ,哪來查DB環境用
        elif env in ['joy188','joy188.teny2020','joy188.195353','joy188.88hlqp']:
            env_ = 1
        
        AutoTest.Joy188Test.select_userid(AutoTest.Joy188Test.get_conn(env_),username)#查詢用戶 userid,合營
        userid = AutoTest.userid
        #joint_venture = AutoTest.joint_venture #joint_venture 為合營,  0 為一般, 1為合營
        print(userid)#joint_venture)
        #print(len(userid))
        print(username)

        for test in test_case:
            testcase.append(test)
        print(testcase)
        if len(userid) > 0: # userid 值為空,　代表該ＤＢ　環境　沒有此用戶名　，　就不用做接下來的事
            AutoTest.suite_test(testcase,username,env,red)#呼叫autoTest檔 的測試方法, 將頁面參數回傳到autoTest.py
            return_('done')
            #print(response_status)
            return redirect('report')
        else:
            
            return_('done')
            #print(response_status)
            return '此環境沒有該用戶'

        #return redirect("/report")
    return render_template('autoTest.html')


@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')



@app.route('/progress')
def progress():#執行測試案例時, 目前 還位判斷 request街口狀態,  需 日後補上
    def generate():
        x = 0
        #global response_status
        #print(response_status)
        while x <= 100 :
            #print(response_status)
            yield "data:" + str(x) + "\n\n"#data內容, 換行
            x = x + 1
            sleep(0.5)
        #yield "data:"+ str(100)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/benefit',methods=["GET","POST"])#日工資頁面  按鈕提交後, 在導往  benefit_日工資/分紅頁面
def benefit():
    if request.method == "POST":
        testInfo = {}#存放資廖
        cookies_dict = {}#存放cookie
        global result# 日工資 data資料

        cookies_ = request.cookies#目前的改瀏覽器上的cookie 
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

        print(testInfo)#方便看資料用
        
        if env not in cookies_.keys():#請求裡面 沒有 這些環境cookie,就再登入各環境後台 
            test_benefit.admin_Login(env)#登入生產環境 後台
            admin_cookie = test_benefit.admin_cookie#呼叫  此function ,
            
            cookies_dict[env] = admin_cookie['admin_cookie']
            cookies= admin_cookie['admin_cookie']
            #print(cookies_dict)
        else:
            cookies = cookies_[env]#cookies_已經有了, 就直接使用

        if benefit_type == 'day':
            test_benefit.game_report_day(user=username,month=int(month),day=int(day),cookies=cookies,env=env)
            result = test_benefit.result_data
            print(result)
            if result['msg'] == '你輸入的日期或姓名不符,請再確認': # 有cookie, 但cookie失效, 需再重新做
                test_benefit.admin_Login(env)
                admin_cookie = test_benefit.admin_cookie#呼叫  此function ,
                cookies_dict[env] = admin_cookie['admin_cookie']
                cookies= admin_cookie['admin_cookie']
                test_benefit.game_report_day(user=username,month=int(month),day=int(day),cookies=cookies,env=env)
                result = test_benefit.result_data
                res = redirect('benefit_day')
            else:
                res = redirect('benefit_day')
            if cookies_dict == {}: #會為空 代表,瀏覽器 有存在的cookie. 不用再額外在set
                pass
            else:
                res.set_cookie(env,cookies_dict[env])
            return res
        elif benefit_type == 'month':#需將 頁面獲得的 0或1  轉帳 日期 上半月: 15 ,下半月: 當月最後一天
            #print(type(day))
            print(type(day),day)
            if day == '0':
                day = 15
            elif day == '1':
                now = datetime.datetime.now()
                day = calendar.monthrange(now.year,int(month))[1]# 獲取當月 最後一天
            test_benefit.game_report_month(user=username,month=int(month),day=int(day),cookies=cookies,env=env)
            result = test_benefit.result_data
            res = redirect('benefit_month')
            if cookies_dict == {}:
                pass
            else:
                res.set_cookie(env,cookies_dict[env])
            return res
        else:
            print('福利中心 類型錯誤')
    return render_template('benefit.html')#這邊是 單存get,表單填寫頁面


@app.route('/benefit_day',methods=["GET"])
def benefit_day():
    return render_template('benefit_day.html',result=result)

@app.route('/benefit_month',methods=["GET"])
def benefit_month():
    return render_template('benefit_month.html',result=result)


@app.route('/report_APP',methods=["GET","POST"])#APP戰報
def report_APP():
    global result
    if request.method == 'POST':
        envtype = request.form.get('env_type')
        print(envtype)
        if envtype == 'dev':
            env = 0
        else:# 188
            env = 1
        test_lotteryRecord.all_lottery(env)
        result = test_lotteryRecord.result
        
        return redirect('report_AppData')

    return render_template('report_APP.html')

@app.route('/report_AppData',methods=["GET"])#APP戰報資料顯示
def report_AppData():
    return render_template('report_AppData.html',result=result)

@app.route('/error')#錯誤處理
def error():
    abort(404)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404
'''
@celery.task()
def test_fun():
    for _ in range(10000):
        for j in range(50000):
            i = 1
    print('hello')
'''


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True,port=4444,threaded=True)
    #app.config.from_object(DevConfig)

