from test_mail2 import mail_analyze
import re
import itertools
from datetime import datetime

def sisomaki(num,value):
  a = 0 #aが300円
  b = num - a
  sum = a*300 + b*500
  while sum != value:
    a += 1
    b = num - a #bが500円
    sum = a * 300 + b * 500
  return(a,b)

def count_word(wordlist,tup): #tupは(a,a,a,b,c)などの形
  word_count = []
  for j in wordlist:
    count = 0
    for i in range(0,len(tup)):
      if j == tup[i]:
        count += 1
    word_count.append(count)
  return tuple(word_count) #返り値は(3,1,1)などの形
        

import itertools
def processed_food(num,value): #たれ、極、麻婆豆腐の3つ
  ans = []
  all = itertools.combinations_with_replacement('abc', num) #abcはあくまで種類の数
  for x in all:
    item_num = count_word('abc',x)
    if 398 * item_num[0] + 280 * item_num[1] + 350 * item_num[2] == value:
      ans.append(item_num)
  return ans #返り値は2重リスト

def ito_chain():

    #dicのフォーマットを作る
    stores = []
    stores.append('伊藤チェーン泉店')
    stores.append('伊藤チェーン玉浦店')
    stores.append('伊藤チェーン松森店')
    stores.append('伊藤チェーン閖上店')
    items = []
    items.append('しそ巻(3個入り)')
    items.append('しそ巻(5個入り)')
    items.append('勝負だれ')
    items.append('極')
    items.append('麻婆豆腐の素')
    item_dic = {}
    for item in items:
        item_dic[item] = 0
    dic = {}
    for store in stores:
        dic[store] = item_dic.copy() 
    
    choices = ['泉店','玉浦店','松森店','閖上店']
    arr_dict = {}
    data = mail_analyze('nebotaka1@yahoo.co.jp')
    s_range_time = datetime.strptime('20時00分','%H時%M分') #1900/01/01となっている。
    f_range_time = datetime.strptime('22時00分','%H時%M分')
    if data != [['']]:
        for data_dict in data: #dataには複数のメールデータがリスト化されている。subが件名、r_arrがsplitされたデータ
            for sub, r_arr in data_dict.items():    
                if '本日の売上状況' in sub and '伊藤チェーン' in sub: #本日の売上状況という件名のものだけを取り出し、ノイズメールは省く
                    n = len(r_arr) #改行でsplitされた1つのメールデータの長さ
                    for i in range(0,n):
                        match_date = re.search(r'(\d+年\d+月\d+日)',r_arr[i])
                        if match_date:
                            match_time = re.search(r'(\d+時\d+分)',r_arr[i])
                            if match_time:
                                tmp_time = datetime.strptime(match_time.group(1),'%H時%M分')
                                if s_range_time < tmp_time and tmp_time < f_range_time:
                                    arr_dict[match_date.group(1)] = r_arr                            
        #print(arr_dict)
        for arr in arr_dict.values():
            n = len(arr) #改行でsplitされた1つのメールデータの長さ
            for choice_num in range(0,len(choices)): #storesとchoicesの順番はそろえなければならない
                for i in range(0,n):
                    if choices[choice_num] in arr[i]:
                        #print(choices[choice_num])
                        for j in range(i+1,n): #店舗名以後から、次の店舗名までの行をサーチ
                            if '店' in arr[j]: #店舗名の順番がわからないから、全ての店舗名をサーチ
                                break      
                            if 'しそ巻' in arr[j]:                     
                                match_num = re.search(r'(\d+)点',arr[j])
                                match_value = re.search(r'(\d?,?\d+)円',arr[j])
                                if match_num:
                                    #print("2")
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                if match_value:
                                    #print("3")
                                    raw_value = match_value.group(1)
                                    value = int(re.sub(r"\\|,|\D", "", raw_value)) #商品の売り上げを取得
                                dic[stores[choice_num]]['しそ巻(3個入り)'] += sisomaki(num,value)[0] #sisomaki(num,value)[0]が300円の数
                                dic[stores[choice_num]]['しそ巻(5個入り)'] += sisomaki(num,value)[1] #sisomaki(num,value)[1]が500円の数
                            if '加工食品' in arr[j]:
                                match_num = re.search(r'(\d+)点',arr[j])
                                match_value = re.search(r'(\d?,?\d+)円',arr[j])
                                if match_num:
                                    num = int(match_num.group(1)) #商品の売れた個数を取得
                                if match_value:
                                    raw_value = match_value.group(1)
                                    value = int(re.sub(r"\\|,|\D", "", raw_value)) #商品の売り上げを取得
                                if len(processed_food(num,value)) == 1:
                                    dic[stores[choice_num]]['勝負だれ'] += processed_food(num,value)[0][0]
                                    dic[stores[choice_num]]['極'] += processed_food(num,value)[0][1]
                                    dic[stores[choice_num]]['麻婆豆腐の素'] += processed_food(num,value)[0][2]
                            
    return dic
#print(ito_chain())
