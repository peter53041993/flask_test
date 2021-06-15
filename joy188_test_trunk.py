#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8


# In[37]:


'''
NOTE : JsonDecoder ERROR : json.decoder.JSONDecodeError: Unexpected UTF-8 BOM

參考:(已解決)
https://speedysense.com/python-fix-json-loads-unexpected-utf-8-bom-error/
'''


# In[2]:


#-*- coding: utf-8 -*-
import HTMLTestRunner,unittest,requests,hashlib,time,random,cx_Oracle,json
from bs4 import BeautifulSoup
import unittest
import datetime
from time import sleep
from selenium import webdriver
from faker import Factory
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException 
import os 
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import MySQLdb
import threading
from collections import defaultdict
import FF_
from queue import Queue


# In[3]:


lottery_dict = FF_.Lottery().lottery_dict
lottery_sh = FF_.Lottery().lottery_sh
lottery_sh2000 =  FF_.Lottery().lottery_sh2000
lottery_3d =  FF_.Lottery().lottery_3d
lottery_115 = FF_.Lottery().lottery_115
lottery_k3 =  FF_.Lottery().lottery_k3
lottery_sb = FF_.Lottery().lottery_sb
lottery_fun = FF_.Lottery().lottery_fun
lottery_noRed = FF_.Lottery().lottery_noRed
third_list = FF_.Third().third_list
env_dict = FF_.Env().env_dict
usdt_dict = FF_.Others().usdt_dict
url_dict  = FF_.Env().url_dict
iapi_url = FF_.Env().iapi_url


# In[4]:


fake = Factory.create()
card = (fake.credit_card_number(card_type='visa16'))#產生一個16位的假卡號
print(card)


# In[42]:


Joy188Test.test_188()


# In[38]:


Joy188Test(case='test_Login').test_Login()


# In[45]:


class Joy188Test(unittest.TestCase):
    u"trunk接口測試"
    '''
    如果要在 unittest的架構下,多傳參數, 必續 先繼承 uniitest 的case
    預設帶一個 登入case, 是為了單純使用 接口 ,不用unittest 話 , 如下
    ex: Joy188Test().test_Login() ,case參數如果不給 ,如下
    ex: Joy188Test(case='test_Login').test_Login() 
    之前寫的staticmethod 完全不影響, 因為完全沒加參數 ,有在案例增加self參數的 才有(test_LotterySubmit 投注)
    '''
    def __init__(self,case='test_Login',account=''):
        self.case = super().__init__(case)
        self.account = account

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
    def admin_login():
        global admin_cookie,admin_url,admin_header,admin_session
        admin_cookie = {}
        admin_dict = {0:'http://admin.dev02.com',1:'http://admin.joy188.com'}
        admin_url = admin_dict[envs] 
        admin_session = requests.Session()
        admin_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36',
                  'Content-Type': 'application/x-www-form-urlencoded'}
        admin_data = {'username':'cancus','password':  pass_list[envs],'bindpwd':123456}
        r = admin_session.post(admin_url+'/admin/login/login',data=admin_data,headers=admin_header)
        decoded_data = r.text.encode().decode('utf-8-sig')
        data = json.loads(decoded_data)
        if data['isSuccess'] == 1:# 這邊如果登入失敗, 正常會爆錯 ,因為沒有 r.json()
            print('後台登入成功')
        else:
            print('後台登入失敗')
        global cookies
        cookies = r.cookies.get_dict()#獲得登入的cookies 字典
        admin_header['ANVOAID'] =  cookies['ANVOAID'] 
    def test_Login(self):
        u"登入測試"
        global user#傳給webdriver方法 當登入用戶參數
        global  pass_list#傳入 werbdriver登入的密碼 
        global post_url#非em開頭
        global em_url#em開頭 
        global userAgent
        global Pc_header
        #global envs#回傳redis 或 sql 環境變數   ,dev :0, 188:1
        global cookies_
        cookies_ = {}
        post_url  = url_dict[envs][0]
        em_url = url_dict[envs][1]
        pass_list = {0: b'123qwe',1:b'amberrd'}
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"             
        Pc_header = {
            'User-Agent': userAgent 
        }
        global session
        while True:
            try:
                if self.account == '':#預設
                    account_ = FF_.Env().trunk_login
                    for e in account_[envs].keys():# e為環境
                        print(e,account_[envs][e][1])#環境和名稱 
                        for user,username in account_[envs][e][0].items():# account_[e] 為環境key 的values , 在loop 找出user名
                            postData = {
                            "username": user,
                            "password": Joy188Test.md(pass_list[envs],b'f4a30481422765de945833d10352ea18'),#密碼和param直
                            "param" :b'f4a30481422765de945833d10352ea18'
                             }
                            session = requests.Session()
                            if envs == 0:# dev 環境
                                login_url = "http://www.%s.com"%e
                            else:
                                login_url = 'http://www2.%s.com'%e
                            r = session.post(  login_url +'/login/login',data = postData,
                                    headers = Pc_header )
                            cookies = r.cookies.get_dict()#獲得登入的cookies 字典
                            cookies_.setdefault(user,cookies['ANVOID'])
                            t = time.strftime('%Y%m%d %H:%M:%S')
                            print('r:', r, type(r))
                            print(u'登錄帳號: %s,登入身分: %s'%(user,username)+u',現在時間:'+t)
                            print(r.text)
                    Joy188Test.admin_login()
                    break
                else:# 跑動帶 指教參數 的account_list 
                    for user in self.account:
                        postData = {
                            "username": user,
                            "password": Joy188Test.md(pass_list[envs],b'f4a30481422765de945833d10352ea18'),#密碼和param直
                            "param" :b'f4a30481422765de945833d10352ea18'
                        }
                        session = requests.Session()
                        r = session.post(  post_url +'/login/login',data = postData,
                                headers = Pc_header )
                        cookies = r.cookies.get_dict()#獲得登入的cookies 字典
                        cookies_.setdefault(user,cookies['ANVOID'])
                        t = time.strftime('%Y%m%d %H:%M:%S')
                        print(u'登錄帳號: %s'%(user)+u',現在時間:'+t)
                        print(r.text)
                    break
            except requests.exceptions.ConnectionError:
                print('please wait!')
                break

            except IOError:
                print('please wait!!!')
                break
    @staticmethod
    def web_issuecode(lottery):#頁面產生  獎期用法,  取代DB連線問題
        global issuecode
        now_time = int(time.time())
        Pc_header['Cookie']= 'ANVOID='+cookies_[env_dict['一般帳號'][envs]]
        try:
            if lottery == 'lhc':
                r = session.get(em_url+'/gameBet/lhc/dynamicConfig?_=%s'%(now_time),headers=Pc_header)
                issuecode = r.json()['data']['issueCode']
            else:
                r = session.get(em_url+'/gameBet/%s/lastNumber?_=%s'%(lottery,now_time),
                                headers=Pc_header)
                issuecode = r.json()['issueCode']
        except :
            print("%s採種沒抓到 獎號"%lottery)

        #print(issuecode)
    
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
    def get_conn(env):#連結數據庫 env 0: dev02 , 1:188
        oracle_ = {'password':['LF64qad32gfecxPOJ603','JKoijh785gfrqaX67854'],
        'ip':['10.13.22.161','10.6.1.41'],'name':['firefog','game']}
        conn = cx_Oracle.connect('firefog',oracle_['password'][env],oracle_['ip'][env]+
        ':1521/'+oracle_['name'][env])
        return conn
    @staticmethod
    def select_issue(conn,lotteryid):#查詢正在銷售的 期號
        #Joy188Test.date_time()
        #today_time = '2019-06-10'#for 預售中 ,抓當天時間來比對,會沒獎期
        try:
            with conn.cursor() as cursor:
                #sql = "select web_issue_code,issue_code from game_issue where lotteryid = '%s' and sysdate between sale_start_time and sale_end_time"%(lotteryid)
                
                # 休市查詢槳期用
                sql = "select web_issue_code,issue_code from game_issue where lotteryid = '%s' and sysdate < sale_end_time"%lotteryid
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
    def select_FundSn(conn,userid):# 找充值單號
        with conn.cursor() as cursor:
            
            sql = "select sn from fund_charge where apply_time >= to_date(trunc(sysdate,'DD'))              and USER_ID = %s order by apply_time desc"%userid
            cursor.execute(sql)
            rows = cursor.fetchall()
            fund_sn = []
            for i in rows:
                fund_sn.append(i[0])
            return fund_sn[0]
    @staticmethod
    def select_WithDrawSn(conn,userid):# 找提現單號
        with conn.cursor() as cursor:
            sql = "select sn from FUND_WITHDRAW where apply_time >= to_date(trunc(sysdate,'DD'))              and USER_ID = %s order by apply_time desc"%userid
            cursor.execute(sql)
            rows = cursor.fetchall()
            withdraw_sn = []
            for i in rows:
                withdraw_sn.append(i[0])
            return withdraw_sn[0]
    @staticmethod
    def select_Lockid(conn,account):# 查詢綁卡鎖定id, 用來 鎖卡用
        with conn.cursor() as cursor:
            sql = "select ID from USER_BANK_LOCKED where user_id = (select id from user_customer             where account = '%s')"%account
            cursor.execute(sql)
            rows = cursor.fetchall()
            lockid = []
            for i in rows:
                lockid.append(i[0])
            return lockid
    @staticmethod
    def select_GroupId(conn,lotteryid,account):#查詢用戶 該彩種的 groupid, APP追號 需要用該參數
        with conn.cursor() as cursor:
            sql = "select sys_award_group_id from user_customer uc inner join             game_award_user_group game             on uc.id = game.userid             where game.lotteryid = %s and uc.account = '%s' and game.bet_type = 1"%(lotteryid,account)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for i in rows:
                return i[0]
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
    def select_OrderCodeTitle(conn,order_code):# 查詢中文 頭注玩法
        with conn.cursor() as cursor:
            sql = "SELECT slip.bet_detail, betttype.group_code_title,             betttype. set_code_title , betttype.method_code_title             FROM game_slip slip INNER JOIN user_customer user_ ON             slip.userid = user_.id INNER JOIN game_bettype_status             betttype ON slip.bet_type_code = betttype.bet_type_code AND             slip.lotteryid = betttype.lotteryid inner join game_order             order_ on slip.orderid = order_.id WHERE             order_.order_code  = '%s'"%order_code
            cursor.execute(sql)
            
            rows = cursor.fetchall()
            order_detail = []
            for i in rows:# i 生成tuple
                order_detail.append(i)
            return order_detail
        conn.close()
 
    '''
    type_ = '' 使用orderid 去找單號, 其它type_ 使用 parentid
    '''
    @staticmethod
    def select_orderCode(conn,id_,type_=''):# 從iapi投注的orderid對應出 order_code 方案編號
        with conn.cursor() as cursor:
            if type_ == '':
                sql = "select order_code from game_order where id in (select orderid from game_slip where orderid = '%s')"%id_
            else:
                sql = "select order_code from game_order where parentid = '%s'"%id_
            
            cursor.execute(sql)
            rows = cursor.fetchall()

            global order_code 
            order_code = []
            for i in rows:# i 生成tuple
                order_code.append(i[0])
        conn.close()
    @staticmethod
    def select_PlanCode(conn,lotteryid='',account='',type_='Pc',planid=''):#找追號單號
        with conn.cursor() as cursor:
            if type_ == 'Pc':
                sql = f"select game_plan.plan_code from game_package  inner join game_plan "                f"on game_package.id = game_plan.PACKAGE_ID "                f"where game_package.userid = (select id from user_customer "                f"where account = '{account}') and game_package.LOTTERYID = {lotteryid} "                f"and game_package.sale_time > to_date(trunc(sysdate,'DD')) "                f"order by game_package.sale_time desc " 
            else:# APP ,用 planid 直接找出來  單號 和 game_packageid 用來抓投注單號 去找 玩法名稱
                sql = "select game_package.id,game_plan.plan_code from game_package                 inner join game_plan on game_package.id = game_plan.PACKAGE_ID                 where  game_plan.id = %s"%planid
                
            cursor.execute(sql)
            rows = cursor.fetchall()
            plan_code = []
            for i in rows:
                plan_code.append(i)
            #conn.close()
            return plan_code
            
        
    @staticmethod
    def select_CancelId(conn,user):# 找撤銷街口 可以撤銷的orderid
        with conn.cursor() as cursor:
            sql = "select g.id,c.lottery_name,g.order_code from game_order g inner join "             "user_customer  u on g.userid = u.id inner join  game_series c on "             f"g.lotteryid = c.lotteryid where u.account = '{user}' and "            "g. order_time > to_date(trunc(sysdate,'DD')) and g.status = 1             order by g.order_time desc"
            #print(sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            order_cancel = defaultdict(list)
            for i in rows:
                order_cancel[i[0]].append(i[1])
                order_cancel[i[0]].append(i[2])
        return order_cancel
        
            
    @staticmethod
    def select_PcOredrCode(conn,user,lottery):#webdriver頁面投注產生定單
        Joy188Test.date_time()#先產生今天日期
        with conn.cursor() as cursor:
            sql = "select order_code from game_order where userid in (select id from user_customer where account = '%s' and order_time > to_date('%s','YYYY-MM-DD')and lotteryid = %s)"%(user,today_time,lottery_dict[lottery][1])
            cursor.execute(sql)
            rows = cursor.fetchall()

            global order_code 
            order_code = []
            for i in rows:# i 生成tuple
                order_code.append(i[0])
        conn.close()
    @staticmethod
    def select_RedBal(conn,user):
        with conn.cursor() as cursor:
            sql = "SELECT bal FROM RED_ENVELOPE WHERE             USER_ID = (SELECT id FROM USER_CUSTOMER WHERE account ='%s')"%user
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
            sql = "SELECT ID FROM RED_ENVELOPE_LIST WHERE status=1 and             USER_ID = (SELECT id FROM USER_CUSTOMER WHERE account ='%s')"%user
            cursor.execute(sql)
            rows = cursor.fetchall()

            global red_id
            red_id = []
            for i in rows:# i 生成tuple
                red_id.append(i[0])
        conn.close()
    @staticmethod
    #查詢轉移用戶 , usr_lvl : 代理等級 , top_account 總代
    def select_tranUser(conn,joint=0,type_=""):
        global new_user
        account_tran = {
            0:[['%hsieh%','hsieh001','hsieh00'],['%hsiehwin%','hsiehwin','hsiehwinnew']],
            1:[['%kerr%','kerr000','kerr00'],['%kerrwin%','kerrwin1940','kerrnewwin']]
        }
        new_user = account_tran[envs][joint][2] # 轉移後的新總待
        with conn.cursor() as cursor:
            if type_ == "":# 預設 
                sql = "select account,user_chain from user_customer where account like  '%s'                 and joint_venture = %s and parent_id = (select id from user_customer where                 account='%s')                 order by register_date desc"%(account_tran[envs][joint][0]
                                              ,joint,account_tran[envs][joint][1])
            else:#  帶 type_ 不等於 "" . 用意 找出  指定一代 ,上級 為kerr00 
                sql = "select account,user_chain from user_customer where account like  '%s'                 and joint_venture = %s and parent_id = (select id from user_customer where                 account = '%s')                 order by register_date desc"%(account_tran[envs][joint][0],joint,
                                              new_user)
            #print(sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            global tran_user,user_chain
            tran_user = []
            user_chain = []

            for i in rows:
                tran_user.append(i[0])
                user_chain.append(i[1])
        conn.close()
    @staticmethod
    def select_tranChainUser(conn,account,account2,joint=0,user_lvl=0):#找尋上級相關用戶 , for代理線轉一代用,不同總代
        with conn.cursor() as cursor:
            sql ="select account from user_customer where user_lvl = %s and account != '%s'            and joint_venture = %s and account like '%s'"%(user_lvl,account,joint,account2)
            #print(sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            global tran_user
            tran_user = []

            for i in rows:
                tran_user.append(i[0])
        conn.close()
    @staticmethod
    def select_tranUserStaut(conn,account):#找尋上級相關用戶 , for代理線轉一代用,不同總代
        with conn.cursor() as cursor:
            sql ="select id,ff_flag from user_chain_transfer_log  where account like '%s' order by id desc"%(account)
            cursor.execute(sql)
            rows = cursor.fetchall()
            global ff_flage
            ff_flage = {}
            #print(rows[0])
            ff_flage[rows[0][0]] = rows[0][1]
        conn.close()
    @staticmethod
    def select_userPass(conn,account):#找尋用戶密碼 ,給APP皆口用
        with conn.cursor() as cursor:
            sql ="select passwd from user_customer where account = '%s'"%account
            cursor.execute(sql)
            #print(sql)
            rows = cursor.fetchall()
            password = []
            #print(rows[0])
            for i in rows:
                password.append(i[0])
            return password
        conn.close()

    @staticmethod    
    def my_con(evn,third):#第三方  mysql連線
        third_dict = {'lc':['lcadmin',['cA28yF#K=yx*RPHC','XyH]#xk76xY6e+bV'],'ff_lc'],
            'ky':['kyadmin',['ALtfN#F7Zj%AxXgs=dT9','kdT4W3#dEug3$pMM#z7q'],'ff_ky'],
            'city':['761cityadmin',['KDpTqUeRH7s-s#D*7]mY','bE%ytPX$5nU3c9#d'],'ff_761city'],
            'im':['imadmin',['D97W#$gdh=b39jZ7Px','nxDe2yt7XyuZ@CcNSE'],'ff_im'],
            'shaba':['sbadmin',['UHRkbvu[2%N=5U*#P3JR','aR8(W294XV5KQ!Zf#"v9'],'ff_sb'],
            'bbin':['bbinadmin','Csyh*P#jB3y}EyLxtg','ff_bbin'],
            'gns':['gnsadmin','Gryd#aCPWCkT$F4pmn','ff_gns'],
            'yb':['ybadmin',['HseSdD2yf!^F32cR3f','aD5cWpMr%BdX#9t7mdBwr$tSjzvM'],'ff_yb'],
            'bg':['bgadmin',['fxWqpKnRm#ArxPhzm','vmFw8N!#hVkAHMdwZY'],'ff_bg'],
            'pg':['pgadmin',['pfW95$XvAYuS#dUntk','zWHvPpekr#rnbV#qwp'],'ff_pg']
             }  

        user_ =  third_dict[third][0]
        db_ = third_dict[third][2]

        if third == 'gns':#gns只有一個 測試環境
            passwd_ = third_dict[third][1]
            ip = '10.6.32.147'
        else:
            if evn == 0:#dev
                ip = '10.13.22.151'
            elif evn == 1:#188
                ip = '10.6.32.147'
            else:
                print('evn 錯誤')
            passwd_ = third_dict[third][1][evn] 
        
        db = MySQLdb.connect(
        host = ip,
        user = user_,
        passwd = passwd_,
        db = db_)
        return db

    @staticmethod
    def thirdly_tran(db,tran_type,third,user):
        cur = db.cursor()
        if  third  == 'gns':
            table_name = 'GNS_TRANSCATION_LOG'
            if tran_type == 0:
                trans_name = 'FIREFROG_TO_GNS'
            else:
                trans_name = 'GNS_TO_FIREFROG'
        else:
            table_name = 'THIRDLY_TRANSCATION_LOG'
            if tran_type == 0:#轉入
                trans_name = 'FIREFROG_TO_THIRDLY'
            else:#轉出
                trans_name = 'THIRDLY_TO_FIREFROG'
        sql ="SELECT SN,STATUS FROM %s WHERE FF_ACCOUNT = '%s'        AND CREATE_DATE > DATE(NOW()) AND TRANS_NAME= '%s'        order by CREATE_DATE desc"%(table_name,user,trans_name)
        #print(sql)
        thirdly_dict = {}#轉帳單號 key 和 狀態
        cur.execute(sql)
        for index,row in enumerate(cur.fetchall()):
            thirdly_dict[index] = list(row)
        cur.close()
        return thirdly_dict

    @staticmethod
    def random_mul(num):#生成random數, NUM參數為範圍
        return(random.randint(1,num))
    
    @staticmethod
    def plan_num(envs,lottery,plan_len):#追號生成
        plan_ = []#存放 多少 長度追號的 list
        Joy188Test.select_issue(Joy188Test.get_conn(envs),lottery_dict[lottery][1])
        for i in range(plan_len):
            plan_.append({"number":issueName[i],"issueCode":issue[i],"multiple":1})
        return plan_
    @staticmethod
    def play_type(lottery,game_type1,game_type2,game_type3):#隨機生成  group .  五星,四星....
        LotterySsh_group = FF_.Lottery().LotterySsh_group
        Lottery115_group = FF_.Lottery().Lottery115_group
        if lottery == 'btcctp':
            game_group = {'chungtienpao':'冲天炮'}
            num = 0
        elif lottery in  lottery_fun:
            game_group = {'guanya':'冠亞','guanyaji': '冠亞季' , 'qiansi':'前四', 'qianwu':'前五'}
            num = 3
        elif lottery in lottery_sh:
            num = len(LotterySsh_group)-1# 減一用意 list keys() 從0 開始 
            '''
            沒有超級2000彩種, 有可能會有 大小單雙/龍虎 (趣味) ex: jlffc,slmmc.....
            '''
            if lottery not in  lottery_sh2000:# 沒有超級2000 彩種
                del LotterySsh_group['housan_2000']
                del LotterySsh_group['houer_2000']
                del LotterySsh_group['yixing_2000']
                num = num -3 
                if lottery == 'ptxffc':
                    del LotterySsh_group['wuxing']
                    num = num - 1
            if lottery in ['jlffc','txffc','ptxffc']:# 騰訊和 奇趣的龍虎格式 和其它龍虎 / 大小單雙 格是不同 (jlffc是有的 但測試 先關閉)
                num = num - 2
                del LotterySsh_group['longhu']
                del LotterySsh_group['daxiaodanshuang']
            if game_type1 == ''and game_type2 =='' and game_type3 =='':# 全部隨機
                play_key1 = list(LotterySsh_group.keys())[random.randint(0,num)]# 隨機生成 LotterySsh_group 的key  五星/四星....
                len_playKey1 = len(LotterySsh_group[play_key1])# 五星 當key, 取得的 value
                play_key2 = list(LotterySsh_group[play_key1].keys())[random.randint(0,len_playKey1-1 )]#wuxing 到時需到  play_key
                len_playKey2 = len(LotterySsh_group[play_key1][play_key2])# 取得五星 某個玩法的長度,ex 五星組選
                play_key3 = LotterySsh_group[play_key1][play_key2 ][random.randint(0,len_playKey2 -1 )]
            elif game_type1 != ''and game_type2 !='' and game_type3 !='':# 全部指定
                play_key1 = game_type1
                play_key2 = game_type2
                play_key3 = game_type3
            elif game_type1 != ''and game_type2 =='' and game_type3 =='':# 五星/四星 指定
                play_key1 = game_type1
                len_playKey1 = len(LotterySsh_group[play_key1])# 五星 當key, 取得的 value
                play_key2 = list(LotterySsh_group[play_key1].keys())[random.randint(0,len_playKey1-1 )]#wuxing
                len_playKey2 = len(LotterySsh_group[play_key1][play_key2])# 取得五星 某個玩法的長度,ex 五星組選
                play_key3 = LotterySsh_group[play_key1][play_key2 ][random.randint(0,len_playKey2 -1 )]
            else:
                if game_type2 == "": #中間隨機
                    play_key3 = game_type3
                    if game_type3 == 'fushi': # 直選/組選  複試
                        if game_type1 == '':# 隨機
                            play_list = ['wuxing','sixing','houer','qianer','zhongsan','qiansan',
                                         'housan','qianer','houer']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_list = ['zhixuan','zuxuan']
                        play_key2 = play_list[random.randint(0,len(play_list)-1)]
                    elif game_type3 == 'kuadu':
                        if game_type1 == '':
                            play_list = ['houer','qianer','zhongsan','qiansan','housan']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_key2 = 'zhixuan'
                    elif game_type3 in ['yimabudingwei','ermabudingwei']:
                        if game_type1 == '': 
                            play_list = ['sixing','zhongsan','qiansan','housan']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_key2 = 'budingwei'
                    elif game_type3 == 'hezhi':# 直選和值 或者組選和值
                        if game_type1 == '': 
                            play_list = ['zhongsan','qiansan','housan','qianer','houer']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_list = ['zhixuan','zuxuan']
                        play_key2 = play_list[random.randint(0,len(play_list)-1)]

                else:# 中間有待 值
                    play_key2 = game_type2
                    if game_type2 == 'budingwei':
                        if game_type1 == '':#沒有待五星/四星 ,就是隨機
                            play_list = ['sixing','zhongsan','qiansan','housan']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_list = LotterySsh_group[play_key1]['budingwei']
                        play_key3 = play_list[random.randint(0,len(play_list)-1)]
                    elif game_type2 == 'zhixuan':#直選
                        if game_type1 == '':
                            play_list = ['wuxing','sixing','houer','qianer','zhongsan','qiansan',
                                             'housan','qianer','houer']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_list = LotterySsh_group[play_key1]['zhixuan']
                        play_key3 = play_list[random.randint(0,len(play_list)-1)]
                    elif game_type2 == 'zuxuan':# 組選
                        if game_type1 == '':
                            play_list = ['wuxing','sixing','qiansan','housan','zhongsan']
                            play_key1 = play_list[random.randint(0,len(play_list)-1)]
                        else:
                            play_key1 = game_type1
                        play_list = LotterySsh_group[play_key1]['zuxuan']
                        play_key3 = play_list[random.randint(0,len(play_list)-1)]
                    elif game_type2 == 'quwei':
                        play_key1 = 'wuxing'
                        play_list = LotterySsh_group['wuxing']['quwei']
                        play_key3 = play_list[random.randint(0,len(play_list)-1)]
            return play_key1,play_key2,play_key3
        elif lottery in lottery_115:# 11選5 玩法全部隨機
            num = len(Lottery115_group)-1
            if 'renxuan' in  game_type2:# 先加入 11 選五 任選系列, 後續再補上其它玩法 
                del Lottery115_group['quwei']# 趣味沒任選
                num = num -1
                play_key1 = list(Lottery115_group.keys())[random.randint(0,num)]# 隨機生成
                if play_key1 in ['xuanyi','xuaner','xuansan']:# 這三個任選,play_type2 不只一個
                    play_key3 = 'renxuanfushi'#只有選1 叫fushi
                    if play_key1 == 'xuanyi':
                        play_key2 = 'renxuanyizhongyi'
                        play_key3 = 'fushi'
                    elif play_key1 == 'xuaner':
                        play_key2 = 'renxuanerzhonger'
                    else:# 選三
                        play_key2 = 'renxuansanzhongsan'
                else:# 剩下的都是 只有一個 play_type2
                    play_key2 = list(Lottery115_group[play_key1].keys())[0]
                    play_key3 = 'fushi'# 都是 叫複試
            else:#全部隨機
                play_key1 = list(Lottery115_group.keys())[random.randint(0,num)]# 隨機生成 Lottery115_group 的key  
                len_playKey1 = len(Lottery115_group[play_key1])# 五星 當key, 取得的 value
                play_key2 = list(Lottery115_group[play_key1].keys())[random.randint(0,len_playKey1-1 )]#wuxing 到時需到  play_key
                len_playKey2 = len(Lottery115_group[play_key1][play_key2])# 取得五星 某個玩法的長度,ex 五星組選
                play_key3 = Lottery115_group[play_key1][play_key2 ][random.randint(0,len_playKey2 -1 )]
            return play_key1,play_key2,play_key3

        else: # 其它彩種走這邊  目前是沒意義 ,會在  game_type 在去定義寫死 玩法.後續補上
            num = len(LotterySsh_group)-1
            game_group = LotterySsh_group# 只是不再 game_type 納編報錯
            #print(lottery)
        play_key = list(game_group.keys())[random.randint(0,num)]
        return play_key,'',''

    # str_ 為 完法後的序列, ex前二 帶五 = 012345, 
    #len_play為 玩法長度, ex前二 帶2 , 
    #cal 為計算 總和,  ex: str帶 012345 = 5
    # play_type 為投注類型,前二, 後二....., game_type 為投注完法 , 組選, 直選....
    @staticmethod
    def return_P(str_,cal_,play_type,game_type):
        import itertools
        new_list = []
        if play_type in ['15','14','48']: #15 前二 14後二 48 後二2000
            len_play = 2
        elif play_type in ['12','13','33','47']:# 12 前三. 13 後三 ,33 中三, 47 後三
            len_play = 3
        elif play_type == '10':#五星
            len_play = 5
        elif play_type == '11':#四星
            len_play = 4
        else:
            return  '投注類型確認'
        if game_type == "11":# 11 組選  
            # 有AB 就不會有 BA元素可重复 
            a = ["".join(tuple_) for tuple_ in [i for i in 
            itertools.combinations_with_replacement(str_,len_play)] ]# 組選key(號碼) 為tuple,需轉乘str ,
            #存redis才不會有問題
        elif game_type == '10':# 10 直選 
            a = [i for i in itertools.product(str_,repeat=len_play)]#所有總類, AB BA 是包含的
        else:
            return '投注玩法確認'

        #[i for i in itertools.product(str_,repeat=len_play)]# itertools.product 直選和值
        #print(a)
        for i in a:
            sum_ = 0
            for b in i:
                sum_ += int(b)
            #print(sum_)
            if game_type == '11':#  組選 要過濾掉 三哥號碼重複的 ex : 222
                if i.count(b) == len_play:
                    sum_ =0
            if sum_ == cal_:
                new_list.append(i)# 加起來為指定數值
        #print(new_list)
        #print('共 %s 注'%len(new_list))# 
        return new_list,len(new_list)
    
    @staticmethod
    def return_randomFushi():
        ball_list = [str(random.randint(0,9)) for i in range(5)]
        ball = "".join(ball_list)
        return ball
    
    @staticmethod
    def random_ball(num,type_=''):# 這個是給list裡面不能重號號碼球的, 比如組選 .type_ = ''預設給 時彩的玩法
        ball = []
        if type_ == '':
            range_ball = [str(i) for i in range(0,10)] #號碼0-9
        elif type_ == '115':#11選5
            range_ball = ['{:02d}'.format(i) for i in range(1,12)]# 格式 01 02  號碼 1-11
        for i in range(num):
            len_range = len(range_ball)
            ball_ = range_ball[random.randint(0,len_range-1)]
            ball.append(ball_)
            range_ball.remove(ball_)
        return ball
    @staticmethod
    def list_Transtr(ball_list):
        a = (",".join(ball_list))
        return a
    @staticmethod
    def ball_type(play_type1, play_type2,play_type3):#對應完法,產生對應最大倍數和 投注完法
        #  (Joy188Test.random_mul(9)) 隨機生成 9以內的數值

        play_num  = 1
        if play_type1 == 'wuxing':
            mul = Joy188Test.random_mul(10)
            if play_type3 == 'fushi':
                ball = [str(Joy188Test.random_mul(9)) for i in range(5)]#五星都是數值
                mul = 1
            elif play_type3 == 'zuxuan120':
                ball = Joy188Test.random_ball(5)
            elif play_type3== 'zuxuan60':
                ball = Joy188Test.random_ball(4)
                ball = ['%s,%s%s%s'%(ball[0],ball[1],ball[2],ball[3])]
            elif play_type3 == 'zuxuan30':
                ball = Joy188Test.random_ball(3)
                ball = ['%s%s,%s'%(ball[0],ball[1],ball[2])]
            elif play_type3 == 'zuxuan20':
                ball = Joy188Test.random_ball(3)
                ball = ['%s,%s%s'%(ball[0],ball[1],ball[2])]
            elif play_type3 in ['zuxuan10','zuxuan5','ermabudingwei']:
                ball = Joy188Test.random_ball(2)
                ball = ['%s,%s'%(ball[0],ball[1])]
            elif play_type3 == 'sanmabudingwei':
                #mul = random.randint(100,1000)
                ball = Joy188Test.random_ball(3)
                ball = ['%s,%s,%s'%(ball[0],ball[1],ball[2])]
            else:
                ball  = [str(Joy188Test.random_mul(9)) ]
        elif play_type1 == 'sixing':
            mul = Joy188Test.random_mul(22)
            if play_type3== 'fushi':
                mul = 1
                ball = ['-' if i ==0  else str(Joy188Test.random_mul(9)) for i in range(5)]#第一個為-
                #ball = ['-' if i ==0  else str(Joy188Test.random_mul(9)) for i in range(5)]#第一個為-
            elif play_type3 == 'zuxuan24':
                ball = Joy188Test.random_ball(4)
            elif play_type3 == 'zuxuan12':
                ball = Joy188Test.random_ball(4)
                ball = ['%s,%s%s'%(ball[0],ball[1],ball[2])]
            elif play_type3 in ['zuxuan6','zuxuan4','ermabudingwei']:
                ball = Joy188Test.random_ball(2)
                ball = ['%s,%s'%(ball[0],ball[1])]
            else:
                #mul = random.randint(100,1000)
                ball = [str(Joy188Test.random_mul(9)) ]
        elif play_type1  in ['housan','housan_2000','qiansan','zhongsan']:
            #mul = Joy188Test.random_mul(22)
            if play_type3 == 'fushi':
                mul = Joy188Test.random_mul(10)
                if play_type1 in ['housan','housan_2000']:
                    ball = ['-' if i in [0,1]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第1和2為-
                elif play_type1  == 'qiansan' :
                    ball = ['-' if i in[3,4]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第4和5為-
                elif play_type1 == 'zhongsan':
                    ball = ['-' if i in[0,4]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第2,3,4為-
            elif play_type3 == 'hezhi':#和值
                play_dict = {'housan': '13', 'qiansan': '12', 'zhongsan': '33',
                'housan_2000': '47'}
                if play_type2== 'zhixuan':# 直選 ,先寫死 ball, 因為直選和值 注數會因為投注內容改變
                    ball = [str(random.randint(0,27)  ) ]
                    gameid = '10'#組選
                else:
                    ball = [str(random.randint(1,26)  ) ]
                    gameid = '11'#直選 
                play_num = Joy188Test.return_P(str_='0123456789',cal_= int(ball[0]) 
                ,play_type= play_dict[play_type1] , game_type = gameid)[1]
            
            elif play_type3 == 'ermabudingwei':
                ball = Joy188Test.random_ball(2)
                ball = ['%s,%s'%(ball[0],ball[1])]
                #mul = Joy188Test.random_mul(1000)
            elif play_type3 == 'zuliu':
                ball = Joy188Test.random_ball(3)
                ball = ['%s,%s,%s'%(ball[0],ball[1],ball[2])]
            elif play_type3 == 'zusan':
                play_num = 2
                ball = Joy188Test.random_ball(2)
                ball = ['%s,%s'%(ball[0],ball[1])]
            elif play_type3 == 'kuadu':
                ball =['0']
                play_num = 10
            else:
                ball = [str(Joy188Test.random_mul(9)) ]
                if play_type3 == 'baodan':
                    play_num = 54
            mul = Joy188Test.random_mul(10)
        elif play_type1 in ['houer','houer_2000','qianer']:
            if play_type3 == 'fushi':
                mul = Joy188Test.random_mul(10)
                if play_type2 == 'zhixuan':# 直選
                    if play_type1 in ['houer','houer_2000']:
                        ball = ['-' if i in [0,1,2]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第1,2,3為-
                    elif play_type1 == 'qianer':
                        ball = ['-' if i in [2,3,4]  else str(Joy188Test.random_mul(9)) for i in range(5)]#第3,4,5為-
                else:# 組選
                    ball = Joy188Test.random_ball(2)
                    ball = ['%s,%s'%(ball[0],ball[1])]
            elif play_type3== 'hezhi':
                play_dict = {'qianer': '15', 'houer': '14', 'houer_2000': '48'}
                if play_type2 == 'zhixuan':# 直選
                    ball = [ str(random.randint(0,18))]
                    gameid = '10'#組選
                else:
                    ball = [ str(random.randint(1,17))]
                    gameid = '11'#組選
                play_num = Joy188Test.return_P(str_='0123456789',cal_= int(ball[0] ) ,
                        play_type= play_dict[play_type1] ,
                         game_type = gameid)[1]
            elif play_type3== 'kuadu':
                ball =['0']
                play_num = 10
            else:
                if play_type3 == 'baodan':
                    play_num = 9
                ball = [str(Joy188Test.random_mul(9)) ]
            mul = Joy188Test.random_mul(10)
        elif play_type1 in ['yixing','yixing_2000']:# 五個號碼,只有一個隨機數值
            ran = Joy188Test.random_mul(4)
            ball = ['-' if i !=ran else str(Joy188Test.random_mul(9)) for i in range(5)]
            mul = Joy188Test.random_mul(50)
        elif play_type1 == 'longhu':#龍虎
            mul = random.randint(1,5)
            longhu_list = ['龙','虎','和']
            ran = random.randint(0,9)
            ball = [longhu_list[random.randint(0,2)] if i ==ran else '-' for i in range(10)]
        elif play_type1 == 'daxiaodanshuang':#大小單雙
            dax_list = ['小','大','单','双']
            mul = Joy188Test.random_mul(5)
            if play_type3 in ['qianer','houer']: #這兩個 一注 需產兩個 號碼
                ball = [ dax_list[random.randint(0,3)] for i in range(2)]
            else:# 產出一個即可
                ball = [dax_list[random.randint(0,3)]]
        elif play_type1 == 'chungtienpao':#快開
            ball = [str(round(random.uniform(1.01,2),2))]
            mul = Joy188Test.random_mul(1)
        elif play_type1== "guanya":#冠亞
            range_ball = [i for i in range(1,11)]
            ball = ['-' if i not in [0,1]  else '0%s'%range_ball[i] for i in range(10)]
            mul = Joy188Test.random_mul(10)
        elif play_type1== 'guanyaji':#冠亞季
            range_ball = [i for i in range(1,11)]
            ball = ['-' if i not in [0,1,2]  else '0%s'%range_ball[i]  for i in range(10)]
            mul = Joy188Test.random_mul(10)
        elif play_type1 == 'qiansi':# lottery_fun
            ball = ["07 08 09 10,09 10,10,08 09 10,-,-,-,-,-,-"]
            mul = Joy188Test.random_mul(10)
        elif play_type1 == 'qianwu':# lottery_fun
            ball = ["07 08 09 10,07 08 10,07 10,10,06 07 08 09 10,-,-,-,-,-"]
            mul = Joy188Test.random_mul(10)
        elif 'renxuan' in play_type2:# 任選系列, 11 選 5
            mul = Joy188Test.random_mul(15)
            ran_dict = { 'xuanyi': 1,'xuaner':2 ,'xuansan':3,'xuansi':4,'xuanwu':5,'xuanliu':6,
            'xuanqi':7,'xuanba':8}#用來知道要產出多少個隨機 號碼
            ball = Joy188Test.random_ball(ran_dict[play_type1],type_='115')
        else:
             mul = Joy188Test.random_mul(1)
        
        
        a = Joy188Test.list_Transtr(ball)
        #global Joy188Test.ball_value
        #print(ball)

        return a,play_num, mul
    @staticmethod
    def game_type(lottery,game_type1='',game_type2='' ,game_type3='' ):
        
        if lottery in lottery_115:
            game_type2 = 'renxuan'
        group_ = Joy188Test.play_type(lottery,game_type1,game_type2,game_type3)# group_ 決定 改採種要投注什麼玩法 ,ex: wuxing.zhixuan.fushi
        #print(group_[0])
        lottery_ball = Joy188Test.ball_type(play_type1=group_[0],
        play_type2=group_[1],play_type3=group_[2])# 投注號碼球 邏輯

        test_dicts = {   
        0 : ["%s.zhixuan.fushi"%(group_,),lottery_ball] , 
        1 : ["qianer.zhixuan.zhixuanfushi",'3,6,-'],
        2 : ["%s.%s.%s"%(group_[0],group_[1],group_[2]),lottery_ball[0]] ,# 11選5
        3 : ["sanbutonghao.biaozhun.biaozhuntouzhu","1,2,6"],
        4 : ["santonghaotongxuan.santonghaotongxuan.santonghaotongxuan","111 222 333 444 555 666"],
        5 : ["%s.zhixuan.fushi"%(group_[0],),lottery_ball[0]],
        6 : ['qianer.zuxuan.fushi','4,8'],
        7 : ["biaozhuntouzhu.biaozhun.fushi","04,08,13,19,24,27+09",],
        8 : ["zhengma.pingma.zhixuanliuma","04"],
        9 : ["p3sanxing.zhixuan.p3fushi","9,1,0",],
        10: ["renxuan.putongwanfa.renxuan7","09,13,16,30,57,59,71"],   
        11: ["%s.chungtienpao.chungtienpao"%(group_[0],),lottery_ball[0]],#快開
        12: ["zhenghe.hezhi.hezhi","3"],#pc蛋蛋,
        13: ["%s.%s.%s"%(group_[0],group_[1],group_[2]),lottery_ball[0]]  
        }
        play_num = 1
        if lottery in lottery_sh:
            num = 13# 新測試
            play_num = lottery_ball[1]
            mul = lottery_ball[2]
           
        elif lottery in lottery_3d:
            num = 1
        elif lottery in lottery_noRed:
            if lottery in ['p5','np3']:
                num = 9
            else:
                num = 1
        elif lottery in lottery_115:
            num = 2
            play_num = lottery_ball[1]
        elif lottery in lottery_k3:
            num = 3
        elif lottery in lottery_sb:
            num = 4
        elif lottery in lottery_fun:
            num = 5
        elif lottery == 'shssl':
            num = 6
            play_num = lottery_ball[1]
        elif lottery ==  'ssq':
            num = 7
        elif lottery == 'lhc':
            num = 8
        elif lottery in ['bjkl8','fckl8']:
            num = 10
        elif lottery == 'pcdd':
            num = 12
        else:
            num = 11
        return test_dicts[num][0],test_dicts[num][1],play_num
    @staticmethod
    def req_post_submit(account,lottery,data_,moneyunit,awardmode,plan, plan_type=''):
        awardmode_dict = {0:u"非一般模式",1:u"非高獎金模式",2:u"高獎金"}
        money_dict = {1:u"元模式",0.1:u"分模式",0.01:u"角模式"}
        Pc_header['Cookie']= 'ANVOID='+ cookies_[account]
        #Pc_header['Cookie']= 'ANVOID='+ FF_().cookies[account]
    

        r = session.post(em_url+'/gameBet/'+lottery+'/submit', 
        data = json.dumps(data_),headers=Pc_header)

        global content_ 
        lottery_name= u'投注彩種: %s'%lottery_dict[lottery][0]  
        try:
            msg = (r.json()['msg'])
            orderid = (r.json()['data']['orderId'])#用來 到時撤銷接口使用
            mode = money_dict[moneyunit]
            mode1 = awardmode_dict[awardmode]
            project_id = (r.json()['data']['projectId'])#訂單號
            submit_amount = (r.json()['data']['totalprice'])#投注金額
            #submit_mul = u"投注倍數: %s"%m#隨機倍數     
            #print(r.json()['isSuccess'])

            if r.json()['isSuccess'] == 0:#
                #select_issue(get_conn(envs),lottery_dict[lottery][1])#呼叫目前正在販售的獎期
                content_ = (lottery_name+"\n"+ mul_+ "\n" +"\n"+ msg+"\n")

                if r.json()['msg'] == u'存在封锁变价':#有可能封鎖變價,先跳過   ()
                    print(r.json()['msg'])
                elif r.json()['msg'] == u'您的投注内容 超出倍数限制，请调整！':
                    #print(u'倍數超出了唷,下次再來')
                    pass # 因為 超出被數 已經 在msg 裡.不用重複 顯示
                elif  r.json()['msg']==u'方案提交失败，请检查网络并重新提交！':

                    print (data_) 
                    #print(r.json()['msg'])

                else:#可能剛好 db抓到獎期剛好截止
                    #Joy188Test.select_issue(Joy188Test.get_conn(1),lottery_dict[lottery][1])
                    Joy188Test.web_issuecode(lottery)#抓獎其
                    plan_ = [{"number":"123","issueCode":issuecode,"multiple":1}]
                    data_['orders'] = plan_

                    r = session.post(em_url+'/gameBet/'+lottery+'/submit', 
                    data = json.dumps(data_),headers=Pc_header)
            else:#投注成功
                play_ = Joy188Test.select_OrderCodeTitle(Joy188Test.get_conn(envs),project_id)
                #print(play_)
                play_1 = "投注內容: %s"%play_[0][0]
                play_2 = "投注玩法: %s.%s.%s"%(play_[0][1],play_[0][2],play_[0][3])
                if plan > 1:# 追號

                    print(u'追號, 期數:%s'%plan)
                    if plan_type == 0:
                        print('追中不停')
                    else:
                        print('追中即停')
                    plan_code = Joy188Test.select_PlanCode(conn=Joy188Test.get_conn(envs),
                                lotteryid=lottery_dict[lottery][1],account=account)
                    #print(plan_code)
                    content_ = (lottery_name+"\n"+u'追號單號: '+plan_code[0][0]+"\n"
                                +mul_+ "\n"+play_1+"\n"
                                +play_2+"\n"+u"投注金額: "+ str(float(submit_amount*0.0001*plan))+"\n"
                                +mode+"/"+mode1+"\n"+msg+"\n")
                else:
                    content_ = (lottery_name+"\n"+u'投注單號: '+project_id+"\n"
                                +mul_+ "\n" 
                                +play_1+"\n"
                                +play_2+"\n"+u"投注金額: "+ str(float(submit_amount*0.0001))+"\n"
                                +mode+"/"+mode1+"\n"+msg+"\n")
                #order_dict[lottery]  = {project_id: orderid}# 存放, 後續 掣單使用
        except:
            content_ = lottery_name + "失敗"
        print(content_)
    @staticmethod
    #@jit_func_time
    def test_Submit(account,moneyunit,plan ):#彩種投注,plan_type 0 不停, 1中級停
        print('投注帳號: %s'%account)
        for i in lottery_dict.keys(): 
        #for i in lottery_115:
        #for i in ['jlffc','ptxffc','hnffc','cqssc','xjssc','hljssc','slmmc']:
        #for i in lottery_sh:
            while True:
                try:
                    
                    global mul_ #傳回 投注出去的組合訊息 req_post_submit 的 content裡
                    global mul
                    #ball_type_post = Joy188Test.game_type(i)# 找尋彩種後, 找到Mapping後的 玩法後內容
                    if i in ['btcctp','btcffc','xyft','xyft168','pcdd']:# 只開放開獎金彩種
                        awardmode = 2
                        mul = Joy188Test.random_mul(10)
                        if i == 'btcctp':#快開
                            mul = Joy188Test.random_mul(1)#不支援倍數,所以random參數為1
                        elif i == 'pcdd':
                            if account ==  'hsiehwin1940test':
                                odds = 97.5
                            elif account == 'kerrwin1940test':
                                odds = 95
                            else:
                                awardmode = 1
                                odds = 90
                    elif  i == 'super2000':
                        break
                    else:
                        mul = Joy188Test.random_mul(5)
                        awardmode = 1
                      
                    ball_type_post = Joy188Test.game_type(i)
                    play_num = ball_type_post[2]
                    mul_ = (u'選擇倍數: %s'%mul)
                    amount = 2*mul*moneyunit

                    if plan == 1   :# 一般投住
                        Joy188Test.web_issuecode(i)#抓獎其
                        plan_ = [{"number":'123',"issueCode":issuecode,"multiple":1}]
                        print(u'一般投住')
                        isTrace=0
                        traceWinStop=0
                        traceStopValue=-1
                        plan_type = ""# 一般不需要
                    else: #追號
                        if i in ['slmmc','sl115','jsdice','jldice1','jldice2','btcctp','lhc']:
                            print("彩種: %s 沒開放追號"%lottery_dict[i][0]+"\n")
                            break
                        plan_ = Joy188Test.plan_num(envs,i,random.randint(2,plan))#隨機生成 50期內的比數 

                        #plan_  = Joy188Test.plan_num(envs,i,plan)
                        isTrace=1
                        plan_type = random.randint(0,1)
                         
                        traceWinStop= plan_type
                        traceStopValue=1
                    len_ = len(plan_)# 一般投注, 長度為1, 追號長度為
                    post_data = {"gameType":i,"isTrace":isTrace,"traceWinStop":traceWinStop,
                    "traceStopValue":traceWinStop,
                    "balls":[{"id":1,"ball":ball_type_post[1],"type":ball_type_post[0],
                    "moneyunit":moneyunit,"multiple":mul,"awardMode":awardmode,
                    "num":1}],"orders": plan_,"redDiscountAmount": 0 ,"amount" : len_*amount}

                    global post_noRed
                    post_noRed = {"gameType":i,"isTrace":isTrace,"traceWinStop":traceWinStop,
                    "traceStopValue":traceWinStop,
                    "balls":[{"id":1,"ball":ball_type_post[1],"type":ball_type_post[0],
                    "moneyunit":moneyunit,"multiple":mul,"awardMode":awardmode,
                    "num":play_num}],"orders": plan_ ,"amount" : len_*amount*play_num}

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
                    
                    if account ==  'hsiehwin1940test':
                        odds = 97.5
                    elif account == 'kerrwin1940test':
                        odds = 95
                    else:
                        odds = 90 
                    post_data_pcdd = {"balls":[{"id":1,"moneyunit":1,"multiple":1,"num":1,
                    "type":"zhenghe.hezhi.hezhi","amount":50,"ball":"3","odds":odds,"awardMode":awardmode}],
                    "orders":plan_,
                    "redDiscountAmount":0,"amount":50*len_,"isTrace":isTrace,
                    "traceWinStop":traceWinStop,"traceStopValue":traceStopValue}
                    
                    
                    if i == 'lhc':
                        Joy188Test.req_post_submit(account,'lhc',post_data_lhc,moneyunit,awardmode,len_)
                    elif i == 'pcdd':
                        Joy188Test.req_post_submit(account,'pcdd',post_data_pcdd,moneyunit,awardmode,
                                                   len_)
                    elif i in lottery_sb:
                        Joy188Test.req_post_submit(account,i,post_data_sb,moneyunit,awardmode,len_) 
                    else:
                        Joy188Test.req_post_submit(account,i,post_noRed,moneyunit,awardmode,len_,plan_type)
                    break
                except IndexError as e :
                    #print(e)
                    print("彩種: %s 投注失敗"%lottery_dict[i][0]+"\n")
                    break
    def test_LotterySubmit(self):
        u"投注測試"
        Joy188Test.test_Submit(account=self.account,plan=1,moneyunit=1)#env_dict['一般帳號'][envs],moneyunit=1,))#
    @staticmethod
    def test_LotteryPlanSubmit():
        u"追號測試"
        Joy188Test.test_Submit(account=env_dict['合營1940'][envs],plan=10,moneyunit=1)
            #plan=10)#plan= random.randint(2,plan)
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
            print(third)
            print(u'連線有問題,請稍等')
    @staticmethod
    def session_post(user,third,url,post_data,q='',em_=''):#共用 session post方式 (Pc)
        Pc_header['Cookie']= 'ANVOID='+cookies_[user]
        try:
            if em_ != '':
                url_type = em_url# em開頭
            else:
                url_type = post_url#預設 使用 post_url , www 開頭
            r = session.post(url_type+url,headers= Pc_header,data=json.dumps(post_data))

            if 'Balance' in url:
                print('%s, 餘額: %s'%(third,r.json()['balance']))
            elif 'transfer' in url:
                if r.json()['status'] == True:
                    print('帳號 %s 轉入 %s ,金額:1, 進行中'%(user,third))
                else:
                    print('%s 轉帳失敗'%third)
            elif 'getuserbal' in url:
                print('4.0 餘額: %s'%r.json()['data'])
            else:
                q.put(r)
            #print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
            #print('result: '+statu_code+"\n"+'---------------------')

        except requests.exceptions.ConnectionError:
            print(third)
            print(u'連線有問題,請稍等')
    @staticmethod
    def session_get(url_,url,type_='',q=''):#共用 session get方式,type不帶 '' ,列出內容 ,q queue
        Pc_header['Cookie']= 'ANVOID='+cookies_[env_dict['一般帳號'][envs]]
        try:
            r = session.get(url_+url,headers=Pc_header)
            if type_ != '':# 給走勢圖 多增加 print  內容
                q.put(r)
                '''
                print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
                print(url)
                print('回覆內容: ')
                print(r.json()['data'])
                print('---------------------')
                '''
            else:
                html = BeautifulSoup(r.text,'lxml')# type為 bs4類型
                title = str(html.title)
                statu_code = str(r.status_code)#int 轉  str
                print(title)#強制便 unicode, 不燃顯示在html報告  會有誤
                print(url)
                print('result: '+statu_code+"\n"+'---------------------')


        except requests.exceptions.ConnectionError:
            print(title)
            print(u'連線有問題,請稍等')
    
    @staticmethod
    def test_ThirdHome():#登入第三方頁面,創立帳號
        u"第三方頁面測試"
        threads = []
        for i in third_list:
            url = '/%s/home'%i
            if i == 'shaba':#沙巴特立
                url = url+'?act=esports'
            #print(url)
            t = threading.Thread(target=Joy188Test.session_get,args=(post_url,url))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
    @staticmethod
    def test_188():
        u"4.0頁面測試"
        threads = []
        q = Queue()
        timeStamp = int(time.time()*1000)#時間戳
        now = datetime.datetime.now()
        now_start = '%s-%s-1'%(now.year,now.month)# 當月 1 號
        now_date = '%s-%s-%s'%(now.year,now.month,now.day)
        user =  env_dict['一般帳號'][envs]
        userid = {'hsieh001': '1341294', 'kerr001': '1373224'}

        view_page = {'/activity_system/?controller=activity&action=getnewestlist&siteId=1&userId=%s&_=%s'%(userid[user],timeStamp): '活動商城','/frontCheckIn/doCheckInByUserId': ['簽到',{},''], 
        '/proxy/loadchartdata?timestart={now_start}&timeend={now_date}&model=lottery&type=bet&plat=%20&_={timeStamp}'.format(now_start=now_start,now_date=now_date,timeStamp=timeStamp): '舊代理彩種', '/proxy/loadchartdata?timestart={now_start}&timeend={now_date}&model=thirdly&type=bet&plat=%20&_={timeStamp}'.format(timeStamp=timeStamp,now_date=now_date,now_start=now_start): '舊代理三方', '/agentcenter/getallcalagentdata': ['新代理',{"starDate":"{now_start} 00:00:00".format(now_start=now_start),"endDate":"{now_date} 23:59:59".format(now_date=now_date)},'']
        }
        for view_key in view_page.keys():
            if any(post_func in view_key for post_func in ['frontCheckIn','getallcalagentdata']  ): #post
                post_data = view_page[view_key][1]
                url_type = view_page[view_key][2]
                t = threading.Thread(target=Joy188Test.session_post,args=(user,
                '',view_key,post_data,q,url_type))# view_page[view_key][1]  為data
            else: #GET
                t = threading.Thread(target=Joy188Test.session_get,args=(post_url,
                view_key,'v',q))
            threads.append(t)

        for i in threads:
            i.start()
        for i in threads:
            i.join()
        que_result = []# 取得queue裡的值
        for _ in range(len(threads)):
            que_result.append(q.get())
        for response in que_result:
            response_url = response.url
            try:
                decoded_data = response.text.encode().decode('utf-8-sig')
                data = json.loads(decoded_data)
                r_json = data
            except:
                print('%s  有錯誤'%response_url)
            print(response_url)
            if 'activity_system' in response_url:
                print('活动商城 api')
                len_data = len(r_json['data'])
                print('回復訊息: '+"\n")
                print(r_json['data'][random.randint(0,len_data-1)])
            elif 'frontCheckIn' in response_url:
                print('簽到 api')
                print('用戶名: %s'%user)
                print('回復訊息: %s'%r_json['message'])
                print('回復狀態: %s'%r_json['isSuccess'])
            elif 'proxy' in response_url:
                if 'lottery' in response_url:
                    msg = '彩種'
                else:
                    msg = '三方'
                print('舊代理中心%s api'%msg)
                try:
                    bet = r_json['total']['bet']
                    profit = r_json['total']['profit']
                    win = r_json['total']['win']
                except TypeError:# 有可能沒資料 會造成抱錯
                    bet = 0
                    profit = 0
                    win = 0
                print('用戶名: %s'%user)
                print('查詢時間 ,本月: %s-%s'%(now_start,now_date))
                print('回復訊息: '+"\n")
                print('投注: %s'%bet)
                print('盈虧: %s'%profit)
                print('中獎金額: %s'%win)
            elif 'getallcalagentdata' in response_url:
                print('新代理中心 api')
                bet = r_json['caldata']['allCalData']['bet']
                win = r_json['caldata']['allCalData']['win']
                profit = r_json['caldata']['allCalData']['profit']
                teamCount = r_json['countdata']['teamCount']
                print('用戶名: %s'%user)
                print('查詢時間 ,本月: %s-%s'%(now_start,now_date))
                print('回復訊息: '+"\n")
                print('投注: %s'%bet)
                print('輸贏: %s'%profit)
                print('中獎金額: %s'%win)
                print('團隊用戶: %s'%teamCount)



            print('---------------------')
    @staticmethod
    def test_chart():
        u"走勢圖測試"
        threads = []
        q = Queue()
        lottery_chart = {'d3':'Qiansan','v3d':'Qiansan','shssl': 'Housan','lottery_sh': 'Wuxing',
            'lottery_115': 'Wuxing', 'lottery_k3': 'chart', 'lottery_fun':
            'CaipaiweiQianfushi', 'fckl8': 'Quwei','p5':'p5chart', 'ssq':'ssq_basic'}
        while True:
            for i in lottery_dict:
                if i in lottery_sh:
                    if i == 'fhjlssc':
                        i = 'cqssc'# 只有鳳凰吉利時彩 特殊
                    chart_lottery = 'lottery_sh'
                elif i == 'fc3d':
                    i = 'd3'
                    chart_lottery = i
                elif i in lottery_115:
                    chart_lottery = 'lottery_115'
                elif i in lottery_k3 or i in  lottery_sb:
                    chart_lottery = 'lottery_k3'
                elif i in lottery_fun:
                    chart_lottery = 'lottery_fun'
                elif i in ['bjkl8','fckl8']:
                    chart_lottery = 'fckl8'
                else:
                    chart_lottery = i
                    if i  == 'lhc':
                        print('六合彩無走勢')
                        print('---------------------')
                        break
                chart_url = '/game/chart/%s/%s/data?periodsType=periods&gameType=%s&gameMethod=%s&periodsNum=1'%(i,lottery_chart[chart_lottery],i,lottery_chart[chart_lottery])
                t1 = threading.Thread(target=Joy188Test.session_get,args=(em_url,chart_url,'content',q))
                threads.append(t1)
            for i in threads:
                i.start()
            for i in threads:
                i.join()
            que_result = []# 取得queue裡的值
            for _ in range(len(threads)):
                que_result.append(q.get())
            for response in que_result:
                r_json = response.json()
                #print(r_json)
                try:
                    print('彩種: %s'%lottery_dict[ r_json['lotteryCode'] ][0] )
                    print('狀態: %s'%r_json['isSuccess'])
                    print('資料: '+"\n")
                    print(r_json['data'])
                    print('---------------------')
                except KeyError:# fc3d 和 d3 會有keyerror發生 lottery_dict 原因
                    print('彩種: %s'%r_json['lotteryCode'] )
                    print('狀態: %s'%r_json['isSuccess'])
                    print('資料: '+"\n")
                    print(r_json['data'])
                    print('---------------------')

            break
    @staticmethod
    def test_thirdBalance():
        '''4.0/第三方餘額'''
        threads = []
        user = env_dict['轉入/轉出'][envs]
    
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
    @staticmethod
    def test_transferin():#第三方轉入
        '''第三方轉入'''
        user = env_dict['轉入/轉出'][envs]
        Pc_header['Cookie']= 'ANVOID='+cookies_[user]
        Pc_header['Content-Type'] = 'application/json; application/json; charset=UTF-8' 
        statu_list = []
        post_data = {"amount":1}
        for third in third_list:
            if third == 'gns':
                url = '/gns/transferToGns'

            else:
                url = '/%s/transferToThirdly'%third
            r = session.post(post_url+url,data=json.dumps(post_data),headers= Pc_header)
            if r.json()['status'] == True:
                print('帳號: %s 轉入 %s ,金額:1, 進行中'%(user,third))
                statu_list.append(third)
            else:
                print('%s轉帳接口失敗, api回復訊息: %s'%(third,r.json()['errorMsg']))
        print('--------------------------------------------')
        for third in statu_list:
            thirdly_status = Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=0,
            third=third,user=user)# 先確認資料轉帳傳泰
            staut_mapping = thirdly_status[0][1]
            msg = '%s 轉帳單號: %s . '%(third,thirdly_status[0][0])
            if staut_mapping == '2':
                msg = msg +" 狀態成功"
            else:
                msg = msg +" 狀態待確認"
            sleep(3)
            print(msg)
        Joy188Test.test_thirdBalance()
    @staticmethod
    def test_transferout():#第三方轉回
        '''第三方轉出'''
        statu_list = []
        user = env_dict['轉入/轉出'][envs]
        Pc_header['Cookie']= 'ANVOID='+cookies_[user]
        Pc_header['Content-Type'] = 'application/json; application/json; charset=UTF-8' 
        post_data = {"amount":1}
        for third in third_list:
            url = '/%s/transferToFF'%third
            r = session.post(post_url+url,data=json.dumps(post_data),headers= Pc_header)
            if r.json()['status'] == True:
                print('帳號: %s, %s轉回4.0 ,金額:1, 進行中'%(user,third))
                statu_list.append(third)
            else:
                print('%s轉帳接口失敗'%third)
        for third in statu_list:
            thirdly_status = Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),tran_type=1,
                third=third,user=user)# 先確認資料轉帳傳泰
            staut_mapping = thirdly_status[0][1]
            msg = '%s 轉帳單號: %s . '%(third,thirdly_status[0][0])
            if staut_mapping == '2':
                msg = msg +" 狀態成功"
            else:
                msg = msg +" 狀態待確認"
            sleep(3)
            print(msg)
            
        Joy188Test.test_thirdBalance()
    @staticmethod
    def test_tranUser(): # 代理線轉移
        '''代理線轉移'''
        #Joy188Test.admin_login()
        for move_type in [3]: #擇一個做
            if move_type ==0:#提升總代
                move_type = 'ga'
                target = ''# 提升總代 無需目標
                Joy188Test.select_tranUser(Joy188Test.get_conn(envs),'%kerr%',1)#抓出一代用戶
                random_user = random.randint(1,len(tran_user))
                user = tran_user[random_user]# 隨機找出用戶
                print('一代用戶: %s轉移至總代'%user)
            elif move_type ==1:#跨代理轉一代
                move_type = 'loa'
                Joy188Test.select_tranUser(Joy188Test.get_conn(envs),'%kerr%',2)#抓出二代用戶,目標需為不同上級
                random_user = random.randint(1,len(tran_user))# 隨機取出用戶,避免容易失敗,
                user = tran_user[random_user]#要做的用戶
                target = user_chain[0].split('/')[1]# 此為  抓出來的總帶,  需找出  不是這個總帶的一帶
                Joy188Test.select_tranChainUser(Joy188Test.get_conn(envs),target,'%kerr%')# 抓出 不同的代理 預設總帶,
                random_user = random.randint(1,len(tran_user))# 隨機取出總代,避免容易失敗,
                target = tran_user[random_user]#此用戶 即為  目標
                #print(target)
                print('二代: %s用戶,轉移至一代,新總代為: %s'%(user,target))
            elif move_type == 2:#相同代理,跨上去一層
                move_type = 'lua'
                Joy188Test.select_tranUser(Joy188Test.get_conn(envs),'%kerr%',3)#抓出三代用戶,目標需為相同上級
                user = tran_user[0]#要做的用戶
                target = user_chain[0].split('/')[1]# 此為  抓出來的總帶,  需找出  是這個用戶的總代
                print('三代: %s用戶,轉移至一代,相同總代為: %s'%(user,target))
            elif move_type == 3:#代理線轉移, 隨意跨線 ,可以是 同條線 ,也可以是 別條線
                for i in range(2):# 0 和 1  也能用來 joint_venture
                    move_type = 'lca'
                    random_lvl = random.randint(2,10) # 隨意等級 ,2 -6 
                    Joy188Test.select_tranUser(conn=Joy188Test.get_conn(envs),joint=i )#一般抓一個
                    user = tran_user[0]#要做的用戶
                    #Joy188Test.select_tranUser(conn=Joy188Test.get_conn(envs),joint=i,type_='t')#一般
                    if i == 0:
                        print('一般用戶轉移')
                    else:
                        print('合營用戶轉移')
                        sleep(5)
                    print('%s用戶,做代理線移轉 ,新上級代理: %s'%(user,
                                                         new_user))
                    admin_header['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
                    data = 'moveAccount=%s&targetAccount=%s&moveType=%s'%(user, new_user,move_type)# 要做轉移的用戶,目標用戶 ,類型 
                    r = admin_session.post(admin_url+'/admin/user/userchaincreate',headers=admin_header,
                                           data=data)
                    if 'errorMsg' in r.text:
                        print('代理線需確認')
                    else:
                        print('轉移成功')
                    print('----------------')

                
    @staticmethod
    def test_redEnvelope():#紅包加壁,審核用
        '''紅包測試'''
        #user = 'kerr001'
        user = env_dict['一般帳號'][envs]
        print('用戶: %s'%user)
        red_list = [] #放交易訂單號id
        Joy188Test.select_RedBal(Joy188Test.get_conn(envs),user)
        print('紅包餘額: %s'%(int(red_bal[0])/10000))
        
        #Joy188Test.admin_login()#登入後台
        data = {"receives":user,"blockType":"2","lotteryType":"1","lotteryCodes":"",
        "amount":"100","note":"test"}
        #header['Cookie'] = 'ANVOAID='+ admin_cookie['admin_cookie']#存放後台cookie
        admin_header['Content-Type'] ='application/json'
        r = admin_session.post(admin_url+'/redAdmin/redEnvelopeApply',#後台加紅包街口 
        data = json.dumps(data),headers=admin_header)
        if r.json()['status'] ==0:
            print('紅包加幣100')
        else:
            print ('失敗')
        Joy188Test.select_RedID(Joy188Test.get_conn(envs),user)#查詢教地訂單號,回傳審核data
        #print(red_id)
        red_list.append('%s'%red_id[0])
        #print(red_list)
        data = {"ids":red_list ,"status":2}
        r = admin_session.post(admin_url+'/redAdmin/redEnvelopeConfirm',#後台審核街口 
        data = json.dumps(data),headers=admin_header)
        if r.json()['status'] ==0:
            print('審核通過')
        else:
            print('審核失敗')
        Joy188Test.select_RedBal(Joy188Test.get_conn(envs),user)
        print('紅包餘額: %s'%(int(red_bal[0])/10000))
    
    @staticmethod
    def test_CancelOrder():#撤銷皆口
        '''撤消測試'''
        user =  env_dict['一般帳號'][envs]
        Pc_header['Cookie']= 'ANVOID='+cookies_[user]
        cancelID_dict = Joy188Test.select_CancelId(Joy188Test.get_conn(envs),user)#抓出 該用戶 今天投注 還在等待開獎的 key: orderid .value: lotteryid
        orderid = random.choices(list(cancelID_dict.keys()))[0]#隨機取一個orderid
        lotteryname = cancelID_dict[orderid][0]
        order_code = cancelID_dict[orderid][1]
        try:
            r = session.post(em_url+'/gameUserCenter/cancelOrder?orderId=%s'%orderid,headers=Pc_header)
            print('撤消彩種: %s ,方案編號: %s '%(lotteryname ,order_code))
            if r.json()['status'] == 1:
                print('撤消成功')
            else:
                print('撤銷失敗')
        except:
            #print(can_lottery)
            print('撤消問題確認')
    @staticmethod
    def test_ChargeLimit():
        '''充值解限測試'''
        user =  env_dict['一般帳號'][envs]
        userid = {'hsieh001': '1341294', 'kerr001': '1373224'}
        #Joy188Test.admin_login()
        admin_data = 'userId=%s&unlimitType=1&userLvl=1&username=%s&note=sdsdsds'%(userid[user],
                                                                                        user)
        admin_header['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        r = admin_session.post(admin_url+'/admin/user/userchargelimit' ,data=admin_data,
                               headers=admin_header)
        if r.json()['isSuccess'] == "1":
            print('%s 後台充值解限次數, 成功'%user)
        else:
            print('%s 後台充值解限次數, 失敗'%user)


# In[ ]:





# In[34]:


class Joy188Test2(unittest.TestCase):
    u"trunk頁面測試"
    @classmethod
    def setUpClass(cls):
        global dr,user,post_url
        try:
            cls.dr = webdriver.Chrome(executable_path=r'.\chromedriver.exe')
            dr = cls.dr
            post_url = url_dict[envs][0]
            if envs == 1: 
                cls.dr.get(post_url)
                user = 'kerr002'
                env_info = '188'
            else:
                cls.dr.get(post_url)
                user = 'hsieh002'
                env_info = 'dev'
            password = Joy188Test.select_userPass(Joy188Test.get_conn(envs),user)# 從DB
            print(password[0])
            if password[0] == 'fa0c0fd599eaa397bd0daba5f47e7151':#123qwe
                password  = '123qwe'
            elif password[0] == '3bf6add0828ee17c4603563954473c1e':
                password = 'amberrd'
            else:
                password = 'amberrd'
            print(u'登入環境: %s,登入帳號: %s'%(env_info ,user))
            cls.dr.find_element_by_id('J-user-name').send_keys(user)
            print(password)
            cls.dr.find_element_by_id('J-user-password').send_keys(password)
            #sleep(3)
            cls.dr.find_element_by_id('J-form-submit').click()
            sleep(3)
        except NoSuchElementException as e:
            print(e)
    @staticmethod
    def ID(element):
        return  dr.find_element_by_id(element)
    def CSS( element):
        return  dr.find_element_by_css_selector(element)
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
    def result():#投注結果
        soup = BeautifulSoup(dr.page_source, 'lxml')
        a = soup.find_all('ul',{'class':'ui-form'})
        for i in range(5):
            for b in a:
                c = b.find_all('li')[i]
                print(c.text)
    @staticmethod
    def test_cqssc():
        u'重慶時彩投注'
        
        sleep(3)
        dr.get(em_url+'/gameBet/cqssc')
        print(dr.title)
        
        Joy188Test2.game_ssh()
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(envs),user,'cqssc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_hljssc():#黑龍江
        
        sleep(3)
        dr.get(em_url+'/gameBet/hljssc')
        print(dr.title)
        
        Joy188Test2.game_ssh()
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'hljssc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_hn5fc():
        
        sleep(3)
        dr.get(em_url+'/gameBet/hn5fc')
        print(dr.title)
        
        Joy188Test2.game_ssh()
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'hn5fc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod    
    def test_fhxjc():
        
        sleep(3)
        dr.get(em_url+'/gameBet/fhxjc')
        print(dr.title)
        
        Joy188Test2.game_ssh()
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'fhxjc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_fhcqc():
        
        sleep(3)
        dr.get(em_url+'/gameBet/fhcqc')
        print(dr.title)
        
        Joy188Test2.game_ssh()
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'fhcqc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_shssl():# 五星完髮不同
        sleep(3)
        dr.get(em_url+'/gameBet/shssl')
        print(dr.title)
        
        Joy188Test2.game_ssh('no')# 
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'shssl')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_txffc():# 五星完髮不同
        sleep(3)
        dr.get(em_url+'/gameBet/txffc')
        print(dr.title)
        
        Joy188Test2.game_ssh('no')# 
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'txffc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_llssc():
        sleep(3)
        dr.get(em_url+'/gameBet/llssc')
        print(dr.title)
        
        Joy188Test2.game_ssh('no')# 
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'llssc')
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_btcffc():
        sleep(3)
        dr.get(em_url+'/gameBet/btcffc')
        print(dr.title)
        
        Joy188Test2.game_ssh('no')# 
                    
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'btcffc')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_ahk3():
        sleep(3)
        dr.get(em_url+'/gameBet/ahk3')
        print(dr.title)
        
        k3_element = ['li.hezhi.normal','li.santonghaotongxuan.normal','li.santonghaodanxuan.normal',
        'li.sanbutonghao.normal','li.sanlianhaotongxuan.normal','li.ertonghaofuxuan.normal',
        'li.ertonghaodanxuan.normal','li.erbutonghao.normal','li.yibutonghao.normal']
        for i in k3_element:            
            Joy188Test2.css_element(i)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'ahk3')
        
        print("方案編號: %s"%order_code[0])
        
    @staticmethod
    def test_jsk3():
        sleep(3)
        dr.get(em_url+'/gameBet/jsk3')
        print(dr.title)
        
        k3_element = ['li.hezhi.normal','li.santonghaotongxuan.normal','li.santonghaodanxuan.normal',
        'li.sanbutonghao.normal','li.sanlianhaotongxuan.normal','li.ertonghaofuxuan.normal',
        'li.ertonghaodanxuan.normal','li.erbutonghao.normal','li.yibutonghao.normal']
        for i in k3_element:            
            Joy188Test2.css_element(i)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        Joy188Test2.link_element("确 认")
        sleep(3)
        
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'jsk3')
        
        print("方案編號: %s"%order_code[0])
    @staticmethod
    def test_jsdice():
        sleep(3)
        dr.get(em_url+'/gameBet/jsdice')
        print(dr.title)
        global sb_element
        # 江蘇骰寶 列表, div 1~ 52
        sb_element = ['//*[@id="J-dice-sheet"]/div[%s]/div'%i for i in range(1,53,1)]
        
        for i in sb_element:
            sleep(1)
            Joy188Test2.xpath_element(i)
        sleep(0.5)
        Joy188Test2.xpath_element('//*[@id="J-dice-bar"]/div[5]/button[1]')#下注
        Joy188Test2.result()
        Joy188Test2.CSS('a.btn.btn-important').click()#確認
        
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'jsdice')
        
        print("方案編號: %s"%order_code[0])
    
    @staticmethod
    def test_jldice():
        sleep(3)
        for lottery in ['jldice1','jldice2']:
            dr.get(em_url+'/gameBet/%s'%lottery)
            print(dr.title)

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
            Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,lottery)
        
            print("方案編號: %s"%order_code[0])
                
    @staticmethod
    def test_bjkl8():
        sleep(3)
        dr.get(em_url+'/gameBet/bjkl8')
        print(dr.title)
        
        bjk_element = ['dd.renxuan%s'%i for i in range(1,8)]#任選1 到 任選7
        Joy188Test2.id_element('randomone')
        sleep(1)
        Joy188Test2.css_element('li.renxuan.normal')
        for element in bjk_element:
            Joy188Test2.css_element(element)
            sleep(0.5)
            Joy188Test2.id_element('randomone')
        
        Joy188Test2.id_element('J-submit-order')#馬上投注
        Joy188Test2.result()
        sleep(1)
        Joy188Test2.link_element("确 认")
        
        Joy188Test.select_PcOredrCode(Joy188Test.get_conn(1),user,'bjkl8')
        
        print("方案編號: %s"%order_code[0])
        
    @staticmethod
    def test_safepersonal():
        u"修改登入密碼"
        #print(post_url)
        dr.get(post_url+'/safepersonal/safecodeedit')
        print(dr.title)
        password = Joy188Test.select_userPass(Joy188Test.get_conn(envs),user)# 從DB 抓取 限在 密碼

        if password[0] == 'fa0c0fd599eaa397bd0daba5f47e7151':#123qwe
            newpass = "amberrd"#amberrd  新密碼
            oldpass = '123qwe'# 原本的密碼
            msg = '新密碼為amberrd'
        else:# 密碼為amberrd
            newpass = "123qwe"
            oldpass = "amberrd"
            msg = '新密碼為123qwe'
        Joy188Test2.ID( 'J-password').send_keys(oldpass)
        print(u'當前登入密碼: %s'%oldpass)
        Joy188Test2.ID( 'J-password-new').send_keys(newpass)
        Joy188Test2.ID( 'J-password-new2').send_keys(newpass)
        print(u'新登入密碼: %s,確認新密碼: %s'%(newpass,newpass))
        Joy188Test2.ID( 'J-button-submit-text').click()
        sleep(2)
        if Joy188Test2.ID( 'Idivs').is_displayed():#成功修改密碼彈窗出現
            print(u'恭喜%s密码修改成功，请重新登录。'%user)
            Joy188Test2.ID( 'closeTip1').click()#關閉按紐,跳回登入頁
            sleep(1)
        else:
            print(u'密碼輸入錯誤')
            pass
    @staticmethod
    def test_applycenter():
        u'開戶中心'
        sleep(2)
        OpenUrl_dict = {
            0: "/register?id=18417062&exp=1902283553071&pid=13412941&token=e618",
            1: "/register/?id=27402734&exp=1885877796573&pid=13732231&token=3738"
        }# list[0] : 一般用戶 , list[1] : 合營用戶
        passwd_dict = {
            0: '123qwe',1:'amberrd'
        }
        dr.get(post_url+OpenUrl_dict[envs])#kerr000的連結
        print(dr.title)
        global user_random
        user_random = user+'%s'%random.randint(1,1000000)#隨機生成 kerr下面用戶名
        print(u'註冊用戶名: %s'%user_random)
        Joy188Test2.ID('J-input-username').send_keys(user_random)#用戶名
        Joy188Test2.ID('J-input-password').send_keys(passwd_dict[envs])#第一次密碼
        Joy188Test2.ID('J-input-password2').send_keys(passwd_dict[envs])#在一次確認密碼
        Joy188Test2.ID('J-button-submit').click()#提交註冊        
        sleep(5)
        if dr.current_url == post_url + '/index':
            (u'kerr%s註冊成功'%user_random)
            print(post_url)
            print(u'%s登入成功'%user_random)
        else:
            print(u'登入失敗')
    @staticmethod
    def test_safecenter():
        u"安全中心"
        global safe_dict
        safe_dict = {0:['hsieh','hsieh123'],1: ['kerr','kerr123']}# 安全問題 .安全密碼
        sleep(3)
        dr.get(post_url+'/safepersonal/safecodeset')#安全密碼連結
        print(dr.title)
        Joy188Test2.ID('J-safePassword').send_keys(safe_dict[envs][1])
        Joy188Test2.ID('J-safePassword2').send_keys(safe_dict[envs][1])
        print(u'設置安全密碼/確認安全密碼: %s'%safe_dict[envs][1])
        Joy188Test2.ID('J-button-submit').click()
        if dr.current_url == post_url+ '/safepersonal/safecodeset?act=smt':#安全密碼成功Url
            print(u'恭喜%s安全密码设置成功！'%user_random)
        else:
            print(u'安全密碼設置失敗')
        dr.get(post_url+'/safepersonal/safequestset')#安全問題
        print(dr.title)
        for i in range(1,4,1):#J-answrer 1,2,3  
            Joy188Test2.ID('J-answer%s'%i).send_keys(safe_dict[envs][0])#問題答案
        for i in range(1,6,2):# i產生  1,3,5 li[i], 問題選擇
            Joy188Test2.XPATH('//*[@id="J-safe-question-select"]/li[%s]/select/option[2]'%i).click()
        Joy188Test2.ID('J-button-submit').click()#設置按鈕
        Joy188Test2.ID('J-safequestion-submit').click()#確認
        if dr.current_url == post_url +'/safepersonal/safequestset?act=smt':#安全問題成功url
            print(u'恭喜%s安全问题设置成功！'%user_random)
        else:
            print(u'安全問題設置失敗')
    @staticmethod
    def test_bindcard():
        u"銀行卡綁定"
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
        Joy188Test2.ID('securityPassword').send_keys(safe_dict[envs][1])#安全密碼
        Joy188Test2.ID('J-Submit').click()#提交
        sleep(3)
        if Joy188Test2.ID('div_ok').is_displayed():
            print(u'%s银行卡绑定成功！'%user_random)
            Joy188Test2.ID('CloseDiv2').click()#關閉
        else:
            print(u'銀行卡綁定失敗')
    @staticmethod
    def test_bindcardUs():
        u"數字貨幣綁卡"
        #dr.get(post_url+'/bindcard/bindcarddigitalwallet?bindcardType=2')
        #print(dr.title)
        #card = random.randint(1000,1000000000)#usdt數字綁卡,隨機生成
        for key in usdt_dict.keys():
            dr.get(post_url+'/bindcard/bindcarddigitalwallet?bindcardType=2')
            Joy188Test2.ID('protocol').click()#幣種選擇
            Joy188Test2.XPATH('//*[@id="protocol"]/option[{value}]'.format(value=usdt_dict[key][1])).click()# 選擇 trc-20
            card = usdt_dict[key][0]
            Joy188Test2.ID('walletAddr').send_keys(card)#
            print(u'usdt 幣種協議: %s , 提現錢包地址: %s'%(key,card))
            Joy188Test2.ID('securityPassword').send_keys(safe_dict[envs][1])
            print(u'安全密碼:%s'%safe_dict[envs][1])
            Joy188Test2.ID('J-Submit').click()#提交
            sleep(2)
            if Joy188Test2.ID('div_ok').is_displayed():#彈窗出現
                print(u'%s数字货币钱包账户绑定成功！'%user_random)
                Joy188Test2.ID('CloseDiv2').click()
            else:
                print(u"數字貨幣綁定失敗")

        
    @classmethod
    def tearDownClass(cls):
        cls.dr.quit()





# In[ ]:





# In[35]:


class Joy188Test3(unittest.TestCase):
    u'trunkAPP接口測試'
    def Iapi_LoginData(username,uuid_,passwd,joint= 0 ):
        login_data = {
            "head": {
                "sessionId": ''
            },
            "body": {
                "param": {
                "username": username+"|"+ uuid_,
                "loginpassSource":passwd ,
                "appCode": 1,
                "uuid": uuid,
                "loginIp": 2130706433,
                "device": 2,
                "app_id": 9,
                "come_from": "3",
                "appname": "1",
                "jointVenture": joint
            }
            }
            }
        return login_data
        
    @staticmethod
    def test_iapiLogin():
        '''APP登入測試'''
        account_ ={0: {'hsieh00':'總代','hsieh001':'一代','hsiehapp001':'一代','hsieh0620':'玩家',
                      'hsiehwin':'APP合營'} 
                   ,1:{'kerr00':u'總代','kerr001':u'一代','kerrapp001':'二代','kerr010':'玩家',
                      'kerrwin1940': 'APP合營'}
                  }
        global token_,userid_,loginpasssource,uuid
        token_  ={}
        userid_ ={}
        global App_header
        
        App_header = {
        'User-Agent': userAgent, 
        'Content-Type': 'application/json'
        }
        
        #判斷用戶是dev或188,  uuid和loginpasssource為固定值
        global env# ipai環境
        if envs == 0:
            uuid = "2D424FA3-D7D9-4BB2-BFDA-4561F921B1D5"
            loginpasssource = "fa0c0fd599eaa397bd0daba5f47e7151"# 123qwe 加密
        elif envs == 1:
            uuid = 'f009b92edc4333fd'
            loginpasssource = "3bf6add0828ee17c4603563954473c1e"# amberrd加密
        else:
            pass
        env =  iapi_url[envs]
        #登入request的json
        for i in account_[envs].keys():
            if i in ['kerr010','hsieh0620']:# 玩家 會使用更換密碼街口
                password = Joy188Test.select_userPass(Joy188Test.get_conn(envs),i)#找出動態的密碼, 避免更換密碼被更動
                login_data = Joy188Test3.Iapi_LoginData(username=i,uuid_=uuid,passwd=password[0])
            elif i in env_dict['APP合營']:
                login_data = Joy188Test3.Iapi_LoginData(username=i,uuid_=uuid,
                passwd=loginpasssource,joint=1)
            else:
                login_data = Joy188Test3.Iapi_LoginData(username=i,uuid_=uuid,passwd=loginpasssource)
            try:
                #print(loginpasssource)
                r = requests.post(env+'front/login',data=json.dumps(login_data),headers= App_header)
                #print(r.json())
                token = r.json()['body']['result']['token']
                userid = r.json()['body']['result']['userid']
                token_.setdefault(i,token)
                userid_.setdefault(i,userid)
                print(u'APP登入成功,登入帳號: %s,登入身分: %s'%(i,account_[envs][i]))
                print("Token: %s"%token)
                print("Userid: %s"%userid)
            except ValueError as e:
                print(e)
                print(u"登入失敗")
                break
            #user_list.setdefault(userid,token) 
    def IapiData(user):
        data = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"",
        "sessionId":token_[user]},"body":{"param":{"CGISESSID":token_[user],"app_id":"9",
        "come_from":"3","appname":"1"},"pager":{"startNo":"","endNo":""}}}
        return data
    @staticmethod
    def test_iapiCheckIn():
        '''APP簽到'''
        user = env_dict['APP帳號'][envs]
        data_ = Joy188Test3.IapiData(user)
        r = requests.post(env+'/exp/checkInByUserId',
                    data=json.dumps(data_),headers=App_header)
        if r.json()['head']['status'] == 0:
            print('%s 簽到成功'%user)
        else:
            print('%s 簽到確認')
    @staticmethod
    def test_iapiSubmit():
        '''APP投注'''
        #Joy188Test3.test_iapiLogin(user='kerr001',envir='188')# evir = 'dev','188'
        global user,order_dict
        user = env_dict['APP帳號'][envs]
        t = time.strftime('%Y%m%d %H:%M:%S')
        print(u'投注帳號: %s, 現在時間: %s'%(user,t))
        order_dict = {}# 存放  到時 要撤消單
        for i in lottery_dict.keys():
        #for i in lottery_115:
        #for i in ['slmmc','sl115']:
            while True:
                try:
                    #print(i)
                    now = int(time.time()*1000)#時間戳
                    lotteryid = lottery_dict[i][1]
                    if i == 'pcdd': # 先寫死 固定完法 和投注內容, 因為動態完法 賠率會不同
                        Joy188Test.web_issuecode(i)
                        data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"",
                        "sessionId":token_[user]},"body":{"pager":{"startNo":"1","endNo":"99999"},"param":
                        {"saleTime":now,"userIp":"168627247","isFirstSubmit":0,"channelId":202,
                        "channelVersion":"2.0.21.0013","lotteryId":"99204","issue":issuecode,
                         "traceStop":0,"money":50,"redDiscountTotal":0,"awardGroupId":"263","list":
                         [{"methodid":"66_28_71","codes":"15","nums":1,"fileMode":0,"mode":1,
                           "odds":"12.32","times":1,"money":50,"awardMode":1}]}}}
                    elif i == 'super2000':
                        break
                    else:
                        if i in ['sl115','slmmc']:# 不用要講其
                            pass
                        else:
                            Joy188Test.web_issuecode(i)
                        ball_type_post = Joy188Test.game_type(i)#玩法和內容,0為玩法名稱, 1為投注內容
                        methodid = ball_type_post[0].replace('.','')#ex: housan.zhuiam.fushi , 把.去掉


                        #找出對應的玩法id , bet_type[0]
                        Joy188Test.select_betTypeCode(Joy188Test.get_conn(envs),lotteryid,methodid)
                        data_ = {"head":
                        {"sessionId":token_[user]},
                        "body":{"param":{"CGISESSID":token_[user],# 產生  kerr001的token
                        "lotteryId":str(lotteryid),"chan_id":1,"userid":1373224,
                        "money":2*mul,"issue":issuecode,"issueName":issuecode,"isFirstSubmit":0,
                        "list":[{"methodid":bet_type[0],"codes":ball_type_post[1],"nums":1,
                        "fileMode":0,"mode":1,"times":mul,"money":2*mul}],#times是倍數
                        "traceIssues":"","traceTimes":"","traceIstrace":0,
                        "saleTime":now,
                        "userIp":168627247,"channelId":402,"traceStop":0}}}
                        if i in ['btcffc','btcctp','xyft','xyft168']: #高獎金玩法 彩種
                            data_['body']['param']['list'][0]['awardMode'] = 2# 彼特幣分彩 需增加awarcmode

                    r = requests.post(env+'game/buy',data=json.dumps(data_),headers=App_header) 

                    if r.json()['head']['status'] == 0: #status0 為投注成功
                        print(u'%s投注成功'%lottery_dict[i][0])
                        print(u"投注內容: %s"%ball_type_post[1])
                        print(u"投注金額: %s, 投注倍數: %s"%(2*mul,mul))#mul 為game_type方法對甕倍數
                        #print(r.json())
                        orderid = (r.json()['body']['result']['orderId'])
                        Joy188Test.select_orderCode(Joy188Test.get_conn(envs),orderid)#找出對應ordercode
                        play_ = Joy188Test.select_OrderCodeTitle(Joy188Test.get_conn(envs),order_code[0])
                        print('玩法名稱: %s.%s.%s'%(play_[0][1],
                        play_[0][2],play_[0][3]) )
                        print(u'投注單號: %s'%order_code[0])
                        print('------------------------------')
                        order_dict[i]  = {order_code[0]: orderid}# 存放, 後續 掣單使用
                        break
                    else:
                        pass
                        break
                    break
                        #pass
                except requests.exceptions.ConnectionError:
                    print('please wait')
                    break
                except IndexError as e:
                    #print(e)
                    print(lottery_dict[i][0])
                    break
    @staticmethod
    def test_IapiPlanSubmit():
        '''APP追號投注'''
        user = env_dict['APP合營'][envs]
        data = Joy188Test3.IapiData(user)
        t = time.strftime('%Y%m%d %H:%M:%S')
        print(u'投注帳號: %s, 現在時間: %s'%(user,t))
        for lottery in lottery_dict.keys():
        #for lottery in lottery_115:
            while True:
                try:
                    if lottery in ['slmmc','sl115','btcctp','lhc']:
                        print('%s 沒開放追號'%lottery_dict[lottery][0])
                        print('------------------------------')
                        break
                    elif lottery in ['pcdd','fckl8','np3','n3d']:#awardmode 需待1
                        awardmode = 1
                    elif lottery == 'super2000':
                        break
                    else:
                        awardmode = 2
                    lotteryid = lottery_dict[lottery][1]
                    now = int(time.time()*1000)#時間戳
                    plan_ = Joy188Test.plan_num(envs,lottery,random.randint(2,10))#隨機生成 50期內的比數
                    issue = plan_[0]['issueCode']# 追號 data傳到isuue參數
                    plan_issue = []  #傳到 traceIssues 參數
                    time_list = [] # 傳到 traceTimes 參數
                    for i in plan_:
                        plan_issue.append(str(i['issueCode']))# 轉str用意, 下面 join可以直接 轉出
                        time_list.append('1')
                    len_plan = len(plan_issue)# 把長度算出, 去乘上 單柱 2圓
                    plan_issue = ",".join(plan_issue)# 傳到data traceIssues 參數
                    time_list = ",".join(time_list)

                    ball_type_post = Joy188Test.game_type(lottery)#玩法和內容,0為玩法名稱, 1為投注內容
                    methodid = ball_type_post[0].replace('.','')#ex: housan.zhuiam.fushi , 把.去掉
                    awardGroupId = Joy188Test.select_GroupId(Joy188Test.get_conn(envs),lotteryid,user)
                    Joy188Test.select_betTypeCode(Joy188Test.get_conn(envs),lotteryid, methodid)

                    param_data = data["body"]["param"]
                    plan_list = [{"methodid": bet_type[0] ,"codes": ball_type_post[1],"nums":1,
                    "fileMode":0,"mode":1,"times":1,"money":2,"awardMode":awardmode}]
                    
                    plan_data = {"saleTime": now,"userIp":"1037863469","isFirstSubmit":0,
                    "channelId":202,"channelVersion":"12.0.23.0013",
                    "lotteryId": "%s"%lotteryid,"issue":"%s"%issue , "traceStop":2,"money": 2*len_plan,
                    "redDiscountTotal":0,
                    "awardGroupId":"%s"%awardGroupId ,"list":plan_list,"traceIstrace":1,
                    "traceIssues":"%s"%plan_issue,"traceTimes":"%s"%time_list}
                    param_data.update(plan_data)
                    data['body']['param'] = param_data
                    
                    r = requests.post(env+'game/plan',data=json.dumps(data),headers=App_header)
                    #print(r.json())
                    if r.json()['head']['status'] == 0: #status0 為投注成功
                        planid = r.json()['body']['result']['gamePlanId']
                        plan_code = Joy188Test.select_PlanCode(conn=Joy188Test.get_conn(envs),
                                                               type_='app',planid=planid)
                        #plan_code為一個tuple , [0][0]是packageid , [0][1]是追號單號
                        print('%s 投注成功'%lottery_dict[lottery][0])
                        Joy188Test.select_orderCode(Joy188Test.get_conn(envs),plan_code[0][0],type_='packageid')#抓出
                        play_ = Joy188Test.select_OrderCodeTitle(Joy188Test.get_conn(envs),order_code[0])
                        print('玩法名稱: %s.%s.%s'%(play_[0][1],
                        play_[0][2],play_[0][3]) )
                        print(u"投注內容: %s"%ball_type_post[1])
                        print(u"投注金額: %s, 追號期數: %s"%(2*len_plan ,len_plan ))#mul 為game_type方法對甕倍數
                        print('追號單號: %s'%plan_code[0][1])
                        print('------------------------------')
                        break

                    else:
                        #print('%s 追號失敗'%lottery_dict[lottery][0])
                        #print('------------------------------')
                        break
                    break
                except IndexError as e:
                    print('%s, %s'%(e,lottery_dict[lottery][0]))
                    print('------------------------------')
                    break
    @staticmethod
    def test_IapiOgAgent():
        '''舊代裡中心'''
        now = datetime.datetime.now()
        start_date = '%s-%s-1'%(now.year,now.month)# 本月 1號
        now_date = '%s-%s-%s'%(now.year,now.month,now.day)
        user = env_dict['APP合營'][envs]
    
        OgAgent_dict = {'彩票': ['/agentCenter/queryAgentCenterData', {"identity":1,"duration":{"start":start_date,"end":now_date}} ],'三方': ['/agentCenter/queryThirdlyAgentCenterData',{"userId":userid_[user],"userName":None,"plat":"","searchItem":None,"identity":1,"startDate":start_date,"endDate":now_date}] }
        print('%s 查詢'%user)
        print('查詢時間 ,本月: %s - %s '%(start_date,now_date))
        for key in OgAgent_dict.keys():
            print('%s: '%key)
            data = Joy188Test3.IapiData(user)
            param_data = data["body"]["param"]
            param_data.update(OgAgent_dict[key][1])# 將post的data更新
            data['body']['param'] = param_data

            r = requests.post(env+OgAgent_dict[key][0],
            data=json.dumps(data),headers=App_header)
            r_json = r.json()
            if r_json['head']['status'] != 0: # 狀態待確認 ,成功 0
                print('狀態待確認')
            else:
                result = r_json['body']['result']
                print(result)
    @staticmethod
    def test_IapiNewAgent():
        '''新代理中心'''
        now = datetime.datetime.now()
        start_date = '%s-%s-1'%(now.year,now.month)# 本月 1號
        now_date = '%s-%s-%s'%(now.year,now.month,now.day)
        user = env_dict['APP合營'][envs]
        print('%s 查詢'%user)
        print('查詢時間 ,本月: %s - %s '%(start_date,now_date))

        data = Joy188Test3.IapiData(user)
        agent_data = {"startDate":"{start_date} 00:00:00".format(start_date=start_date),"endDate":"{now_date} 23:59:59".format(now_date=now_date)}
        param_data = data["body"]["param"]
        param_data.update(agent_data)
        data['body']['param'] = param_data

        r = requests.post(env+'/agentCenter/getAgentCenterIndexPageAllData',
            data=json.dumps(data),headers=App_header)
        r_json = r.json()
        result = r_json['body']['result']
        print(result)


    @staticmethod
    def test_IapiTransfer():
        '''APP上下級轉帳'''
        user_dict = {
            0:['hsieh00','hsiehapp001'],
            1:['kerr00','kerrapp001']
        }
        user = user_dict[envs][0]# 上級用戶 
        user_ = user_dict[envs][1]#下級用戶
        while True:
            for i in user,user_:
                data = Joy188Test3.IapiData(i)
                r = requests.post(env+'/information/getBalance',
                    data=json.dumps(Joy188Test3.IapiData(i)),headers=App_header)
                balance =  r.json()['body']['result']['balance']
                print('%s用戶餘額: %s'%(i,balance))
            
            data = Joy188Test3.IapiData(user)#從新生成初始 data
            money = random.randint(1,100)#  隨機金額 格式 需成 10000
            transfer_data = {"applyTime": int(time.time()*1000), "direction":0,"isUpward":0,
            "rcvAccount":user_ ,"transferAmt":money*10000,"userId":userid_[user]}# 上下級轉帳data
            param_data = data["body"]["param"]
            param_data.update(transfer_data)
            data['body']['param'] = param_data
            r = requests.post(env+'fund/confirmFundTransfer',data=json.dumps(data),headers=App_header)
            if r.json()['head']['status'] !=0: # 發起提現
                print('發起上下級轉帳確認')
                break
            
            question_dict = {
                0: "\\u6211\\u6700\\u559c\\u6b22\\u7684\\u7403\\u661f\\uff1f",
                1: "\\u6211\\u6700\\u559c\\u6b22\\u7684\\u6f14\\u5458\\uff1f"
            }
            qid_dict = {0:4,1:3}
            #安全問題
            data = Joy188Test3.IapiData(user)#從新生成初始 data
            safeQuestVerify_data = {"quests":[{"qid":qid_dict[envs],
            "question":question_dict[envs],
            "qpwd":passwd_info[envs][1],"isUsed":1}]}
            param_data = data["body"]["param"]
            param_data.update(safeQuestVerify_data)
            data['body']['param'] = param_data
            r = requests.post(env+'security/safeQuestVerify',data=json.dumps(data),headers=App_header)
            if r.json()['head']['status'] !=0: 
                print('安全問題確認')
                break

            #安全密碼
            data = Joy188Test3.IapiData(user)#從新生成初始 data
            checkSecpass_data = {"secpass":passwd_info[envs][0],"isCheckLoginPassword":0}
            param_data = data["body"]["param"]
            param_data.update(checkSecpass_data)
            data['body']['param'] = param_data
            r = requests.post(env+'/security/checkSecpass',data=json.dumps(data)
                              ,headers=App_header)# 安全密碼確認
            if r.json()['head']['status'] !=0: 
                print('安全密碼確認')
                break
            #提現提交
            data = Joy188Test3.IapiData(user)#從新生成初始 data
            confirm_data = {"applyTime": int(time.time()*1000), "direction":0,"isUpward":0,
            "rcvAccount":user_ ,"transferAmt":money*10000,"userId":userid_[user]}
            param_data = data["body"]["param"]
            param_data.update(confirm_data)
            data['body']['param'] = param_data
            r = requests.post(env+'fund/fundTransfer',data=json.dumps(data),headers=App_header)
            if r.json()['head']['status'] !=0: 
                print('上下級轉帳提交確認')# 確認
                break
            print('上級: %s 轉帳給下級: %s .金額: %s 成功'%(user,user_,money))
            for i in user,user_:
                data = Joy188Test3.IapiData(i)
                r = requests.post(env+'/information/getBalance',
                    data=json.dumps(Joy188Test3.IapiData(i)),headers=App_header)
                balance =  r.json()['body']['result']['balance']
                print('%s用戶餘額: %s'%(i,balance))
            break
        
        
        
    
    @staticmethod
    def test_IapiRecharge():
        '''APP充值發起'''
        user = env_dict['一般帳號'][envs]

        admin_fund = {# 後台 充值相關配置 , dev: APP 三合 . 188: APP plg
            0: "userGroupSetting[4][]=247&singleLowlimit[4]=1&singleUplimit[4]=10&dailyUplimit[4]=1000&chargeWaySet[4]=11&platform[4]=1&id[4]=90&isOpen[4]=N&userGroupSetting[15][]=247&singleLowlimit[15]=1&singleUplimit[15]=1000&dailyUplimit[15]=1000&chargeWaySet[15]=11&platform[15]=1&id[15]=62&isOpen[15]=Y&userGroupSetting[29][]=247&singleLowlimit[29]=1&singleUplimit[29]=100&dailyUplimit[29]=10000&chargeWaySet[29]=11&platform[29]=1&id[29]=100&isOpen[29]=N&userGroupSetting[41][]=247&singleLowlimit[41]=103&singleUplimit[41]=103&dailyUplimit[41]=1000&chargeWaySet[41]=11&platform[41]=1&id[41]=122&isOpen[41]=N&userGroupSetting[56][]=247&singleLowlimit[56]=104&singleUplimit[56]=104&dailyUplimit[56]=1000&chargeWaySet[56]=11&platform[56]=1&id[56]=107&isOpen[56]=N&userGroupSetting[64][]=247&singleLowlimit[64]=105&singleUplimit[64]=105&dailyUplimit[64]=1000&chargeWaySet[64]=11&platform[64]=1&id[64]=124&isOpen[64]=N&userGroupSetting[89][]=247&singleLowlimit[89]=1&singleUplimit[89]=10000&dailyUplimit[89]=10000&chargeWaySet[89]=11&platform[89]=1&id[89]=180&isOpen[89]=N&userGroupSetting[105][]=247&userGroupSetting[105][]=704&singleLowlimit[105]=20&singleUplimit[105]=5000&dailyUplimit[105]=100000&chargeWaySet[105]=11&platform[105]=1&id[105]=172&isOpen[105]=N",
            1: "userGroupSetting[4][]=27&singleLowlimit[4]=1&singleUplimit[4]=200&dailyUplimit[4]=0&chargeWaySet[4]=11&platform[4]=1&id[4]=90&isOpen[4]=N&userGroupSetting[15][]=27&singleLowlimit[15]=1&singleUplimit[15]=100000&dailyUplimit[15]=4500000&chargeWaySet[15]=11&platform[15]=1&id[15]=62&isOpen[15]=N&userGroupSetting[29][]=27&singleLowlimit[29]=102&singleUplimit[29]=102&dailyUplimit[29]=10000&chargeWaySet[29]=11&platform[29]=1&id[29]=100&isOpen[29]=N&userGroupSetting[41][]=27&singleLowlimit[41]=103&singleUplimit[41]=103&dailyUplimit[41]=1000&chargeWaySet[41]=11&platform[41]=1&id[41]=122&isOpen[41]=N&userGroupSetting[59][]=27&singleLowlimit[59]=5000&singleUplimit[59]=80000&dailyUplimit[59]=1000&chargeWaySet[59]=11&platform[59]=1&id[59]=107&isOpen[59]=N&userGroupSetting[67][]=27&singleLowlimit[67]=105&singleUplimit[67]=105&dailyUplimit[67]=1000&chargeWaySet[67]=11&platform[67]=1&id[67]=124&isOpen[67]=N&userGroupSetting[84][]=27&singleLowlimit[84]=1&singleUplimit[84]=10000&dailyUplimit[84]=10000&chargeWaySet[84]=11&platform[84]=1&id[84]=148&isOpen[84]=Y&userGroupSetting[113][]=27&singleLowlimit[113]=1&singleUplimit[113]=5000&dailyUplimit[113]=100000&chargeWaySet[113]=11&platform[113]=1&id[113]=181&isOpen[113]=N"
        }
        recharge_data = admin_fund[envs]
        r = admin_session.post(admin_url+'/admin/Rechargemange/index?parma=saveBypassCfg',
        headers=admin_header,
        data=recharge_data)# 後台 將 APP 銀聯掃馬 後台 開啟三和一個渠道 ,避免 發起充值 時 ,渠道沒開

        data_ = Joy188Test3.IapiData(user)
        money = random.randint(10,20)#  隨機金額
        fund_data = {"bankId":37,"money":money,"bankAccount":"","exchangeRate":"6.37",
        "cashBackSetId":None,"cashBackSetType":None,"originalCurrencyAmount":0,"userId":userid_[user],
        "customerIp":"10.13.12.47","system":1}
        param_data = data_["body"]["param"]
        param_data.update(fund_data)
        data_['body']['param'] = param_data
        
        r = requests.post(env+'recharge/quickCommit',data=json.dumps(data_),headers=App_header) 
        if r.json()['head']['status'] in [901000,0]:
            sn = Joy188Test.select_FundSn(Joy188Test.get_conn(envs),userid_[user])
            print('%s 充值發起成功 金額: %s, 單號:%s'%(user,money,sn))
        else:
            print('%s 充值發起失敗'%user)
                
    @staticmethod
    def test_IapiCancelSubmit():
        '''APP撤消投注'''
        user = env_dict['APP帳號'][envs]
        
        cancelID_dict = Joy188Test.select_CancelId(Joy188Test.get_conn(envs),user)#抓出 該用戶 今天投注 還在等待開獎的 key: orderid .value: lotteryid
        orderid = random.choices(list(cancelID_dict.keys()))[0]#隨機取一個orderid
        lotteryname = cancelID_dict[orderid][0]
        order_code = cancelID_dict[orderid][1]

        data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"","sessionId":token_[user]},"body":{"pager":{"startNo":"1","endNo":"99999"},"param":{
            "CGISESSID":token_[user],"id": str(orderid),"app_id":"9","come_from":"3","appname":"1"}}}
        r = requests.post(env+'game/cancelGame',data=json.dumps(data_),headers=App_header)
        print('撤消彩種: %s ,方案編號: %s '%(lotteryname ,order_code))  
        if r.json()['head']['status'] == 0:
            print('撤消成功')
        else:
            print('撤銷失敗')
            
    @staticmethod
    def test_OpenLink():
        '''APP開戶中心'''
        global token_result
        token_result = {}# 到時會回傳給 註冊用, 裡面存放  開戶連結 exp, token ....
        for i in range(2):
            if i ==0:
                print('一般: ')
                user = env_dict['一般帳號'][envs]
            else:
                print('合營: ')
                user = env_dict['APP合營'][envs]
            data_ = Joy188Test3.IapiData(user)
            param_data = data_["body"]["param"]
            #info_dict ,dev和 188會因為用戶反點不同而不同
            info_dict = {0: [
            [{"lotteryId":"77101","lotteryName":"\\u4e50\\u5229\\u771f\\u4eba\\u5f69",
            "lotterySeriesCode":10,"lotterySeriesName":"\\u771f\\u4eba\\u5f69\\u7968","awardGroupId":77101,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","directLimitRet":5000},
            {"lotteryId":"99101","lotteryName":"\\u6b22\\u4e50\\u751f\\u8096","lotterySeriesCode":1,
             "lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":12,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99103","lotteryName":"\\u65b0\\u7586\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":19,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99104","lotteryName":"\\u5929\\u6d25\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":36,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":13,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":5,"awardName":"\\u5956\\u91d1\\u7ec41700","directRet":"790","threeoneRet":"290","directLimitRet":1000,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":16,"awardName":"\\u5956\\u91d1\\u7ec41500","directRet":"1790","threeoneRet":"1090","directLimitRet":2000,"threeLimitRet":1300,"superLimitRet":100},{"lotteryId":"99106","lotteryName":"\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":33,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99107","lotteryName":"\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":15,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99108","lotteryName":"3D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":101,"awardName":"\\u5956\\u91d1\\u7ec41700","directRet":"790","threeoneRet":"290","directLimitRet":1000,"threeLimitRet":500},{"lotteryId":"99109","lotteryName":"P5","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":102,"awardName":"\\u5956\\u91d1\\u7ec41700","directRet":"790","threeoneRet":"290","directLimitRet":1000,"threeLimitRet":500},{"lotteryId":"99111","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":41,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99112","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":56,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99113","lotteryName":"\\u8d85\\u7ea72000\\u79d2\\u79d2\\u5f69(APP\\u7248)","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":11416083,"awardName":"2000\\u5956\\u91d1\\u7ec4","superLimitRet":100},{"lotteryId":"99114","lotteryName":"\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":208,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99115","lotteryName":"\\u51e4\\u51f0\\u6bd4\\u7279\\u5e01\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":214,"awardName":"\\u5956\\u91d1\\u7ec41000","directRet":"4590","threeoneRet":"4590","directLimitRet":4800,"threeLimitRet":4800},{"lotteryId":"99116","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":228,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99117","lotteryName":"\\u51e4\\u51f0\\u91cd\\u5e86\\u5168\\u7403\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":263,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99118","lotteryName":"\\u51e4\\u51f0\\u65b0\\u7586\\u5168\\u7403\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":264,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99119","lotteryName":"\\u6cb3\\u5185\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":268,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99120","lotteryName":"\\u6cb3\\u5185\\u4e94\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":273,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99121","lotteryName":"360\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":274,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99122","lotteryName":"360\\u4e94\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":275,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500,"superLimitRet":100},{"lotteryId":"99123","lotteryName":"\\u8d8a\\u5357\\u798f\\u5f69","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":278,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99124","lotteryName":"\\u8d8a\\u53573D\\u798f\\u5f69","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":279,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99125","lotteryName":"\\u5947\\u8da3\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":308,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99126","lotteryName":"\\u591a\\u5f69\\u6cb3\\u5185\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":316,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99201","lotteryName":"\\u5317\\u4eac\\u5feb\\u4e508","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":32,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"1290","threeoneRet":"790","directLimitRet":1500,"threeLimitRet":1000},{"lotteryId":"99202","lotteryName":"PK10","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":206,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","directLimitRet":500},{"lotteryId":"99203","lotteryName":"\\u98de\\u8247","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":233,"awardName":"\\u5956\\u91d1\\u7ec41000","directRet":"4590","directLimitRet":4800},{"lotteryId":"99204","lotteryName":"PC\\u86cb\\u86cb","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":283,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","directLimitRet":500},{"lotteryId":"99205","lotteryName":"168\\u98de\\u8247","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":293,"awardName":"\\u5956\\u91d1\\u7ec41000","directRet":"4590","directLimitRet":4800},{"lotteryId":"99206","lotteryName":"\\u798f\\u5f69\\u5feb\\u4e508","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":298,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"1290","threeoneRet":"790","directLimitRet":1500,"threeLimitRet":1000},{"lotteryId":"99207","lotteryName":"\\u5feb\\u4e508\\u5168\\u7403\\u5f69","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":303,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"1290","threeoneRet":"790","directLimitRet":1500,"threeLimitRet":1000},{"lotteryId":"99301","lotteryName":"\\u5c71\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":24,"awardName":"\\u5956\\u91d1\\u7ec41782","directRet":"290","directLimitRet":500},{"lotteryId":"99302","lotteryName":"\\u6c5f\\u897f11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":27,"awardName":"\\u5956\\u91d1\\u7ec41782","directRet":"290","directLimitRet":500},{"lotteryId":"99303","lotteryName":"\\u5e7f\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":29,"awardName":"\\u5956\\u91d1\\u7ec41782","directRet":"290","directLimitRet":500},{"lotteryId":"99306","lotteryName":"\\u51e4\\u51f0\\u987a\\u522911\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":192,"awardName":"\\u5956\\u91d1\\u7ec41782","directRet":"290","directLimitRet":500},{"lotteryId":"99401","lotteryName":"\\u53cc\\u8272\\u7403","lotterySeriesCode":5,"lotterySeriesName":"\\u53cc\\u8272\\u7403\\u7cfb","awardGroupId":107,"awardName":"\\u53cc\\u8272\\u7403\\u5956\\u91d1\\u7ec4","directRet":"790","directLimitRet":1000},{"lotteryId":"99501","lotteryName":"\\u6c5f\\u82cf\\u5feb\\u4e09","lotterySeriesCode":6,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":188,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"590","directLimitRet":800},{"lotteryId":"99502","lotteryName":"\\u5b89\\u5fbd\\u5feb\\u4e09","lotterySeriesCode":6,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":190,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"590","directLimitRet":800},{"lotteryId":"99601","lotteryName":"\\u6c5f\\u82cf\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":189,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"290","directLimitRet":500},{"lotteryId":"99602","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u5a31\\u4e50\\u5385)","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":203,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"290","directLimitRet":500},{"lotteryId":"99603","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u81f3\\u5c0a\\u5385)","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":204,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"290","directLimitRet":500},{"lotteryId":"99604","lotteryName":"\\u5b89\\u5fbd\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":11416087,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"290","directLimitRet":500},{"lotteryId":"99605","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":207,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"290","directLimitRet":500,"threeLimitRet":150},{"lotteryId":"99701","lotteryName":"\\u516d\\u5408\\u5f69","lotterySeriesCode":9,"lotterySeriesName":"\\u516d\\u5408\\u7cfb","awardGroupId":202,"awardName":"\\u516d\\u5408\\u5f69\\u5956\\u91d1\\u7ec4","directRet":"1190","lhcFlatcode":"190","lhcYear":"90","lhcColor":"90","lhcHalfwave":"90","lhcNotin":"90","lhcContinuein23":"90","lhcContinuein4":"290","lhcContinuein5":"290","lhcContinuenotin23":"90","lhcContinuenotin4":"290","lhcContinuenotin5":"290","lhcContinuecode":"290","directLimitRet":1400,"lhcYearLimit":300,"lhcColorLimit":300,"lhcFlatcodeLimit":400,"lhcHalfwaveLimit":300,"lhcOneyearLimit":200,"lhcNotinLimit":300,"lhcContinuein23Limit":300,"lhcContinuein4Limit":500,"lhcContinuein5Limit":500,"lhcContinuenotin23Limit":300,"lhcContinuenotin4Limit":500,"lhcContinuenotin5Limit":500,"lhcContinuecodeLimit":500},{"lotteryId":"99801","lotteryName":"\\u51e4\\u51f0\\u5409\\u52293D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":223,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"290","threeoneRet":"290","directLimitRet":500,"threeLimitRet":500},{"lotteryId":"99901","lotteryName":"\\u5feb\\u5f00","lotterySeriesCode":11,"lotterySeriesName":"\\u9ad8\\u9891\\u5f69\\u7cfb",
            "awardGroupId":238,"awardName":"\\u5956\\u91d1\\u7ec41800","directLimitRet":200}],
            [{"lotteryId":"77101","lotteryName":"\\u4e50\\u5229\\u771f\\u4eba\\u5f69","lotterySeriesCode":10,"lotterySeriesName":"\\u771f\\u4eba\\u5f69\\u7968","awardGroupId":77101,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"420","directLimitRet":500},{"lotteryId":"99101","lotteryName":"\\u6b22\\u4e50\\u751f\\u8096","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":12,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":141},{"lotteryId":"99103","lotteryName":"\\u65b0\\u7586\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":19,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":143},{"lotteryId":"99104","lotteryName":"\\u5929\\u6d25\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":36,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":144},{"lotteryId":"99105","lotteryName":"\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":13,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":145},{"lotteryId":"99106","lotteryName":"\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":33,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":146},{"lotteryId":"99107","lotteryName":"\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":15,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":147},{"lotteryId":"99108","lotteryName":"3D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":101,"awardName":"\\u5956\\u91d1\\u7ec41700","directRet":"1320","threeoneRet":"920","directLimitRet":1400,"threeLimitRet":1000},{"lotteryId":"99109","lotteryName":"P5","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":102,"awardName":"\\u5956\\u91d1\\u7ec41700","directRet":"1320","threeoneRet":"920","directLimitRet":1400,"threeLimitRet":1000},{"lotteryId":"99111","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":41,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":150},{"lotteryId":"99112","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":56,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":151},{"lotteryId":"99113","lotteryName":"\\u8d85\\u7ea72000\\u79d2\\u79d2\\u5f69(APP\\u7248)","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":11416083,"awardName":"2000\\u5956\\u91d1\\u7ec4","superRet":"20","superLimitRet":100},{"lotteryId":"99114","lotteryName":"\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":208,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":152},{"lotteryId":"99115","lotteryName":"\\u51e4\\u51f0\\u6bd4\\u7279\\u5e01\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":214,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"220","threeoneRet":"220","directLimitRet":300,"threeLimitRet":300,"sysAwardGroupExtraId":153},{"lotteryId":"99116","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":228,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":154},{"lotteryId":"99117","lotteryName":"\\u51e4\\u51f0\\u91cd\\u5e86\\u5168\\u7403\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":263,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":155},{"lotteryId":"99118","lotteryName":"\\u51e4\\u51f0\\u65b0\\u7586\\u5168\\u7403\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":264,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":156},{"lotteryId":"99119","lotteryName":"\\u6cb3\\u5185\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":268,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":157},{"lotteryId":"99120","lotteryName":"\\u6cb3\\u5185\\u4e94\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":273,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":158},{"lotteryId":"99121","lotteryName":"360\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":274,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":159},{"lotteryId":"99122","lotteryName":"360\\u4e94\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":275,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","superRet":"20","directLimitRet":400,"threeLimitRet":500,"superLimitRet":100,"sysAwardGroupExtraId":160},{"lotteryId":"99123","lotteryName":"\\u8d8a\\u5357\\u798f\\u5f69","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":278,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"820","threeoneRet":"920","directLimitRet":900,"threeLimitRet":1000},{"lotteryId":"99124","lotteryName":"\\u8d8a\\u53573D\\u798f\\u5f69","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":279,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"820","threeoneRet":"920","directLimitRet":900,"threeLimitRet":1000},{"lotteryId":"99125","lotteryName":"\\u5947\\u8da3\\u817e\\u8baf\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":308,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":261},{"lotteryId":"99126","lotteryName":"\\u591a\\u5f69\\u6cb3\\u5185\\u5206\\u5206\\u5f69","lotterySeriesCode":1,"lotterySeriesName":"\\u65f6\\u65f6\\u5f69\\u7cfb","awardGroupId":316,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":262},{"lotteryId":"99201","lotteryName":"\\u5317\\u4eac\\u5feb\\u4e508","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":32,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"1920","threeoneRet":"1320","directLimitRet":2000,"threeLimitRet":1400},{"lotteryId":"99202","lotteryName":"PK10","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":206,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":164},{"lotteryId":"99203","lotteryName":"\\u98de\\u8247","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":233,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"220","directLimitRet":300,"sysAwardGroupExtraId":165},{"lotteryId":"99204","lotteryName":"PC\\u86cb\\u86cb","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":283,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"220","directLimitRet":300,"sysAwardGroupExtraId":201},{"lotteryId":"99205","lotteryName":"168\\u98de\\u8247","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":293,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"220","directLimitRet":300,"sysAwardGroupExtraId":241},{"lotteryId":"99206","lotteryName":"\\u798f\\u5f69\\u5feb\\u4e508","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":298,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"1920","threeoneRet":"1320","directLimitRet":2000,"threeLimitRet":1400},{"lotteryId":"99207","lotteryName":"\\u5feb\\u4e508\\u5168\\u7403\\u5f69","lotterySeriesCode":4,"lotterySeriesName":"\\u57fa\\u8bfa\\u7cfb","awardGroupId":303,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"1920","threeoneRet":"1320","directLimitRet":2000,"threeLimitRet":1400},{"lotteryId":"99301","lotteryName":"\\u5c71\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":24,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":166},{"lotteryId":"99302","lotteryName":"\\u6c5f\\u897f11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":27,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":167},{"lotteryId":"99303","lotteryName":"\\u5e7f\\u4e1c11\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":29,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":168},{"lotteryId":"99306","lotteryName":"\\u51e4\\u51f0\\u987a\\u522911\\u90095","lotterySeriesCode":3,"lotterySeriesName":"11\\u90095\\u7cfb","awardGroupId":192,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":171},{"lotteryId":"99401","lotteryName":"\\u53cc\\u8272\\u7403","lotterySeriesCode":5,"lotterySeriesName":"\\u53cc\\u8272\\u7403\\u7cfb","awardGroupId":107,"awardName":"\\u53cc\\u8272\\u7403\\u5956\\u91d1\\u7ec4","directRet":"1420","directLimitRet":1500},{"lotteryId":"99501","lotteryName":"\\u6c5f\\u82cf\\u5feb\\u4e09","lotterySeriesCode":6,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":188,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":221},{"lotteryId":"99502","lotteryName":"\\u5b89\\u5fbd\\u5feb\\u4e09","lotterySeriesCode":6,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":190,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"420","directLimitRet":500,"sysAwardGroupExtraId":222},{"lotteryId":"99601","lotteryName":"\\u6c5f\\u82cf\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":189,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"820","directLimitRet":900},{"lotteryId":"99602","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u5a31\\u4e50\\u5385)","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":203,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"820","directLimitRet":900},{"lotteryId":"99603","lotteryName":"\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u81f3\\u5c0a\\u5385)","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":204,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"820","directLimitRet":900},{"lotteryId":"99604","lotteryName":"\\u5b89\\u5fbd\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":11416087,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"820","directLimitRet":900},{"lotteryId":"99605","lotteryName":"\\u51e4\\u51f0\\u987a\\u5229\\u9ab0\\u5b9d","lotterySeriesCode":7,"lotterySeriesName":"\\u5feb\\u4e50\\u5f69\\u7cfb","awardGroupId":207,"awardName":"\\u6df7\\u5408\\u5956\\u91d1\\u7ec4","directRet":"820","threeoneRet":"70","directLimitRet":900,"threeLimitRet":150},{"lotteryId":"99701","lotteryName":"\\u516d\\u5408\\u5f69","lotterySeriesCode":9,"lotterySeriesName":"\\u516d\\u5408\\u7cfb","awardGroupId":202,"awardName":"\\u516d\\u5408\\u5f69\\u5956\\u91d1\\u7ec4","directRet":"1320","lhcFlatcode":"320","lhcYear":"220","lhcColor":"220","lhcHalfwave":"220","lhcOneyear":"120","lhcNotin":"220","lhcContinuein23":"220","lhcContinuein4":"420","lhcContinuein5":"420","lhcContinuenotin23":"220","lhcContinuenotin4":"420","lhcContinuenotin5":"420","lhcContinuecode":"420","directLimitRet":1400,"lhcYearLimit":300,"lhcColorLimit":300,"lhcFlatcodeLimit":400,"lhcHalfwaveLimit":300,"lhcOneyearLimit":200,"lhcNotinLimit":300,"lhcContinuein23Limit":300,"lhcContinuein4Limit":500,"lhcContinuein5Limit":500,"lhcContinuenotin23Limit":300,"lhcContinuenotin4Limit":500,"lhcContinuenotin5Limit":500,"lhcContinuecodeLimit":500},{"lotteryId":"99801","lotteryName":"\\u51e4\\u51f0\\u5409\\u52293D","lotterySeriesCode":2,"lotterySeriesName":"3D\\u7cfb","awardGroupId":223,"awardName":"\\u5956\\u91d1\\u7ec41900","directRet":"320","threeoneRet":"420","directLimitRet":400,"threeLimitRet":500,"sysAwardGroupExtraId":180},{"lotteryId":"99901","lotteryName":"\\u5feb\\u5f00","lotterySeriesCode":11,"lotterySeriesName":"\\u9ad8\\u9891\\u5f69\\u7cfb","awardGroupId":238,"awardName":"\\u5956\\u91d1\\u7ec41800","directRet":"120","directLimitRet":200}]
            
            ]
            , 1: [[{"lotteryId": "77101", "lotterySeriesCode": 10, "lotterySeriesName": "\\\\u771f\\\\u4eba\\\\u5f69\\\\u7968", "awardGroupId": 77101, 
                    "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99101", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 12, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99103", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 19, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99104", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 36, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 405, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99105", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 13, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99106", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 33, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99107", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 15, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99108", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\\\u7cfb", "awardGroupId": 101, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41700", "directLimitRet": 950, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99109", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\\\u7cfb", "awardGroupId": 102, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41700", "directLimitRet": 950, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99111", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 41, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99112", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 56, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99113", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 205, "awardName": "2000\\\\u5956\\\\u91d1\\\\u7ec4", "superLimitRet": 90, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99114", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 208, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99115", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 219, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41000", "directLimitRet": 4300, "threeLimitRet": 4300, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99116", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 231, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99117", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 248, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99118", "lotterySeriesCode": 1, "lotterySeriesName": "\\\\u65f6\\\\u65f6\\\\u5f69\\\\u7cfb", "awardGroupId": 249, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99201", "lotterySeriesCode": 4, "lotterySeriesName": "\\\\u57fa\\\\u8bfa\\\\u7cfb", "awardGroupId": 32, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99202", "lotterySeriesCode": 4, "lotterySeriesName": "\\\\u57fa\\\\u8bfa\\\\u7cfb", "awardGroupId": 206, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99203", "lotterySeriesCode": 4, "lotterySeriesName": "\\\\u57fa\\\\u8bfa\\\\u7cfb", "awardGroupId": 238, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41000", "directLimitRet": 4300, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99301", "lotterySeriesCode": 3, "lotterySeriesName": "11\\\\u90095\\\\u7cfb", "awardGroupId": 24, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41782", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99302", "lotterySeriesCode": 3, "lotterySeriesName": "11\\\\u90095\\\\u7cfb", "awardGroupId": 26, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41620", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99303", "lotterySeriesCode": 3, "lotterySeriesName": "11\\\\u90095\\\\u7cfb", "awardGroupId": 29, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41782", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99306", "lotterySeriesCode": 3, "lotterySeriesName": "11\\\\u90095\\\\u7cfb", "awardGroupId": 192, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41782", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99401", "lotterySeriesCode": 5, "lotterySeriesName": "\\\\u53cc\\\\u8272\\\\u7403\\\\u7cfb", "awardGroupId": 107, "awardName": "\\\\u53cc\\\\u8272\\\\u7403\\\\u5956\\\\u91d1\\\\u7ec4", "directLimitRet": 950, "threeLimitRet": 950, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99501", "lotterySeriesCode": 6, "lotterySeriesName": "\\\\u5feb\\\\u4e50\\\\u5f69\\\\u7cfb", "awardGroupId": 188, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99502", "lotterySeriesCode": 6, "lotterySeriesName": "\\\\u5feb\\\\u4e50\\\\u5f69\\\\u7cfb", "awardGroupId": 190, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99601", "lotterySeriesCode": 7, "lotterySeriesName": "\\\\u5feb\\\\u4e50\\\\u5f69\\\\u7cfb", "awardGroupId": 189, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99602", "lotterySeriesCode": 7, "lotterySeriesName": "\\\\u5feb\\\\u4e50\\\\u5f69\\\\u7cfb", "awardGroupId": 203, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99604", "lotterySeriesCode": 7, "lotterySeriesName": "\\\\u5feb\\\\u4e50\\\\u5f69\\\\u7cfb", "awardGroupId": 213, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99605", "lotterySeriesCode": 7, "lotterySeriesName": "\\\\u5feb\\\\u4e50\\\\u5f69\\\\u7cfb", "awardGroupId": 207, "awardName": "\\\\u6df7\\\\u5408\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99701", "lotterySeriesCode": 9, "lotterySeriesName": "\\\\u516d\\\\u5408\\\\u7cfb", "awardGroupId": 202, "awardName": "\\\\u516d\\\\u5408\\\\u5f69\\\\u5956\\\\u91d1\\\\u7ec4", "directRet": 0, "threeoneRet": 0, "superRet": 0, "lhcYear": 0, "lhcColor": 0, "lhcFlatcode": 0, "lhcHalfwave": 0, "lhcOneyear": 0, "lhcNotin": 0, "lhcContinuein23": 0, "lhcContinuein4": 0, "lhcContinuein5": 0, "lhcContinuenotin23": 0, "lhcContinuenotin4": 0, "lhcContinuenotin5": 0, "lhcContinuecode": 0}, {"lotteryId": "99801", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\\\u7cfb", "awardGroupId": 223, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", "directLimitRet": 450, "threeLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}, {"lotteryId": "99901", "lotterySeriesCode": 11, "lotterySeriesName": "\\\\u9ad8\\\\u9891\\\\u5f69\\\\u7cfb", "awardGroupId": 243, "awardName": "\\\\u5956\\\\u91d1\\\\u7ec41800", 
                    "directLimitRet": 450, "directRet": 0, "threeoneRet": 0, "superRet": 0}],
                  [{"lotteryId": "77101", "lotteryName": "\\u4e50\\u5229\\u771f\\u4eba\\u5f69", "lotterySeriesCode": 10, "lotterySeriesName": "\\u771f\\u4eba\\u5f69\\u7968", "awardGroupId": 77101, "awardName": "\\u5956\\u91d1\\u7ec41800", "directRet": "490", "directLimitRet": 500}, {"lotteryId": "99101", "lotteryName": "\\u6b22\\u4e50\\u751f\\u8096", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 12, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 1}, {"lotteryId": "99103", "lotteryName": "\\u65b0\\u7586\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 19, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 3}, {"lotteryId": "99104", "lotteryName": "\\u5929\\u6d25\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 36, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 4}, {"lotteryId": "99105", "lotteryName": "\\u9ed1\\u9f99\\u6c5f\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 13, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 5}, {"lotteryId": "99106", "lotteryName": "\\u51e4\\u51f0\\u4e50\\u5229\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 33, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 6}, {"lotteryId": "99107", "lotteryName": "\\u4e0a\\u6d77\\u65f6\\u65f6\\u4e50", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 15, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 7}, {"lotteryId": "99108", "lotteryName": "3D", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 101, "awardName": "\\u5956\\u91d1\\u7ec41700", "directRet": "1290", "threeoneRet": "790", "directLimitRet": 1300, "threeLimitRet": 800}, {"lotteryId": "99109", "lotteryName": "P5", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 102, "awardName": "\\u5956\\u91d1\\u7ec41700", "directRet": "1290", "threeoneRet": "790", "directLimitRet": 1300, "threeLimitRet": 800}, {"lotteryId": "99111", "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 41, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 8}, {"lotteryId": "99112", "lotteryName": "\\u51e4\\u51f0\\u987a\\u5229\\u79d2\\u79d2\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 56, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 9}, {"lotteryId": "99113", "lotteryName": "\\u8d85\\u7ea72000\\u79d2\\u79d2\\u5f69(APP\\u7248)", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 205, "awardName": "2000\\u5956\\u91d1\\u7ec4", "superRet": "90", "superLimitRet": 100}, {"lotteryId": "99114", "lotteryName": "\\u817e\\u8baf\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 208, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 10}, {"lotteryId": "99115", "lotteryName": "\\u51e4\\u51f0\\u6bd4\\u7279\\u5e01\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 219, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 11}, {"lotteryId": "99116", "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u65f6\\u65f6\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 231, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 12}, {"lotteryId": "99117", "lotteryName": "\\u51e4\\u51f0\\u91cd\\u5e86\\u5168\\u7403\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 248, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 13}, {"lotteryId": "99118", "lotteryName": "\\u51e4\\u51f0\\u65b0\\u7586\\u5168\\u7403\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 249
                    , "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 14}, {"lotteryId": "99119", "lotteryName": "\\u6cb3\\u5185\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 253, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 15}, {"lotteryId": "99120", "lotteryName": "\\u6cb3\\u5185\\u4e94\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 254, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 16}, {"lotteryId": "99121", "lotteryName": "360\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 255, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 17}, {"lotteryId": "99122", "lotteryName": "360\\u4e94\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 256, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "superRet": "90", "directLimitRet": 300, "threeLimitRet": 300, "superLimitRet": 100, "sysAwardGroupExtraId": 18}, {"lotteryId": "99123", "lotteryName": "\\u8d8a\\u5357\\u798f\\u5f69", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 258, "awardName": "\\u5956\\u91d1\\u7ec41800", "directRet": "740", "threeoneRet": "740", "directLimitRet": 800, "threeLimitRet": 800}, {"lotteryId": "99124", "lotteryName": "\\u8d8a\\u53573D\\u798f\\u5f69", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 259, "awardName": "\\u5956\\u91d1\\u7ec41800", "directRet": "740", "threeoneRet": "740", "directLimitRet": 800, "threeLimitRet": 800}, {"lotteryId": "99125", "lotteryName": "\\u5947\\u8da3\\u817e\\u8baf\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 283, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 800, "threeLimitRet": 800 ,"sysAwardGroupExtraId": 101}, {"lotteryId": "99126", "lotteryName": "\\u591a\\u5f69\\u6cb3\\u5185\\u5206\\u5206\\u5f69", "lotterySeriesCode": 1, "lotterySeriesName": "\\u65f6\\u65f6\\u5f69\\u7cfb", "awardGroupId": 288, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 102}, {"lotteryId": "99201", "lotteryName": "\\u5317\\u4eac\\u5feb\\u4e508", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 32, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "1790", "threeoneRet": "1290", "directLimitRet": 1800, "threeLimitRet": 1300}, {"lotteryId": "99202", "lotteryName": "PK10", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 206, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 19}, {"lotteryId": "99203", "lotteryName": "\\u98de\\u8247", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 243, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 20}, {"lotteryId": "99204", "lotteryName": "PC\\u86cb\\u86cb", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 263, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 61}, {"lotteryId": "99205", "lotteryName": "168\\u98de\\u8247", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 268, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 81}, {"lotteryId": "99206", "lotteryName": "\\u798f\\u5f69\\u5feb\\u4e508", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 273, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "1790", "threeoneRet": "1290", "directLimitRet": 1800, "threeLimitRet": 1300}, {"lotteryId": "99207", "lotteryName": "\\u5feb\\u4e508\\u5168\\u7403\\u5f69", "lotterySeriesCode": 4, "lotterySeriesName": "\\u57fa\\u8bfa\\u7cfb", "awardGroupId": 278, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "1790", "threeoneRet": "1290", "directLimitRet": 1800, "threeLimitRet": 1300}, {"lotteryId": "99301", "lotteryName": "\\u5c71\\u4e1c11\\u90095", "lotterySeriesCode": 3, "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 24, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 21}, {"lotteryId": "99302", "lotteryName": "\\u6c5f\\u897f11\\u90095", "lotterySeriesCode": 3, "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 27, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 22}, {"lotteryId": "99303", "lotteryName": "\\u5e7f\\u4e1c11\\u90095", "lotterySeriesCode": 3, "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 29, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 23}, {"lotteryId": "99306", "lotteryName": "\\u51e4\\u51f0\\u987a\\u522911\\u90095", "lotterySeriesCode": 3, "lotterySeriesName": "11\\u90095\\u7cfb", "awardGroupId": 192, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 26
                    }, {"lotteryId": "99401", "lotteryName": "\\u53cc\\u8272\\u7403", "lotterySeriesCode": 5, "lotterySeriesName": "\\u53cc\\u8272\\u7403\\u7cfb", "awardGroupId": 107, "awardName": "\\u53cc\\u8272\\u7403\\u5956\\u91d1\\u7ec4", "directRet": "1290", "directLimitRet": 1300}, {"lotteryId": "99501", "lotteryName": "\\u6c5f\\u82cf\\u5feb\\u4e09", "lotterySeriesCode": 6, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 188, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 41
                    }, {"lotteryId": "99502", "lotteryName": "\\u5b89\\u5fbd\\u5feb\\u4e09", "lotterySeriesCode": 6, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 190, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "290", "directLimitRet": 300, "sysAwardGroupExtraId": 42}, {"lotteryId": "99601", "lotteryName": "\\u6c5f\\u82cf\\u9ab0\\u5b9d", "lotterySeriesCode": 7, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 189, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "790", "directLimitRet": 800}, {"lotteryId": "99602", "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u5a31\\u4e50\\u5385)", "lotterySeriesCode": 7, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 203, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "740", "directLimitRet": 800}, {"lotteryId": "99603", "lotteryName": "\\u51e4\\u51f0\\u5409\\u5229\\u9ab0\\u5b9d(\\u81f3\\u5c0a\\u5385)", "lotterySeriesCode": 7, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 204, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "740", "directLimitRet": 800}, {"lotteryId": "99604", "lotteryName": "\\u5b89\\u5fbd\\u9ab0\\u5b9d", "lotterySeriesCode": 7, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 213, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "740", "directLimitRet": 800}, {"lotteryId": "99605", "lotteryName": "\\u51e4\\u51f0\\u987a\\u5229\\u9ab0\\u5b9d", "lotterySeriesCode": 7, "lotterySeriesName": "\\u5feb\\u4e50\\u5f69\\u7cfb", "awardGroupId": 207, "awardName": "\\u6df7\\u5408\\u5956\\u91d1\\u7ec4", "directRet": "700", "threeoneRet": "100", "directLimitRet": 800, "threeLimitRet": 150}, {"lotteryId": "99701", "lotteryName": "\\u516d\\u5408\\u5f69", "lotterySeriesCode": 9, "lotterySeriesName": "\\u516d\\u5408\\u7cfb", "awardGroupId": 202, "awardName": "\\u516d\\u5408\\u5f69\\u5956\\u91d1\\u7ec4", "directRet": "1390", "lhcFlatcode": "390", "lhcYear": "290", "lhcColor": "290", "lhcHalfwave": "290", "lhcOneyear": "190", "lhcNotin": "290", "lhcContinuein23": "290", "lhcContinuein4": "490", "lhcContinuein5": "490", "lhcContinuenotin23": "290", "lhcContinuenotin4": "490", "lhcContinuenotin5": "490", "lhcContinuecode": "490", "directLimitRet": 1400, "lhcYearLimit": 300, "lhcColorLimit": 300, "lhcFlatcodeLimit": 400, "lhcHalfwaveLimit": 300, "lhcOneyearLimit": 200, "lhcNotinLimit": 300, "lhcContinuein23Limit": 300, "lhcContinuein4Limit": 500, "lhcContinuein5Limit": 500, "lhcContinuenotin23Limit": 300, "lhcContinuenotin4Limit": 500, "lhcContinuenotin5Limit": 500, "lhcContinuecodeLimit": 500}, {"lotteryId": "99801", "lotteryName": "\\u51e4\\u51f0\\u5409\\u52293D", "lotterySeriesCode": 2, "lotterySeriesName": "3D\\u7cfb", "awardGroupId": 223, "awardName": "\\u5956\\u91d1\\u7ec41900", "directRet": "290", "threeoneRet": "290", "directLimitRet": 300, "threeLimitRet": 300, "sysAwardGroupExtraId": 34}, {"lotteryId": "99901", "lotteryName": "\\u5feb\\u5f00", "lotterySeriesCode": 11, "lotterySeriesName": "\\u9ad8\\u9891\\u5f69\\u7cfb", "awardGroupId": 238, "awardName": "\\u5956\\u91d1\\u7ec41800", "directRet": "190", "directLimitRet": 200}]
                 ]
                        }
            domain_dict = {0: "http://www.dev02.com",
                           1: "http:\\\\/\\\\/www2.joy188.com:888"
                          }
            OpenLink_data = {"type": 1, "days": -1, "infos":info_dict[envs][i],
                            "memo": "autoTest", "setUp": 1,"domain": domain_dict[envs]}
            param_data.update(OpenLink_data)
            data_['body']['param'] = param_data
            r = requests.post(env+'information/doRetSetting',data=json.dumps(data_),headers=App_header) 
            if r.json()['head']['status'] == 0:
                print('開戶連結創立成功')
                data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"",
                "sessionId":token_[user]},"body":{"param":{"CGISESSID":token_[user],"app_id":"10","come_from":"4",
                "appname":"1"},"pager":{"startNo":"","endNo":""}}}                                                                                     

                r = requests.post(env+'information/openLinkList',data=json.dumps(data_),headers=App_header) 
                result = r.json()['body']['result']['list'][0]
                #print(result)
                regCode = result['regCode']#回傳開戶 的 id
                new_token = result['urlstring'].split('token=')[1]#回傳 開戶 的token
                exp = result['urlstring'].split('exp=')[1].split('&')[0]
                pid = result['urlstring'].split('pid=')[1].split('&')[0]
                token_result[i] = {'regCode': regCode ,'new_token':new_token,'exp': exp, 'pid':pid} 
                
                #token_result[i] 
                print('%s 的 開戶連結'%user)
                print("註冊連結: %s, 註冊碼: %s, 建置於: %s"%(result['urlstring'],result['regCode']
                ,result['start']))
            else:
                print('創立失敗')
    @staticmethod
    def test_AppRegister():
        '''APP註冊'''
        #print(new_token)
        global AppRegister_user # 到時 會用這用戶 來綁銀行卡 ,安全問題/密碼
        
        for i in range(2):
            if i ==0:
                print('一般: ')
                user = env_dict['一般帳號'][envs]
                user_random = random.randint(1000,9999999)
            else:
                print('合營: ')
                user = env_dict['APP合營'][envs]
                user_random = random.randint(10,99999)
            account_dict = {0:['hsiehapp%s'%user_random,'hsiehwinapp%s'%user_random],
                            1:['kerrapp%s'%user_random,'kerrwinapp%s'%user_random]}
            AppRegister_user = account_dict[envs][i]
            data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":""},
            "body":{"param":{"token": token_result[i]['new_token'],"accountName":AppRegister_user,
            "password":  loginpasssource,"jointVenture": i,
            "cellphone":"", "qqAccount":"","wechat":"","id":int(token_result[i]['regCode']),
                    "exp":token_result[i]['exp'],"pid":int(token_result[i]['pid']),"qq":'',
            "ip":"192.168.137.182","app_id":"10", "come_from":"4","appname":"1"},
            "pager":{"startNo":"","endNo":""}}} 

            r = requests.post(env+'user/register',data=json.dumps(data_),headers=App_header) 
            if r.json()['head']['status'] == 0:
                print('%s 註冊成功, 上級用戶: %s'%(AppRegister_user ,user))
            else:
                print('註冊失敗')
        login_data = Joy188Test3.Iapi_LoginData(username=AppRegister_user,uuid_=uuid,
                                                passwd=loginpasssource,joint=1)
        r = requests.post(env+'front/login',data=json.dumps(login_data),headers= App_header)
        # 需登入新的用戶, 產生token ,後續綁卡 用
        token = r.json()['body']['result']['token']
        userid = r.json()['body']['result']['userid']
        token_.setdefault(AppRegister_user,token)
        userid_.setdefault(AppRegister_user,userid)
    
    @staticmethod
    def test_IapiSecurityPass():
        '''APP設置安全密碼'''
        user = AppRegister_user 
        data_ = Joy188Test3.IapiData(user)
        global passwd_info
        passwd_info = {
            0:["cd85fad371fd1c668b01c5d5f8d91354","b232f1fde130e8e27f5a9bcdb7b1b2e0"],
            1:["c229c901ef92cd889a2bc850f72be30b","249d9c0cdec6df9aa51753af03adeaac"]
        }# list[0] 是安全密碼, 1 是安全問題
        safePass  = {"newpass2": passwd_info[envs][0],
        "confirmNewpass2":passwd_info[envs][0]}
        param_data = data_["body"]["param"]
        param_data.update(safePass)
        data_['body']['param'] = param_data
        r = requests.post(env+'security/addSecpass',data=json.dumps(data_),
                          headers=App_header)# 安全密碼設定
        if r.json()['head']['status'] == 0:
            print('%s 安全密碼設定成功'%user)
        else:
            print('安全密碼設置確認')
    @staticmethod
    def test_IapiSecurityQues():
        '''APP設置安全問題'''
        user = AppRegister_user 
        data_ = Joy188Test3.IapiData(user)
        quests = [{"qid":1,"question":"\\u6211\\u5ba0\\u7269\\u7684\\u540d\\u5b57\\uff1f",
          "qpwd":passwd_info[envs][1] ,"isUsed":0},
         {"qid":2,"question":"\\u6211\\u6700\\u4eb2\\u5bc6\\u7684\\u670b\\u53cb\\u662f\\uff1f",
          "qpwd": passwd_info[envs][1],"isUsed":0},
         {"qid":3,"question":"\\u6211\\u6700\\u559c\\u6b22\\u7684\\u6f14\\u5458\\uff1f",
          "qpwd": passwd_info[envs][1],"isUsed":0}]# 安全問題
        param_data = data_["body"]["param"]
        param_data['quests'] = quests
        data_['body']['param'] = param_data
        r = requests.post(env+'security/safeQuestSet',data=json.dumps(data_),
                          headers=App_header)# 安全密碼設定
        if r.json()['head']['status'] == 0:
            print('%s 安全問題設定成功'%user)
        else:
            print('安全問題設置確認')
        
    @staticmethod
    def test_IapiCardBind():
        '''APP銀行綁卡'''
        global card
        while True:
            user = AppRegister_user 
            data_ = Joy188Test3.IapiData(user)#從新生成初始 data
            fake = Factory.create()
            card = (fake.credit_card_number(card_type='visa16'))#產生一個16位的假卡號
            bind_data = {"bankId":1,"bank":"安璞分行",
             "province":"內湖省","city":"內湖市",
                         "branch":"安璞銀行",
             "accountName":"kerr","account":"%s"%card,
            "secpass":passwd_info[envs][0],"bindCardType":0,"digitalWalletNumber":""}# 綁卡資訊
            param_data = data_["body"]["param"]
            param_data.update(bind_data)
            data_['body']['param'] = param_data
            r = requests.post(env+'security/cardBindingCommit',data=json.dumps(data_),
                              headers=App_header)# 綁一般銀酐卡
            if r.json()['head']['status'] == 0:
                print('%s 一般綁卡成功, 卡號: %s'%(user,card))
            else:
                print('一般綁卡確認')
                break
            print('-----------------------------')
            for key in usdt_dict.keys():
                data_ = Joy188Test3.IapiData(user)#從新生成初始 data 
                param_data = data_["body"]["param"]
                usdt_card = usdt_dict[key][0]
                bind_data = {"bankId":1,"bank":"安璞分行",
                "province":"","city":"",
                "branch":"","accountName":"","account":"",
                "secpass":passwd_info[envs][0],"bindCardType":2,
                "digitalWalletNumber": usdt_card,
                "protocol": key  }# usdt
                param_data.update(bind_data)
                data_['body']['param'] = param_data
                r = requests.post(env+'security/cardBindingCommit',data=json.dumps(data_),
                                headers=App_header)# 綁數字貨幣
                if r.json()['head']['status'] == 0:
                    print('幣種協議: %s'%key)
                    print('usdt 綁卡成功, 卡號: %s'%(usdt_card))
                else:
                    print('數字綁卡確認')
            break
    @staticmethod
    def test_IapiLockCard():
        '''APP綁卡立即鎖定'''
        user = AppRegister_user 
        data_ = Joy188Test3.IapiData(user)#從新生成初始 data
        lockid = Joy188Test.select_Lockid(Joy188Test.get_conn(envs),user)#　lockid 鎖卡
        param_data = data_["body"]["param"]
        param_data['lockedId'] = lockid[0] 
        data_['body']['param'] = param_data
        r = requests.post(env+'security/bankCardNowLock',data=json.dumps(data_),
                              headers=App_header)# 鎖定卡
        if r.json()['head']['status'] == 0:
            print('%s 卡號: %s 鎖定成功'%(user,card))
        else:
            print('綁卡鎖定確認')
        
    @staticmethod
    def test_IapiWithDraw():
        '''APP提現發起'''
        user =  env_dict['一般帳號'][envs]
        data_ = Joy188Test3.IapiData(user)
        money = random.randint(10,20)#  隨機金額
        bank_info = {
            0: ["8642018#2",8642018], 1:["25640091#7",25640091]
        }# 銀行卡資訊
        
        withdraw_data = {"bankinfo":bank_info[envs][0],"money":money,"originalCurrencyAmount":10}
        param_data = data_["body"]["param"]
        param_data.update(withdraw_data)
        data_['body']['param'] = param_data
        r = requests.post(env+'withdraw/verify',data=json.dumps(data_),headers=App_header)# 發起提限

        data_ = Joy188Test3.IapiData(user)#在呼叫一次  ,提限確認 需新的data
        commit_data = {"bindId":bank_info[envs][1],"money":money,"secpwd":
                       passwd_info[envs][0],
        "questionId":1,"questionpwd":passwd_info[envs][1],"serviceFeeFlag":0,
                "originalCurrencyAmount":10,"ipAddr":"168627247"} # 提限確認 ,安全問題 安全密碼
        param_data = data_["body"]["param"]
        param_data.update(commit_data)
        data_['body']['param'] = param_data
        r = requests.post(env+'withdraw/commit',data=json.dumps(data_),headers=App_header)# 發起提限

        if r.json()['head']['status'] == 0:
            sn = Joy188Test.select_WithDrawSn(Joy188Test.get_conn(envs),userid_[user])
            print('%s 發起提現,金額: %s 成功,單號: %s'%(user,money,sn))
        else:
            print('%s 發起提現失敗'%(user))

        
    @staticmethod
    def test_AppBalance():
        '''APP 4.0/第三方餘額'''
        threads = []
        user = env_dict['APP帳號'][envs]
        data_ =  Joy188Test3.IapiData(user)
        print('帳號: %s'%user)
        for third in third_list:
            if third == 'shaba':
                third = 'sb'
            t = threading.Thread(target=Joy188Test.APP_SessionPost,args=(third,'balance',data_))
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        r = requests.post(env+'/information/getBalance',data=json.dumps(data_),headers=App_header)
        balance =  r.json()['body']['result']['balance']
        print('4.0餘額: %s'%balance)


    @staticmethod
    def test_ApptransferIn():
        '''APP轉入'''
        user = env_dict['APP帳號'][envs]
        data_ =  Joy188Test3.IapiData(user)
        data_['body']['param']['amount'] = 10

        statu_list = []
        print('帳號: %s'%user)
        #third_list = ['gns','sb','im','ky','lc','city']
        for third in third_list:
            tran_url = 'Gns' if third=='gns' else 'Thirdly' # gns規則不同
            if third == 'shaba':
                third = 'sb'
            r = requests.post(env+'/%s/transferTo%s'%(third,tran_url),data=json.dumps(data_)
                              ,headers=App_header)
            #print(r.json())#列印出來
            status = r.json()['body']['result']['status']
            if status == 'Y':
                print('轉入%s金額 10'%third)
                statu_list.append(third)
            else:
                print('%s轉入失敗'%third)
        for third in statu_list:
            if third == 'sb':
                third = 'shaba'
            thirdly_status = Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),
                                                     tran_type=0,
                third=third,user=user)# 先確認資料轉帳傳泰
            #print(thirdly_status)
            staut_mapping = thirdly_status[0][1]
            msg = '%s 轉帳單號: %s . '%(third,thirdly_status[0][0])
            if staut_mapping == '2':
                msg = msg +" 狀態成功"
            else:
                msg = msg +" 狀態待確認"
            sleep(3)
            print(msg)
            
            
        Joy188Test3.test_AppBalance()
    @staticmethod
    def test_ApptransferOut():
        '''APP轉出'''
        user = env_dict['APP帳號'][envs]
        data_ =  Joy188Test3.IapiData(user)
        data_['body']['param']['amount'] = 10

        statu_list = []
        print('帳號: %s'%user)
        for third in third_list:# PC 沙巴 是 shaba , iapi 是 sb
            if third == 'shaba':
                third = 'sb'
            r = requests.post(env+'/%s/transferToFF'%third,data=json.dumps(data_),headers=App_header)
            #print(r.json())
            status = r.json()['body']['result']['status']
            if status == 'Y':
                print('%s轉出金額 10'%third)
                statu_list.append(third)
            else:
                print('%s轉出失敗'%third)
        for third in statu_list:
            if third == 'sb':
                third = 'shaba'
            thirdly_status= Joy188Test.thirdly_tran(Joy188Test.my_con(evn=envs,third=third),
            tran_type=1,third=third,user=user)# 先確認資料轉帳傳泰
            staut_mapping = thirdly_status[0][1]
            msg = '%s 轉帳單號: %s . '%(third,thirdly_status[0][0])
            if staut_mapping == '2':
                msg = msg +" 狀態成功"
            else:
                msg = msg +" 狀態待確認"
            sleep(3)
            print(msg)

        Joy188Test3.test_AppBalance()
    @staticmethod
    def test_AppcheckPassword():
        '''更換密碼'''
        user = env_dict['玩家'][envs]
        print('用戶: %s'%user)
        password = Joy188Test.select_userPass(Joy188Test.get_conn(envs),user)
        if password[0] == 'fa0c0fd599eaa397bd0daba5f47e7151':#123qwe
            newpass = "3bf6add0828ee17c4603563954473c1e"#amberrd  新密碼
            oldpass = 'fa0c0fd599eaa397bd0daba5f47e7151'# 原本的密碼
            msg = '新密碼為amberrd'
            print('舊密碼 為123qwe')
        else:# 密碼為amberrd
            newpass = "fa0c0fd599eaa397bd0daba5f47e7151"
            oldpass = "3bf6add0828ee17c4603563954473c1e"
            msg = '新密碼為123qwe'
            print('舊密碼為 amberrd')
        data_ = {"head":{"sowner":"","rowner":"","msn":"","msnsn":"","userId":"","userAccount":"",
        "sessionId":token_[user]},"body":{"pager":{"startNo":"1","endNo":"99999"},
        "param":{"CGISESSID":token_[user],"newpass":newpass,
        "oldpass": oldpass,
        #new,comfirm皆為新密買  ,old為救密碼
        "confirmNewpass":newpass,"app_id":"9","come_from":"3","appname":"1"}}}
        #3bf6add0828ee17c4603563954473c1e 為amberrd 加密 , # fa0c0fd599eaa397bd0daba5f47e7151 為123qwe
        r = requests.post(env+'/security/modifyLoginpass/',data=json.dumps(data_),
                          headers=App_header)#確認密碼皆口
        #print(r.text)
        if r.json()['head']['status'] == 0:
            print("密碼更換成功"+msg)
            print('重新登入')
            login_data = {
            "head": {
                "sessionId": ''
            },
            "body": {
                "param": {
                "username": user+"|"+ 'f009b92edc4333fd',
                "loginpassSource":newpass,
                "appCode": 1,
                "uuid": 'f009b92edc4333fd',
                "loginIp": 2130706433,
                "device": 2,
                "app_id": 9,
                "come_from": "3",
                "appname": "1"
            }
            }
            }
            
            r = requests.post(env+'front/login',data=json.dumps(login_data),headers=App_header)
            if r.json()['head']['status'] ==0:
                print('登入成功')
        else:
            print(r.json())
            print('失敗')
    


# In[ ]:





# In[47]:


'''
自動化測試報告   , test_LotterySubmit 執行trunk腳本時, 需注意  req_post_submit 的cookie和 lottery是否更換
'''

envs = 1# 0 dev , 1 : 188
env_name = {0: 'dev',1: '188' }
# 追號 先測試 用
if __name__ == '__main__':
    suite = unittest.TestSuite()

    tests = [Joy188Test('test_Login'),Joy188Test('test_redEnvelope'),Joy188Test('test_LotterySubmit',account=env_dict['一般帳號'][envs]),
             Joy188Test('test_CancelOrder'),Joy188Test('test_LotteryPlanSubmit'),
             Joy188Test('test_ThirdHome'),Joy188Test('test_188'),Joy188Test('test_chart'),
    Joy188Test('test_thirdBalance'),Joy188Test('test_transferin'),Joy188Test('test_transferout'),
    Joy188Test('test_tranUser'),Joy188Test('test_ChargeLimit')]
    
    tests2 = [Joy188Test2('test_safepersonal'),Joy188Test2('test_applycenter')
    ,Joy188Test2('test_safecenter'),Joy188Test2('test_bindcard'),Joy188Test2('test_bindcardUs')]
      
    app = [Joy188Test3('test_iapiLogin'),Joy188Test3('test_iapiSubmit'),
           Joy188Test3('test_IapiCancelSubmit'),Joy188Test3('test_IapiPlanSubmit'),
           Joy188Test3('test_OpenLink'),
           Joy188Test3('test_AppRegister'),
           Joy188Test3('test_IapiSecurityPass'),Joy188Test3('test_IapiSecurityQues'),
           Joy188Test3('test_IapiCardBind'),Joy188Test3('test_IapiLockCard'),
           Joy188Test3('test_IapiRecharge'),
           Joy188Test3('test_IapiWithDraw'),Joy188Test3('test_iapiCheckIn'),
           Joy188Test3('test_AppBalance'),
           Joy188Test3('test_ApptransferIn'),Joy188Test3('test_ApptransferOut'),
           Joy188Test3('test_AppcheckPassword'),Joy188Test3('test_IapiTransfer'),
           Joy188Test3('test_IapiOgAgent'),Joy188Test3('test_IapiNewAgent')
          ]

    test = [Joy188Test('test_Login'),Joy188Test('test_redEnvelope')] 
    
    #suite.addTests(test)


    suite.addTests(tests)
    suite.addTests(tests2)
    suite.addTests(app)


    now = time.strftime('%Y_%m_%d^%H-%M-%S')
    filename = now + u'自動化測試' + '.html'
    fp = open(filename, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title=u'測試報告',
            description=u'環境: %s '%env_name[envs]
            )
    runner.run(suite)
    fp.close()


# In[46]:


envs = 1# 0 dev , 1 : 188
env_name = {0: 'dev',1: '188' }
# 追號 先測試 用
if __name__ == '__main__':
    suite = unittest.TestSuite()

    tests = [Joy188Test('test_188')]
    
    suite.addTests(tests)
    
    now = time.strftime('%Y_%m_%d^%H-%M-%S')
    filename = now + u'自動化測試' + '.html'
    fp = open(filename, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title=u'測試報告',
            description=u'環境: %s '%env_name[envs]
            )
    runner.run(suite)
    fp.close()


# In[ ]:


#ipynb檔  轉成 python檔
def IpynbToPython(): 
    try:
        get_ipython().system('jupyter nbconvert --to python joy188_test.ipynb   ')
    except:
        pass
IpynbToPython()

