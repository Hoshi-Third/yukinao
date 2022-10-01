import imapclient
from backports import ssl
from OpenSSL import SSL 
import pyzmail
import pandas as pd

# SSL暗号化
context = ssl.SSLContext(SSL.TLSv1_2_METHOD)

# IMAP接続用のオブジェクト作成
imap = imapclient.IMAPClient("imap.gmail.com", ssl=True, ssl_context=context)

# ログイン情報
my_mail = "siryu20020809@gmail.com"
app_password = "wwfw ojmd fcyn snqx"

# IMAPサーバーログイン
imap.login(my_mail,app_password)

# メールフォルダを指定
imap.select_folder("INBOX", readonly=True)

#① 検索キーワードを設定 & 検索キーワードに紐づくメールID検索
KWD = imap.search(["SINCE","01-Jan-2022","FROM","mitaka-jimu.c@gs.mail.u-tokyo.ac.jp"])

#② メールID→メール本文取得
raw_message = imap.fetch(KWD,["BODY[]"])

#解析メールの結果保存用
From_list = []
Cc_list = []
Bcc_list = []
Subject_list = []
Body_list = []


#検索結果保存
for j in range(len(KWD)):
    
    #特定メール取得
    message = pyzmail.PyzMessage.factory(raw_message[KWD[j]][b"BODY[]"])
    
    #宛先取得
    From = message.get_addresses("from")
    From_list.append(From)
    
    Cc = message.get_addresses("cc")
    Cc_list.append(Cc)
    
    Bcc = message.get_addresses("bcc")
    Bcc_list.append(Bcc)
    
    #件名取得
    Subject = message.get_subject()
    Subject_list.append(Subject)
    
    #本文
    Body = message.text_part.get_payload().decode(message.text_part.charset)
    Body_list.append(Body)

    

#④出力
#table = pd.DataFrame({"From":From_list,
                     # "Cc":Cc_list,
                     # "Bcc":Bcc_list,
                      #"Subject":Subject_list,
                     # "Body":Body_list,
                     #})
pd.set_option('display.max_row',10000)
pd.set_option('display.max_columns', 10000)
print(Body_list)