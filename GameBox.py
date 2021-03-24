import FF_Joy188, flask_test
import pymysql as p
import random, time, hashlib, json, unittest, HTMLTestRunner
from functools import wraps
from utils import Config
from selenium import webdriver



class GameBox:
    def __init__(self, clientId='', username='', app_Id='', member_Id='', password='', amount='10', bill_No='',
                 api_key='', api_url='',
                 supplier_type='', update_type=1,game_id = '',env_id=''):  # update_type 1唯修改, 0唯刪除
        self.clientId = clientId
        self._conn = None
        self.env_id = env_id
        self.env_dict = {0:['152.32.185.241',21330,'amberrd','Gvmz8DErUcHgMgQh','test'],
                    1: ['54.248.18.149', 3306, 'gamebox', 'sgkdjsdf^mdsD1538', 'game_box_api']}
        self.client_type = {
            "api_key":
                {0: "1566e8efbdb444dfb670cd515ab99fda",1: "XT",2: "9RJ0PYLC5Ko4O4vGsqd",3:"",
            4:"a93f661cb1fcc76f87cfe9bd96a3623f",5:"BgRWofgSb0CsXgyY",6:"b86fc6b051f63d73de262d4c34e3a0a9",
            7:"8153503006031672EF300005E5EF6AEF",8:"000268d7cf113cb434e80f2de71188ddc3f45a0c8643c9fadf7d639\
            2ec4dd42b3f2b82687999588fab2722814c62f650f98a588e8f372cb377b4e62302dc4addfdaa3e95cc48cfa9\
            e308e3285e0eb54781b0ab29c2a95d544c64847c216c2f2b10a9e083de4506b0a901dac71651be86e680f5\
            f61c4a2fb1fbccaa56ce9d88715a8c",9:"",10:"DF0FAEB6171BDEF9",11:"fe9b68fca25f2fe2",12:"dbettest",
            13: "89CA25C2BA65AC9DD12E04BD66B6B467",14: "FB9EFF5983F0683F",15:"2RuIYUKYkWrWBnNG",
                16: "5dfc2a02f995f9b94defc4ed2c5613e5",17:"07f96e685a9f7252ebb001bca52a14a4",18:"testKey",19:"XVN",
            20:"A5264ADC-4A3A-470D-98CA-4CDDFFC1041A"},
            "api_url":
                {0: "https://api.dg99web.com",1:"http://tsa.l0044.xtu168.com",
            2:"https://testapi.onlinegames22.com",3:"http://api.cqgame.games",4:"http://gsmd.336699bet.com",
            5:"https://api.ybzr.online/",6:"http://ab.test.gf-gaming.com",
            7:'http://am.bgvip55.com/open-cloud/api/',8:"https://spi-test.r4espt.com",
            9:"http://operatorapi.staging.imaegisapi.com",10:'https://api.cp888.cloud',11:"http://api.jygrq.com",
            12:"https://linkapi.bbinauth.net/app/WebService/JSON/display.php",13:"https://api.0x666666.com",
            14: "https://wc-api.hddv1.com/channelHandle",15:"https://marsapi-test.oriental-game.com:8443",
                16: "http://tapi.aiqp001.com:10018/",17:"https://api.a45.me/api/public/Gateway.php",
                18:"https://api.prerelease-env.biz/IntegrationService/v3/http/CasinoGameAPI",
            19:"http://agastage.playngonetwork.com:23219/CasinoGameService",
            20:"https://ws-test.insvr.com/jsonapi"},
            "supplier_type":
                {0:"dream_game",1:"sa_ba_sports",2: "ae_sexy",3:"cq_9",4:"gpi",5:"ya_bo_live",6:"pg_game",
            7:{"game":"bg_game","fish":'bg_fishing','chess':'bg_chess','lottery':'bg_lottery'},
            8:"tf_gaming",9:"im_sb",10: "ya_bo_lottery",11: "jdb_electronic",
            12: "bb_in",13:"yx_game",14: "ky_chess",15: "og_live", 16: "ace_poker",17:"wm_live",18:"pp_game",19:"png_game",
            20:"haba_game"},
            "supplier_user":
            {0: "DGTE01011T",1: "6yayl95mkn",2: "fhlmag",3: "cq9_test",4: "xo8v",5: "ZSCH5",
            6: "aba4d198602ba6f2a3a604edcebd08f1",7:"am00",8:"711",9:"OPRikJXEbbH36LAphfbD5RXcum6qifl8",
            10:"fhagen",11:"XT",12: "test",13: "FH",14: "72298",15: "mog251sy",16: "1334",17:"wmtesttwapi",
            18:"vb_xoso",19:"XVNTESTAPI01",20:"e040dc28-1d77-eb11-9889-00155db5435a"}# DB 裡 client_id
            }
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
                {"19":{"agentLogin": "XVN","birthDate": "1990-01-01","country": "CN","lang":"cs","registrationDate":"2020-02-02","member": {"username":"XVN"+username,"user": username}}},
                {"20":{"member": {"username":username,"password": password}}}]
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
                {"19":{"deviceId":"1","lang":"cs","gameId":game_id,"member": {"username": "XVN"+username}}},
                {"20":{"lang": "cs","backUrl":"https://www.baidu.com","type":"real","member": {"memberId":game_id,"username": username,"password": password}}}]
                ],
                #haba_game : type參數, fun為試玩, real為正式登入, 目前寫死之後再看是否要改成變數
                #haba_game, login需要game_id
                "freeLogin":["客戶/試玩登入",
                "/api/member/freeLogin?agent_name=%s"%clientId,[
                {"0":{"lang": "cs"}},{"1":{}},{"2":{}},{"3":{}},{"4":{}},
                {"5":{"backUrl": "https://www.baidu.com","deviceId": "1","lang": "cs"}},
                {"6":{"lang": "cs"}},
                {"7":{"deviceId": "4","lang":"cs","backUrl":"http:///www.baidu.com"}},
                {"8":{}},{"9":{}},{"10":{}},
                {"11":{"lang": "cs"}},
                {"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
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
                {"17":{}},{"18":{}},{"19":{}},{"20":{}}]
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
                {"19":{"member": {"username": "XVN"+username}}},
                {"20":{"member": {"password": password,"username": username}}}]
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
                {"19":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount":amount ,"username": "XVN"+username}}},
                {"20":{"billNo": '%s'%random.randint(1,1000000000),"member": {"amount": amount,"password": password,"username": username}}}]
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
                {"19":{}},
                {"20":{"billNo":bill_No,"member": {"username": username,"password": password}}}]
                ],
                "updateLimit":['客戶/修改会员限红组',
                "/api/member/updateLimit?agent_name=%s"%clientId,[
                {"0":{"member": {"username": username},"oddType": "A"}},
                {"1":{}},
                {"2":{"member": {"username": "testsz8"},"oddType": "260301"}},
                {"3":{}},{"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
                ],
                "checkOnline":["客戶/查询玩家在线状态",
                "/api/member/checkOnline?agent_name=%s"%clientId,[
                {"0":{"member": {"username": username.upper()}}},
                {"1":{"member": {"username": "%s_test"%username.upper()}}},
                {"2":{}},
                {"3":{"member": {"username": username}}},
                {"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},
                {"14":{"member": {"username": username}}},{"15":{}},{"16":{"member": {"username": username}}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
                ],
                "onlineCount":['客戶/查询在线玩家数量','/api/member/onlineCount?agent_name=%s'%clientId,[
                {"0":{}},{"1":{}},{"2":{}},{"3":{}},{"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}}
                ,{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
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
                {"19":{}},
                {"20":{"member": {"username": username,"password":password}}}]
                ],
                "lockMember":['客戶/封鎖會員','/api/member/lockMember?agent_name=%s'%clientId,[
                {"0":{"member": {"password":password,"username": username}}},
                {"1":{"member": {"username": "%s_test"%username}}},
                {"2":{}},{"3":{}},{"4":{}},
                {"5":{"member": {"username": username}}},
                {"6":{}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
                ],
                "unlockMember":['客戶/解封鎖會員','/api/member/unlockMember?agent_name=%s'%clientId,[
                {"0":{"member": {"password":password,"username": username}}},
                {"1":{"member": {"username": "%s_test"%username}}},
                {"2":{}},{"3":{}},{"4":{}},
                {"5":{"member": {"username": username}}},
                {"6":{}},
                {"7":{"agentLogin": "amberdev","member": {"username": username}}},
                {"8":{"member": {"username": username}}},
                {"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},{"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
                ],
                "onlineMember":['客戶/查询在线玩家','/api/member/onlineMember?agent_name=%s&page=1&size=100'%clientId,
                [{"0":{}},{"1":{}},{"2":{}},{"3":{}},{"4":{}},{"5":{}},{"6":{}},{"7":{}},{"8":{}},{"9":{}},{"10":{}},{"11":{}},{"12":{}},{"13":{}},
                    {"14":{}},{"15":{}},{"16":{}},{"17":{}},{"18":{}},{"19":{}},{"20":{}}]
                ],  
                }


    def GameBox_Con(self):  # 連線 mysql
        self._conn = p.connect(
            host=self.env_dict[self.env_id][0],
            port=self.env_dict[self.env_id][1],
            user=self.env_dict[self.env_id][2],
            passwd=self.env_dict[self.env_id][3],
        )
        return self._conn
    def GameBox_clinet(self):
        cur = self.GameBox_Con().cursor()
        table_name = self.env_dict[self.env_id][4]
        sql = "SELECT app_id,app_key FROM %s.t_client where client_id = '%s'" % (table_name, self.clientId )  # clien_id 找出 id,key
        print(sql)
        cur.execute(sql)
        client_detail = {}
        rows = cur.fetchall()
        for i in rows:
            client_detail[self.clientId ] = i
        print(client_detail)
        cur.close()
        return client_detail
    def GameBox_Gameid(self,game_type):
        cur = self.GameBox_Con().cursor()
        table_name = self.env_dict[self.env_id][4]
        sql = "select detail from %s.t_supplier_game where supplier_type = '%s'" % (table_name,game_type )  
        print(sql)
        cur.execute(sql)
        rows = cur.fetchall()
        gameId_dict = {} 
        for i in rows:
            for str_a in i :
                a = eval(str_a)
                #print(a)
            for keys in a.keys():
            #keys = list(a.keys())
                gameId_dict[ a[keys]['gameCode']] = a[keys]['gameNameCn']
        return gameId_dict
        cur.close()


    # func_name: 是用function 名, clientId = client帳號
    def GameBox_test(clientId,func_name, username, client_detail, password, url, api_key, api_url, supplier_type,
                     game_type, cq_9Key,game_id):
        try:
            global access_token, token_type, pc_url, dr, memberId, appId, billNo

            data_ = GameBox(clientId=clientId, username=username, password=password, api_key=api_key,
                            api_url=api_url, supplier_type=supplier_type,game_id=game_id).data_type[func_name]
            print(func_name, data_[0])
            # url_content = data_[1]
            test_header = {
                "Content-Type": "application/json",
                'User-Agent': FF_Joy188.FF_().user_agent['Pc']
            }
            # 有可能DB 沒有該 clinet_id
            # print(appId,appKey)
            appId = client_detail[clientId][0]
            appKey = client_detail[clientId][1]
            if func_name in ['createApp', 'updateIpWhitelist', 'updateSupplierAccount', 'getClientInfo', 'token']:
                data_ = GameBox(clientId, username, app_Id=appId).data_type[func_name]
                if func_name != 'token':
                    test_header['Authorization'] = token_type + " %s" % access_token
                data = data_[2]
            # elif func_name in ['signUp','login','freeLogin','checkOnline','balance','transfer','updateLimit']:
            else:  # 客戶端
                if func_name == 'checkOnline':
                    if game_type in [0, 1, 3]:  # 大部分都沒有, 避免每次新增家都要加, 改寫
                        dr = webdriver.Chrome(executable_path=r'C:\python3\Scripts\jupyter_test\chromedriver_84.exe')
                        print('需先瀏覽器登入PC login_url: %s' % pc_url)
                        dr.get(pc_url)  # 用 瀏覽器登入, 才能 獲得 memberid(DG踢人才需要 memberid)
                        dr.quit()
                    else:
                        memberId = ''
                        print("%s沒有查询玩家在线状态" % game_type)
                elif func_name == 'offline':  # 踢人 ,在把 global memberid 傳還init
                    data_ = GameBox(clientId, username,password=password ,member_Id='').data_type[func_name]
                elif func_name == 'checkTransfer':  # 檢查 轉帳轉太, 需把 transfer的 bill_no 傳回來
                    data_ = GameBox(clientId, username, bill_No=billNo, password=password).data_type[func_name] # haba_game, CheckTranfer需要password參數
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
            if game_type == 19 and func_name == 'login':
                return response
            r_json = response.json()
            global status_code
            status_code = response.status_code
            print('連線狀態: %s' % status_code)
            print(response.text)
            if func_name == 'token':
                access_token = r_json['access_token']
                token_type = r_json['token_type']
            elif func_name == 'checkOnline':
                if game_type == 0:  # dramegame 才需要memberid
                    memberId = r_json['data']['member']['memberId']
                else:
                    memberId = ''
                    return 'ok'
            elif func_name == 'login':
                pc_url = r_json['data']['pc']  # 拿來 checkOnline  要先登入,才能  獲得memberId
            elif func_name == 'transfer':
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
                if func_name == 'createApp':
                    test_header['Authorization'] = token_type + " %s" % access_token
                url_content = data_[1]
                data = data_[2][game_type]
                response = FF_Joy188.FF_().session_post(url, url_content, json.dumps(data), test_header)
                r_json = response.json()
                status_code = response.status_code
                print('連線狀態: %s' % status_code)
                print(r_json)
                if func_name == 'token':
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
        return GameBox.GameBox_test(func_name=func_name, clientId=arg_dict['clientId'], username=arg_dict['user'],
                                    client_detail=arg_dict['client_detail'], password='123qwe', url=arg_dict['url'],
                                    api_key=arg_dict['api_key'],
                                    api_url=arg_dict['api_url'], supplier_type=arg_dict['supplier_type'],
                                    cq_9Key=arg_dict['cq_9Key'],
                                    game_type=int(arg_dict['game_type']), game_id= arg_dict['game_id']
                                    ), GameBoxTest_Admin().assert_()
                                   

    def func_wrap(func):  # 獲取當前 測試案例的 名稱 ,扣除 test
        @wraps(func)
        def tmp(*args, **kwargs):
            global func_name
            func_name = (func.__name__).split('_')[1]  # 切割 名稱 , unittest 統一案例,都已 test_ 為開頭
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
               user_items, admin_items, cq_9Key,game_id):
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
    arg_dict['game_id'] = game_id

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
