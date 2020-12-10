#!/usr/bin/env python
# coding: utf-8


import cx_Oracle

lottery_dict = {  # 給 抓取講期號碼, lotteryid 使用
    # 時時彩
    'cqssc': [u'重慶時彩(歡樂生效)', '99101'], 'xjssc': [u'新彊時彩', '99103'], 'tjssc': [u'天津時彩', '99104'],
    'hljssc': [u'黑龍江', '99105'], 'llssc': [u'樂利時彩', '99106'], 'shssl': [u'上海時彩', '99107'],
    'jlffc': [u'吉利分彩', '99111'], 'slmmc': [u'順利秒彩', '99112'], 'txffc': [u'騰訊分彩', '99114'],
    'btcffc': [u'比特幣分彩', '99115'], 'fhjlssc': [u'吉利時彩', '99116'], 'fhxjc': [u'鳳凰新疆全球彩', '99118'],
    'fhcqc': [u'鳳凰重慶全球彩', '99117'], '3605fc': [u'360分分彩', '99121'], '360ffc': [u'360五分彩', '99122'],
    'ptxffc': [u'奇趣腾讯分分彩', '99125'], 'v3d': [u'吉利3D', '99801'],
    # 115
    'sd115': [u'山東11選5', '99301'], 'jx115': [u"江西11選5", '99302'],
    'gd115': [u'廣東11選5', '99303'], 'sl115': [u'順利11選5', '99306'],
    # 快三
    'jsk3': [u'江蘇快3', '99501'], 'ahk3': [u'安徽快3', '99502'], 'jsdice': [u'江蘇骰寶', '99601'],
    'jldice1': [u'吉利骰寶(娛樂)', '99602'], 'jldice2': [u'吉利骰寶(至尊)', '99603'],
    'ahsb':[u'安徽骰宝', '99604'], 'slsb': [u'凤凰顺利骰宝', '99605'],
    # 國際
    'hnffc':[u'河内分分彩','99119'], 'hn5fc': [u'河内五分彩','99120'], 'np3':[u'越南福彩','99123'],
    'n3d':[u'越南3D福彩','99124'],
    # 低頻
    'fc3d': [u'3D', '99108'], 'p5': [u'排列5', '99109'],'ssq': [u'雙色球', '99401'], 'lhc': [u'六合彩', '99701'],
    'fckl8': [u'福彩快乐8', '99206'], 'hn60': [u'多彩河内分分彩', '99126'],
    # 趣味
    'bjkl8': [u'快樂8', '99201'], 'pk10': [u"pk10", '99202'], 'xyft': [u'幸運飛艇', '99203'],
    'pcdd': [u'PC蛋蛋', '99204'], 'xyft168': [u'168幸运飞艇', '99205'],
    'btcctp': [u'比特币冲天炮', '99901'],'fhkl8': [u'快乐8全球彩', '99207']
}


def get_conn(env):  # 連結數據庫 env 0: dev02 , 1:188 ,2: 生產
    if env == 2:
        username = 'rdquery'
        service_name = 'gamenxsXDB'
    else:
        username = 'firefog'
        service_name = ''
    oracle_ = {'password': ['LF64qad32gfecxPOJ603', 'JKoijh785gfrqaX67854', 'eMxX8B#wktFZ8V'],
               'ip': ['10.13.22.161', '10.6.1.41', '10.6.1.31'],
               'sid': ['firefog', 'game', '']}
    conn = cx_Oracle.connect(username, oracle_['password'][env], oracle_['ip'][env] + ':1521/' +
                             oracle_['sid'][env] + service_name)
    return conn


def select_numberRecord(conn, lottery, num):  # 開獎號
    with conn.cursor() as cursor:
        sql = "select * from (select number_record , rank() over (partition by lotteryid order by sale_start_time desc) as rank_num from game_issue where lotteryid = %s and number_record is not NULL and  sale_start_time <  sysdate and  sale_start_time >  sysdate - 20) a where rank_num <=  %s" % (
        lottery_dict[lottery][1], num)

        cursor.execute(sql)
        rows = cursor.fetchall()
        global number_record
        number_record = []

        for i in rows:
            number_record.append(i[0])
    conn.close()


def cal_type(type_, list_, big):  # 計算大小單雙 ,type_找哪個計算方式, list_: 列表內容, big: 大小的判斷
    global number_big, number_small, number_odd, number_double
    if type_ == 1:  # 計算大
        number_big = 0
        for i in list_:
            if float(i) >= big:
                number_big = number_big + 1
            else:
                break
    elif type_ == 2:  # 計算小
        number_small = 0
        for i in list_:
            if float(i) < big:
                number_small = number_small + 1
            else:
                break
    elif type_ == 3:  # 計算單
        number_odd = 0
        for i in list_:
            if float(i) % 2 == 1:
                number_odd = number_odd + 1
            else:
                break
    else:  # 計算雙
        number_double = 0
        for i in list_:
            if float(i) % 2 == 0:
                number_double = number_double + 1
            else:
                break


def con_type(list_, big, mulissue):  # 確認 大小單雙次數
    global result
    global msg4
    for i in range(1, 5):  # 把列表的值,大小單雙 各做一次
        cal_type(i, list_, big)
    msg4.append("大次數:%s,小次數:%s,單次數:%s,雙次數:%s" % (number_big, number_small, number_odd, number_double))
    print("大次數:%s,小次數:%s,單次數:%s,雙次數:%s" % (number_big, number_small, number_odd, number_double))
    result['msg4'] = msg4
    # print(msg4)
    for i in enumerate([number_big, number_small, number_odd, number_double]):
        if i[1] >= mulissue:  # 判斷是否等於 臨界次數
            # 0:大, 1:小, 2:單, 3:雙
            if i[0] == 0:
                print("大上榜")
            elif i[0] == 1:
                print('小上榜')
            elif i[0] == 2:
                print('單上榜')
            else:
                print('雙上榜')
        else:  # 都不符合
            pass


def record_other(lottery, envs, mulissue):  # 戰報 做 百十位 的計算, big 判斷彩種大小連界參數
    global msg3, msg5
    millon = []
    thousand = []
    hundred = []
    ten = []
    digit = []
    # 下面for pk10, xyft用 有10個號碼
    select_numberRecord(get_conn(envs), lottery, mulissue)

    print("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record))
    big = 5
    print('規則: 小:0-4, 大:5-9')
    msg5.append('規則: 小:0-4, 大:5-9')
    if lottery in ['fc3d', 'v3d']:
        digit_dict = {'百位數': hundred, '十位數': ten, '個位數': digit}
        for i in number_record:
            hundred.append(i[0])
            ten.append(i[1])
            digit.append(i[2])
    elif lottery in ['p5']:
        digit_dict = {'萬位數': millon, '千位數': thousand, '百位數': hundred, '十位數': ten, '個位數': digit}
        for i in number_record:
            millon.append(i[0])
            thousand.append(i[1])
            hundred.append(i[2])
            ten.append(i[3])
            digit.append(i[4])
    elif lottery in ['txffc', 'shssl']:  # 抓後 一個值
        print('取後一')
        digit_dict = {'個位數': digit}
        if lottery == 'shssl':  # 開三位數
            num = 2
        else:
            num = 4
        for i in number_record:
            digit.append(i[num])
    while True:
        for number_ in digit_dict:  # 百,十,個
            print('%s 開獎號: %s' % (number_, digit_dict[number_]))  # digit_dict[number_] 為百,十,個 的列表
            msg3.append("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record) + '%s 開獎號: %s' % (
            number_, digit_dict[number_]))
            con_type(digit_dict[number_], big, mulissue)  # 呼叫此method, 計算連續大小單雙個數
            break
        break


def first_record(lottery, envs, mulissue):  # 戰報  取冠軍第一個值
    global msg3, msg5
    select_numberRecord(get_conn(envs), lottery, mulissue)
    print("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record))
    print('規則: 大:6-10, 小:1-5')
    msg5.append('規則: 大:6-10, 小:1-5')
    first_list = []  # 冠軍, pk10 xyft 取講期第一個值
    big = 6
    for record in number_record:
        record = record.split(',')  # 列表開獎號有逗點: ['1,2,3' ,  '2,4,5']改成 ['1,2,3'],['2,4,5']
        first_list.append(int(record[0]))
    print('近%s期冠軍號碼: %s' % (mulissue, first_list))
    msg3.append("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record) +
                '近%s期冠軍號碼: %s' % (mulissue, first_list))
    while True:
        con_type(first_list, big, mulissue)  # 呼叫此method, 計算連續大小單雙個數
        break


def record_dice(lottery, envs, mulissue):  # 戰報 完法 取總和
    global msg3, msg5
    record_total = []
    select_numberRecord(get_conn(envs), lottery, mulissue)

    print("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record))
    if lottery in ['bjkl8']:
        big = 811
        print('規則: 大: >=811,小: <811')
        msg5.append('規則: 大: >=811,小: <811')
        for total in number_record:
            total = total.split(',')  # 快垃8 開獎號 list,字串再包逗點
            sum = 0
            for i in total:
                sum = sum + int(i)
            record_total.append(sum)
    else:
        if lottery in ['jldice1', 'jsdice']:
            big = 11
            print('規則: 大:11-17,小:4-10')
            msg5.append('規則: 大:11-17,小:4-10')
        else:
            big = 23
            print('規則: 大:23-45,小:0-22')
            msg5.append('規則: 大:23-45,小:0-22')
        for total in number_record:
            sum = 0
            for i in total:
                sum = sum + int(i)
            record_total.append(sum)
    while True:
        print("開獎號總和: %s" % (record_total))
        msg3.append(
            "%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record) + "開獎號總和: %s" % (record_total))
        con_type(record_total, big, mulissue)  # 呼叫此method, 計算連續大小單雙個數
        break


def record_btcctp(lottery, envs, mulissue):  # 戰報 快開顯示
    global result, msg3, msg5
    msg3 = []
    msg5 = []
    select_numberRecord(get_conn(envs), lottery, mulissue)  # 先抓10期
    msg3.append("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record))
    print("%s 彩種近%s期開獎號: %s" % (lottery_dict[lottery][0], mulissue, number_record))
    msg5.append("規則: 大: 大於2,小: 小於2")
    result['msg3'] = msg3
    result['msg5'] = msg5
    big = 2  # 判斷大小臨界
    while True:
        con_type(number_record, big, mulissue)
        break


def all_lottery(envs, mulissue=3):  # 戰報顯示, envs環境 0:dev ,1:188, mulissue: 抓取幾期
    global result, msg4
    result = {}
    msg2 = []
    msg4 = []
    lottery_list = ['btcctp', 'jldice1', 'jsdice', 'fc3d', 'p5', 'xyft', 'v3d', 'pk10', 'bjkl8',
                    'cqssc', 'btcffc', 'txffc', 'llssc', 'jlffc', 'fhjlssc', 'hljssc', 'xjssc', 'shssl',
                    'tjssc']  # 顯示彩種順序

    if envs == 1:
        msg1 = '188戰報,抓取%s期' % mulissue
        print('188戰報,抓取%s期' % mulissue)
    else:
        msg1 = 'dev戰報,抓取 %s期' % mulissue
        print('dev戰報,抓取 %s期' % mulissue)
    result['msg1'] = msg1
    for lottery in enumerate(lottery_list):
        # print(lottery)
        # print(lottery[0]+1)
        msg2.append(lottery[0] + 1)
        result['msg2'] = msg2
        if lottery[1] in 'btcctp':
            record_btcctp(lottery[1], envs, mulissue)
        elif lottery[1] in ['fc3d', 'p5', 'v3d', 'txffc', 'shssl']:
            record_other(lottery[1], envs, mulissue)
        elif lottery[1] in ['xyft', 'pk10']:
            first_record(lottery[1], envs, mulissue)
        else:  # for大部分 時彩列列, 所以總合
            record_dice(lottery[1], envs, mulissue)
        # lottery_num[lottery[1]] = [number_big,number_small,number_odd,number_double]#
    # print(lottery_num)

# all_lottery(0,3)#環境,和抓取次數
