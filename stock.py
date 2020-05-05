import pymysql as p

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