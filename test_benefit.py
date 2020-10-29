#!/usr/bin/env python
# coding: utf-8
from interval import Interval
import requests
import cx_Oracle
import time
import datetime
import json
import calendar
import random


def admin_Login(url):
    global admin_cookie
    global admin_url
    global envs
    global userAgent
    global session
    admin_cookie = {} 
    session = requests.Session()
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"     

    while True:
        header = {
            'User-Agent': userAgent
        }

        admin_url = 'http://admin.%s.com'%url
        username = 'cancus'
        bindpwd = 123456
        if url in ['dev02','dev03']:
            password = '123qwe'
            envs = 0
        elif url == 'joy188':
            password = 'amberrd'
            envs = 1
        else:#生產  phl58'
            admin_url = 'http://admin.phl58.com'
            username = 'tprd'
            password = 'amberrd'
            r = session.get('http://admin.dev03.com'+'/admin/login/bindpwd',headers=header)
            num = random.randint(2,7)
            bindpwd = (r.text.split('<br>')[num])
            envs = 2

        data_ = {
            'username':username,
            'password':password,
            'bindpwd':bindpwd 
        }

    # 'username=cancus&password=123qwe&bindpwd=123456'

        r = session.post(admin_url+'/admin/login/login',data = data_, headers = header)
        cookies = r.cookies.get_dict()#獲得登入的cookies 字典

        admin_cookie['admin_cookie'] =  cookies['ANVOAID']
        t = time.strftime('%Y%m%d %H:%M:%S')

        if 'isSuccess' in r.text:
            print('登錄環境%s,'%url+'現在時間:'+t)
            print(r.text)
            break

        else:
            pass
            continue

def get_conn(env):#連結數據庫 env 0: dev02 , 1:188 ,2: 生產
    if env == 2:
        username = 'rdquery'
        service_name = 'gamenxsXDB'
    else:
        username = 'firefog'
        service_name = ''
    oracle_ = {'password':['LF64qad32gfecxPOJ603','JKoijh785gfrqaX67854','eMxX8B#wktFZ8V'],
    'ip':['10.13.22.161','10.6.1.41','10.6.1.31'],
    'sid':['firefog','game','']}
    conn = cx_Oracle.connect(username,oracle_['password'][env],oracle_['ip'][env]+':1521/'+
    oracle_['sid'][env]+service_name)
    return conn
def select_registerDate(conn,date,account_):
    with conn.cursor() as cursor:
        account_ = account_
        
        sql = "select  trunc(to_date('%s','YYYY-MM-DD')+1) - trunc(register_date) as bron_day from  user_customer where account = '%s'"%(date,account_)# date參數 為  指定選擇日棋
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        global bron_day
        bron_day = []

        for i in rows:
            bron_day.append(i[0])
    conn.close()
def select_red(conn,date_start,date_end,account):
    with conn.cursor() as cursor:
        sql = "select \
        UC.ACCOUNT,\
        REPORT.btc_xyft_amount as a,\
        REPORT.BTC_XYFT_RED_DISCOUNT as b,\
        REPORT.SUPER_AMOUNT as c,\
        REPORT.SUPER_RED_DISCOUNT as d,\
        REPORT.DASHIAW_AMOUNT as e,\
        REPORT.DASHIAW_RED_DISCOUNT as f\
        FROM (select\
        SUM(NVL(A.total_amount,0)) AS V1,\
        SUM(NVL(A.total_win,0)) AS V2,\
        SUM(NVL(A.total_ret,0)) AS V3,\
        SUM(NVL(A.total_red_discount,0)) AS V4,\
        B.U_ID V7,\
        SUM(nvl(CASE WHEN a.lotteryid IN(99115,99203,99205) THEN ceil(a.total_amount) ELSE 0 END,0) ) AS btc_xyft_amount,\
        SUM(nvl(CASE WHEN a.lotteryid IN(99115,99203,99205) THEN ceil(a.total_red_discount) ELSE 0 END,0) ) AS btc_xyft_red_discount,\
        SUM(nvl(CASE WHEN substr(a.bet_type_code,0,3) in ('47_','48_','50_','51_','52_') THEN ceil(a.total_amount) ELSE 0 END,0) )\
        AS super_amount,\
        SUM(nvl(CASE WHEN substr(a.bet_type_code,0,3) in ('47_','48_','50_','51_','52_') THEN ceil(a.TOTAL_RED_DISCOUNT)  ELSE 0 END,0) ) AS super_red_discount,\
        SUM(nvl(CASE WHEN bet_type_code in ('43_37_79', '43_37_80') THEN ceil(a.total_amount) ELSE 0END,0) ) AS dashiaw_amount,\
        SUM(nvl(CASE WHEN bet_type_code in ('43_37_79', '43_37_80') THEN ceil(a.TOTAL_RED_DISCOUNT) ELSE 0 END,0) ) AS dashiaw_red_discount\
        from GAME_ORDER_REPORT A \
        join USER_CUSTOMER_FOR_REPORT_TEMP B on A.USER_ID = B.O_ID\
        where A.CREATE_TIME >= TO_DATE('%s000000','yyyy-MM-ddHH24miss') and A.CREATE_TIME <= TO_DATE('%s235959','yyyy-MM-ddHH24miss')\
        group by B.U_ID) REPORT JOIN USER_CUSTOMER UC ON REPORT.V7 = UC.ID\
        WHERE (REPORT.V1 > 0 OR REPORT.V2 > 0 OR REPORT.V3 > 0) and uc.account ='%s'" %(date_start,date_end,account)
        cursor.execute(sql)
        print(sql)
        rows = cursor.fetchall()
        global red_dict
        red_dict = {}
        for a,b in enumerate(rows):
            #print(a,b)
            red_dict[a] = b
    conn.close()

def game_report_day(user,month,day,cookies,env):#盈虧報表數據,   日工資 派發
    global result_data # 回傳 json 資料用
    result_data = {}
    userAgent= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"     
    header={
    'User-Agent': userAgent,
    'Cookie': 'ANVOAID='+ cookies,
    #+';ActivitySSID=o4dd8gr758r68q1jqr6vc5bma5'  活動系統
    #'Content-Type': 'application/json; charset=UTF-8', 
    'Accept':  'application/json, text/javascript, */*; q=0.01',
        }
    session = requests.session()
    
    try:
        now = datetime.datetime.now()#年找出今年.  月和日做參數化.因為可能會找先前日棋
        year = now.year
        #month = now.month
        format_month = '{:02d}'.format(month)  #需對 月和日 做 格式化, 因為參數 無法帶 01  這種類型
        format_day = '{:02d}'.format(day) 
        Time = '%s-%s-%s'%(year,format_month,format_day)
        #Time2 = '%s%s%s'%(year,format_month,format_day)#給紅包使用的時間
        print(Time)
        
        

        # 4.0 后台盈虧data
        data_ = {
            'userGroup':'','userPlayMethod':'',
            'userGameGroup':'','userFreeze':'','userUnit':'','username':user,
            'SearchTime1':Time,'SearchTime2':Time,'page':'0',#日工資 起始和尾的時間 通常是一致
            'perPageNum':'30'
        }

        data_fhll = {
            "ffAccount":user,"lotteryId":"","userLvl":"","isFreeze":"",
            "startDate":Time,"endDate":Time,"userId":'null',"pageNo":1}

        if env == 'dev02':
            envs = 0
            admin_url = 'http://admin.dev02.com'
        elif env == 'joy188':
            envs = 1
            admin_url = 'http://admin.joy188.com'
        elif env == 'phl58':
            envs = 2
            admin_url = 'http://admin.phl58.com'

        print('用戶名: %s'%user)
        select_registerDate(get_conn(envs),Time,user)#查詢註冊天數 
        print('註冊天數: %s'%bron_day[0])
        print('查詢日期: %s'%Time)

        result_data['user']=user
        result_data['bron_day'] = bron_day[0]
        result_data['time']=Time

        select_red(get_conn(envs),Time,Time,user)#抓取紅包數據
        print(red_dict)# 
        
    
        url = '/admin/Reporting/index?parma=tada'#4.0 盈虧url
        fhll_url = '/fhllAdmin/query/profitListSearch'#真人贏虧url 

        r = session.post(admin_url+url,data=data_,headers=header)#4.0 
        if r.text == '{"text":[],"count":[]}': #4.0 報表 需額外判斷, response關係
            All_bet = 0
            #Bet = 0
            sbdxdsBet = 0
            effectiveBet = 0
            win = 0
            ret = 0
            activityGifts = 0
            totalRedDiscount = 0
            pass
        else: 
            All_bet = float(r.json()['text'][0]['bet'].replace(',',''))#總銷量 減掉 紅包
            effectiveBet = float(r.json()['text'][0]['effectiveBet'].replace(',',''))#盈虧的有效消量,不包含大小單雙 ,再去減掉紅包
            sbdxdsBet  = float(r.json()['text'][0]['sbdxdsBet'].replace(',',''))#骰寶大小單雙,需抓出來
            #effectiveBet = round(Bet+0.2*(sbdxdsBet),10)#4.0實際有效消量 ,需加回 20% 的大小單雙
            win = float(r.json()['text'][0]['win'].replace(',',''))#中獎金額
            ret = float(r.json()['text'][0]['ret'].replace(',',''))#反點
            activityGifts = float(r.json()['text'][0]['activityGifts'].replace(',',''))#活動禮金
            try:
                totalRedDiscount = float(r.json()['text'][0]['totalRedDiscount'].replace(',',''))#紅包禮金
            except KeyError :
                totalRedDiscount = 0
                print('紅包功能暫未開放')
        All_bet = round(All_bet - totalRedDiscount,4)#從總待盈虧抓出來的總銷量, 需再扣掉 紅包
        try :
            red_xybtc = round(red_dict[0][2]*0.0001,4)#幸運/比特幣 紅包值
            red_2000 = round(red_dict[0][4]*0.0001,4)#超級2000 紅包
            red_sb = round(red_dict[0][6]*0.0001,4)#骰寶大小單雙 紅包
            red_remain = totalRedDiscount - (red_xybtc+red_2000+red_sb)#剩下的紅包值,  全部紅包 - (幸運/比特幣+2000+骰寶大小單雙)
        except KeyError:
            red_xybtc = 0
            red_2000 = 0
            red_sb = 0
            red_remain = totalRedDiscount - (red_xybtc+red_2000+red_sb)


        red_total = (red_xybtc*0.2)+(red_2000*0.8) + red_remain # 這裡將 分別的紅包 + 剩下的紅包  ,再拿去給有效銷量減掉
        print(red_total)
        effectiveBet_ = round(effectiveBet - red_total +  0.2*(sbdxdsBet-red_sb),4)#最後需加上  骰寶實際的投注 (需減掉 紅包 骰寶)

        header['Content-Type'] = 'application/json; charset=UTF-8'# 為了真人 加header
        #fhll 需加 content_type這段內容, 但4.0的盈虧不需要 (所以先做4.0,再做真人)

        fhll_r = session.post(admin_url+fhll_url,data=json.dumps(data_fhll),headers=header)
        #print(fhll_r.json())

        trueBet = round(fhll_r.json()['profitStruc'][0]['bet']*0.0001,10)#真人實際投注.抓出來除1萬
        fh_ret =  round(fhll_r.json()['profitStruc'][0]['ret']*0.0001,10)#真人反點
        fh_win = round(fhll_r.json()['profitStruc'][0]['win']*0.0001,10)#真人中獎
        fh_activityGifts = 0#真人活動禮金   都是0

        #日工資 有效消量: 需計算 20% 大小單雙   ,然後再加上 真人實際投注額 
        effectiveBet_day = effectiveBet_ + trueBet
        #日工資總銷量 : 4.0總銷量 + 真人銷量 
        Allbet_day = All_bet + trueBet 

        #print(r.json())

        #日工資  盈虧報表欄位
        user_award = round(fh_win+fh_ret+fh_activityGifts+win+ret+activityGifts,10)#4.0和真人  獲得獎獎金 

        # 輸額: 有效投注-(总返点+总中奖金+活动礼金)
        winLost_day = round(Allbet_day-(user_award),5)#日工資輸額: 總帶夠費 - 總獎金
        #winLost_month = effectiveBet_month-(ret+win+activityGifts)#分紅 輸額: 不是派發條件,是獎金依據
        print('4.0總投注額: %f /有效投注額: %f ,真人總/有效投注額: %f'%(All_bet,effectiveBet,trueBet))
        print('4.0: 中獎金額: %f, 反點: %f, 活動禮金: %f \n真人: 中獎金額: %f, 反點: %f, 活動禮金: %f' 
        %(win,ret,activityGifts,fh_win,fh_ret,fh_activityGifts))

        result_data['All_bet']=All_bet
        result_data['effectiveBet']=effectiveBet
        result_data['trueBet']=trueBet
        result_data['win']=win
        result_data['ret']=ret
        result_data['activityGifts']=activityGifts
        result_data['fh_win']=fh_win
        result_data['fh_ret']=fh_ret
        result_data['fh_activityGifts']=fh_activityGifts
        result_data['totalRedDiscount']=totalRedDiscount
        result_data['red_xybtc'] = red_xybtc*0.2
        result_data['red_2000'] = red_2000*0.8
        result_data['red_sb'] = red_sb*0.2
        result_data['red_remain'] = red_remain


        print('總紅包: %s, 幸運/比特幣紅包: %s, 超級2000紅包: %s, 骰寶大小單雙紅包: %s, 剩餘紅包: %s'
        %(totalRedDiscount,red_xybtc,red_2000,red_sb,red_remain))

        print('日工資總銷量: %f/有效消量: %f,總中獎金: %f, 輸額: %f'
        %(Allbet_day,effectiveBet_day,user_award,winLost_day))

        result_data['Allbet_day']=Allbet_day
        result_data['effectiveBet_day']=effectiveBet_day
        result_data['user_award']=user_award
        result_data['winLost_day']=winLost_day

        if winLost_day > 0:
            print('投注金額大於中獎金額.')
        else:
            print('中獎金額大於投注金額.')
        print('---------------------')

        #日工資: award   = effectiveBet_day * 工資比例
        if winLost_day < 0:# 輸額小於 0 ,代表 贏的比投的多
            print('你的輸額為負數,不符合活動資格')
            msg = '你的輸額為負數,不符合活動資格'
            award = 0
            per =0
        elif winLost_day == 0:
            msg = '你的輸額為0,不符合活動資格'
            print('你的輸額為0,不符合活動資格')
            award = 0
            per = 0
        #輸額大於0 ,代表  輸得比贏多, 為派發條件   ,在用 註冊日期來判段  派獎區間
        elif winLost_day in Interval(0,10000):
            print('你的日工資輸額在0-1W區間')
            msg = '你的日工資輸額在0-1W區間'
            if bron_day[0] > 180:
                award = 0
                per = 0
                print('註冊天數大於180,不符合派獎資格')
                msg = msg + '註冊天數大於180,不符合派獎資格'
            elif bron_day[0] in Interval(91,180):
                print('註冊天數在91-180區間')
                msg = msg + '註冊天數在91-180區間'
                if effectiveBet_day > 10000:#有效銷量 判斷
                    award = round(3*effectiveBet_day/1000,10)# 0.3% = 乘3除1000
                    print('銷量大於10000以上,工資比利為0.3%')
                    msg = msg + '銷量大於10000以上'
                    per = 0.3
                else:
                    award = 0
                    ('銷量小於10000,不符合派獎資格')
                    msg = msg + '銷量小於10000,不符合派獎資格'
                    per = 0
            elif bron_day[0] <91:
                award = round(3*effectiveBet_day/1000,10)
                msg = msg + '註冊天數在1-90區間'
                print('註冊天數在1-90區間,工資比利為0.3%')
                per = 0.3
        elif winLost_day in Interval(10001,100000):
            award = round(3*effectiveBet_day/1000,10)
            msg = '你的日工資輸額在10001-10W區間\n銷量無要求'
            print('你的日工資輸額在10001-10W區間\n銷量無要求,工資比利為0.3%')
            
            per = 0.3
        elif winLost_day in Interval(100001,500000):
            award = round(5*effectiveBet_day/1000,10)
            msg = '你的日工資輸額在100001-50W區間\n銷量無要求'
            print('你的日工資輸額在100001-50W區間\n銷量無要求,工資比利為0.5%')
            per = 0.5
        elif winLost_day in Interval(500001,600000):
            print('你的日工資輸額在500001-60W區間')
            msg = '你的日工資輸額在500001-60W區間'
            if effectiveBet_day < 2000000:
                award = round(8*effectiveBet_day/1000,10)
                print('銷量小於2百萬,工資比利為0.8%')
                msg = msg + '銷量小於2百萬'
                per = 0.8
            else:
                award = round(10*effectiveBet_day/1000,10)
                msg = msg + '銷量大於2百萬'
                print('銷量大於2百萬,工資比利為1%')
                per = 1
        elif winLost_day in Interval(600001,800000):
            print('你的輸額在600001-80W區間')
            msg = '你的輸額在600001-80W區間'
            if effectiveBet_day < 2000000:
                award = round(8*effectiveBet_day/1000,10)
                msg = msg + '銷量小於2百萬'
                print('銷量小於2百萬,工資比利為0.8%')
                per = 0.8
            elif effectiveBet_day in Interval(2000001,3000000):
                award = round(10*effectiveBet_day/1000,10)
                msg = msg + '銷量200W以上-300W'
                print('銷量200W以上-300W,工資比利為1%')
                per = 1
            else:
                award = round(12*effectiveBet_day/1000,10)
                print('銷量大於3百萬,工資比利為1.2%')
                msg = msg + '銷量大於3百萬'
                per = 1.2
        elif winLost_day in Interval(800001,1000000):
            print('你的輸額在800001-100W區間')
            msg = '你的輸額在800001-100W區間'
            if effectiveBet_day < 2000000:
                award = round(8*effectiveBet_day/1000,10)
                msg = msg + '銷量小於2百萬'
                print('銷量小於2百萬,工資比利為0.8%')
                per = 0.8
            elif effectiveBet_day in Interval(2000001,3000000):
                award = round(10*effectiveBet_day/1000,10)
                msg =msg + '銷量200W以上-300W'
                print('銷量200W以上-300W,工資比利為1%')
                per = 1
            elif effectiveBet_day in Interval(3000001,5000000):
                award = round(12*effectiveBet_day/1000,10)
                msg = msg + '銷量300W以上-500W'
                print('銷量300W以上-500W,工資比利為1.2%')
                per = 1.2
            else:
                award = round(15*effectiveBet_day/1000,10)
                msg =msg + '銷量大於5百萬'
                print('銷量大於5百萬,工資比利為1.5%')
                per = 1.5
        else:#輸額大於 100萬的
            print('你的輸額大於100W')
            msg = '你的輸額大於100W'
            if effectiveBet_day < 2000000:
                award = round(8*effectiveBet_day/1000,10)
                msg = msg + '銷量小於2百萬'
                print('銷量小於2百萬,工資比利為0.8%')
                per = 0.8
            elif effectiveBet_day in Interval(2000001,3000000):
                award = round(10*effectiveBet_day/1000,10)
                msg = msg + '銷量200W以上-300W'
                print('銷量200W以上-300W,工資比利為1%')
                per = 1
            elif effectiveBet_day in Interval(3000001,5000000):
                award = round(12*effectiveBet_day/1000,10)
                msg = msg + '銷量300W以上-500W'
                print('銷量300W以上-500W,工資比利為1.2%')
                per = 1.2
            elif effectiveBet_day in Interval(5000001,10000000):
                award = round(15*effectiveBet_day/1000,10)
                msg = msg + '銷量500W以上-1000W'
                print('銷量500W以上-1000W,工資比利為1.5%')
                per = 1.5
            else:
                award = round(18*effectiveBet_day/1000,10)
                msg = msg + '銷量大於1千萬'
                print('銷量大於1千萬,工資比利為1.8%')
                per = 1.8
        print('日工資派發: %s'%award)
        result_data['award']=award
        result_data['per'] = per
        result_data['msg'] = msg
    except requests.exceptions.ConnectionError:
        print('連線有問題,請稍等')

    except  ValueError as e:
        print(e)
        msg = '你輸入的日期或姓名不符,請再確認'
        result_data['msg'] = msg
        print('你輸入的日期或姓名不符,請再確認')
        #game_report_day(user=username,month=int(month),day=int(day),cookies=cookies,env=env)
        
    except IndexError as e:
        print(e)
        print('用戶名無此名單')
        msg = '用戶名無此名單'
        result_data['msg'] = msg   
    
def game_report_month(user,month,day,cookies,env): #分紅
    global result_data # 回傳 json 資料用
    result_data = {}
    userAgent ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"     
    header={
    'User-Agent': userAgent,
    'Cookie': 'ANVOAID='+cookies,
    #+';ActivitySSID=o4dd8gr758r68q1jqr6vc5bma5'  活動系統
    #'Content-Type': 'application/json; charset=UTF-8', 
    'Accept':  'application/json, text/javascript, */*; q=0.01',
        }
    #查詢現在時間.  用來判斷  找尋的是 上半月 還是下半月的資料
    
    try:
        now = datetime.datetime.now()
        now_year = now.year
        now_month = '{:02d}'.format(month)#現在這個月  ,需要轉為兩位數  給 盈虧報表用 
        #now_day = now.day# 先不轉類別 要判斷  時間點用
    
        if day > 15: #代表 為下半個月 ,大於 15 不用轉類型, 一定會為 兩位數

            startTime = ('%s-%s-16'%(now_year,now_month))#盈虧報表 起使日期 從16號開始
            stopTime = ('%s-%s-%s'%(now_year,now_month,day))# 尾巴日期 用現在當下日期為依據
            day_range = day-15 #用來 算出 日均銷量的分母, -15用意  因為16號算第一天
            month_type = '下半個月'
        else:#小於等於15 上半個月
            now_day = '{:02d}'.format(day)
            startTime = ('%s-%s-01'%(now_year,now_month))#盈虧報表 起使日期 從1號開始
            stopTime = ('%s-%s-%s'%(now_year,now_month,now_day))# 尾巴日期 用現在當下日期為依據
            day_range = 15 # 上半個月 日均天數 一定為15 
            month_type = '上半個月'
        
        data_ = {
            'userGroup':'','userPlayMethod':'',
            'userGameGroup':'','userFreeze':'','userUnit':'','username':user,
            'SearchTime1':startTime,'SearchTime2':stopTime,'page':'0',
            'perPageNum':'30'
        }
        data_fhll = {
        "ffAccount":user,"lotteryId":"","userLvl":"","isFreeze":"",
        "startDate":startTime,"endDate":stopTime,"userId":'null',"pageNo":1}

        if env == 'dev02':
            envs = 0
            admin_url = 'http://admin.dev02.com'
        elif env =='joy188':
            envs = 1
            admin_url = 'http://admin.joy188.com'
        elif env == 'phl58':
            envs = 2
            admin_url = 'http://admin.phl58.com'

        select_registerDate(get_conn(envs),startTime,user)#查詢上下半月第一天的註冊天數
        start_bronday = bron_day[0]
        select_registerDate(get_conn(envs),stopTime,user)#查詢上下半月最後一天的註冊天數
        stop_bronday = bron_day[0]


        print('用戶名: %s'%user) 
        #print('註冊天數: %s'%bron_day[0])
        print('查詢日期: %s到%s, 屬於: %s, 註冊天數範圍: %s~%s'
        %(startTime,stopTime,month_type,start_bronday,stop_bronday))
        result_data['user'] = user
        result_data['startTime'] = startTime
        result_data['stopTime'] = stopTime
        result_data['month_type'] = month_type
        result_data['start_bronday'] = start_bronday
        result_data['stop_bronday'] = stop_bronday

        select_red(get_conn(envs),startTime,stopTime,user)#抓取紅包數據
        print(red_dict)#分紅紅包 只需要抓 超級2000 , 因為  分紅有效銷量  只差在總待盈虧的 總投注 -超級2000 額外 8折

        # 判斷如果在上半月或下半月中, 註冊天數有含到 90,91 或者  180,181的
        if 90 in Interval(start_bronday,stop_bronday):
            min_bronday = 90
            print('取小的值: 90天')
        elif 180 in Interval(start_bronday,stop_bronday):
            min_bronday = 180
            print('取小的值: 180天')
        else:
            min_bronday = stop_bronday# 其它沒有含 90或180的,就已最後一天 來看他的註冊日期
            print('註冊天數為: %s'%min_bronday)
        result_data['min_bronday'] = min_bronday

        print('日均銷量天數: %s'%day_range)
        result_data['day_range'] = day_range
        print('查詢中,請稍等')

        session = requests.session()

        url = '/admin/Reporting/index?parma=tada'
        fhll_url = '/fhllAdmin/query/profitListSearch'#真人贏虧url 
        r = session.post(admin_url+url,data=data_,headers=header)
        #print(r.json())
        if r.text == '{"text":[],"count":[]}':
            bet = 0
            super2kBet = 0
            effectiveBet = 0
            win = 0
            ret = 0
            activityGifts = 0
            totalRedDiscount = 0
        else:#後台有抓到
            #分紅 有效銷量 : 盈虧報表的  bet欄位
            bet = float(r.json()['text'][0]['bet'].replace(',',''))#4.0總投注額
            super2kBet = float(r.json()['text'][0]['super2kBet'].replace(',',''))#超級2000金額 ,型態為str,是拿來判斷依據
            totalRedDiscount = float(r.json()['text'][0]['totalRedDiscount'].replace(',',''))#總紅包
            bet = round(bet -totalRedDiscount,4) #4.0總銷量 - 紅包
            super2kRed = red_dict[0][4]/10000 #級2000 是否有投注 紅包
            if super2kBet == 0:# 超級2000 如果是 0 的話,分紅總投注額 跟有效銷量 是一樣的 ,紅包也不會有 超級2000問題
                print('超級2000投注為0,總投注額跟有效銷量是一致的')
                effectiveBet = bet
            else: # 有投注 超級2000 ,要在抓出 red_dict 裡  超級2000 是否有投注 紅包,
                print('超級2000有投注, 有效銷量: 總投注需扣掉 超級2000的 2折')
                if super2kRed == 0:# 超級2000 紅包為0
                    print('超級2000紅包為0,有效消亮就可直接減去 super2kBet')
                    effectiveBet = bet- (super2kBet*0.2)# 有效銷量  = 總投注 -(超級2000投注*0.2), 因為超級2000算 8折 
                else:# 超級2000 紅包有值
                    print('超級2000紅包有值, 需把 總待盈虧的超級2000-紅包超級2000')
                    super2kBet = super2kBet - super2kRed#需把盈虧的 超級2000 - 紅包超級2000 ,為實際的 超級2000 投注
                    print('實際超級2000投注額為:%s '%super2kBet)
                    effectiveBet = bet- (super2kBet*0.2)

            win = float(r.json()['text'][0]['win'].replace(',',''))#中獎金額
            ret = float(r.json()['text'][0]['ret'].replace(',',''))#反點
            activityGifts = float(r.json()['text'][0]['activityGifts'].replace(',',''))#活動禮金
        ''' 
        bet = round(bet -totalRedDiscount,4) #4.0總銷量 - 紅包
        effectiveBet = round(effectiveBet -totalRedDiscount,4) #有效銷量 也需減
        '''
        header['Content-Type'] = 'application/json; charset=UTF-8'# 為了真人 加header
        #fhll 需加 content_type這段內容, 但4.0的盈虧不需要 (所以先做4.0,再做真人)

        fhll_r = session.post(admin_url+fhll_url,data=json.dumps(data_fhll),headers=header)
        #print(fhll_r.json())
        trueBet = round(fhll_r.json()['profitStruc'][0]['bet']*0.0001,5)#真人實際投注.抓出來除1萬
        fh_ret =  round(fhll_r.json()['profitStruc'][0]['ret']*0.0001,5)#真人反點
        fh_win = round(fhll_r.json()['profitStruc'][0]['win']*0.0001,5)#真人中獎
        fh_activityGifts = 0#真人活動禮金   都是0


        Allbet_month = bet +trueBet#4.0 + 真人
        effectiveBet_month = effectiveBet+ trueBet# 總有效銷量:  真人加上4.0  ,
        averge =  round(effectiveBet_month/day_range,5)#四捨五入 第二位 ,總日均有效銷量

        user_award = round(fh_win+fh_ret+fh_activityGifts+win+ret+activityGifts,4)#使用者全部中獎金額, 總獎金
        winLost_month = round(Allbet_month- user_award,5)#分紅 輸額: 不是派發條件,是獎金依據

        print('4.0總投注額: %f/總有效銷量: %f ,真人總投注額/總有效銷量: %f '
        %(bet,effectiveBet,trueBet))
        print('4.0: 中獎金額: %f, 反點: %f, 活動禮金: %f, 紅包: %f \n真人: 中獎金額: %f, 反點: %f, 活動禮金: %f'
        %(win,ret,activityGifts,totalRedDiscount,fh_win,fh_ret,fh_activityGifts))
        print('總投注: %f /總有效投: %f /總獎金: %f'%(Allbet_month,effectiveBet_month,user_award))
        print('分紅日均銷量: %f ,總輸額: %f'%(averge,winLost_month))
        print('------------------------------')

        result_data['bet'] = bet
        result_data['effectiveBet'] = effectiveBet
        result_data['trueBet'] = trueBet
        result_data['win'] = win
        result_data['ret'] = ret
        result_data['activityGifts'] = activityGifts
        result_data['fh_win'] = fh_win
        result_data['fh_ret'] = fh_ret
        result_data['fh_activityGifts'] = fh_activityGifts
        result_data['Allbet_month'] = Allbet_month
        result_data['effectiveBet_month'] = effectiveBet_month
        result_data['user_award'] = user_award
        result_data['averge'] = averge
        result_data['winLost_month'] = winLost_month
        result_data['totalRedDiscount']=totalRedDiscount
        result_data['super2kBet'] = super2kBet
        result_data['super2kRed'] = super2kRed



        if winLost_month < 0:
            print('您輸額為負的,不符合派發標準, 工資為0')
            msg = '您輸額為負的,不符合派發標準'
            award = 0
            per = 0
        elif winLost_month == 0:
            msg = '你輸額為0,工資為0'
            award = 0
            per = 0
            print('你沒銷量唷,工資為0')
        else:        
            if averge in Interval(0,10000):
                print('你日均消量在0-1W區間') 
                msg = '你日均消量在0-1W區間'
                if min_bronday < 91:
                    award = round(5*winLost_month/100,10)
                    msg = msg + '你屬於註冊1-90天'
                    per = 5
                    print('你屬於註冊1-90天,工資比例為5%')
                else:
                    award = 0
                    per = 0
                    msg = msg + '你註冊91天以上,沒有工資比例'
                    print('你註冊91天以上,沒有工資比例')
            elif averge in Interval(10001,100000):
                print('你日均消量在10001-10W區間')
                msg = '你日均消量在10001-10W區間'
                if min_bronday < 181:
                    award = round(5*winLost_month/100,10)
                    msg = msg + '你屬於註冊1-180天'
                    per = 5
                    print('你屬於註冊1-180天,工資比利為5%')
                else:
                    award = 0
                    per = 0
                    msg = msg + '你註冊181天以上'
                    print('你註冊181天以上,沒有工資比例')
            elif averge in Interval(100001,300000):
                msg = '你日均消量在100001-30W區間\n註冊沒有限制'
                award = round(5*winLost_month/100,10)
                per = 5
                print('你日均消量在100001-30W區間\n註冊沒有限制,工資比利為5%')
            elif averge in Interval(300001,500000):
                award = round(6*winLost_month/100,10)
                per = 6
                msg = '你日均消量在300001-50W區間\n註冊沒有限制'
                print('你日均消量在300001-50W區間\n註冊沒有限制,工資比利為6%')
            elif averge in Interval(500001,800000):
                msg = '你日均消量在500001-80W區間\n註冊沒有限制'
                award = round(7*winLost_month/100,10)
                per = 7
                print('你日均消量在500001-80W區間\n註冊沒有限制,工資比利為7%')
            elif averge in Interval(800001,1100000):
                msg = '你日均消量在800001-110W區間\n註冊沒有限制'
                award = round(10*winLost_month/100,10)
                per = 10
                print('你日均消量在800001-110W區間\n註冊沒有限制,工資比利為10%')
            elif averge in Interval(1100001,1500000):
                msg = '你日均消量在1100001-150W區間\n註冊沒有限制'
                award = round(15*winLost_month/100,10)
                per = 15
                print('你日均消量在1100001-150W區間\n註冊沒有限制,工資比利為15%')
            elif averge in Interval(1500001,2000000):
                msg = '你日均消量在1500001-200W區間\n註冊沒有限制'
                award = round(16*winLost_month/100,10)
                per = 16
                print('你日均消量在1500001-200W區間\n註冊沒有限制,工資比利為16%')
            elif averge in Interval(2000001,10000000):
                msg = '你日均消量在2000001-1000W區間\n註冊沒有限制'
                award = round(18*winLost_month/100,10)
                per = 18
                print('你日均消量在2000001-1000W區間\n註冊沒有限制,工資比利為18%')
            elif averge in Interval(10000001,15000000):
                msg = '你日均消量在10000001-1500W區間\n註冊沒有限制'
                award = round(20*winLost_month/100,10)
                per = 20
                print('你日均消量在10000001-1500W區間\n註冊沒有限制,工資比利為20%')
            else:
                award = round(23*winLost_month/100,10)
                msg = '你日均消量在1千5百萬以上\n註冊沒有限制'
                per = 23
                print('你日均消量在1千5百萬以上\n註冊沒有限制,工資比利為23%')
            print('你的分紅派發: %f'%award)
        result_data['msg'] = msg
        result_data['award'] = award
        result_data['per'] = per

    except requests.exceptions.ConnectionError:
        print('連線有問題,請稍等')

    except ValueError as e:
        print(e)
        print('你輸入的日期或姓名不符,請再確認')
    except IndexError as e:
        #print(e)
        print('用戶名無此名單')


#admin_Login('phl58')
#game_report_month(user='hdddh1188',month= 10,day=)

