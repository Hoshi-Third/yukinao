from test_mail2 import mail_analyze
import re
from datetime import datetime

def midori_service():
    #dicのフォーマットを作る
    stores = []
    stores.append('みどりのサービス仙台店')
    stores.append('みどりのサービス仙台南店')
    store_items = []
    store_items.append('しそ巻(3個入り)')
    store_items.append('しそ巻(5個入り)')
    store_items.append('勝負だれ')
    store_items.append('極')
    store_items.append('麻婆豆腐の素')
    item_dic = {}
    for item in store_items:
        item_dic[item] = 0
    dic = {}
    for store in stores:
        dic[store] = item_dic.copy() 

    data = mail_analyze('nebotaka1@yahoo.co.jp')
    stores = ['みどりのサービス仙台店','みどりのサービス仙台南店']
    arr_dict = {}
    s_range_time = datetime.strptime('18時00分','%H時%M分') #1900/01/01となっている。
    f_range_time = datetime.strptime('20時00分','%H時%M分')
    if data != [['']]:
        for data_dict in data: #dataには複数のメールデータがリスト化されている。subが件名、r_arrがsplitされたデータ
            for sub, r_arr in data_dict.items():    
                if '本日の売上状況' in sub and 'みどりのサービス' in sub: #本日の売上状況という件名のものだけを取り出し、ノイズメールは省く
                    n = len(r_arr) #改行でsplitされた1つのメールデータの長さ
                    for i in range(0,n):
                        match_date = re.search(r'(\d+年\d+月\d+日)',r_arr[i])
                        if match_date:
                            match_time = re.search(r'(\d+時\d+分)',r_arr[i+1])
                            if match_time:
                                tmp_time = datetime.strptime(match_time.group(1),'%H時%M分')
                                if s_range_time < tmp_time and tmp_time < f_range_time:
                                    arr_dict[match_date.group(1)] = r_arr                            
        #arr_dictはキーにstr型の日付、値にその日の中で18時-20時に来たメールが格納されている
        for arr in arr_dict.values():
            n = len(arr) #改行でsplitされた1つのメールデータの長さ
            for store_num in range(0,len(stores)):
                for i in range(0,n):
                    if stores[store_num] in arr[i]:
                        for j in range(i+1,n): #店舗名以後から、次の店舗名までの行をサーチ
                            if store_num < len(stores) - 1: #最終ループはstores[store_num + 1]が存在しないから、以下のコードとなる
                                if stores[store_num + 1] in arr[j]:
                                    break
                            if 'しそ巻き' in arr[j] and '300円' in arr[j]:                            
                                match_num = re.search(r'(\d+)点',arr[j+1])
                                if match_num:
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                    dic[stores[store_num]]['しそ巻(3個入り)'] += num
                            if 'しそ巻き' in arr[j] and '500円' in arr[j]:                 
                                match_num = re.search(r'(\d+)点',arr[j+1])
                                if match_num:
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                    dic[stores[store_num]]['しそ巻(5個入り)'] += num
                            if 'その他加工品' in arr[j] and '398円' in arr[j]:
                                match_num = re.search(r'(\d+)点',arr[j+1])
                                if match_num:
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                    dic[stores[store_num]]['勝負だれ'] += num
                            if 'その他加工品' in arr[j] and '280円' in arr[j]:
                                match_num = re.search(r'(\d+)点',arr[j+1])
                                if match_num:
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                    dic[stores[store_num]]['極'] += num
                            if 'その他加工品' in arr[j] and '350円' in arr[j]:
                                match_num = re.search(r'(\d+)点',arr[j+1])
                                if match_num:
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                    dic[stores[store_num]]['麻婆豆腐の素'] += num

    return dic
#print(midori_service())



