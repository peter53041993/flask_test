import FF_Joy188, flask_test
import pymysql as p
import random, time, hashlib, json, unittest, HTMLTestRunner
from functools import wraps
from utils import Config
from selenium import webdriver


class GameBox():
    def __init__(self, clientId='', username='', app_Id='', member_Id='', password='', amount='10', bill_No='',
                 api_key='', api_url='',
                 supplier_type='', update_type=1,game_id = '331'):  # update_type 1唯修改, 0唯刪除
        self.data_type = {
            "token": ['管理/獲取令牌',
                      "/oauth/token?client_id=admin&client_secret=gameBox-2020-08-11*admin&username=admin&password=gameBox-2020-08-11*admin&grant_type=password&scope=all"
                , ""],
            "createApp": ["管理/創建APP帳號",
                          "/admin/client/createApp", {
                              "clientId": username, "clientSecret": "string", "dec": "string",
                              "email": "%s@gmail.com" % username,
                              "ipWhitelist": "61.220.138.45", "supplierAccountDTOList": [
                        {"apiKey": api_key, "apiUrl": api_url, "password": password,
                         "supplierType": supplier_type, "username": clientId}]
                          }],
            "getClientInfo": ["获取client信息",
                              "/admin/client/getClientInfo?appId=%s&" % app_Id, ""],
            "updateIpWhitelist": ["管理/修改客户的ip白名单",
                                  "/admin/client/updateIpWhitelist?appId=%s&ipWhitelist=61.220.138.45" % app_Id, ""],
            "updateIpWhitelist": ["管理/修改客户的ip白名单",
                                  "/admin/client/updateIpWhitelist?appId=%s&ipWhitelist=61.220.138.45" % app_Id, {}],
            "updateSupplierAccount": ["管理/修改三方账号信息",
                                      "/admin/client/updateSupplierAccount?appId=%s&type=%s" % (app_Id, update_type), {
                                          "apiKey": api_key, "apiUrl": api_url, "password": "qwe123",
                                          "username": clientId, "supplierType": supplier_type}],
                "signUp":["客戶/註冊",
                "/api/member/signUp?agent_name=%s"%clientId,[
                {"0":{"member": {"currencyName": "CNY", "password": password, "username": username, "winLimit": 0 },"oddType": "A" }},
                {"1":{"member": {"currencyName": "UUS", "maxtransfer": 1000,"mintransfer": 1,"payRadioType": "2","username": "%s_test"%username}}},
                {"2":{"member": {"currencyName": "CNY", "username": username },"oddType": "260301,260302" }},
                {"3":{"member": {"password": password,"username": username}}},
                {"4":{"member": {"password": 'q'+password.upper(),"username": username}}},
                {"5":{"lang": "cs","member": {"password": password, "username": username},"oddType":"4440"}},
                {"6":{"member": {"currencyName": "CNY", "username": username }}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{"member": { "currencyName": "CNY","password": password, "username": username }}},
                {"10":{"member": {"password": password,"username": username}}},
                {"11":{"agentLogin": "xosouat","member": {"username": username}}},
                {"12":{"member": {"username": username}}},
                {"13":{"member": {"username": username}}},
                {"14":{"ipAddress": "61.220.138.45","member": {"amount": amount,"username": username }}},
                {"15":{"birthDate": "1994-07-01","country": "china","email": "%s@asd.com"%username,"lang": "cs","member": {"username": username}}},
                {"16":{"member": {"username": username}}},
                {"17":{"member": {"username":username,"password":password,"user":username}}},
                {"18":{"agentLogin":"vb_xoso","member": {"username": username}}},
                {"19":{"agentLogin": "XVN","birthDate": "1990-01-01","country": "CN","lang":"cs","registrationDate":"2020-02-02","member": {"username":"XVN"+username,"user": username}}}]
                ],
                "login":["客戶/登入",
                "/api/member/login?agent_name=%s"%clientId,[
                {"0":{"lang": "CNY","member": {"password": password, "username": username}}},
                {"1":{"member": {"username":"%s_test"%username}}},
                {"2":{"member": {"username":username}}},
                {"3":{"lang": "cs","member": {"password": password, "username": username}}},
                {"4":{"lang": "cs","type":"LC","member": {"password": 'q'+password.upper(), "username": username}}},
                {"5":{"deviceId": "1","lang": "cs","member": {"password": password,"username": username},
                "oddType": "4445","backUrl":"https://www.baidu.com"}},
                {"6":{"lang":"cs","member": {"username": username}}},
                {"7":{"deviceId": "1","lang":"cs","backUrl":"http:///www.baidu.com","agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{"ipAddress":"192.168.1.1","lang":"cs","deviceId":"1","member": {"password": password,"username": username}}},
                {"10":{"member": {"password": password,"username": username}}},
                {"11":{"lang":"cs","member": {"username": username}}},
                {"12":{"lang":"cs","member": {"username": username}}},
                {"13":{"member": {"username": username}}},
                {"14":{"ipAddress": "61.220.138.45","member": {"amount": amount,"username": username }}},
                {"15":{"deviceId": "1","member": {"username": username}}},
                {"16":{"member": {"username": username}}},
                {"17":{"lang": "CNY","member": {"password": password, "username": username}}},
                {"18":{"agentLogin":"vb_xoso","gameId":game_id,"lang": "en","deviceId": "1","backUrl": "null","cashierURL":"null","member": {"username": username}}},
                {"19":{"deviceId":"1","lang":"cs","gameId":game_id,"member": {"username": "XVN"+username}}}]
                ],
                "freeLogin":["客戶/試玩登入",
                "/api/member/freeLogin?agent_name=%s"%clientId,[
                {"0":{"lang": "cs"}},{"1":{}},{"2":{}},{"3":{}},{"4":{}},
                {"5":{"backUrl": "https://www.baidu.com","deviceId": "1","lang": "cs"}},
                {"6":{"lang": "cs"}},
                {"7":{"deviceId": "4","lang":"cs","backUrl":"http:///www.baidu.com"}},
                {"8":{}},{"9":{}},{"10":{}},
                {"11":{"lang": "cs"}},
                {"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}}]
                ],
                "update":["客戶/修改会员信息","/api/member/update?agent_name=%s"%clientId,[
                {"0":{"member": {"status": 1, "winLimit": 0,"password": password, "username":username }}}, 
                {"1":{"member":{"maxtransfer": 1000,"mintransfer": 1,"payRadioType": "2","username": "%s_test"%username}}},
                {"2":{}},
                {"3":{"member": {"password": password,"username": username}}},
                {"4":{"member": {"password": 'q'+password.upper(),"oldPw": 'q'+password.upper(),"username": username}}},
                {"5":{"member": {"password": password,"username": username}}},
                {"6":{}},{"7":{}},{"8":{}},
                {"9":{"member": {"password": password,"username": username}}},
                {"10":{}},
                {"11":{}},
                {"12":{}},
                {"13":{}},
                {"14":{}},
                {"15":{}},
                {"16":{}},
                {"17":{}},{"18":{}},{"19":{}}]
                ],
                "balance":['客戶/获取会员余额接口',
                "/api/member/balance?agent_name=%s"%clientId,[
                {"0":{"member": {"username": username,}}},
                {"1":{"member": {"username": "%s_test"%username}}},
                {"2":{"member": {"username": username,}}},
                {"3":{"member": {"username": username,}}},
                {"4":{"member": {"username": username,"password": 'q'+password.upper()}}},
                {"5":{"member": {"username": username,}}},
                {"6":{"member": {"username": username,}}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{"member": {"username": username}}},
                {"10":{"member": {"username": username}}},
                {"11":{"agentLogin": "xosouat","member": {"username": username}}},
                {"12":{"member": {"username": username}}},
                {"13":{"member": {"username": username,}}},
                {"14":{"member": {"username": username,}}},
                {"15":{"member": {"username": username,}}},
                {"16":{"member": {"username": username,}}},
                {"17":{"member": {"username": username,}}},
                {"18":{"agentLogin": "vb_xoso","member": {"username": username}}},
                {"19":{"member": {"username": "XVN"+username}}}]
                ],
                "transfer":["客戶/会员存取款接口",
                "/api/member/transfer?agent_name=%s"%clientId,[
                {"0":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"1":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"currencyName": "UUS","username": "%s_test"%username}}},
                {"2":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount,"username": username,}}},
                {"3":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"4":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"password": 'q'+password.upper(),"username": username,}}},
                {"5":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"6":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"7":{"billNo": '%s'%random.randint(1,1000000000),"agentLogin": "amberdev","member": {"amount":amount,"username": username}}},
                {"8":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"9":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"10":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"11":{"billNo": '%s'%random.randint(1,1000000000),"agentLogin": "xosouat","member": {"amount":amount,"username": username}}},
                {"12":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"13":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"14":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"15":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"16":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"17":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": username,}}},
                {"18":{"agentLogin": "vb_xoso","billNo": '%s'%random.randint(1,1000000000),"member": {"amount": amount,"username": username}}},
                {"19":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": "XVN"+username}}}]
                ],
                "checkTransfer":["客戶/检查存取款操作是否成功",
                "/api/member/checkTransfer?agent_name=%s"%clientId,[
                {"0":{"billNo": bill_No}},{"1":{"billNo": bill_No}},
                {"2":{"billNo": bill_No}},{"3":{"billNo": bill_No}},
                {"4":{}},
                {"5":{"billNo": bill_No,"member": {"username": username}}},
                {"6":{"billNo": bill_No,"member": {"username": username}}},
                {"7":{"billNo": bill_No,"member": {"username": username}}},
                {"8":{"billNo": bill_No,"member": {"username": username}}},
                {"9":{"billNo": bill_No,"member": {"username": username}}},
                {"10":{"billNo": bill_No,"member": {"username": username}}},
                {"11":{"billNo":bill_No,"agentLogin":"xosouat"}},
                {"12":{"billNo": bill_No}},
                {"13":{}},
                {"14":{"billNo": bill_No,"member": {"username": username}}},
                {"15":{"billNo": bill_No,"member": {"username": username}}},
                {"16":{"billNo": bill_No,"member": {"username": username}}},
                {"17":{}},
                {"18":{"billNo":bill_No,"agentLogin": "vb_xoso"}},
                {"19":{}}]
                ],
                "updateLimit":['客戶/修改会员限红组',
                "/api/member/updateLimit?agent_name=%s"%clientId,[
                {"0":{"member": {"username": username},"oddType": "A"}},
                {"1":{}},
                {"2":{"member": {"username": "testsz8"},"oddType": "260301"}},
                {"3":{}},{"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}}]
                ],
                "checkOnline":["客戶/查询玩家在线状态",
                "/api/member/checkOnline?agent_name=%s"%clientId,[
                {"0":{"member": {"username": username.upper()}}},
                {"1":{"member": {"username": "%s_test"%username.upper()}}},
                {"2":{}},
                {"3":{"member": {"username": username}}},
                {"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},
                {"14":{"member": {"username": username}}},{"15":{}},{"16":{"member": {"username": username}}},{"17":{}},{"18":{}},{"19":{}}]
                ],
                "onlineCount":['客戶/查询在线玩家数量','/api/member/onlineCount?agent_name=%s'%clientId,[
                {"0":{}},{"1":{}},{"2":{}},{"3":{}},{"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}}
                ,{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}}]
                ],
                "offline":['客戶/踢人','/api/member/offline?agent_name=%s'%clientId,[
                {"0":{"member": {"memberId":member_Id}}},
                {"1":{"member": {"username": "%s_test"%username}}},
                {"2":{"member": {"username": username}}},
                {"3":{"member": {"username": username}}},
                {"4":{}},{"5":{}},{"6":{}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{}},
                {"10":{"member": {"username": username}}},
                {"11":{"agentLogin": "xosouat","member": {"username": username}}},
                {"12":{}},
                {"13":{}},
                {"14":{"member": {"username": username}}},
                {"15":{}},{"16":{"member": {"username": username}}},
                {"17":{"member": {"username": username}}},
                {"18":{"agentLogin": "vb_xoso","member": {"username": username}}},
                {"19":{}}]
                ],
                "lockMember":['客戶/封鎖會員','/api/member/lockMember?agent_name=%s'%clientId,[
                {"0":{"member": {"password":password,"username": username}}},
                {"1":{"member": {"username": "%s_test"%username}}},
                {"2":{}},{"3":{}},{"4":{}},
                {"5":{"member": {"username": username}}},
                {"6":{}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}}]
                ],
                "unlockMember":['客戶/解封鎖會員','/api/member/unlockMember?agent_name=%s'%clientId,[
                {"0":{"member": {"password":password,"username": username}}},
                {"1":{"member": {"username": "%s_test"%username}}},
                {"2":{}},{"3":{}},{"4":{}},
                {"5":{"member": {"username": username}}},
                {"6":{}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}}]
                ],
                "onlineMember":['客戶/查询在线玩家','/api/member/onlineMember?agent_name=%s&page=1&size=100'%clientId,
                [{"0":{}},{"1":{}},{"2":{}},{"3":{}},{"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},
                    {"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}}]
                ],  
                }

    def GameBox_Con(client_id, env):  # 連線 mysql
        env_dict = {0:['152.32.185.241',21330,'amberrd','Gvmz8DErUcHgMgQh','test.t_client'],
                    1: ['54.248.18.149', 3306, 'gamebox', 'sgkdjsdf^mdsD1538', 'game_box_api.t_client']}
        db = p.connect(
            host=env_dict[env][0],
            port=env_dict[env][1],
            user=env_dict[env][2],
            passwd=env_dict[env][3],
        )
        table_name = env_dict[env][4]
        cur = db.cursor()
        sql = "SELECT app_id,app_key FROM %s where client_id = '%s'" % (table_name, client_id)  # clien_id 找出 id,key
        print(sql)
        cur.execute(sql)
        client_detail = {}
        rows = cur.fetchall()
        for i in rows:
            client_detail[client_id] = i
        print(client_detail)
        cur.close()
        return client_detail

    # type_: 是用function 名, clientId = client帳號
    def GameBox_test(type_, clientId, username, client_detail, password, url, api_key, api_url, supplier_type,
                     game_type, cq_9Key):
        try:
            global access_token, token_type, pc_url, dr, memberId, appId, billNo
            # client_detail = GameBox.GameBox_Con(clientId)
            # username = 'kerr%s'%random.randint(1,1000)
            data_ = GameBox(clientId=clientId, username=username, password=password, api_key=api_key,
                            api_url=api_url, supplier_type=supplier_type).data_type[type_]
            print(type_, data_[0])
            # url_content = data_[1]
            test_header = {
                "Content-Type": "application/json",
                'User-Agent': FF_Joy188.FF_().user_agent['Pc']
            }
            # 有可能DB 沒有該 clinet_id
            # print(appId,appKey)
            appId = client_detail[clientId][0]
            appKey = client_detail[clientId][1]
            if type_ in ['createApp', 'updateIpWhitelist', 'updateSupplierAccount', 'getClientInfo', 'token']:
                data_ = GameBox(clientId, username, app_Id=appId).data_type[type_]
                if type_ != 'token':
                    test_header['Authorization'] = token_type + " %s" % access_token
                data = data_[2]
            # elif type_ in ['signUp','login','freeLogin','checkOnline','balance','transfer','updateLimit']:
            else:  # 客戶端
                if type_ == 'checkOnline':
                    if game_type in [0, 1, 3]:  # 大部分都沒有, 避免每次新增家都要加, 改寫
                        dr = webdriver.Chrome(executable_path=r'C:\python3\Scripts\jupyter_test\chromedriver_84.exe')
                        print('需先瀏覽器登入PC login_url: %s' % pc_url)
                        dr.get(pc_url)  # 用 瀏覽器登入, 才能 獲得 memberid(DG踢人才需要 memberid)
                        dr.quit()
                    else:
                        memberId = ''
                        print("%s沒有查询玩家在线状态" % game_type)
                elif type_ == 'offline':  # 踢人 ,在把 global memberid 傳還init
                    data_ = GameBox(clientId, username, member_Id=memberId).data_type[type_]
                elif type_ == 'checkTransfer':  # 檢查 轉帳轉太, 需把 transfer的 bill_no 傳回來
                    data_ = GameBox(clientId, username, bill_No=billNo).data_type[type_]
                time_ = int(time.time())
                test_header['appId'] = appId  # appId#"930ea5d5a258f4f"#appId
                test_header['nonce-str'] = "ibuaiVcKdpRxkhJA"
                # test_header['appKey'] = "316489e115371ed23808a9ce2ee094a38ca4411a"
                test_header['timestamp'] = str(time_)  # "1597729724"#str(time_)
                m = hashlib.md5()
                str_ = "appId=%s&nonce-str=ibuaiVcKdpRxkhJA&timestamp=%s&appKey=%s" % (appId, str(time_), appKey)
                # print(str_)
                # print(str_,type(str_))
                m.update(str_.encode())
                str_md = m.hexdigest()
                test_header['signature'] = str_md.upper()  # '9A0A8659F005D6984697E2CA0A9CF3B7'#str_md.upper()
                data = data_[2][game_type][str(game_type)]
                print(data)
            url_content = data_[1]
            if game_type == 3:  # cq9
                url_content = url_content.replace(clientId, cq_9Key)
            response = FF_Joy188.FF_().session_post(url, url_content, json.dumps(data), test_header)
            if game_type == 19 and type_ == 'login':
                return response
            r_json = response.json()
            global status_code
            status_code = response.status_code
            print('連線狀態: %s' % status_code)
            print(response.text)
            if type_ == 'token':
                access_token = r_json['access_token']
                token_type = r_json['token_type']
            elif type_ == 'checkOnline':
                if game_type == 0:  # dramegame 才需要memberid
                    memberId = r_json['data']['member']['memberId']
                else:
                    memberId = ''
                    return 'ok'
            elif type_ == 'login':
                pc_url = r_json['data']['pc']  # 拿來 checkOnline  要先登入,才能  獲得memberId
            elif type_ == 'transfer':
                if game_type in [3,4,5,7]:  # cq_9,gpi,YB,bg   response不會回傳  billNo , 需自己帶
                    billNo = data["billNo"]
                else:
                    billNo = r_json['data']['billNo']
        except KeyError as e:
            error_msg = 'KeyError : %s' % e
            print(error_msg)
            if 'memberId' in error_msg:
                for i in range(5):
                    try:
                        time.sleep(10)
                        FF_Joy188.FF_().session_post(url, url_content, json.dumps(data), test_header)
                        memberId = (FF_Joy188.r.json()['data']['member']['memberId'])
                        print(memberId)
                        return memberId
                    except:
                        print('繼續等候登入要memeberId')
            elif clientId in error_msg:  # 創紀 createAPP 走這段, 因為 client_detail 為空 ,
                if type_ == 'createApp':
                    test_header['Authorization'] = token_type + " %s" % access_token
                url_content = data_[1]
                data = data_[2][game_type]
                response = FF_Joy188.FF_().session_post(url, url_content, json.dumps(data), test_header)
                r_json = response.json()
                status_code = response.status_code
                print('連線狀態: %s' % status_code)
                print(r_json)
                if type_ == 'token':
                    access_token = r_json['access_token']
                    token_type = r_json['token_type']
        except NameError as e:
            status_code = response.status_code
            error_msg = "NameError : %s" % e
            print(error_msg)
            if 'token_type' in error_msg:  # 需要從新獲取令牌
                print('需從新獲取令牌 token')
                url_content = "/oauth/token?client_id=admin&client_secret=gameBox-2020-08-11*admin&username=admin&password=gameBox-2020-08-11*admin&grant_type=password&scope=all"
                test_header = {
                    "Content-Type": "application/json",
                    'User-Agent': FF_Joy188.FF_().user_agent['Pc']
                }
                FF_Joy188.FF_().session_post(url, url_content, '', test_header)
                access_token = response.json()['access_token']
                token_type = response.json()['token_type']


class GameBoxTest_Admin(unittest.TestCase):
    '''GameBox管理端'''

    def assert_(self):
        return self.assertEqual(200, status_code, msg='請求狀態有誤')

    def func():  # 共用 的方法, 差別再type_ ,需宿改 各參數 再這邊加
        return GameBox.GameBox_test(type_=type_, clientId=arg_dict['clientId'], username=arg_dict['user'],
                                    client_detail=arg_dict['client_detail'], password='123qwe', url=arg_dict['url'],
                                    api_key=arg_dict['api_key'],
                                    api_url=arg_dict['api_url'], supplier_type=arg_dict['supplier_type'],
                                    cq_9Key=arg_dict['cq_9Key'],
                                    game_type=int(arg_dict['game_type'])), GameBoxTest_Admin().assert_()

    def func_wrap(func):  # 獲取當前 測試案例的 名稱 ,扣除 test
        @wraps(func)
        def tmp(*args, **kwargs):
            global type_
            type_ = (func.__name__).split('_')[1]  # 切割 名稱 , unittest 統一案例,都已 test_ 為開頭
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

    @func_wrap
    def test_getClientInfo(self):
        '''管理端-获取client信息'''
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

    @GameBoxTest_Admin.func_wrap
    def test_unlockMember(self):
        '''用戶端-解封鎖會員'''
        GameBoxTest_Admin.func()

    @GameBoxTest_Admin.func_wrap
    def test_onlineMember(self):
        '''用戶端-查询在线玩家'''
        GameBoxTest_Admin.func()


def suite_test(game_type, url_type, clientId, user, client_detail, api_key, api_url, supplier_type, url, game_list,
               user_items, admin_items, cq_9Key):
    suite = unittest.TestSuite()
    global arg_dict
    arg_dict = {}
    arg_dict['clientId'] = clientId
    arg_dict['user'] = user
    arg_dict['client_detail'] = client_detail
    arg_dict['api_key'] = api_key
    arg_dict['api_url'] = api_url
    arg_dict['supplier_type'] = supplier_type
    arg_dict['url'] = url
    arg_dict['game_type'] = game_type
    arg_dict['cq_9Key'] = cq_9Key

    TestCase = []  # 存放測試案例
    for test_case in game_list:
        if test_case == 'user_all':
            for test in user_items.keys():
                TestCase.append(GameBoxTest_User('test_%s' % user_items[test]))
        elif test_case == 'admin_all':
            for test in admin_items.keys():
                TestCase.append(GameBoxTest_Admin('test_%s' % admin_items[test]))
        elif test_case in list(user_items.values()):
            TestCase.append(GameBoxTest_User('test_%s' % test_case))
        else:
            TestCase.append(GameBoxTest_Admin('test_%s' % test_case))
    suite.addTests(TestCase)
    now = time.strftime('%Y_%m_%d %H-%M-%S')
    filename = Config.reportHtml_Path  # now + u'自動化測試' + '.html'
    print(filename)
    fp = open(filename, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
        stream=fp,
        title=u'測試報告',
        description='環境: %s, client商戶: %s, 用戶名: %s ' % (url_type, clientId, user)
    )
    runner.run(suite)
    fp.close()

    # time.sleep(10)
    # dr.quit()
