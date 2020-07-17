import pathlib
import random
import time
from typing import Dict

from selenium.webdriver.chrome.options import Options
from enum import Enum

from utils.Connection import get_conn, get_domain_default_url

project_path = str(pathlib.Path(__file__).parent.parent.absolute())  # 專案路徑
# project_path = os.path.abspath('.')  # 專案路徑
chromeDriver_Path = project_path + r'\Drivers\chromedriver_83.exe'  # ChromeDriver 取用路徑 (若環境參數無法獲取時取用)
reportHtml_Path = project_path + r"\templates\report.html"  # report.html 絕對路徑
logging_config_path = project_path + r"\logs\logging_config.ini"

# ChromeDriver 設定參數
chrome_options = Options()
chrome_options.add_argument("--headless")  # 背景執行
chrome_options.add_argument("--start-maximized")  # 全螢幕


class LotteryData:
    lottery_dict = {
        'cqssc': [u'重慶', '99101'], 'xjssc': [u'新彊時彩', '99103'], 'tjssc': [u'天津時彩', '99104'],
        'hljssc': [u'黑龍江', '99105'], 'llssc': [u'樂利時彩', '99106'], 'shssl': [u'上海時彩', '99107'],
        'jlffc': [u'吉利分彩', '99111'], 'slmmc': [u'順利秒彩', '99112'], 'txffc': [u'騰訊分彩', '99114'],
        'btcffc': [u'比特幣分彩', '99115'], 'fhjlssc': [u'吉利時彩', '99116'],
        'sd115': [u'山東11選5', '99301'], 'jx115': [u"江西11選5", '99302'],
        'gd115': [u'廣東11選5', '99303'], 'sl115': [u'順利11選5', '99306'], 'jsk3': [u'江蘇快3', '99501'],
        'ahk3': [u'安徽快3', '99502'], 'jsdice': [u'江蘇骰寶', '99601'], 'jldice1': [u'吉利骰寶(娛樂)', '99602'],
        'jldice2': [u'吉利骰寶(至尊)', '99603'], 'fc3d': [u'3D', '99108'], 'p5': [u'排列5', '99109'],
        'lhc': [u'六合彩', '99701'], 'btcctp': [u'快開', '99901'],
        'bjkl8': [u'快樂8', '99201'], 'pk10': [u"pk10", '99202'], 'v3d': [u'吉利3D', '99801'],
        'xyft': [u'幸運飛艇', '99203'], 'fhxjc': [u'鳳凰新疆', '99118'], 'fhcqc': [u'鳳凰重慶', '99117'], 'ssq': [u'雙色球', '99401'],
        'n3d': [u'越南3d', '99124'], 'np3': [u'越南福利彩', '99123']
    }
    lottery_sh = ['cqssc', 'xjssc', 'tjssc', 'hljssc', 'llssc', 'jlffc', 'slmmc', 'txffc',
                  'fhjlssc', 'btcffc', 'fhcqc', 'fhxjc']
    lottery_3d = ['v3d']
    lottery_115 = ['sd115', 'jx115', 'gd115', 'sl115']
    lottery_k3 = ['ahk3', 'jsk3']
    lottery_sb = ['jsdice', "jldice1", 'jldice2']
    lottery_fun = ['pk10', 'xyft']
    lottery_noRed = ['fc3d', 'n3d', 'np3', 'p5']  # 沒有紅包


class UserAgent(Enum):
    PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.100 Safari/537.36"
    ANDROID = "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36"
    IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"


class EnvConfig:
    devDomains = ['dev02', 'dev03', 'fh82dev02', '88hlqpdev02', 'teny2020dev02']
    joyDomains = ['joy188', 'joy188.teny2020', 'joy188.195353', 'joy188.88hlqp']
    joySunDomains = ['joy188.fh888']
    hyDomains = ['maike2020']
    productDomains = ['fh968']

    env_domain = None

    def __init__(self, domain):
        try:
            if domain in self.devDomains + self.joySunDomains + self.joyDomains + self.hyDomains + self.productDomains:
                self.env_domain = domain
        except ValueError:
            raise Exception('無對應網域 請至 Config.EnvConfig 添加')

    def get_domain(self):
        return self.env_domain

    def get_post_url(self) -> str:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains + self.hyDomains + self.productDomains:
            return "http://www.%s.com" % self.env_domain
        elif self.env_domain in self.joyDomains:
            return "http://www2.%s.com" % self.env_domain
        elif self.env_domain in self.joySunDomains:
            return "http://www2.%s.bet" % self.env_domain
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_em_url(self) -> str:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.joySunDomains:
            return "http://em.%s.bet" % self.env_domain
        elif self.env_domain in self.devDomains + self.joyDomains + self.hyDomains + self.productDomains:
            return "http://em.%s.com" % self.env_domain
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_password(self) -> str:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return "123qwe"
        elif self.env_domain in self.joyDomains + self.hyDomains + self.joySunDomains:
            return "amberrd"
        elif self.env_domain in self.productDomains:
            return "tsuta0425"
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_safe_password(self) -> str:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains + self.joyDomains + self.hyDomains + self.joySunDomains:
            return "Amberrd"
        elif self.env_domain in self.productDomains:
            return "tsuta0425"
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_env_id(self) -> int:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return 0
        elif self.env_domain in self.joyDomains + self.joySunDomains + self.hyDomains:
            return 1
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_admin_url(self) -> str:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return "http://admin.dev02.com"
        elif self.env_domain in self.joyDomains + self.joySunDomains:
            return "http://admin.joy188.com"
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_admin_data(self) -> Dict:
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return {'username': 'cancus', 'password': '123qwe', 'bindpwd': 123456}
        elif self.env_domain in self.joyDomains + self.joySunDomains:
            return {'username': 'cancus', 'password': 'amberrd', 'bindpwd': 123456}
        else:
            raise Exception('無對應網域參數，請至Config envConfig()新增')

    def get_joint_venture(self, env, domain):
        domain_urls = get_domain_default_url(get_conn(int(env)), domain)  # 先去全局 找是否有設定 該domain
        if not domain_urls:  # 若無對應domain_url, default domain type = 0 ?
            return 0
        try:
            domain_type = domain_urls[0][5]  # 判斷 該domain 再後台全局設定 的 joint_venture 是多少
            print("後台設置: %s" % domain_type)
            return domain_type
        except KeyError:
            print("全局後台沒設置 : {}".format(self.env_domain))


class EnvConfigApp(EnvConfig):
    def __init__(self, domain):
        super().__init__(domain)

    def get_iapi(self):
        print(self.env_domain)
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return "http://10.13.22.152:8199"
        elif self.env_domain in self.joyDomains:
            return "http://iphong.joy188.com"
        else:
            raise Exception('無對應網域參數，請至Config envConfigApp()新增')

    def get_uuid(self):
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return "2D424FA3-D7D9-4BB2-BFDA-4561F921B1D5"
        elif self.env_domain in self.joyDomains:
            return "f009b92edc4333fd"
        else:
            raise Exception('無對應網域參數，請至Config envConfigApp()新增')

    def get_login_pass_source(self):
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in self.devDomains:
            return "fa0c0fd599eaa397bd0daba5f47e7151"
        elif self.env_domain in self.joyDomains:
            return "3bf6add0828ee17c4603563954473c1e"
        else:
            raise Exception('無對應網域參數，請至Config envConfigApp()新增')

    def get_joint_venture(self):
        if self.env_domain is None:
            raise Exception('env 環境未初始化')
        elif self.env_domain in ['dev02', 'joy188']:
            return 0
        elif self.env_domain in ['fh82dev02', 'teny2020dev02', 'joy188.teny2020', 'joy188.195353']:
            return 1
        elif self.env_domain in ['joy188.88hlqp', '88hlqpdev02']:
            return 2
        else:
            raise Exception('無對應網域參數，請至Config envConfigApp()新增')


def random_mul(num):  # 生成random數, NUM參數為範圍
    return random.randint(1, num)


def play_type():  # 隨機生成  group .  五星,四星.....
    game_group = {'wuxing': u'五星', 'sixing': u'四星', 'qiansan': u'前三', 'housan': u'後三',
                  'zhongsan': u'中三', 'qianer': u'前二', 'houer': u'後二'}
    return list(game_group.keys())[random_mul(6)]


def func_time(func):  # 案例時間
    def wrapper(*args):
        start_ = time.time()
        func(*args)
        end_ = time.time() - start_
        print("用時: {}秒".format(end_))

    return wrapper
