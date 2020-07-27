game_default = '{"lotteryType":"","currIssueNo":"","stopOnWon":"","totalAmount":"","issueList":[],"schemeList":[],"timeZone":"GMT+8","isWap":false,"online":true}'
fhxyft_games = ['pt330bt02', 'pt333bt02', 'pt320bt02', 'pt321bt01', 'pt321bt02', 'pt322bt01', 'pt322bt02', 'pt323bt02',
                'pt325bt01', 'pt325bt02', 'pt326bt02', 'pt326bt02', 'pt327bt02']
bjpk10_games = ['pt330bt02', 'pt333bt02', 'pt320bt02', 'pt321bt01', 'pt321bt02', 'pt322bt01', 'pt322bt02', 'pt323bt02',
                'pt325bt01', 'pt325bt02', 'pt326bt02', 'pt326bt02', 'pt327bt02']
game_dict = {
    # 大小單雙龍虎
    'pt330bt02': [
        {"playType": "pt330", "betType": "bt02",
         "betItem": "123457#123457#123457#123457#123457#1234#1234#1234#1234#1234#1234", "betTimes": 1, "potType": "Y",
         "doRebate": "yes"},
        108],
    # 牛牛
    'pt333bt02': [[
        {"playType": "pt333", "betType": "bt02", "betItem": "5@5", "betTimes": 1, "potType": "Y", "doRebate": "no"},
        {"playType": "pt333", "betType": "bt02", "betItem": "4@5", "betTimes": 1, "potType": "Y", "doRebate": "no"},
        {"playType": "pt333", "betType": "bt02", "betItem": "3@5", "betTimes": 1, "potType": "Y", "doRebate": "no"},
        {"playType": "pt333", "betType": "bt02", "betItem": "2@5", "betTimes": 1, "potType": "Y", "doRebate": "no"},
        {"playType": "pt333", "betType": "bt02", "betItem": "1@5", "betTimes": 1, "potType": "Y", "doRebate": "no"}],
        5],
    # 冠軍
    'pt320bt02': [
        {"playType": "pt320", "betType": "bt02", "betItem": "01,02,03,04,05,06,07,08,09,10", "betTimes": 1,
         "potType": "Y", "doRebate": "no"},
        20],
    # 冠亞直選
    'pt321bt02': [
        {"playType": "pt321", "betType": "bt02",
         "betItem": "01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10", "betTimes": 1, "potType": "Y",
         "doRebate": "no"},
        180],
    # 冠亞直選單式
    'pt321bt01': [
        {"playType": "pt321", "betType": "bt01", "betItem": "01#02", "betTimes": 1, "potType": "Y", "doRebate": "no"},
        2],
    # 冠亞組選
    'pt322bt02': [{"playType": "pt322", "betType": "bt02", "betItem": "01,02,03,04,05,06,07,08,09,10", "betTimes": 1,
                   "potType": "Y", "doRebate": "no"}, 90],
    # 冠亞組選單式
    'pt322bt01': [
        {"playType": "pt322", "betType": "bt01", "betItem": "01,02", "betTimes": 1, "potType": "Y", "doRebate": "no"},
        2],
    # 冠亞和值
    'pt323bt02': [{"playType": "pt323", "betType": "bt02", "betItem": "3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19",
                   "betTimes": 1, "potType": "Y", "doRebate": "no"}, 34],
    # 前三直選
    'pt325bt02': [{"playType": "pt325", "betType": "bt02",
                   "betItem": "01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10",
                   "betTimes": 1, "potType": "Y", "doRebate": "no"}, 1440],
    # 前三直選單式
    'pt325bt01': [{"playType": "pt325", "betType": "bt01",
                   "betItem": "01#02#03",
                   "betTimes": 1, "potType": "Y", "doRebate": "no"}, 2],
    # 前四直選
    'pt326bt02': [{"playType": "pt326", "betType": "bt02",
                   "betItem": "01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10",
                   "betTimes": 1, "potType": "Y", "doRebate": "no"}, 10080],
    # 前四直選單式
    'pt326bt01': [{"playType": "pt326", "betType": "bt01",
                   "betItem": "01#02#03#04",
                   "betTimes": 1, "potType": "Y", "doRebate": "no"}, 2],
    # 定位膽
    'pt327bt02': [{"playType": "pt327", "betType": "bt02",
                   "betItem": "01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10#01,02,03,04,05,06,07,08,09,10",
                   "betTimes": 1, "potType": "Y", "doRebate": "no"}, 200]
}
