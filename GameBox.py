import FF_Joy188,flask_test
import pymysql as p
import random,time,hashlib,json,unittest,HTMLTestRunner
from functools import wraps
from Utils import Config
from selenium import webdriver
class GameBox():
    def __init__(self,clientId='',username='',app_Id='',member_Id='',password='',amount='',bill_No='',api_key='',api_url='',
        supplier_type='',update_type=1):# update_type 1唯修改, 0唯刪除
        self.data_type = {
        "token":['管理/獲取令牌',
        "/oauth/token?client_id=admin&client_secret=gameBox-2020-08-11*admin&username=admin&password=gameBox-2020-08-11*admin&grant_type=password&scope=all"
        ,""],
        "createApp":["管理/創建APP帳號",
        "/admin/client/createApp",{
        "clientId": username,"clientSecret": "string","dec": "string","email": "%s@gmail.com"%username,
        "ipWhitelist": "61.220.138.45","supplierAccountDTOList": [
        {"apiKey": api_key,"apiUrl": api_url,"password": password,
        "supplierType": supplier_type,"username":clientId }]
        }],
        "updateIpWhitelist":["管理/修改客户的ip白名单",
        "/admin/client/updateIpWhitelist?appId=%s&ipWhitelist=61.220.138.45"%app_Id,""],
        "updateSupplierAccount":["管理/修改三方账号信息",
        "/admin/client/updateSupplierAccount?appId=%s&type=%s"%(app_Id,update_type),{
        "apiKey": api_key,"apiUrl": api_url,"password": "qwe123",
        "username": clientId,"supplierType": supplier_type}],
        "signUp":["客戶/註冊",
        "/api/member/signUp?agent_name=%s"%clientId,[
        {"member": {"currencyName": "CNY", "password": password, "username": username, "winLimit": 0 },"oddType": "A" },
        {"member": {"currencyName": "UUS", "maxtransfer": 1000,"mintransfer": 1,"payRadioType": "2","username": "%s_test"%username}},
        {"member": {"currencyName": "CNY", "username": username },"oddType": "260301,260302" },
        {"member": {"password": password,"username": username}},
        {"member": {"password":  'q'+password.upper(),"username": username}}]
        ],
        "login":["客戶/登入",
        "/api/member/login?agent_name=%s"%clientId,[
        {"lang": "CNY","member": {"password": password, "username": username}},
        {"member": {"username":"%s_test"%username}},
        {"member": {"username":username}},
        {"lang": "CNY","member": {"password": password, "username": username}},
        {"lang": "cs","type":"LC","member": {"password":  'q'+password.upper(), "username": username}}]
        ],
        "freeLogin":["客戶/試玩登入",
        "/api/member/freeLogin?agent_name=%s"%clientId,[{"lang": "string"},"","","",""]
        ],
        "update":["客戶/修改会员信息","/api/member/update?agent_name=%s"%clientId,[
        {"member": {"status": 1, "winLimit": 0,"password": password, "username":username }}, 
        {"member":{"maxtransfer": 1000,"mintransfer": 1,"payRadioType": "2","username": "%s_test"%username}},
        "",
        {"member": {"password": password,"username": username}},
        {"member": {"password": password,"oldPw": password,"username": username}}]
        ],
        "balance":['客戶/获取会员余额接口',
        "/api/member/balance?agent_name=%s"%clientId,
        [{"member": {"username": username,}},
        {"member": {"username": "%s_test"%username}},
        {"member": {"username": username,}},
        {"member": {"username": username,}},
        {"member": {"username": username,"password": 'q'+password.upper()}}]
        ],
        "transfer":["客戶/会员存取款接口",
        "/api/member/transfer?agent_name=%s"%clientId,
        [{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount": "10","username": username,}},
        {"billNo": '%s'%random.randint(1,1000000000),"member": {"amount": 50,"currencyName": "UUS","username": "%s_test"%username}},
        {"billNo": '%s'%random.randint(1,1000000000),"member": {"amount": "10","username": username,}},
        {"billNo": '%s'%random.randint(1,1000000000),"member": {"amount": "10","username": username,}},
        {"billNo": '%s'%random.randint(1,1000000000),"member": {"amount": "10","password":'q'+password.upper(),"username": username,}}]
        ],
        "checkTransfer":["客戶/检查存取款操作是否成功",
        "/api/member/checkTransfer?agent_name=%s"%clientId,
        [{"billNo": bill_No},{"billNo": bill_No},
        {"billNo": bill_No},{"billNo": bill_No}
        ,""]
        ],
        "updateLimit":['客戶/修改会员限红组',
        "/api/member/updateLimit?agent_name=%s"%clientId,
        [{"member": {"username": username},"oddType": "A"},"",
        {"member": {"username": "testsz8"},"oddType": "260301"},"",""]
        ],
        "checkOnline":["客戶/查询玩家在线状态",
        "/api/member/checkOnline?agent_name=%s"%clientId,
        [{"member": {"username": username.upper()}},{"member": {"username": "%s_test"%username.upper()}},
        "",{"member": {"username": username}},""]
        ],
        "onlineCount":['客戶/查询在线玩家数量','/api/member/onlineCount?agent_name=%s'%clientId
        ,["","","","",""]
        ],
        "offline":['客戶/踢人','/api/member/offline?agent_name=%s'%clientId,
        [{"member": {"memberId":member_Id}},{"member": {"username": "%s_test"%username}},
        {"member": {"username": username}},{"member": {"username": username}},""]
        ],
        "lockMember":['客戶/封鎖會員','/api/member/lockMember?agent_name=%s'%clientId,
        [{"member": {"password":password,"username": username}},
        {"member": {"username": "%s_test"%username}},"","",""]
        ],
        "unlockMember":['客戶/解封鎖會員','/api/member/unlockMember?agent_name=%s'%clientId,
        [{"member": {"password":password,"username": username}},{"member": 
        {"username": "%s_test"%username}},"","",""]
        ],
        "onlineMember":['客戶/查询在线玩家','/api/member/onlineMember?agent_name=%s&page=1&size=100'%clientId,
        ["","","","",""]
        ],  
        }
    def GameBox_Con(client_id,env):# 連線 mysql
        env_dict = {0:['43.240.38.15',21330,'amberrd','Gvmz8DErUcHgMgQh','test.t_client'],
                    1:['54.248.18.149',3306,'gamebox','sgkdjsdf^mdsD1538','game_box_api.t_client']}
        db = p.connect(
        host = env_dict[env][0],
        port = env_dict[env][1],
        user = env_dict[env][2],
        passwd = env_dict[env][3],
        )
        table_name = env_dict[env][4]
        cur = db.cursor()
        sql = "SELECT app_id,app_key FROM %s where client_id = '%s'"%(table_name,client_id)# clien_id 找出 id,key
        #print(sql)
        cur.execute(sql)
        client_detail = {}
        rows = cur.fetchall()
        for i in rows:
            client_detail[client_id] = i
        print(client_detail)
        return client_detail
        cur.close()
    
    # type_: 是用function 名, clientId = client帳號
    def GameBox_test(type_,clientId,username,client_detail,password,url,api_key,api_url,supplier_type,game_type,cq_9Key):
        try:
            global access_token,token_type,pc_url,dr,memberId,appId,billNo
            #client_detail = GameBox.GameBox_Con(clientId)
            #username = 'kerr%s'%random.randint(1,1000)
            data_ =  GameBox(clientId=clientId,username=username,password=password,api_key=api_key,
            api_url=api_url,supplier_type=supplier_type).data_type[type_]
            print(type_,data_[0])
            #url_content = data_[1]
            test_header = { 
                "Content-Type": "application/json",
                'User-Agent':FF_Joy188.FF_().user_agent['Pc']
            }
         # 有可能DB 沒有該 clinet_id
            if type_ != 'token':
                appId = client_detail[clientId][0]
                appKey = client_detail[clientId][1]
            #print(appId,appKey)
            if type_ in ['createApp','updateIpWhitelist','updateSupplierAccount','token']:
                test_header['Authorization'] = token_type + " %s"%access_token
                if type_!= 'createApp':#另外兩個  需 在產 global appId
                    data_ =  GameBox(clientId,username,app_Id=appId).data_type[type_]
                data = data_[2]
            #elif type_ in ['signUp','login','freeLogin','checkOnline','balance','transfer','updateLimit']:
            else:#客戶端
                if type_ == 'checkOnline':
                    if game_type in [2,4]:# sexy, gpi 沒有 查詢再線玩家功能
                        memberId = ''
                        print("sexy, gpi沒有查询玩家在线状态")
                        return "sexy, gpi沒有查询玩家在线状态"
                    dr = webdriver.Chrome(executable_path=r'C:\python3\Scripts\jupyter_test\chromedriver_84.exe')
                    print('需先瀏覽器登入PC login_url: %s'%pc_url)
                    dr.get(pc_url)# 用 瀏覽器登入, 才能 獲得 memberid(DG踢人才需要 memberid)
                    dr.quit()
                elif type_ == 'offline':# 踢人 ,在把 global memberid 傳還init
                    data_ =  GameBox(clientId,username,member_Id=memberId).data_type[type_]
                elif type_ == 'checkTransfer':# 檢查 轉帳轉太, 需把 transfer的 bill_no 傳回來
                    data_ =  GameBox(clientId,username,bill_No=billNo).data_type[type_]
                time_ = int(time.time())
                test_header['appId'] = appId #appId#"930ea5d5a258f4f"#appId
                test_header['nonce-str'] = "ibuaiVcKdpRxkhJA"
                #test_header['appKey'] = "316489e115371ed23808a9ce2ee094a38ca4411a"
                test_header['timestamp'] = str(time_)#"1597729724"#str(time_)
                m = hashlib.md5()
                str_ = "appId=%s&nonce-str=ibuaiVcKdpRxkhJA&timestamp=%s&appKey=%s"%(appId,str(time_),appKey)
                #print(str_)
                #print(str_,type(str_))
                m.update(str_.encode())
                str_md = m.hexdigest()
                test_header['signature'] = str_md.upper()#'9A0A8659F005D6984697E2CA0A9CF3B7'#str_md.upper()
                data = data_[2][game_type]
            url_content = data_[1]
            if game_type == 3:# cq9
                url_content = url_content.replace(clientId,cq_9Key)
            
            #print(test_header)
            FF_Joy188.FF_().session_post(url,url_content,json.dumps(data),test_header)
            r_json = FF_Joy188.r.json()
            global status_code
            status_code = FF_Joy188.r.status_code
            print('連線狀態: %s'%status_code)
            print(FF_Joy188.r.text)
            if type_ == 'token':
                access_token = r_json['access_token']
                token_type = r_json['token_type']
            elif type_ == 'checkOnline':
                if game_type == 0:# dramegame 才需要memberid
                    memberId = r_json['data']['member']['memberId']
                else:    
                    memberId = ''
                    return 'ok'
            elif type_ == 'login':
                pc_url = r_json['data']['pc']# 拿來 checkOnline  要先登入,才能  獲得memberId   
            elif type_ == 'transfer':
                if game_type == 3:# cq9
                    billNo = data["billNo"]
                else:
                    billNo = r_json['data']['billNo']
        except KeyError as e:
            error_msg = 'KeyError : %s'%e
            print(error_msg)
            if 'memberId' in error_msg:
                for i in range(5):
                    try:
                        sleep(10)
                        FF_Joy188.FF_().session_post(url,url_content,json.dumps(data),test_header)
                        memberId = (FF_Joy188.r.json()['data']['member']['memberId'])
                        print(memberId)
                        return memberId
                    except:
                        print('繼續等候登入要memeberId')
            elif clientId in error_msg:# 創紀 createAPP 走這段, 因為 client_detail 為空 ,
                if type_ == 'createApp':
                    test_header['Authorization'] = token_type + " %s"%access_token
                url_content = data_[1]
                data = data_[2][game_type]
                FF_Joy188.FF_().session_post(url,url_content,json.dumps(data),test_header)
                r_json = FF_Joy188.r.json()
                print('連線狀態: %s'%status_code)
                print(r_json)
                if type_ == 'token':
                    access_token = r_json['access_token']
                    token_type = r_json['token_type']
        except NameError as e:
            error_msg  = "NameError : %s"%e
            print(error_msg)
            if 'token_type' in error_msg:# 需要從新獲取令牌
                print('需從新獲取令牌 token')
                url_content="/oauth/token?client_id=admin&client_secret=gameBox-2020-08-11*admin&username=admin&password=gameBox-2020-08-11*admin&grant_type=password&scope=all"
                test_header = { 
                "Content-Type": "application/json",
                'User-Agent':FF_Joy188.FF_().user_agent['Pc']
                }
                FF_Joy188.FF_().session_post(url,url_content,'',test_header) 
                access_token = FF_Joy188.r.json()['access_token']
                token_type = FF_Joy188.r.json()['token_type']

class GameBoxTest_Admin(unittest.TestCase):
    '''GameBox管理端'''
    def assert_(self):
        return self.assertEqual(200,status_code,msg='請求狀態有誤')
    def func():# 共用 的方法, 差別再type_ ,需宿改 各參數 再這邊加
        return GameBox.GameBox_test(type_=type_,clientId = arg_dict['clientId'],username = arg_dict['user'],
            client_detail=arg_dict['client_detail'],password='123qwe',url=arg_dict['url'],api_key=arg_dict['api_key'],
            api_url=arg_dict['api_url'],supplier_type=arg_dict['supplier_type'],cq_9Key=arg_dict['cq_9Key'],
            game_type=int(arg_dict['game_type'])),GameBoxTest_Admin().assert_()
    def func_wrap(func):# 獲取當前 測試案例的 名稱 ,扣除 test
        @wraps(func)
        def tmp(*args, **kwargs):
            global type_
            type_ = (func.__name__).split('_')[1]#切割 名稱 , unittest 統一案例,都已 test_ 為開頭
            return func(*args, **kwargs)
        return tmp
    @func_wrap
    def test_token(self):
        '''管理端-獲取token'''
        GameBoxTest_Admin.func()
    @func_wrap
    def test_createApp(self):
        '''管理端-獲取client帳號'''
        GameBoxTest_Admin.func()
    @func_wrap
    def test_updateIpWhitelist(self):
        '''管理端-修改ip白名單'''
        GameBoxTest_Admin.func()
    @func_wrap
    def test_updateSupplierAccount(self):
        '''管理端-修改client信息'''
        GameBoxTest_Admin.func()
class GameBoxTest_User(GameBoxTest_Admin):
    '''GameBox客戶端'''
    @GameBoxTest_Admin.func_wrap
    def test_signUp(self):
        '''用戶端-註冊'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_login(self):
        '''用戶端-登入'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_freeLogin(self):
        '''用戶端-試玩帳號'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_update(self):
        '''用戶端-修改用戶信息'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_balance(self):
        '''用戶端-查詢餘額'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_transfer(self):
        '''用戶端-加幣額度'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_checkTransfer(self):
        '''用戶端-檢查轉帳狀態'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_updateLimit(self):
        '''用戶端-更新用戶限紅組'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_checkOnline(self):
        '''用戶端-在線狀態'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_onlineCount(self):
        '''用戶端-在線人數'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_offline(self):
        '''用戶端-踢人'''
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_lockMember(self):
        '''用戶端-封鎖會員'''
        GameBoxTest_Admin.func()
        global type_
        type_ = 'transfer'# 用意檢查 是否有封鎖成功
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_unlockMember(self):
        '''用戶端-解封鎖會員'''
        GameBoxTest_Admin.func()
        global type_
        type_ = 'balance'
        GameBoxTest_Admin.func()
    @GameBoxTest_Admin.func_wrap
    def test_onlineMember(self):
        '''用戶端-查询在线玩家'''
        GameBoxTest_Admin.func()

def suite_test(game_type,url_type,clientId,user,client_detail,api_key,api_url,supplier_type,url,game_list,user_items,admin_items,cq_9Key):
    suite = unittest.TestSuite()
    global arg_dict
    arg_dict = {}
    arg_dict['clientId']=clientId
    arg_dict['user'] = user
    arg_dict['client_detail']=client_detail
    arg_dict['api_key']=api_key
    arg_dict['api_url']=api_url
    arg_dict['supplier_type']=supplier_type
    arg_dict['url']=url
    arg_dict['game_type']=game_type
    arg_dict['cq_9Key']=cq_9Key

    TestCase  = []#存放測試案例
    for test_case in game_list:
        if test_case == 'user_all':
            for test in  user_items.keys():
                TestCase.append(GameBoxTest_User('test_%s'%user_items[test]))
        elif test_case == 'admin_all':
            for test in  admin_items.keys():
                TestCase.append(GameBoxTest_Admin('test_%s'%admin_items[test]))
        elif test_case in list(user_items.values()):
            TestCase.append(GameBoxTest_User('test_%s'%test_case))
        else:
            TestCase.append(GameBoxTest_Admin('test_%s'%test_case))
    suite.addTests(TestCase)
    now = time.strftime('%Y_%m_%d %H-%M-%S')
    filename = Config.reportHtml_Path  # now + u'自動化測試' + '.html'
    print(filename)
    fp = open(filename, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title=u'測試報告',
            description='環境: %s, client商戶: %s, 用戶名: %s '%(url_type,clientId,user)
            )
    runner.run(suite)
    fp.close()

    #time.sleep(10)
    #dr.quit()