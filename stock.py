import pymysql as p
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime,time
import requests,urllib3
from bs4 import BeautifulSoup

def kerr_conn(): # 本機Mysql 連線
    db = p.connect(
    host="127.0.0.1",
    user="root",
    passwd="password",
    database="STOCK_TEST",
    use_unicode=True,
    charset="utf8"
    )
    return db

def stock_select(db,stock_num):#找出股號, 然後傳到 twstock, 找出股價
    cur = db.cursor()
    sql = "SELECT * from STOCK_TEST where STOCK_NUM = %s"%stock_num
    cur.execute(sql)
    global stock_detail2
    stock_detail2 = {}
    rows = cur.fetchall()
    for tuple_ in rows:
        stock_detail2[stock_num] = list(tuple_)
    cur.close()

def stock_update(db,stock_prize,stock_num):# 找出對應號碼, update股價
    cur = db.cursor()
    sql = "UPDATE STOCK_TEST SET STOCK_Latest_Prize = %s  WHERE STOCK_NUM = %s"%(stock_prize,stock_num)
    cur.execute(sql)
    db.commit()
    print("%s update完成"%stock_num)
    cur.close()
def stock_select2(db):#頁面勾選  前10的選項
    cur = db.cursor()
    sql = "select * from STOCK_TEST where STOCK_LAST_MONRATE > 100 order by STOCK_LAST_MONRATE desc  LIMIT 10 "
    cur.execute(sql)
    rows = cur.fetchall()
    global stock_detail3
    stock_detail3 = {}
    for num,tuple_ in enumerate(rows):
        stock_detail3[num] = list(tuple_)
    print(stock_detail3)
    cur.close()

def soup_stock():# 抓取數據 , len_index  為抓到的東西 , date 為時間 ,格式 109_3
    now = datetime.datetime.now()
    print("執行時間: %s"%now)
    userAgent ="Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    urllib3.disable_warnings()#解決 會跳出 request InsecureRequestWarning問題
    header = {
            'User-Agent': userAgent,
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
        }
    session = requests.Session()
    now = datetime.datetime.now()#年找出今年.  月和日做參數化.因為可能會找先前日棋
    year = now.year -1911# 換算民國
    month = now.month -1#抓上個月
    print("抓取%s月"%month)# 當月
    r = session.get('https://mops.twse.com.tw'+'/nas/t21/sii/t21sc03_%s_%s_0.html'
    %(year,month),headers=header,verify=False)
    r.encoding = 'Big5' #繁體編碼
    soup = BeautifulSoup(r.text,'lxml')
    #soup.encode('gb18030')
    #global len_index
    len_index = [i for i in soup.find_all('tr',{'align':'right'})]
    #print(len(len_index))
    global stock_Name
    stock_Name = [] #存放所有抓到的資訊
    stock_list =[]
    for number in range(len(len_index)-1):#先取出多少長度, -1 用意, 最後一行不是抓股資訊
        stock_list.append(number)# mysql 的 ID 欄位
        for text in len_index[number]:#再從len_index陣列,取出 每個index的資訊
            stock_list.append('0' if text.text.strip() in ['','合計']#strip()把空白部分去除
            else text.text.strip().replace(',',''))
        if stock_list[-1] == '0':#過濾 不是股票名稱的 
            pass
        else:
            for num,text in enumerate(stock_list):# 需判斷 各 欄位 型態, 因為要Inser進去 Mysql, 型態需和mysql 欄位一致
                if num in [0,1]:
                    text = int(text)
                elif num in [2,11]:
                    text = str(text)
                elif num in [6,7,10]:
                    text = float(text)
                else:
                    text = int(text)
                stock_list[num] = text
        if len(stock_list) != 12:# 這邊代表 抓到的 不是股名 那行,可能是 合計
            pass
        else:
            stock_Name.append(tuple(stock_list))# 轉成tuple用意 ,好insert資料進mysql
        stock_list= []
    print(len(stock_Name))
def schedule():
    scheduler = BlockingScheduler()    
    scheduler.add_job(soup_stock,'interval',days=1, start_date= time.strftime('%Y-%m-8 00:00:00'),end_date= time.strftime('%Y-%m-15 00:00:00'))
    scheduler.start()