
import HTMLTestRunner,unittest,requests,hashlib,time,random,cx_Oracle,json
from bs4 import BeautifulSoup
import unittest
import datetime
from time import sleep
from selenium import webdriver
from faker import Factory
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import  ElementClickInterceptedException 
import os
import pymysql as p
import logging
import threading
import redis,re

lottery_dict = {
'cqssc':[u'重慶','99101'],'xjssc':[u'新彊時彩','99103'],'tjssc':[u'天津時彩','99104'],
'hljssc':[u'黑龍江','99105'],'llssc':[u'樂利時彩','99106'],'shssl':[u'上海時彩','99107'],
'jlffc':[u'吉利分彩','99111'],'slmmc':[u'順利秒彩','99112'],'txffc':[u'騰訊分彩','99114'],
'btcffc':[u'比特幣分彩','99115'],'fhjlssc':[u'吉利時彩','99116'],
'sd115':[u'山東11選5','99301'],'jx115':[u"江西11選5",'99302'],
'gd115':[u'廣東11選5','99303'],'sl115':[u'順利11選5','99306'],'jsk3':[u'江蘇快3','99501'],
'ahk3':[u'安徽快3','99502'],'jsdice':[u'江蘇骰寶','99601'],'jldice1':[u'吉利骰寶(娛樂)','99602'],
'jldice2':[u'吉利骰寶(至尊)','99603'],'fc3d':[u'3D','99108'],'p5':[u'排列5','99109'],
'lhc':[u'六合彩','99701'],'btcctp':[u'快開','99901'],
'bjkl8':[u'快樂8','99201'],'pk10':[u"pk10",'99202'],'v3d':[u'吉利3D','99801'],
'xyft':[u'幸運飛艇','99203'],'fhxjc':[u'鳳凰新疆','99118'],'fhcqc':[u'鳳凰重慶','99117'],'ssq':[u'雙色球','99401'],
'n3d':[u'越南3d','99124'],'np3':[u'越南福利彩','99123']   
        }
lottery_sh = ['cqssc','xjssc','tjssc','hljssc','llssc','jlffc','slmmc','txffc',
            'fhjlssc','btcffc','fhcqc','fhxjc']
lottery_3d = ['v3d']
lottery_115 = ['sd115','jx115','gd115','sl115']
lottery_k3 = ['ahk3','jsk3']
lottery_sb = ['jsdice',"jldice1",'jldice2']
lottery_fun = ['pk10','xyft']
lottery_noRed = ['fc3d','n3d','np3','p5']#沒有紅包

def func_time(func):#案例時間
    def wrapper(*args):
        start_ = time.time()
        func(*args)
        end_ = time.time() - start_
        print("用時: {}秒".format(end_))
    return wrapper
def return_user(username):#頁面用戶選擇
    global user_
    user_ = []
    user_.append(username)
def return_env(env):#頁面環境選擇
    global env_
    env_ = []
    env_.append(env)
def return_red(red):#頁面是否紅包投注
    global red_type
    red_type = []
    red_type.append(red)


def get_rediskey(envs):#env參數 決定是哪個環境
    redis_dict = {'ip':['10.13.22.152','10.6.1.82']}#0:dev,1:188
    global r
    pool = redis.ConnectionPool(host = redis_dict['ip'][envs],port = 6379)
    r = redis.Redis(connection_pool=pool)

def get_token(envs,user):
    get_rediskey(envs)
    global redis_
    redis_ = r_keys = (r.keys('USER_TOKEN_%s*'%re.findall(r'[0-9]+|[a-z]+',user)[0]))
    for i in r_keys:
        if user in str(i):
            user_keys = (str(i).replace("'",'')[1:])

    user_dict = (r.get(user_keys))
    timestap = (str(user_dict).split('timeOut')[1].split('"token"')[0][2:-4])#
    token_time = (time.localtime(int(timestap)))
    print('token到期時間: %s-%s-%s %s:%s:%s'%(token_time.tm_year,token_time.tm_mon,token_time.tm_mday,
    token_time.tm_hour,token_time.tm_min,token_time.tm_sec))


class Joy188Test(unittest.TestCase):
        
    u"PC接口測試"
    @staticmethod
    def md(password,param):
        m = hashlib.md5()
        m.update(password)
        sr = m.hexdigest()
        for i in range(3):
            sr= hashlib.md5(sr.encode()).hexdigest()
        rx = hashlib.md5(sr.encode()+param).hexdigest()
        return rx
    @staticmethod
    def get_conn(env):#連結數據庫 env 0: dev02 , 1:188
        oracle_ = {'password':['LF64qad32gfecxPOJ603','JKoijh785gfrqaX67854'],
        'ip':['10.13.22.161','10.6.1.41'],'name':['firefog','game']}
        conn = cx_Oracle.connect('firefog',oracle_['password'][env],oracle_['ip'][env]+
        ':1521/'+oracle_['name'][env])
        return conn
    
    @staticmethod
    def date_time():#給查詢 獎期to_date時間用, 今天時間
        global today_time
        
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        format_day = '{:02d}'.format(day)
        today_time = '%s-%s-%s'%(year,month,format_day)
    @staticmethod
    def select_issue(conn,lotteryid):#查詢正在銷售的 期號
        #Joy188Test.date_time()
        #today_time = '2019-06-10'#for 預售中 ,抓當天時間來比對,會沒獎期
        try:
            with conn.cursor() as cursor:
                sql = "select web_issue_code,issue_code from game_issue where lotteryid = '%s' and sysdate between sale_start_time and sale_end_time"%(lotteryid)

                cursor.execute(sql)
                rows = cursor.fetchall()

                global issueName
                global issue
                issueName = []
                issue = []
                if lotteryid in ['99112','99306']:#順利秒彩,順利11選5  不需 講期. 隨便塞
                    issueName.append('1')
                    issue.append('1')
                else:
                    for i in rows:# i 生成tuple
                        issueName.append(i[0])
                        issue.append(i[1])
            conn.close()
        except:
            pass
    @staticmethod
    def select_RedBal(conn,user):
        with conn.cursor() as cursor:
            sql = "SELECT bal FROM RED_ENVELOPE WHERE \
            USER_ID = (SELECT id FROM USER_CUSTOMER WHERE account ='%s')"%user
            cursor.execute(sql)
            rows = cursor.fetchall()

            global red_bal
            red_bal = []
            for i in rows:# i 生成tuple
                red_bal.append(i[0])
        conn.close()
    @staticmethod
    def select_RedID(conn,user):#紅包加壁  的訂單號查詢 ,用來審核用
        with conn.cursor() as cursor:
            sql = "SELECT ID FROM RED_ENVELOPE_LIST WHERE status=1 and \
            USER_ID = (SELECT id FROM USER_CUSTOMER WHERE account ='%s')"%user
            cursor.execute(sql)
            rows = cursor.fetchall()

            global red_id
            red_id = []
            for i in rows:# i 生成tuple
                red_id.append(i[0])
        conn.close()
    @staticmethod
    def select_betTypeCode(conn,lotteryid,game_type):#從game_type 去對應玩法的數字,給app投注使用
        with conn.cursor() as cursor:
            sql = "select bet_type_code from game_bettype_status where lotteryid = '%s' and group_code_name||set_code_name||method_code_name = '%s'"%(lotteryid,game_type)
            
            cursor.execute(sql)
            rows = cursor.fetchall()

            global bet_type
            bet_type = []
            for i in rows:# i 生成tuple
                bet_type.append(i[0])
        conn.close()
    @staticmethod
    def select_orderCode(conn,orderid):# 從iapi投注的orderid對應出 order_code 方案編號
        with conn.cursor() as cursor:
            sql = "select order_code from game_order where id in (select orderid from game_slip where orderid = '%s')"%orderid
            
            cursor.execute(sql)
            rows = cursor.fetchall()

            global order_code 
            order_code = []
            for i in rows:# i 生成tuple
                order_code.append(i[0])
        conn.close()
        
    @staticmethod
    def select_PcOredrCode(conn,user,lottery):#webdriver頁面投注產生定單
        Joy188Test.date_time()#先產生今天日期
        with conn.cursor() as cursor:
            sql = "select order_code from game_order where userid in \
            (select id from user_customer where account = '%s' \
            and order_time > to_date('%s','YYYY-MM-DD')and lotteryid = %s)"%(user,today_time,lottery_dict[lottery][1])
            cursor.execute(sql)
            rows = cursor.fetchall()

            global order_code 
            order_code = []
            for i in rows:# i 生成tuple
                order_code.append(i[0])
        conn.close()
    @staticmethod
    def select_userid(conn,account_):
        with conn.cursor() as cursor:
            sql = "select id from user_customer where account = '%s'"%account_
            cursor.execute(sql)
            rows = cursor.fetchall()
            global userid#, joint_venture# joint_ventue 判斷合營  ,合營 等 上188 後 在加上
            userid = []
            joint_venture =[]

            for i in rows:
                userid.append(i[0])
                #joint_venture.append(i[1])
        conn.close()

    @staticmethod
    def select_userUrl(conn,userid):
        with conn.cursor() as cursor:
            sql = "select url from user_url where url like '%"+ '%s'%(userid) +"%'"
            cursor.execute(sql)
            rows = cursor.fetchall()
            global user_url
            user_url = []
            
            for i in rows:
                user_url.append(i[0])
        conn.close()
    
    @staticmethod
    def web_issuecode(lottery):#頁面產生  獎期用法,  取代DB連線問題
        now_time = int(time.time())
        header = {
                'User-Agent': userAgent,
                'Cookies': 'ANVOID='+cookies_[user]     
                }
        r = session.get(em_url+'/gameBet/%s/lastNumber?_=%s'%(lottery,now_time),headers=header)
        global issuecode
        try:
            issuecode = r.json()['issueCode']
        except:
            pass
        if lottery == 'lhc':
            pass
    @staticmethod    
    def my_con(evn,third):#第三方  mysql連線
        third_dict = {'lc':['lcadmin',['cA28yF#K=yx*RPHC','XyH]#xk76xY6e+bV'],'ff_lc'],
            'ky':['kyadmin',['ALtfN#F7Zj%AxXgs=dT9','kdT4W3#dEug3$pMM#z7q'],'ff_ky'],
            'city':['761cityadmin',['KDpTqUeRH7s-s#D*7]mY','bE%ytPX$5nU3c9#d'],'ff_761city'],
            'im':['imadmin',['D97W#$gdh=b39jZ7Px','nxDe2yt7XyuZ@CcNSE'],'ff_im'],
            'shaba':['sbadmin',['UHRkbvu[2%N=5U*#P3JR','aR8(W294XV5KQ!Zf#"v9'],'ff_sb'],
            'bbin':['bbinadmin','Csyh*P#jB3y}EyLxtg','ff_bbin'],
            'gns':['gnsadmin','Gryd#aCPWCkT$F4pmn','ff_gns']
             }  
        if evn == 0:#dev
            ip = '10.13.22.151'
        elif evn == 1:#188
            ip = '10.6.32.147'
        else:
            print('evn 錯誤')

        user_ =  third_dict[third][0]
        db_ = third_dict[third][2]

        if third == 'gns':#gns只有一個 測試環境
            passwd_ = third_dict[third][1]
            ip = '10.6.32.147'#gns Db 只有 188
        else:
            passwd_ = third_dict[third][1][evn] 

        db = p.connect(
        host = ip,
        user = user_,
        passwd = passwd_,
        db = db_)
        return db

    @staticmethod
    def thirdly_tran(db,tran_type,third,user):
        cur = db.cursor()
        # third 判斷 第三方 是那個 ,gns table 名稱不同
        if third in ['lc','ky','city','im','shaba']:
            table_name = 'THIRDLY_TRANSCATION_LOG'
            if tran_type == 0:#轉入
                trans_name = 'FIREFROG_TO_THIRDLY'
            else:#轉出
                trans_name = 'THIRDLY_TO_FIREFROG'
        elif third  == 'gns':
            table_name = 'GNS_TRANSCATION_LOG'
            if tran_type == 0: #gns轉入
                trans_name = 'FIREFROG_TO_GNS'
            else:
                trans_name = 'GNS_TO_FIREFROG'
        else:
            print('第三方 名稱錯誤')

        sql ="SELECT SN,STATUS FROM %s WHERE FF_ACCOUNT = '%s'\
        AND CREATE_DATE > DATE(NOW()) AND TRANS_NAME= '%s'"%(table_name,user,trans_name)

        global thirdly_sn,status_list
        thirdly_sn = []#轉帳帳變
        status_list = []#帳變狀態
        cur.execute(sql)
        for row in cur.fetchall():
            thirdly_sn.append(row[0])# 單號
            status_list.append(row[1])# 單號狀態

    @staticmethod
    def random_mul(num):#生成random數, NUM參數為範圍
        return(random.randint(1,num))
    
    @staticmethod
    def plan_num(evn,lottery,plan_len):#追號生成
        plan_ = []#存放 多少 長度追號的 list
        Joy188Test.select_issue(Joy188Test.get_conn(evn),lottery_dict[lottery][1])
        for i in range(plan_len):
            plan_.append({"number":issueName[i],"issueCode":issue[i],"multiple":1})
        return plan_

    @staticmethod
    def play_type():#隨機生成  group .  五星,四星.....
        game_group = {'wuxing':u'五星','sixing':u'四星','qiansan':u'前三','housan':u'後三',
        'zhongsan':u'中三','qianer':u'前二','houer':u'後二'}
        return list(game_group.keys())[Joy188Test.random_mul(6)]
    @staticmethod
    def ball_type(test):#對應完法,產生對應最大倍數和 投注完法
        ball = []
        #  (Joy188Test.random_mul(9)) 隨機生成 9以內的數值
        global mul
        if test == 'wuxing':


            ball = [str(Joy188Test.random_mul(9)) for i in range(5)]#五星都是數值
            mul = Joy188Test.random_mul(2)
        elif test == 'sixing':
            ball = ['-' if i ==0  else str(Joy188Test.random_mul(9)) for i in range(5)]#第一個為-
            mul = Joy188Test.random_mul(22)
        elif test == 'housan':
            ball = ['-' if i in [0,1]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第1和2為-
            mul = Joy188Test.random_mul(222)
        elif test == 'qiansan' :
            ball = ['-' if i in[3,4]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第4和5為-
            mul = Joy188Test.random_mul(222)
        elif test == 'zhongsan':
            ball = ['-' if i in[0,4]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第2,3,4為-
            mul = Joy188Test.random_mul(222)
        elif test == 'houer':
            ball = ['-' if i in [0,1,2]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第1,2,3為-
            mul = Joy188Test.random_mul(2222)
        elif test == 'qianer':
            ball = ['-' if i in [2,3,4]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第3,4,5為-
            mul = Joy188Test.random_mul(2222)
        elif test == 'yixing':# 五個號碼,只有一個隨機數值
            ran = Joy188Test.random_mul(4)
            ball = ['-' if i !=ran else str(Joy188Test.random_mul(9)) for i in range(5)]
            mul = Joy188Test.random_mul(2222)
        else:
             mul = Joy188Test.random_mul(1)
        a = (",".join(ball))
        return a
    @staticmethod
    def game_type(lottery):
        #test___ = play_type()

        game_group = {'wuxing':u'五星','sixing':u'四星','qiansan':u'前三','housan':u'後三',
        'zhongsan':u'中三','qianer':u'前二','houer':u'後二','xuanqi':u'選ㄧ','sanbutonghao':u'三不同號',
        'santonghaotongxuan':u'三同號通選','guanya':u'冠亞','biaozhuntouzhu':u'標準玩法','zhengma':u'正碼',
        'p3sanxing':u'P3三星','renxuan':u'任選'}
        
        game_set = {
        'zhixuan': u'直選','renxuanqizhongwu': u'任選一中一','biaozhun':u'標準','zuxuan':u'組選'
        ,'pingma':u'平碼','putongwanfa':u'普通玩法'}
        game_method = {
        'fushi': u'複式','zhixuanfushi':u'直選複式','zhixuanliuma':u'直選六碼',
        'renxuan7': u'任選7'    
        }

        group_ = Joy188Test.play_type()#建立 個隨機的goup玩法 ex: wuxing,目前先給時彩系列使用
        #set_ = game_set.keys()[0]#ex: zhixuan
        #method_ = game_method.keys()[0]# ex: fushi
        global play_

        #play_ = ''#除了 不是 lottery_sh 裡的彩種

        lottery_ball = Joy188Test.ball_type(group_)# 組出什麼玩法 的 投注內容


        test_dicts = {   
        0 : ["%s.zhixuan.fushi"%(group_,),lottery_ball] , 
        1 : ["qianer.zhixuan.zhixuanfushi",'3,6,-'],
        2 : ["xuanqi.renxuanqizhongwu.fushi","01,02,05,06,08,09,10"],
        3 : ["sanbutonghao.biaozhun.biaozhuntouzhu","1,2,6"],
        4 : ["santonghaotongxuan.santonghaotongxuan.santonghaotongxuan","111 222 333 444 555 666"],
        5 : ["guanya.zhixuan.fushi","09 10,10,-,-,-,-,-,-,-,-"],
        6 : ['qianer.zuxuan.fushi','4,8'],
        7 : ["biaozhuntouzhu.biaozhun.fushi","04,08,13,19,24,27+09",],
        8 : ["zhengma.pingma.zhixuanliuma","04"],
        9 : ["p3sanxing.zhixuan.p3fushi","9,1,0",],
        10: ["renxuan.putongwanfa.renxuan7","09,13,16,30,57,59,71"],   
        11: ["chungtienpao.chungtienpao.chungtienpao","1.01"]#快開
        }

        if lottery in lottery_sh:#時彩系列
            num = 0
            play_ = u'玩法名稱: %s.%s.%s'%(game_group[group_],game_set['zhixuan'],
            game_method['fushi'])

        elif lottery in lottery_3d:
            num = 1
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['qianer'],game_set['zhixuan'],
                    game_method['zhixuanfushi'])
        elif lottery in lottery_noRed:
            if lottery in ['p5','np3']:
                num = 9
                play_ = u'玩法名稱: %s.%s.%s'%(game_group['p3sanxing'],game_set['zhixuan'],
                    game_method['fushi'])
            else:
                num = 1
                play_ = u'玩法名稱: %s.%s.%s'%(game_group['qianer'],game_set['zhixuan'],
                        game_method['zhixuanfushi'])                    
        elif lottery in lottery_115:
            num = 2
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['xuanqi'],game_set['renxuanqizhongwu'],
                    game_method['fushi'])
        elif lottery in lottery_k3:
            num = 3
            play_ = u'玩法名稱: %s.%s'%(game_group['sanbutonghao'],game_set['biaozhun'])
        elif lottery in lottery_sb:
            num = 4
            play_ = u'玩法名稱: %s'%(game_group['santonghaotongxuan'])
        elif lottery in lottery_fun:
            num = 5
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['guanya'],game_set['zhixuan'],
                    game_method['fushi'])
        elif lottery == 'shssl':
            num = 6
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['qianer'],game_set['zuxuan'],
                    game_method['fushi'])
        elif lottery ==  'ssq':
            num = 7
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['biaozhuntouzhu'],game_set['biaozhun'],
                    game_method['fushi'])
        elif lottery == 'lhc':
            num = 8
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['zhengma'],game_set['pingma'],
                    game_method['zhixuanliuma'])
        elif lottery == 'p5':
            num = 9
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['p3sanxing'],game_set['zhixuan'],
                    game_method['fushi'])
        elif lottery == 'bjkl8':
            num = 10
            play_ = u'玩法名稱: %s.%s.%s'%(game_group['renxuan'],game_set['putongwanfa'],
                    game_method['renxuan7'])
        else:
            num = 11
            #play_ = u'玩法名稱: 沖天炮
        return test_dicts[num][0],test_dicts[num][1]
    @staticmethod
    def req_post_submit(account,lottery,data_,moneyunit,awardmode):
        awardmode_dict = {0:u"非一般模式",1:u"非高獎金模式",2:u"高獎金"}
        money_dict = {1:u"元模式",0.1:u"分模式",0.01:u"角模式"}
        while True:
            header = {
                'Cookie': "ANVOID=" + cookies_[account],
                'User-Agent': userAgent
            }


            r = session.post(em_url+'/gameBet/'+lottery+'/submit', 
            data = json.dumps(data_),headers=header)

            global content_
            try:
            #print(r.json())
                msg = (r.json()['msg'])
                mode = money_dict[moneyunit]
                mode1 = awardmode_dict[awardmode]
                project_id = (r.json()['data']['projectId'])#訂單號
                submit_amount = (r.json()['data']['totalprice'])#投注金額
                #submit_mul = u"投注倍數: %s"%m#隨機倍數
                lottery_name= u'投注彩種: %s'%lottery_dict[lottery][0]     
            
                if r.json()['isSuccess'] == 0:#
                    #select_issue(get_conn(envs),lottery_dict[lottery][1])#呼叫目前正在販售的獎期
                    content_ = (lottery_name+"\n"+ mul_+ "\n"+play_ +"\n"+ msg+"\n")
                    #print(content_)
                    
                    if r.json()['msg'] == u'存在封锁变价':#有可能封鎖變價,先跳過   ()
                        break
                    elif r.json()['msg'] == u'您的投注内容 超出倍数限制，请调整！':
                        print(u'倍數超出了唷,下次再來')
                        break
                    elif  r.json()['msg']==u'方案提交失败，请检查网络并重新提交！':
                        print(r.json()['msg'])
                        break
                    else:# 系統內部錯誤
                        print(r.json()['msg'])
                        break
                else:#投注成功
                    if red_type[0]=='yes':
                        content_ = (lottery_name+"\n"+u'投注單號: '+project_id+"\n"
                                    +mul_+ "\n" 
                                    +play_+"\n"+u"投注金額: "+ str(float(submit_amount*0.0001))+"\n"
                                    +"紅包金額: 2"+mode+"/"+mode1+"\n"+msg+"\n")
                    else:
                        content_ = (lottery_name+"\n"+u'投注單號: '+project_id+"\n"
                                    +mul_+ "\n" 
                                    +play_+"\n"+u"投注金額: "+ str(float(submit_amount*0.0001))+"\n"
                                    +mode+"/"+mode1+"\n"+msg+"\n")
                    break
            except ValueError:
                content_ = ('%s 投注失敗'%lottery+"\n")
                break
        print(content_)
    @staticmethod
    #@jit_func_time
    def test_PCLotterySubmit(moneyunit=1,plan=1):#彩種投注
        u"投注測試"
        
        account = user_[0]
        if red_type[0] == 'yes':
            print('使用紅包投注')
        else:
            print('不使用紅包投注')
        while True:
            try:
                for i in lottery_dict.keys():
                #for i in lottery_noRed:
                    statu = 1
                    global mul_ #傳回 投注出去的組合訊息 req_post_submit 的 content裡
                    global mul
                    ball_type_post = Joy188Test.game_type(i)# 找尋彩種後, 找到Mapping後的 玩法後內容

                    awardmode =1
                    if i  == 'btcctp':
                        statu = 0

                        awardmode = 2
                        moneyunit = 1
                        mul = Joy188Test.random_mul(1)#不支援倍數,所以random參數為1
                    elif i == 'bjkl8':
                        mul = Joy188Test.random_mul(5)#北京快樂8
                    elif i == 'p5':
                        mul = Joy188Test.random_mul(5)

                    elif i in ['btcffc','xyft']:
                        awardmode = 2
                    elif i in lottery_sb:#骰寶只支援  元模式
                        moneyunit = 1
                    
                    
                    mul_ = (u'選擇倍數: %s'%mul)
                    amount = 2*mul*moneyunit

                #從DB抓取最新獎期.[1]為 99101類型select_issueselect_issue

                    if plan == 1   :# 一般投住

                        #Joy188Test.select_issue(Joy188Test.get_conn(1),lottery_dict[i][1])
                        #從DB抓取最新獎期.[1]為 99101類型
                        #print(issueName,issue)
                        Joy188Test.web_issuecode(i)
                        plan_ = [{"number":'123',"issueCode":issuecode,"multiple":1}]
                        print(u'一般投住')
                        isTrace=0
                        traceWinStop=0
                        traceStopValue=-1
                    else: #追號
                        plan_ = Joy188Test.plan_num(envs,i,Joy188Test.random_mul(30))#隨機生成 50期內的比數
                        print(u'追號, 期數:%s'%len(plan_))
                        isTrace=1
                        traceWinStop=1
                        traceStopValue=1

                    len_ = len(plan_)# 一般投注, 長度為1, 追號長度為
                    #print(game_type)
                
                    post_data = {"gameType":i,"isTrace":isTrace,"traceWinStop":traceWinStop,
                    "traceStopValue":traceWinStop,
                    "balls":[{"id":1,"ball":ball_type_post[1],"type":ball_type_post[0],
                    "moneyunit":moneyunit,"multiple":mul,"awardMode":awardmode,
                    "num":1}],"orders": plan_ ,"amount" : len_*amount}#不使用紅包
  
                    post_data_lhc = {"balls":[{"id":1,"moneyunit":moneyunit,"multiple":1,"num":1,
                    "type":ball_type_post[0],"amount":amount,"lotterys":"13",
                    "ball":ball_type_post[1],"odds":"7.5"}],
                    "isTrace":0,"orders":plan_,
                    "amount":amount,"awardGroupId":202}

                    post_data_sb ={"gameType":i,"isTrace":0,"multiple":1,"trace":1,
                    "amount":amount,
                    "balls":[{"ball":ball_type_post[1],
                    "id":11,"moneyunit":moneyunit,"multiple":1,"amount":amount,"num":1,
                    "type":ball_type_post[0]}],
                    "orders":plan_}

                    if i in 'lhc':
                        Joy188Test.req_post_submit(account,'lhc',post_data_lhc,moneyunit,awardmode)
                        
                    elif i in lottery_sb:
                        Joy188Test.req_post_submit(account,i,post_data_sb,moneyunit,awardmode) 
                    else:
                        if red_type[0] == 'yes':#紅包投注
                            post_data['redDiscountAmount'] = 2 #增加紅包參數
                            Joy188Test.req_post_submit(account,i,post_data,moneyunit,awardmode)
                        else:
                            Joy188Test.req_post_submit(account,i,post_data,moneyunit,awardmode)
                Joy188Test.select_RedBal(Joy188Test.get_conn(1),user)
                print('紅包餘額: %s'%(int(red_bal[0])/10000))
                break
            except KeyError as e:
                print(u"輸入值有誤")
                break           
            except IndexError as e :
                #print(e)
                break
    @staticmethod
    @func_time
    def test_PcLogin(source='Pc'):
        u"登入測試"
        global user#傳給後面 PC 街口案例  request參數
        global password#傳入 werbdriver登入的密碼 
        global post_url#非em開頭
        global em_url#em開頭 
        global userAgent
        global envs#回傳redis 或 sql 環境變數   ,dev :0, 188:1
        global cookies_
        global msg
        global third_list
        third_list = ['gns','shaba','im','ky','lc','city']
        cookies_ = {}   

        

            
        user = user_[0]
        '''
        account_ = {'kerr000':u'總代','kerr001':u'一代','kerr43453':u'玩家',
        'kerrthird001':'二代',user_[0]:'測試用戶名'}#總代,一代,玩家登入測試
        '''
        account_ = {user_[0]:'輸入的用戶名'}

        if env_[0] in ['dev02','dev03','fh82dev02','88hlqpdev02','teny2020dev02']:# 多增加合營
            password = b'123qwe'
            post_url = "http://www.%s.com"%env_[0]
            envs = 0

        elif env_[0] == 'joy188':

            password = b'amberrd'
            post_url = "http://www2.%s.com"%env_[0]
            envs = 1
        elif env_[0] == 'maike2020':
            password = b'amberrd'
            post_url = "http://www.%s.com"%env_[0]
            envs = 1
        elif env_[0] == 'fh968':
            password = b'tsuta0425'
            post_url = "http://www.%s.com"%env_[0]
        '''
        else:
            print("輸入url有誤")
        '''
        em_url =  'http://em.%s.com'%env_[0] 

        param = b'f4a30481422765de945833d10352ea18'

        #判斷從PC ,ios ,還世 andriod
        #global userAgent
        if source == 'Pc':
            userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"     

        elif source == 'Android':
            userAgent = 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36'

        elif source == 'Ios':
            userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'


        header = {
            'User-Agent': userAgent
        }
        global session
        while True:
            try:
                for i in account_.keys():
                    postData = {
                        "username": i,
                        "password": Joy188Test.md(password,param),
                        "param" :param
                    }
                    session = requests.Session()
                    r = session.post(post_url+'/login/login',data = postData, headers = header,
                                    )

                    cookies = r.cookies.get_dict()#獲得登入的cookies 字典
                    cookies_.setdefault(i,cookies['ANVOID'])
                    t = time.strftime('%Y%m%d %H:%M:%S')
                    #msg = (u'登錄帳號: %s,登入身分: %s'%(i,account_[i])+u',現在時間:'+t+r.text)
                    print(u'登錄帳號: %s'%(i)+u',現在時間:'+t)
                    print(r.text)
                    print(r.json()['isSuccess'])
               
                    #return url
                break
            except requests.exceptions.ConnectionError:
                print('please wait!')
                break

            except IOError:
                print('please wait!!!')
                break
    
    @staticmethod
    def APP_SessionPost(third,url,post_data):#共用 session post方式 (Pc)
        header={
            'User-Agent': userAgent,
            'Content-Type': 'application/json; charset=UTF-8', 
        }
        try:
            session = requests.Session()
            #r = requests.post(env+'/%s/balance'%third,data=json.dumps(data_),headers=header)
            #print(env)
            r = session.post(env+'/%s/%s'%(third,url),headers=header,data=json.dumps(post_data))
            
            if 'balance' in url:
                balance = r.json()['body']['result']['balance']
                print('%s 的餘額為: %s'%(third,balance))
            elif 'getBalance' in url:
                balance = r.json()['body']['result']['balance']
                print('4.0餘額: %s'%balance)

        except requests.exceptions.ConnectionError:
            print(u'連線有問題,請稍等')
    @staticmethod
    def session_post(account,third,url,post_data):#共用 session post方式 (Pc)
        header={
            'User-Agent': userAgent,
            'Cookie': 'ANVOID=' +cookies_[account],
            'Content-Type': 'application/json; charset=UTF-8', 
        }
        try:
            r = session.post(post_url+url,headers=header,data=json.dumps(post_data))

            if 'Balance' in url:
                print('%s, 餘額: %s'%(third,r.json()['balance']))
            elif 'transfer' in url:
                if r.json()['status'] == True:
                    print('帳號 kerrthird001 轉入 %s ,金額:1, 進行中'%third)
                else:
                    print('%s 轉帳失敗'%third)
            elif 'getuserbal' in url:
                print('4.0 餘額: %s'%r.json()['data'])
            #print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
            #print('result: '+statu_code+"\n"+'---------------------')

        except requests.exceptions.ConnectionError:
            print(u'連線有問題,請稍等')
    @staticmethod
    def session_get(user,url_,url):#共用 session get方式
        header={
            'User-Agent': userAgent,
            'Cookie': 'ANVOID=' +cookies_[user],
            'Content-Type': 'application/json; charset=UTF-8', 
        }
        try:
            r = session.get(url_+url,headers=header)
            html = BeautifulSoup(r.text,'lxml')# type為 bs4類型
            title = str(html.title)
            statu_code = str(r.status_code)#int 轉  str
            
            print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
            print(url)
            print('result: '+statu_code+"\n"+'---------------------')

        except requests.exceptions.ConnectionError:
            print(u'連線有問題,請稍等')
    
    @staticmethod
    @func_time
    def test_PcThirdHome():#登入第三方頁面,創立帳號
        u"第三方頁面測試"
        threads = []
        third_url = ['gns','ag','sport','shaba','lc','im','ky','fhx','bc','fhll','bc']

        for i in third_url:
            if i == 'shaba':#沙巴特立
                url = '/shaba/home?act=esports'
            elif i == 'fhll':#真人特例
                fhll_dict = {'77104':u'樂利時彩','77101':u'樂利1.5分彩',
                '77103':u'樂利六合彩','77102':u'樂利快3'}
                for i in fhll_dict.keys():
                    url = '/fhll/home/%s'%i
                    #print(url)
                    #print(fhll_dict[i])#列印 中文(因為fhll的title都是一樣)
                    t = threading.Thread(target=Joy188Test.session_get,args=(user,post_url,url))
                    threads.append(t)
                    #Joy188Test.session_get(user,post_url,url)# get方法
                break#不再跑到 下面 session_get 的func
            elif i == 'fhx':
                url = '/fhx/index'
            else:
                url = '/%s/home'%i
            #print(url)
            t = threading.Thread(target=Joy188Test.session_get,args=(user,post_url,url))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()


            #Joy188Test.session_get(user,post_url,url)
        
    
    
    @staticmethod
    @func_time
    def test_PcFFHome():
        u"4.0頁面測試"
        threads = []
        url_188 = ['/fund','/bet/fuddetail','/withdraw','/transfer','/index/activityMall'
        ,'/ad/noticeList?noticeLevel=2','/frontCheckIn/checkInIndex','/frontScoreMall/pointsMall']        
        em_188 = ['/gameUserCenter/queryOrdersEnter','/gameUserCenter/queryPlans']
        for i in url_188:
            if i in ['/frontCheckIn/checkInIndex','/frontScoreMall/pointsMall']:
                Joy188Test.session_get(user,post_url,i)
            else:
                t = threading.Thread(target=Joy188Test.session_get,args=(user,post_url,i))
                threads.append(t)
            #Joy188Test.session_get(user,post_url,i)
        for i in em_188:
            #Joy188Test.session_get(user,em_url,i)
            t = threading.Thread(target=Joy188Test.session_get,args=(user,em_url,i))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        
    @staticmethod
    @func_time
    def test_PcChart():
        "走勢圖測試"
        ssh_url = ['cqssc','hljssc','tjssc','xjssc','llssc','txffc','btcffc','fhjlssc',
                   'jlffc','slmmc','sd115','ll115','gd115','jx115']
        k3_url = ['jsk3','ahk3','jsdice','jldice1','jldice2']
        low_url = ['d3','v3d']
        fun_url = ['xyft','pk10']
        for i in ssh_url:
            Joy188Test.session_get(user,em_url,'/game/chart/%s/Wuxing'%i)
        for i in k3_url:
            Joy188Test.session_get(user,em_url,'/game/chart/%s/chart'%i)
        for i in low_url:
            Joy188Test.session_get(user,em_url,'/game/chart/%s/Qiansan'%i)
        for i in fun_url:
            Joy188Test.session_get(user,em_url,'/game/chart/%s/CaipaiweiQianfushi'%i)
        Joy188Test.session_get(user,em_url,'/game/chart/p5/p5chart')
        Joy188Test.session_get(user,em_url,'/game/chart/ssq/ssq_basic')
        Joy188Test.session_get(user,em_url,'/game/chart/kl8/Quwei')
    
    
    @staticmethod
    @func_time
    def test_PcThirdBalance():
        '''4.0/第三方餘額'''
        threads = []
        
        header  = {
        'User-Agent': userAgent,
        'Cookie': 'ANVOID='+cookies_[user]
        }
        
        print('帳號: %s'%user)
        for third in third_list:
            if third == 'gns':
                third_url = '/gns/gnsBalance'
            else:
                third_url = '/%s/thirdlyBalance'%third 
            #r = session.post(post_url+third_url,headers=header)
            #print('%s, 餘額: %s'%(third,r.json()['balance']))
            t = threading.Thread(target=Joy188Test.session_post,args=(user,third,third_url,''))
            threads.append(t)
        t = threading.Thread(target=Joy188Test.session_post,args=(user,'','/index/getuserbal',''))
        threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        '''
        r = session.post(post_url+'/index/getuserbal',headers=header)
        print('4.0 餘額: %s'%r.json()['data'])
        '''
    @staticmethod
    @func_time
    def test_PcTransferin():#第三方轉入
        '''第三方轉入'''
        header  = {
            'User-Agent': userAgent,
            'Cookie': 'ANVOID='+cookies_[user],
            'Content-Type' : 'application/json; charset=UTF-8'
            }
        post_data = {"amount":1}
        statu_dict ={} #存放 轉帳的 狀態
        for third in third_list:
            if third == 'gns':
                third_url = '/gns/transferToGns'
            else:
                third_url = '/%s/transferToThirdly'%third
            r = session.post(post_url+third_url,data=json.dumps(post_data),headers=header)

            #t = threading.Thread(target=Joy188Test.session_post,args=('kerrthird001',third,third_url,post_data))
            #threads.append(t)
            
            #判斷轉帳的 狀態
            if r.json()['status'] == True:
                print('帳號 %s 轉入 %s ,金額:1, 進行中'%(user,third))
                status = r.json()['status']
            else:
                status = r.json()['status']
                print('%s 轉帳失敗'%third)#列出錯誤訊息 , 
                
            statu_dict[third] = status#存放 各第三方的轉帳狀態
        #print(statu_dict)
        
        for third in statu_dict.keys():
            if statu_dict[third] == True:#判斷轉帳的狀態, 才去要 單號
                Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=0,third=third,user=user)# tran_type 0為轉轉入
                count =0
                while status_list[-1] != '2' and count !=10:#確認轉帳狀態,  2為成功 ,最多做10次
                    Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=0,third=third,user=user)# 
                    sleep(1.5)
                    count += 1
                    if count== 15:
                        #print('轉帳狀態失敗')# 如果跑道9次  需確認
                        pass
                print('狀態成功. %s ,sn 單號: %s'%(third,thirdly_sn[-1]))
            else:
                pass

        Joy188Test.test_PcThirdBalance()
    
    @staticmethod
    @func_time
    def test_PcTransferout():#第三方轉回
        '''第三方轉出'''
        statu_dict= {}#存放 第三方狀態
        header  = {
            'User-Agent': userAgent,
            'Cookie': 'ANVOID='+cookies_[user],
            'Content-Type' : 'application/json; charset=UTF-8'
            }
        post_data = {"amount":1}
        for third in third_list:
            url = '/%s/transferToFF'%third
            
            r = session.post(post_url+url,data=json.dumps(post_data),headers=header)
            if r.json()['status'] == True:
                print('帳號 %s, %s轉回4.0 ,金額:1, 進行中'%(user,third))
                status = r.json()['status']
            else:
                print(third+r.json()['errorMsg'])
                status = r.json()['status']
                #print('轉帳接口失敗')
            statu_dict[third] = status

        for third in statu_dict.keys():
            if statu_dict[third] == True:
                Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=1,third=third,user=user)# tran_type 1 是 轉出
                count =0
                while status_list[-1] != '2' and count !=10:#確認轉帳狀態,  2為成功 ,最多做10次
                    Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=0,third=third,user=user)# 
                    sleep(1)
                    count += 1
                    if count== 9:
                        #print('轉帳狀態失敗')# 如果跑道9次  需確認
                        pass
                print('狀態成功. %s ,sn 單號: %s'%(third,thirdly_sn[-1]))
            else:
                pass
        Joy188Test.test_PcThirdBalance()
    @staticmethod
    def admin_login():
        global admin_cookie,admin_url,header
        admin_cookie = {}
        if env_[0] in ['dev02','fh82dev02','88hlqpdev02','teny2020dev02']:
            admin_url = 'http://admin.dev02.com'
            password = '123qwe'
        else:
            admin_url = 'http://admin.joy188.com'
            password = 'amberrd'
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36',
                  'Content-Type': 'application/x-www-form-urlencoded'}
        admin_data = {'username':'cancus','password':password,'bindpwd':123456}
        r = session.post(admin_url+'/admin/login/login',data=admin_data,headers=header)
        cookies = r.cookies.get_dict()#獲得登入的cookies 字典
        admin_cookie['admin_cookie'] =  cookies['ANVOAID'] 
    @staticmethod
    def test_redEnvelope():#紅包加壁,審核用
        user = user_[0]
        print('用戶: %s'%user)
        red_list = [] #放交易訂單號id

        try:
            Joy188Test.select_RedBal(Joy188Test.get_conn(envs),user)
            print('紅包餘額: %s'%(int(red_bal[0])/10000))
        except IndexError:
            print('紅包餘額為0')
        Joy188Test.admin_login()#登入後台
        data = {"receives":user,"blockType":"2","lotteryType":"1","lotteryCodes":"",
        "amount":"100","note":"test"}
        header['Cookie'] = 'ANVOAID='+ admin_cookie['admin_cookie']#存放後台cookie
        header['Content-Type'] ='application/json'
        r = session.post(admin_url+'/redAdmin/redEnvelopeApply',#後台加紅包街口 
        data = json.dumps(data),headers=header)
        if r.json()['status'] ==0:
            print('紅包加幣100')
        else:
            print ('失敗')
        Joy188Test.select_RedID(Joy188Test.get_conn(envs),user)#查詢教地訂單號,回傳審核data
        #print(red_id)
        red_list.append('%s'%red_id[0])
        #print(red_list)
        data = {"ids":red_list ,"status":2}
        r = session.post(admin_url+'/redAdmin/redEnvelopeConfirm',#後台審核街口 
        data = json.dumps(data),headers=header)
        if r.json()['status'] ==0:
            print('審核通過')
        else:
            print('審核失敗')
        Joy188Test.select_RedBal(Joy188Test.get_conn(envs),user)
        print('紅包餘額: %s'%(int(red_bal[0])/10000))
   
class Joy188Test3(unittest.TestCase):
    u'APP接口測試'

    @staticmethod
    @func_time
    def test_AppLogin():
        u"APP登入測試"
        global userAgent
        userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36' 
        account_ = {user_[0]:'輸入的用戶名'}
        global token_,userid_
        token_  ={}
        userid_ ={}
        global header
        header = {
        'User-Agent': userAgent, 
        'Content-Type': 'application/json'
        }
        
        #判斷用戶是dev或188,  uuid和loginpasssource為固定值
        global envs,env,domain_url# envs : DB環境 用, env 環境 url ,request url 用
            
        if env_[0] in ['dev02','fh82dev02','88hlqpdev02','teny2020dev02']:
            env = 'http://10.13.22.152:8199/'
            domain_url = 'http://www.%s.com'%env_[0]
            envs = 0
            uuid = "2D424FA3-D7D9-4BB2-BFDA-4561F921B1D5"
            loginpasssource = "fa0c0fd599eaa397bd0daba5f47e7151"
            if env_[0] == 'dev02':#判斷合營,歡樂棋牌
                jointVenture = 0
            elif env_[0] == 'fh82dev02':
                jointVenture = 1
            else:
                jointVenture = 2#歡樂棋牌
        elif env_[0] in ['joy188','maike2020']:
            env = 'http://iphong.joy188.com/'
            domain_url = 'http://iphong.joy188.com/'
            envs = 1
            uuid = 'f009b92edc4333fd'
            loginpasssource = "3bf6add0828ee17c4603563954473c1e"
            if env_[0] == 'joy188':# 判斷是否為一般用戶還是合營用戶
                jointVenture = 0
            else:
                jointVenture = 1
        else:
            pass
        #登入request的json
        for i in account_.keys():
            
            login_data = {
            "head": {
                "sessionId": ''
            },
            "body": {
                "param": {
                "username": i+"|"+ uuid,
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
            try:
                r = requests.post(env+'front/login',data=json.dumps(login_data),headers=header)
                #print(r.json())
                token = r.json()['body']['result']['token']
                userid = r.json()['body']['result']['userid']
                token_.setdefault(i,token)
                userid_.setdefault(i,userid)
                print(u'APP登入成功,登入帳號: %s'%(i))
                print("Token: %s"%token)
                print("Userid: %s"%userid)
            except ValueError as e:
                print(e)
                print(u"登入失敗")
                break
            #user_list.setdefault(userid,token) 
        get_token(envs,user_[0])
        
    @staticmethod
    @func_time
    def test_AppSubmit():
        u"APP投注"
        global user
        
        user = user_[0]#業面用戶登入
        t = time.strftime('%Y%m%d %H:%M:%S')
        print(u'投注帳號: %s, 現在時間: %s'%(user,t))
        try:
            for i in lottery_dict.keys():
                if i in ['slmmc','sl115','btcctp']:
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
                    lotteryid = lottery_dict[i][1]
                    
                    Joy188Test.select_issue(Joy188Test.get_conn(envs),lotteryid)# 目前彩種的獎棋
                    #print(issue,issueName)
                    now = int(time.time()*1000)#時間戳
                    ball_type_post = Joy188Test.game_type(i)#玩法和內容,0為玩法名稱, 1為投注內容
                    methodid = ball_type_post[0].replace('.','')#ex: housan.zhuiam.fushi , 把.去掉
                    
                
                    #找出對應的玩法id
                    Joy188Test.select_betTypeCode(Joy188Test.get_conn(envs),lotteryid,methodid)

                    data_ = {"head":
                    {"sessionId":token_[user]},
                    "body":{"param":{"CGISESSID":token_[user],# 產生  kerr001的token
                    "lotteryId":str(lotteryid),"chan_id":1,"userid":1373224,
                    "money":2*mul,"issue":issue[0],"issueName":issueName[0],"isFirstSubmit":0,
                    "list":[{"methodid":bet_type[0],"codes":ball_type_post[1],"nums":1,
                    "fileMode":0,"mode":1,"times":mul,"money":2*mul}],#times是倍數
                    "traceIssues":"","traceTimes":"","traceIstrace":0,
                    "saleTime":now,
                    "userIp":168627247,"channelId":402,"traceStop":0}}}
                    session = requests.session()

                    r = session.post(env+'game/buy',data=json.dumps(data_),headers=header) 

                    if r.json()['head']['status'] == 0: #status0 為投注成功
                        print(u'%s投注成功'%lottery_dict[i][0])
                        print(play_)#投注完法 中文名稱
                        print(u"投注內容: %s"%ball_type_post[1])
                        print(u"投注金額: %s, 投注倍數: %s"%(2*mul,mul))#mul 為game_type方法對甕倍數
                        #print(r.json())
                        orderid = (r.json()['body']['result']['orderId'])
                        Joy188Test.select_orderCode(Joy188Test.get_conn(envs),orderid)#找出對應ordercode
                        #print('orderid: %s'%orderid)
                        print(u'投注單號: %s'%order_code[-1])
                        print('------------------------------')
                    else:
                        #print(r.json())
                        pass
        except requests.exceptions.ConnectionError:
            print('please wait')
        except IndexError:
            pass
                
    @staticmethod
    def test_AppOpenLink():
        '''APP開戶/註冊'''
        user = user_[0] 
        data_ =  {"head":{"sessionId":token_[user]},"body":{"param":{"CGISESSID":token_[user],"type":1,"days":-1,"infos":[{"lotteryId":"77101","lotteryName":"\\u4e50\\u5229\\u771f\\u4eba\\u5f69","lotterySeriesCode":10,"lotterySeriesName":"\\u771f\\u4eba\\u5f69\\u7968","awardGroupId":77101,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450},{"lotteryId":"99101","lotteryName":"\\u6b22\\u4e50\\u751f\\u8096","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":12,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":890,"threeLimitRet":990},{"lotteryId":"99101","lotteryName":"\\u6b22\\u4e50\\u751f\\u8096","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":1,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99101","lotteryName":"\\u6b22\\u4e50\\u751f\\u8096","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":10,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99103","lotteryName":"\\u65b0\\u7586\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":19,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99103","lotteryName":"\\u65b0\\u7586\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":20,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99103","lotteryName":"\\u65b0\\u7586\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":21,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99104","lotteryName":"\\u5929\\u6d25\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":36,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99104","lotteryName":"\\u5929\\u6d25\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":37,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99104","lotteryName":"\\u5929\\u6d25\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":38,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":13,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":5,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":16,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99106","lotteryName":"\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":33,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99106","lotteryName":"\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":34,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99106","lotteryName":"\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":35,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99107","lotteryName":"\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":15,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99107","lotteryName":"\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":8,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99107","lotteryName":"\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":18,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99108","lotteryName":"3D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":101,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99108","lotteryName":"3D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":103,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99109","lotteryName":"P5","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":102,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99109","lotteryName":"P5","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":106,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99111","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":41,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99111","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":42,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99111","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":43,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99112","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":56,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99112","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":57,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99112","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":58,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99113","lotteryName":"\\u8d85\\u7ea72000\\u79d2\\u79d2\\u5f69(APP\\u7248)","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":11416083,"awardName":"2000\\u5956\\u91d1\\u7ec4","superLimitRet":90},{"lotteryId":"99114","lotteryName":"\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":208,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99114","lotteryName":"\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":209,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99114","lotteryName":"\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":210,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99115","lotteryName":"\\u51e4\\u51f0\\u6bd4\\u7279\\u5e01\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":214,"awardName":"\\u5956\\u91d1\\u7ec41000","directLimitRet":4750,"threeLimitRet":4750},{"lotteryId":"99116","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":228,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99116","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":230,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99116","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":229,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99117","lotteryName":"\\u51e4\\u51f0\\u91cd\\u5e86\\u5168\\u7403\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":263,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99118","lotteryName":"\\u51e4\\u51f0\\u65b0\\u7586\\u5168\\u7403\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":264,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":490,"threeLimitRet":450},{"lotteryId":"99119","lotteryName":"\\u6cb3\\u5185\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":268,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":490,"threeLimitRet":450},{"lotteryId":"99120","lotteryName":"\\u6cb3\\u5185\\u4e94\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":273,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":490,"threeLimitRet":450},{"lotteryId":"99121","lotteryName":"360\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":274,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":490,"threeLimitRet":450},{"lotteryId":"99122","lotteryName":"360\\u4e94\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":275,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":490,"threeLimitRet":450},{"lotteryId":"99123","lotteryName":"\\u8d8a\\u5357\\u798f\\u5f69","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":278,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99124","lotteryName":"\\u8d8a\\u53573D\\u798f\\u5f69","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":279,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99201","lotteryName":"\\u5317\\u4eac\\u5feb\\u4e508","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":32,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":1450,"threeLimitRet":950},{"lotteryId":"99202","lotteryName":"PK10","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":206,"awardName":"\\u5956\\u91d1\\u7ec41800"},{"lotteryId":"99203","lotteryName":"\\u98de\\u8247","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":233,"awardName":"\\u5956\\u91d1\\u7ec41000","directLimitRet":4300},{"lotteryId":"99301","lotteryName":"\\u5c71\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":24,"awardName":"\\u5956\\u91d1\\u7ec41782","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99301","lotteryName":"\\u5c71\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":9,"awardName":"\\u5956\\u91d1\\u7ec41620","directLimitRet":1250,"threeLimitRet":1250},{"lotteryId":"99302","lotteryName":"\\u6c5f\\u897f11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":27,"awardName":"\\u5956\\u91d1\\u7ec41782","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99302","lotteryName":"\\u6c5f\\u897f11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":26,"awardName":"\\u5956\\u91d1\\u7ec41620","directLimitRet":1250,"threeLimitRet":1250},{"lotteryId":"99303","lotteryName":"\\u5e7f\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":29,"awardName":"\\u5956\\u91d1\\u7ec41782","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99303","lotteryName":"\\u5e7f\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":28,"awardName":"\\u5956\\u91d1\\u7ec41620","directLimitRet":1250,"threeLimitRet":1250},{"lotteryId":"99306","lotteryName":"\\u51e4\\u51f0\\u987a\\u522911\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":192,"awardName":"\\u5956\\u91d1\\u7ec41782","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99306","lotteryName":"\\u51e4\\u51f0\\u987a\\u522911\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":191,"awardName":"\\u5956\\u91d1\\u7ec41620","directLimitRet":1250,"threeLimitRet":1250},{"lotteryId":"99401","lotteryName":"\\u53cc\\u8272\\u7403","lotterySeriesCode":5,"lotterySeriesName":"\\u53cc\\u8272\\u7403\\u7cfb","awardGroupId":107,"awardName":"\\u53cc\\u8272\\u7403\\u5956\\u91d1\\u7ec4","directLimitRet":950,"threeLimitRet":950},{"lotteryId":"99501","lotteryName":"\\u6c5f\\u82cf\\u5feb\\u4e09","lotterySeriesCode":6,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":188,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":750,"threeLimitRet":750},{"lotteryId":"99502","lotteryName":"\\u5b89\\u5fbd\\u5feb\\u4e09","lotterySeriesCode":6,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":190,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":750,"threeLimitRet":750},{"lotteryId":"99601","lotteryName":"\\u6c5f\\u82cf\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":189,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":450},{"lotteryId":"99602","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u5a31\\u4e50\\u5385)","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":203,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":450},{"lotteryId":"99604","lotteryName":"\\u5b89\\u5fbd\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":11416087,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":450},{"lotteryId":"99605","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":207,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directLimitRet":450,"threeLimitRet":100},{"lotteryId":"99701","lotteryName":"\\u516d\\u5408\\u5f69","lotterySeriesCode":9,"lotterySeriesName":"\\u516d\\u5408\\u7cfb","awardGroupId":202,"awardName":"\\u516d\\u5408\\u5f69\\u5956\\u91d1\\u7ec4","directLimitRet":1400,"lhcYearLimit":250,"lhcColorLimit":250,"lhcFlatcodeLimit":350,"lhcHalfwaveLimit":250,"lhcOneyearLimit":180,"lhcNotinLimit":250,"lhcContinuein23Limit":250,"lhcContinuein4Limit":450,"lhcContinuein5Limit":400,"lhcContinuenotin23Limit":250,"lhcContinuenotin4Limit":450,"lhcContinuenotin5Limit":450,"lhcContinuecodeLimit":450},{"lotteryId":"99801","lotteryName":"\\u51e4\\u51f0\\u5409\\u52293D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":223,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":450,"threeLimitRet":450},{"lotteryId":"99801","lotteryName":"\\u51e4\\u51f0\\u5409\\u52293D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":224,"awardName":"\\u5956\\u91d1\\u7ec41700","directLimitRet":950,"threeLimitRet":450},{"lotteryId":"99801","lotteryName":"\\u51e4\\u51f0\\u5409\\u52293D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":225,"awardName":"\\u5956\\u91d1\\u7ec41500","directLimitRet":1950,"threeLimitRet":1250},{"lotteryId":"99901","lotteryName":"\\u5feb\\u5f00","lotterySeriesCode":11,"lotterySeriesName":"\\u9ad8\\u9891\\u5f69\\u7cfb","awardGroupId":238,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":950}],"memo":"","setUp":1,"needContact":"N","authenCellphone":"N","showRegisterBtn":"Y","domain":domain_url,"app_id":9,"come_from":"3","appname":"1"}}}
 
        r = requests.post(env+'information/doRetSetting',data=json.dumps(data_),headers=header) #儲存連結反點,生成連結
        print(r.json())
        if r.json()['head']['status'] == 0:
            print('開戶連結創立成功')
            data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"",
            "sessionId":token_[user]},"body":{"param":{"CGISESSID":token_[user],"app_id":"10","come_from":"4",
            "appname":"1"},"pager":{"startNo":"","endNo":""}}}                                                                                     
            
            r = requests.post(env+'information/openLinkList',data=json.dumps(data_),headers=header)#找出開戶連結后的註冊id,回傳註冊 
            #print(r.json())
            result = r.json()['body']['result']['list'][0]
            print(result)
            #print(result)
            global regCode,token,exp,pid
            regCode = result['regCode']#回傳開戶 的 id
            token = result['urlstring'].split('token=')[1]#回傳 開戶 的token
            print(token)
            exp = result['urlstring'].split('exp=')[1].split('&')[0]
            pid = result['urlstring'].split('pid=')[1].split('&')[0]
            print('%s 的 開戶連結'%user)
            print("註冊連結: %s, \n註冊碼: %s, 建置於: %s"%(result['urlstring'],result['regCode'],result['start']))
        else:
            print('創立失敗')
        user_random = random.randint(1,100000)#隨機生成 頁面輸入 用戶名 + 隨機數 的下級
        new_user = user_[0]+str(user_random)
        data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":""},
        "body":{"param":{"token":token,"accountName":new_user,"password":"3bf6add0828ee17c4603563954473c1e",
        "cellphone":"", "qqAccount":"","wechat":"","id":int(regCode),"exp":exp,"pid":int(pid),"qq":'',
        "ip":"192.168.2.18","app_id":"10", "come_from":"4","appname":"1"},"pager":{"startNo":"","endNo":""}}} 
        r = requests.post(env+'user/register',data=json.dumps(data_),headers=header) 
        if r.json()['head']['status'] == 0:
            print('%s 註冊成功'%new_user)
        else:
            print('註冊失敗')
    @staticmethod
    def amount_data(user):
        data = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"",
        "sessionId":token_[user]},"body":{"param":{"amount":10,"CGISESSID":token_[user],"app_id":"9",
        "come_from":"3","appname":"1"},"pager":{"startNo":"","endNo":""}}}
        return data
    @staticmethod
    def balance_data(user):
        data = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"",
        "userAccount":"","sessionId":token_[user]},"body":{"param":{"CGISESSID":token_[user],
        "loginIp":"61.220.138.45","app_id":"9","come_from":"3","appname":"1"},
        "pager":{"startNo":"","endNo":""}}}
        return data
    
    @staticmethod
    @func_time
    def test_AppBalance():
        '''APP 4.0/第三方餘額'''
        threads = []
        user = user_[0]
        data_ = Joy188Test3.balance_data(user)
        third_list = ['gns','sb','im','ky','lc','city']
        print('帳號: %s'%user)
        for third in third_list:
            if third == 'shaba':
                third = 'sb'
            #r = requests.post(env+'/%s/balance'%third,data=json.dumps(data_),headers=header)
            t = threading.Thread(target=Joy188Test.APP_SessionPost,args=(third,'balance',data_))
            threads.append(t)
        t = threading.Thread(target=Joy188Test.APP_SessionPost,args=('information','getBalance',data_))
        threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
            #print(r.json())
            #balance = r.json()['body']['result']['balance']
            #print('%s 的餘額為: %s'%(third,balance))
        '''
        r = requests.post(env+'/information/getBalance',data=json.dumps(data_),headers=header)
        balance =  r.json()['body']['result']['balance']
        print('4.0餘額: %s'%balance)
        '''
    @staticmethod
    @func_time
    def test_ApptransferIn():
        '''APP轉入'''
        user = user_[0]
        data_ = Joy188Test3.amount_data(user)
        print('帳號: %s'%user)
        third_list = ['gns','sb','im','ky','lc','city']
        for third in third_list:
            tran_url = 'Thirdly'# gns規則不同
            if third =='gns':
                tran_url = 'Gns'
            r = requests.post(env+'/%s/transferTo%s'%(third,tran_url),data=json.dumps(data_),headers=header)
            #print(r.json())#列印出來
            status = r.json()['body']['result']['status']
            if status == 'Y':
                print('轉入%s金額 10'%third)
            else:
                print('%s 轉入失敗'%third)
        for third in third_list:
            if third == 'sb':
                third = 'shaba'
            Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=0,third=third,
            user=user)# 先確認資料轉帳傳泰
            count =0
            #print(status_list)
            while status_list[-1] != '2' and count !=16:#確認轉帳狀態,  2為成功 ,最多做10次
                Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=0,third=third,
                user=user)# 
                sleep(0.5)
                count += 1
                if count== 15:
                    print('轉帳狀態失敗')# 如果跑道9次  需確認
                    #pass
            print('%s ,sn 單號: %s'%(third,thirdly_sn[-1]))
        Joy188Test3.test_AppBalance()
    @staticmethod
    @func_time
    def test_ApptransferOut():
        '''APP轉出'''
        user = user_[0]
        data_ = Joy188Test3.amount_data(user)
        print('帳號: %s'%user)
        third_list = ['gns','sb','im','ky','lc','city']
        for third in third_list:# PC 沙巴 是 shaba , iapi 是 sb
            r = requests.post(env+'/%s/transferToFF'%third,data=json.dumps(data_),headers=header)
            #print(r.json())
            status = r.json()['body']['result']['status']
            if status == 'Y':
                print('%s轉出金額 10'%third)
            else:
                print('%s 轉出失敗'%third)
        for third in third_list:
            if third == 'sb':
                third = 'shaba'
            Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=1,third=third,
            user=user)# 先確認資料轉帳傳泰
            count =0
            while status_list[-1] != '2' and count !=16:#確認轉帳狀態,  2為成功 ,最多做10次
                Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=1,third=third,
                user=user)# 
                sleep(1)
                count += 1
                if count== 15:
                    print('轉帳狀態失敗')# 如果跑道9次  需確認
                    
            print('%s, sn 單號: %s'%(third,thirdly_sn[-1]))
        Joy188Test3.test_AppBalance()
    
class Joy188Test2(unittest.TestCase):
    u"瀏覽器功能測試"
    @classmethod
    def setUpClass(cls):
        global dr,user,post_url,em_url,password,user,env
        try:
            cls.dr = webdriver.Chrome()
            dr = cls.dr
            if env_[0] == 'joy188':
                post_url ='http://www2.joy188.com'
                em_url = 'http://em.joy188.com' 
                cls.dr.get(post_url)
                user = user_[0]
                password = 'amberrd'
                env = 1#後面會用到 環境變數 Db查詢用
            elif env_[0] in ['dev02','dev03','fh82dev02']:
                post_url = 'http://www.%s.com'%env_[0]
                em_url = 'http://em.%s.com'%env_[0]
                cls.dr.get(post_url)
                user = user_[0]
                password = '123qwe'
                env = 0
            elif env_[0] == 'maike2020':
                post_url = 'http://www.%s.com'%env_[0]
                em_url = 'http://em.%s.com'%env_[0]
                cls.dr.get(post_url)
                user = user_[0]
                password = 'amberrd'
                env = 1
            print(u'登入環境: %s,登入帳號: %s'%(env_[0],user))
            cls.dr.find_element_by_id('J-user-name').send_keys(user)
            cls.dr.find_element_by_id('J-user-password').send_keys(password)
            cls.dr.find_element_by_id('J-form-submit').click()
            sleep(1)
            if dr.current_url == post_url+'/index':#判斷是否登入成功
                print('%s 登入成功'%user)
            else:
                print('%s登入失敗'%user)
        except NoSuchElementException as e:
            print(e)
    @staticmethod
    def ID(element):
        return  dr.find_element_by_id(element)
    @staticmethod
    def CSS( element):
        return  dr.find_element_by_css_selector(element)
    @staticmethod
    def CLASS( element):
        return  dr.find_element_by_class_name(element)
    @staticmethod
    def XPATH( element):
        return  dr.find_element_by_xpath(element)
    @staticmethod
    def LINK( element):
        return  dr.find_element_by_link_text(element)
    @staticmethod	
    def id_element(element1):#抓取id元素,判斷提示窗
        
        try:
            element = Joy188Test2.CSS("a.btn.closeTip")
            if element.is_displayed():
                Joy188Test2.LINK("关 闭").click()
            else:
                Joy188Test2.ID(element1).click() 
        except WebDriverException as e:
            pass
        except NoSuchElementException as e:
            pass
    @staticmethod	
    def class_element(element1):#抓取id元素,判斷提示窗
        
        try:
            element = Joy188Test2.CSS("a.btn.closeTip")
            if element.is_displayed():
                Joy188Test2.LINK("关 闭").click()
            else:
                Joy188Test2.CLASS(element1).click() 
        except WebDriverException as e:
            print(e)
        except NoSuchElementException as e:
            print(e)
    @staticmethod	
    def css_element(element1):#抓取css元素,判斷提示窗
        try:
            element = Joy188Test2.CSS("a.btn.closeTip")
            if element.is_displayed():
                sleep(3)
                element.click()
                Joy188Test2.CSS(element1).click()
            else:
                Joy188Test2.CSS(element1).click() 
        except WebDriverException as e:
            pass
        except NoSuchElementException as e:
            pass
        except AttributeError:
            pass
    @staticmethod	
    def xpath_element(element1):#抓取xpath元素,判斷提示窗

        try:
            element = Joy188Test2.CSS("a.btn.closeTip")
            if element.is_displayed():
                element.click()
                Joy188Test2.XPATH(element1).click() 
            else:
                Joy188Test2.XPATH(element1).click() 
        except WebDriverException as e:
            pass
        except NoSuchElementException as e:
            pass
    @staticmethod	
    def link_element(element1):#抓取link_text元素,判斷提示窗
        try:
            element = Joy188Test2.CSS("a.btn.closeTip")
            if element.is_displayed():
                element.click()
                Joy188Test2.LINK(element1).click() 
            else:
                Joy188Test2.LINK(element1).click() 
        except WebDriverException as e:
            pass
        except NoSuchElementException as e:
            pass
    #change > ul.play-select-content.clearfix > li.sixing.normal.current > dl.zhixuan > dd.danshi
    @staticmethod
    def normal_type(game):#普通玩法元素
        global game_list,game_list2
        game_list = ['wuxing','sixing','qiansan','zhongsan','housan','qianer','houer','yixing',
                    'super2000','houer_2000.caojiduizhi','yixing_2000.caojiduizhi',
                     'special','longhu.special']
        game_list2 = ['wuxing','sixing','qiansan','zhongsan','housan','qianer','houer','yixing',
                    'special','longhu.special']
        
        '''五星'''
        wuxing_element = ['dd.danshi','dd.zuxuan120','dd.zuxuan60','dd.zuxuan30',"dd.zuxuan20","dd.zuxuan10",
        "dd.zuxuan5","dd.yimabudingwei","dd.ermabudingwei","dd.sanmabudingwei","dd.yifanfengshun",
        "dd.haoshichengshuang","dd.sanxingbaoxi","dd.sijifacai"]
        '''四星'''
        sixing_element=['li.sixing.current > dl.zhixuan > dd.danshi','dd.zuxuan24',
        'dd.zuxuan12','dd.zuxuan6',"dd.zuxuan4","li.sixing.current > dl.budingwei > dd.yimabudingwei"
        ,"li.sixing.current > dl.budingwei > dd.ermabudingwei"]
        '''前三'''
        qiansan_element = ['li.qiansan.current > dl.zhixuan > dd.danshi','dd.hezhi','dd.kuadu',
        'dl.zuxuan > dd.hezhi','dd.zusan','dd.zuliu','dd.hunhezuxuan',
        'dd.baodan','dd.zusandanshi','dd.zuliudanshi',
        'li.qiansan.current > dl.budingwei > dd.yimabudingwei',
        'li.qiansan.current > dl.budingwei > dd.ermabudingwei']
        '''中三'''
        zhongsan_element = ['li.zhongsan.current > dl.zhixuan > dd.danshi',
        'li.zhongsan.current > dl.zhixuan > dd.hezhi',
        'li.zhongsan.current>  dl.zhixuan > dd.kuadu',
        'li.zhongsan.current > dl.zuxuan > dd.hezhi',
        'li.zhongsan.current > dl.zuxuan > dd.zusan',
        'li.zhongsan.current > dl.zuxuan > dd.zuliu',
        'li.zhongsan.current > dl.zuxuan > dd.hunhezuxuan',
        'li.zhongsan.current > dl.zuxuan > dd.baodan',
        'li.zhongsan.current > dl.zuxuan > dd.zusandanshi',
        'li.zhongsan.current > dl.zuxuan > dd.zuliudanshi',
        'li.zhongsan.current > dl.budingwei > dd.yimabudingwei',
        'li.zhongsan.current > dl.budingwei > dd.ermabudingwei']

        '''後三'''
        housan_element = ['li.housan.current > dl.zhixuan > dd.danshi',
        'li.housan.current > dl.zhixuan > dd.hezhi',
        'li.housan.current > dl.zhixuan > dd.kuadu',
        'li.housan.current > dl.zuxuan > dd.hezhi',
        'li.housan.current > dl.zuxuan > dd.zusan',
        'li.housan.current > dl.zuxuan > dd.zuliu',
        'li.housan.current > dl.zuxuan > dd.hunhezuxuan',
        'li.housan.current > dl.zuxuan > dd.baodan',
        'li.housan.current > dl.zuxuan > dd.zusandanshi',
        'li.housan.current > dl.zuxuan > dd.zuliudanshi',
        'li.housan.current > dl.budingwei > dd.yimabudingwei',
        'li.housan.current > dl.budingwei > dd.ermabudingwei']

        '''前二'''
        qianer_element = ['li.qianer.current > dl.zhixuan > dd.danshi',
        'li.qianer.current > dl.zhixuan > dd.hezhi',
        'li.qianer.current > dl.zhixuan > dd.kuadu',
        'li.qianer.current > dl.zuxuan > dd.fushi',
        'li.qianer.current > dl.zuxuan > dd.danshi',
        'li.qianer.current > dl.zuxuan > dd.hezhi',
        'li.qianer.current > dl.zuxuan > dd.baodan']
        '''後二'''
        houer_element = ['li.houer.current > dl.zhixuan > dd.danshi',
        'li.houer.current > dl.zhixuan > dd.hezhi',
        'li.houer.current > dl.zhixuan > dd.kuadu',
        'li.houer.current > dl.zuxuan > dd.fushi',
        'li.houer.current > dl.zuxuan > dd.danshi',
        'li.houer.current > dl.zuxuan > dd.hezhi',
        'li.houer.current > dl.zuxuan > dd.baodan']
        '''後三2000'''
        housan_2000_element = ['li.housan_2000.current > dl.zhixuan > dd.danshi',
        'li.housan_2000.current > dl.zhixualink_elementan > dd.kuadu',
        'li.housan_2000.current > dl.zuxuan > dd.hezhi',
        'li.housan_2000.current > dl.zuxuan > dd.zusan',
        'li.housan_2000.current > dl.zuxuan > dd.zuliu',
        'li.housan_2000.current > dl.zuxuan > dd.hunhezuxuan',
        'li.housan_2000.current > dl.zuxuan > dd.baodan',
        'li.housan_2000.current > dl.zuxuan > dd.zusandanshi',
        'li.housan_2000.current > dl.zuxuan > dd.zuliudanshi',
        'li.housan_2000.current > dl.budingwei > dd.yimabudingwei',
        'li.housan_2000.current > dl.budingwei > dd.ermabudingwei']
        '''後二2000'''
        houer_2000_element = ['li.houer_2000.current > dl.zhixuan > dd.danshi',
        'li.houer_2000.current > dl.zhixuan > dd.hezhi',
        'li.houer_2000.current > dl.zhixuan > dd.kuadu',
        'li.houer_2000.current > dl.zuxuan > dd.fushi',
        'li.houer_2000.current > dl.zuxuan > dd.danshi',
        'li.houer_2000.current > dl.zuxuan > dd.hezhi',
        'li.houer_2000.current > dl.zuxuan > dd.baodan']
        '''趣味大小單雙'''
        special_big_element = ['dd.qianyi','dd.qianer','dd.houyi','dd.houer']
        
        if game == game_list[0]:
            return wuxing_element
        elif game == game_list[1]:
            return sixing_element
        elif game == game_list[2]:
            return qiansan_element
        elif game == game_list[3]:
            return zhongsan_element
        elif game == game_list[4]:
            return housan_element
        elif game == game_list[5]:
            return qianer_element
        elif game == game_list[6]:
            return houer_element
        elif game == game_list[8]:
            return housan_2000_element
        elif game == game_list[9]:
            return houer_2000_element
        elif game == game_list[11]:
            return special_big_element
        else: #一星只有一個玩法
            pass
    @staticmethod
    def game_ssh(type_='0'):#時彩系列  有含 普通玩法,超級2000,趣味玩法, 預設type_ 是有超級2000
        Joy188Test2.normal_type('wuxing')#先呼叫 normal_type方法, 產生game_list 列表
        if type_ == 'no':
            list_type = game_list2
        else:
            list_type = game_list
        for game in list_type:#產生 五星,四星,.....列表 
            if game == 'special':# 要到趣味玩法頁簽, 沒提供 css_element 的定位方法, 使用xpath
                Joy188Test2.xpath_element('//li[@game-mode="special"]')
            else:
                    
                Joy188Test2.css_element('li.%s'%game)
            sleep(2)
            Joy188Test2.id_element('randomone')#進入tab,複式玩法為預設,值接先隨機一住
            if game in ['yixing','yixing_2000.caojiduizhi','longhu.special']:
                pass
            else:
                element_list = Joy188Test2.normal_type(game)#return 元素列表
                for i in element_list: #普通,五星玩法 元素列表
                    Joy188Test2.css_element(i)
                    Joy188Test2.css_element('a#randomone.take-one')#隨機一住
    @staticmethod
    def game_ssh2(type_='0'):#吉利分彩頁面 特殊用法
        Joy188Test2.normal_type('wuxing')#先呼叫 normal_type方法, 產生game_list 列表
        if type_ == 'no':
            list_type = game_list2
        else:
            list_type = game_list
        for game in list_type:#產生 五星,四星,.....列表 
            if game == 'special':# 要到趣味玩法頁簽, 沒提供 css_element 的定位方法, 使用xpath
                Joy188Test2.xpath_element('//li[@game-mode="special"]')
            else:
                    
                Joy188Test2.css_element('li.%s'%game)
            sleep(2)
            Joy188Test2.id_element('randomone')#進入tab,複式玩法為預設,值接先隨機一住
            if game in ['yixing','yixing_2000.caojiduizhi','longhu.special']:
                pass
            else:
                element_list = Joy188Test2.normal_type(game)#return 元素列表
                for i in element_list: #普通,五星玩法 元素列表
                    Joy188Test2.css_element('li.%s'%game)# 差別在這邊,需再點一次頁面元素
                    Joy188Test2.css_element(i)
                    Joy188Test2.css_element('a#randomone.take-one')#隨機一住
    @staticmethod
    def mul_submit():#追號
        Joy188Test2.id_element('randomone')#先隨機一住
        Joy188Test2.id_element('J-trace-switch')#追號

    @staticmethod
    def result():#投注結果
        soup = BeautifulSoup(dr.page_source, 'lxml')
        a = soup.find_all('ul',{'class':'ui-form'})
        for i in range(7):
            for b in a:
                c = b.find_all('li')[i]
                print(c.text)
    @staticmethod
    def result_sl(element1,element2):
        for i in range(5):
            soup = BeautifulSoup(dr.page_source,'lxml')
        a= soup.find_all('ul',{'class':'program-chase-list program-chase-list-body'})
        for a1 in a:
            a11 = a1.find_all('li')[0]
            a12 = a11.find('div',{'class':element1})
            print(element2+a12.text)

    @staticmethod
    def submit(time_=2):# 業面投注按鈕, 和result() func, 再加上業面確認按鈕
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(time_)

    @staticmethod
    def submit_message(lottery):#投注完的單號
        if '成功' in Joy188Test2.CLASS('pop-text').text:
            Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,lottery)
            print("方案編號: %s"%order_code[-1])
        else:
            print('失敗')
    @staticmethod
    def assert_bouns():# 驗證頁面是否有獎金詳情
        '''
        try:
            if '您选择的彩种目前属于休市期间' in Joy188Test2.XPATH("//h4[@class='pop-text']").text:# 休市彈窗
                Joy188Test2.XPATH('/html/body/div[17]/div[1]/i').click()
            if  Joy188Test2.XPATH("//p[@class='text-title']").text == '请选择一个奖金组，便于您投注时使用。' :#獎金詳情彈窗
                Joy188Test2.XPATH("//input[@class='radio']").click()
                Joy188Test2.LINK('确 认').click()
                dr.refresh()
        except NoSuchElementException:
            dr.refresh()
        '''
        pass
    

    @staticmethod
    def test_cqssc():
        u'重慶時彩投注'
        lottery = 'cqssc'
        
        sleep(1)
        dr.get(em_url+'/gameBet/cqssc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        
        '''
        Joy188Test2.game_ssh()#所以玩法投注
        '''
        Joy188Test2.mul_submit()#追號方法
        
        Joy188Test2.submit()
        
        Joy188Test2.submit_message(lottery)
        
    @staticmethod
    def test_hljssc():#黑龍江
        
        lottery = 'hljssc'
        dr.get(em_url+'/gameBet/hljssc')
        print(dr.title)
        sleep(2)
        Joy188Test2.assert_bouns()
        
        '''
        Joy188Test2.game_ssh()
        '''
        Joy188Test2.mul_submit()           
        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_xjssc():
        
        lottery = 'xjssc'
        dr.get(em_url+'/gameBet/xjssc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        
        #Joy188Test2.game_ssh()
        Joy188Test2.mul_submit()#追號方法
                    
        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod    
    def test_fhxjc():
        
        lottery = 'fhxjc'
        dr.get(em_url+'/gameBet/fhxjc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh()

        Joy188Test2.mul_submit()#追號方法            
        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_fhcqc():
        
        lottery ='fhcqc'
        dr.get(em_url+'/gameBet/fhcqc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh()
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_txffc():# 五星完髮不同
        
        lottery = 'txffc'
        dr.get(em_url+'/gameBet/txffc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    
    @staticmethod
    def test_jlffc():# 五星完髮不同
        
        lottery = 'jlffc'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        Joy188Test2.game_ssh2('no')# 
        #Joy188Test2.mul_submit()#追號方法 
        #sleep(1000)
        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_hnffc():# 
        
        lottery = 'hnffc'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        Joy188Test2.game_ssh('no')# 
        #Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_360ffc():# 
        
        lottery = '360ffc'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        Joy188Test2.game_ssh('no')# 
        #Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    
    
    @staticmethod
    def test_shssl():
        lottery = 'shssl'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_sd115():
        lottery = 'sd115'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_jx115():
        lottery = 'jx115'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_gd115():
        lottery = 'gd115'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_sl115():
        lottery = 'sl115'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 

        Joy188Test2.XPATH("//a[@data-param='action=batchSetBall&row=0&bound=all&start=1']").click()#全玩法
        Joy188Test2.ID('J-add-order').click()#添加號碼
        Joy188Test2.ID('J-submit-order').click()#馬上開獎
        sleep(1)
        Joy188Test2.result_sl('cell1','方案編號:')
        Joy188Test2.result_sl('cell2','投注時間:')
        Joy188Test2.result_sl('cell4','投注金額:')

    @staticmethod
    def test_slmmc():
        lottery = 'slmmc'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        while True:
            try:
                for i in range(3):
                    Joy188Test2.XPATH("//a[@data-param='action=batchSetBall&row=%s&bound=all']"%i).click()#全玩法
                break
            except ElementClickInterceptedException:
                dr.refresh()
                break

        Joy188Test2.ID('J-add-order').click()#添加號碼
        Joy188Test2.ID('J-submit-order').click()#馬上開獎
        sleep(1)
        Joy188Test2.result_sl('cell1','方案編號:')
        Joy188Test2.result_sl('cell2','投注時間:')
        Joy188Test2.result_sl('cell4','投注金額:')

        
        
    @staticmethod
    def test_fhjlssc():
        
        lottery = 'fhjlssc'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    
    @staticmethod
    def test_v3d():# 
        
        lottery = 'v3d'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_p5():# 五星完髮不同
        
        lottery = 'p5'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_ssq():# 五星完髮不同
        
        lottery = 'ssq'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_fc3d():# 五星完髮不同
        
        lottery = 'fc3d'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_llssc():
        
        lottery = 'llssc'
        dr.get(em_url+'/gameBet/llssc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法 

        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_btcffc():
        lottery = 'btcffc'
        dr.get(em_url+'/gameBet/btcffc')
        print(dr.title)
        Joy188Test2.assert_bouns()
        #Joy188Test2.game_ssh('no')# 
        Joy188Test2.mul_submit()#追號方法
        Joy188Test2.submit()
        
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_ahk3():
        lottery = 'ahk3'
        dr.get(em_url+'/gameBet/ahk3')
        print(dr.title)
        Joy188Test2.assert_bouns()
        '''
        k3_element = ['li.hezhi.normal','li.santonghaotongxuan.normal','li.santonghaodanxuan.normal',
        'li.sanbutonghao.normal','li.sanlianhaotongxuan.normal','li.ertonghaofuxuan.normal',
        'li.ertonghaodanxuan.normal','li.erbutonghao.normal','li.yibutonghao.normal']
        for i in k3_element:            
            Joy188Test2.css_element(i)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        '''
        Joy188Test2.mul_submit()#追號方法
        Joy188Test2.submit()
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_jsk3():
        lottery = 'jsk3'
        dr.get(em_url+'/gameBet/jsk3')
        print(dr.title)
        Joy188Test2.assert_bouns()
        '''
        k3_element = ['li.hezhi.normal','li.santonghaotongxuan.normal','li.santonghaodanxuan.normal',
        'li.sanbutonghao.normal','li.sanlianhaotongxuan.normal','li.ertonghaofuxuan.normal',
        'li.ertonghaodanxuan.normal','li.erbutonghao.normal','li.yibutonghao.normal']
        for i in k3_element:            
            Joy188Test2.css_element(i)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        '''
        Joy188Test2.mul_submit()#追號方法
        Joy188Test2.submit()
        
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_jsdice():
        lottery = 'jsdice'
        dr.get(em_url+'/gameBet/jsdice')
        print(dr.title)
        Joy188Test2.assert_bouns()
        global sb_element
        # 江蘇骰寶 列表, div 1~ 52
        num = 1
        sb_element = ['//*[@id="J-dice-sheet"]/div[%s]/div'%i for i in range(1,num,1)]#num 控制  要投注多少玩法, 最多 到 53
        
        for i in sb_element:
            sleep(1)
            Joy188Test2.xpath_element(i)
        sleep(0.5)
        Joy188Test2.xpath_element('//*[@id="J-dice-bar"]/div[5]/button[1]')#下注
        Joy188Test2.result()
        Joy188Test2.CSS('a.btn.btn-important').click()#確認
        
        Joy188Test2.submit_message(lottery)
    
    @staticmethod
    def test_jldice():
        
        for lottery in ['jldice1','jldice2']:
            dr.get(em_url+'/gameBet/%s'%lottery)
            print(dr.title)
            Joy188Test2.assert_bouns()
            for i in sb_element:
                if Joy188Test2.ID('diceCup').is_displayed():#吉利骰寶 遇到中間開獎, 讓他休息,在繼續
                    sleep(15)
                else:
                    sleep(1)
                    Joy188Test2.xpath_element(i)
            sleep(0.5)

            if Joy188Test2.ID('diceCup').is_displayed():
                sleep(15)
            else:
                Joy188Test2.xpath_element('//*[@id="J-dice-bar"]/div[5]/a[1]')#下注
                Joy188Test2.result()
                Joy188Test2.XPATH('/html/body/div[14]/a[1]').click()#確認
            Joy188Test2.submit_message(lottery)
                
    @staticmethod
    def test_bjkl8():
        lottery= 'bjkl8'
        dr.get(em_url+'/gameBet/bjkl8')
        print(dr.title)
        Joy188Test2.assert_bouns()
        '''
        bjk_element = ['dd.renxuan%s'%i for i in range(1,8)]#任選1 到 任選7
        Joy188Test2.id_element('randomone')
        sleep(1)
        Joy188Test2.css_element('li.renxuan.normal')
        for element in bjk_element:
            Joy188Test2.css_element(element)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        '''
        
        Joy188Test2.mul_submit()
        Joy188Test2.submit()
        
        Joy188Test2.submit_message(lottery)
    @staticmethod
    def test_pk10():
        lottery= 'pk10'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        for i in range(2):
            Joy188Test2.XPATH("//a[@data-param='action=batchSetBall&row=%s&bound=all&start=1']"%i).click()
        Joy188Test2.ID('J-add-order').click()#選好了
        Joy188Test2.ID('J-trace-switch').click()#追號
        Joy188Test2.submit()
        
        Joy188Test2.submit_message(lottery)
    
    @staticmethod
    def test_xyft():
        lottery= 'xyft'
        dr.get(em_url+'/gameBet/%s'%lottery)
        print(dr.title)
        Joy188Test2.assert_bouns()
        for i in range(2):
            Joy188Test2.XPATH("//a[@data-param='action=batchSetBall&row=%s&bound=all&start=1']"%i).click()
        Joy188Test2.ID('J-add-order').click()#選好了
        Joy188Test2.ID('J-trace-switch').click()#追號
        Joy188Test2.submit()
        
        Joy188Test2.submit_message(lottery)


        
    
    @staticmethod
    def test_safepersonal():
        u"修改登入密碼"
        #print(post_url)
        dr.get(post_url+'/safepersonal/safecodeedit')
        print(dr.title)
        if password =='123qwe':
            new_password = 'amberrd'
        else:
            new_password = '123qwe'
        Joy188Test2.ID( 'J-password').send_keys(password)
        print(u'當前登入密碼: %s'%password)
        Joy188Test2.ID( 'J-password-new').send_keys(new_password)
        Joy188Test2.ID( 'J-password-new2').send_keys(new_password)
        print(u'新登入密碼: %s,確認新密碼: %s'%(new_password,new_password))
        Joy188Test2.ID( 'J-button-submit-text').click()
        sleep(2)
        if Joy188Test2.ID( 'Idivs').is_displayed():#成功修改密碼彈窗出現
            print(u'恭喜%s密码修改成功，请重新登录。'%user)
            Joy188Test2.ID( 'closeTip1').click()#關閉按紐,跳回登入頁
            sleep(1)
            Joy188Test2.ID( 'J-user-name').send_keys(user)
            Joy188Test2.ID( 'J-user-password').send_keys(new_password)
            Joy188Test2.ID( 'J-form-submit').click()
            sleep(1)
            print((dr.current_url))
            if dr.current_url == post_url+'/index':#判斷是否登入成功
                print(u'%s登入成功'%user)
                dr.get(post_url+'/safepersonal/safecodeedit')
                Joy188Test2.ID( 'J-password').send_keys(new_password)#在重新把密碼改回原本的amberrd
                Joy188Test2.ID( 'J-password-new').send_keys(password)
                Joy188Test2.ID( 'J-password-new2').send_keys(password)
                Joy188Test2.ID( 'J-button-submit-text').click()
                sleep(3)
            else:
                print(u'登入失敗')
                pass

        else:
            print(u'密碼輸入錯誤')
            pass
    @staticmethod
    def test_applycenter():
        u'開戶中心/安全中心/綁卡'
        if password == '123qwe':
            safe_pass = 'hsieh123'
        elif password == 'amberrd':
            safe_pass = 'kerr123'
    
        Joy188Test.select_userid(Joy188Test.get_conn(env),user_[0])# 找出用戶 Userid  , 在回傳給開戶連結
        Joy188Test.select_userUrl(Joy188Test.get_conn(env),userid[0])# 找出 開戶連結

        dr.get(post_url+'/register/?%s'%user_url[0])#動待找尋 輸入用戶名的  開戶連結
        print(dr.title)
        print('註冊連結:%s'%user_url[0])
        global user_random
        user_random = random.randint(1,100000)#隨機生成 kerr下面用戶名
        new_user = user_[0]+str(user_random)
        print(u'註冊用戶名: %s'%new_user)
        Joy188Test2.ID('J-input-username').send_keys('%s'%new_user)#用戶名
        Joy188Test2.ID('J-input-password').send_keys(password)#第一次密碼
        Joy188Test2.ID('J-input-password2').send_keys(password)#在一次確認密碼
        Joy188Test2.ID('J-button-submit').click()#提交註冊        
        sleep(5)
        '''
        if dr.current_url == post_url + '/index':
            (u'%s註冊成功'%new_user)
            print(post_url)
            print(u'%s登入成功'%new_user)
        else:
            print(u'登入失敗')
        '''
        #u"安全中心"
        while dr.current_url == post_url+ '/index':
            break

        dr.get(post_url+'/safepersonal/safecodeset')#安全密碼連結
        print(dr.title)
        Joy188Test2.ID('J-safePassword').send_keys(safe_pass)
        Joy188Test2.ID('J-safePassword2').send_keys(safe_pass)
        print(u'設置安全密碼/確認安全密碼: %s'%safe_pass)
        Joy188Test2.ID('J-button-submit').click()
        if dr.current_url == post_url+ '/safepersonal/safecodeset?act=smt':#安全密碼成功Url
            print(u'恭喜%s安全密码设置成功！'%new_user)
        else:
            print(u'安全密碼設置失敗')
        dr.get(post_url+'/safepersonal/safequestset')#安全問題
        print(dr.title)
        for i in range(1,4,1):#J-answrer 1,2,3  
            Joy188Test2.ID('J-answer%s'%i).send_keys('kerr')#問題答案
        for i in range(1,6,2):# i產生  1,3,5 li[i], 問題選擇
            Joy188Test2.XPATH('//*[@id="J-safe-question-select"]/li[%s]/select/option[2]'%i).click()
        Joy188Test2.ID('J-button-submit').click()#設置按鈕
        Joy188Test2.ID('J-safequestion-submit').click()#確認
        if dr.current_url == post_url +'/safepersonal/safequestset?act=smt':#安全問題成功url
            print(u'恭喜%s安全问题设置成功！'%new_user)
        else:
            print(u'安全問題設置失敗')
        #u"銀行卡綁定"
        dr.get(post_url+ '/bindcard/bindcardsecurityinfo/')
        print(dr.title)
        fake = Factory.create()
        card = (fake.credit_card_number(card_type='visa16'))#產生一個16位的假卡號
        
        Joy188Test2.XPATH('//*[@id="bankid"]/option[2]').click()#開戶銀行選擇
        Joy188Test2.XPATH('//*[@id="province"]/option[2]').click()#所在城市  :北京
        Joy188Test2.ID('branchAddr').send_keys(u'內湖分行')#之行名稱
        Joy188Test2.ID('bankAccount').send_keys('kerr')#開戶人
        Joy188Test2.ID('bankNumber').send_keys(str(card))#銀行卡浩
        print(u'綁定銀行卡號: %s'%card)
        Joy188Test2.ID('bankNumber2').send_keys(str(card))#確認銀行卡浩
        Joy188Test2.ID('securityPassword').send_keys(safe_pass)#安全密碼
        Joy188Test2.ID('J-Submit').click()#提交
        sleep(3)
        if Joy188Test2.ID('div_ok').is_displayed():
            print(u'%s银行卡绑定成功！'%new_user)
            Joy188Test2.ID('CloseDiv2').click()#關閉
        else:
            print(u'銀行卡綁定失敗')
        #u"數字貨幣綁卡"
        dr.get(post_url+'/bindcard/bindcarddigitalwallet?bindcardType=2')
        print(dr.title)
        card = random.randint(1000,1000000000)#usdt數字綁卡,隨機生成
        Joy188Test2.ID('walletAddr').send_keys(str(card))
        print(u'提現錢包地址: %s'%card)
        Joy188Test2.ID('securityPassword').send_keys(safe_pass)
        print(u'安全密碼: %s'%safe_pass)
        Joy188Test2.ID('J-Submit').click()#提交
        sleep(3)
        if Joy188Test2.ID('div_ok').is_displayed():#彈窗出現
            print(u'%s数字货币钱包账户绑定成功！'%new_user)
            Joy188Test2.ID('CloseDiv2').click()
        else:
            print(u"數字貨幣綁定失敗")
        
    @classmethod
    def tearDownClass(cls):
        cls.dr.quit()

def suite_test(testcase,username,env,red):
    global msg
    #pc = []
    #app =[]
    #driver =[]
    suite_list = []
    #threads =[]
    lottery_list = ['cqssc','hljssc','xjssc','fhcqc','fhxjc','btcffc','txffc','jlffc','bjkl8','jsdice','ahk3',
    'pk10','xyft','v3d','fc3d','p5','ssq','slmmc','sl115']
    test_list = ['hljssc']
    return_user(username)# 回傳 頁面上 輸入的用戶名
    return_env(env)#回傳環境
    return_red(red)
    try:
        suite = unittest.TestSuite()
        #suite_pc = unittest.TestSuite()
        #suite_app = unittest.TestSuite()
        now = time.strftime('%Y_%m_%d %H-%M-%S')
        #print(len(testcase))
        for i in testcase:
            if i in ['test_PcLogin','test_PcLotterySubmit','test_PcThirdHome','test_PcFFHome',
            'test_PcChart','test_PcThirdBalance','test_PcTransferin','test_PcTransferout','test_PCLotterySubmit',
            'test_redEnvelope']:#PC 案例
                suite_list.append(Joy188Test(i))
            elif i in ['test_AppLogin','test_AppSubmit','test_AppOpenLink','test_AppBalance','test_ApptransferIn','test_ApptransferOut']:#APP案例
                suite_list.append(Joy188Test3(i))
            elif i in ['test_safepersonal','test_applycenter','test_plan']:#瀏覽器案例
                if i == 'test_plan':
                    for lottery in test_list:
                        suite_list.append(Joy188Test2('test_%s'%lottery))
                else:
                    suite_list.append(Joy188Test2(i))

            else:# NONE
                pass
        #print(suite_list)
        
        
        suite.addTests(suite_list)
        print(suite)
        filename_list = ["C:\\python3\\Scripts\\jupyter_test\\templates\\report.html",
        "/opt/QA/python3/jupyter_test/templates/report.html"]#一個本基測試,另一個 07
        filename = filename_list[0]
        global fp
        fp = open(filename, 'wb')
        global runner
        runner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                title=u'測試報告',
                description='環境: %s,帳號: %s'%(env_[0],user_[0]),
                )
        print('start')
        runner.run(suite)
        '''
        if any(pc) and any(app): #兩個列表都有值時,就可以用thread 併發
            suite_pc.addTests(pc)
            t = threading.Thread(target=runner.run,args=(suite_pc,))
            suite_app.addTests(app)
            t1 = threading.Thread(target=runner.run,args=(suite_app,))
            threads.append(t)
            threads.append(t1)
            for i in threads:
                i.start()
                sleep(2)
            for i in threads:
                i.join()
        elif any(pc):
            suite_pc.addTests(pc)
            runner.run(suite_pc)
        elif any(app):
            suite_app.addTests(app)
            runner.run(suite_app)
        '''

        print('end')
        fp.close()
    except TypeError:
        msg = "錯誤"