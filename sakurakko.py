from test_mail2 import mail_analyze
import re
import imaplib
import email
import base64
import quopri


def sisomaki(num,value):
  a = 0 #aが300円
  b = num - a
  sum = a*300 + b*500
  while sum != value:
    a += 1
    b = num - a #bが500円
    sum = a * 300 + b * 500
  return(a,b)

def sakurakko():
    dic = {'さくらっこ':{'しそ巻(3個入り)':0,'しそ巻(5個入り)':0,'極':0, '麻婆豆腐の素':0 ,}}
    data = mail_analyze('nebotaka1@yahoo.co.jp')
    if data != [['']]:
        for arr in data.values: #dataには複数のメールデータがリスト化されている。それを1つずつ取り出してarrに入れる。
            n = len(arr) #改行でsplitされた1つのメールデータの長さ
            for i in range(0,n):
                    if 'しそ巻' in arr[i]:
                        match_num = re.search(r'(\d+)点',arr[i+1])
                        match_value = re.search(r'(\d?,?\d+)円',arr[i+1])
                        if match_num:
                            num = int(match_num.group(1)) #商品の売れた個数を取得
                        if match_value:
                            raw_value = match_value.group(1)
                            value = int(re.sub(r"\\|,|\D", "", raw_value)) #商品の売り上げを取得
                        dic['さくらっこ']['しそ巻(3個入り)'] += sisomaki(num,value)[0] #sisomaki(num,value)[0]が300円の数
                        dic['さくらっこ']['しそ巻(5個入り)'] += sisomaki(num,value)[1] #sisomaki(num,value)[1]が500円の数
                    if 'にんにくとうがらし' in arr[i]:
                        match_num = re.search(r'(\d+)点',arr[i+1])
                        if match_num:
                            num = int(match_num.group(1)) #商品の売れた個数を取得
                        dic['さくらっこ']['極'] += num
                    if '麻婆豆腐の素' in arr[i]:
                        match_num = re.search(r'(\d+)点',arr[i+1])
                        if match_num:
                            num = int(match_num.group(1)) #商品の売れた個数を取得
                        dic['さくらっこ']['麻婆豆腐の素'] += num
    
    return dic
#print(sakurakko())