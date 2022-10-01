import imaplib
import email
import base64
import quopri
import re


#def parse_uid(data):
    #pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')
    #match = pattern_uid.match(data)
    #return match.group('uid')

def mail_analyze(address):

    UserName = "siryu20020809@gmail.com"
    PassName = "wwfw ojmd fcyn snqx"

    gmail = imaplib.IMAP4_SSL("imap.gmail.com", '993')
    gmail.login(UserName, PassName)
    gmail.select("INBOX", readonly = False)

    search_option = '(FROM {} SENTSINCE "01-Sep-2022" SENTBEFORE "12-Sep-2023")'.format(address)
    
    # 絞り込んだメールの数を取得
    he, da = gmail.search(None, search_option)
    mail_num = len(da[0].split())
    #print(mail_num)
    if mail_num == 0:
        return [['']]
    mail_f = da[0].split()[0] #なぜかデリートした後はリストの最初の識別番号から振りなおされる
    
    datalist = []
    # 取得したメール一覧の処理
    for i in range(0,mail_num): #繰り返す回数を指定する
        #デリートタグを付けるたびに識別番号を取得しなおす
        head, data = gmail.search(None, search_option)
        mail_list = data[0].split()
        m_num = mail_list[0]
        #print(mail_list)
        #print(num)
        h, d = gmail.fetch(m_num, '(RFC822)')
        raw_email = d[0][1]
        # 文字コード取得
        msg = email.message_from_bytes(raw_email)
        
        delete_num = mail_f #deleteのときとメール内容を取得するときのメール識別番号のずれ？
        gmail.copy(m_num.decode(),'yukinao')
        result = gmail.store(delete_num.decode(),'+FLAGS', '(\Deleted)')
        
    
        msg_encoding = email.header.decode_header(msg.get('Subject'))[0][1] or 'iso-2022-jp'
        # タイトルの情報を抽出
        msg_subject = email.header.decode_header(msg.get('Subject'))[0][0]
        # エンコーディング
        subject = str(msg_subject.decode(msg_encoding))
        #print(subject)

        #本文を取得
        if msg.is_multipart():
            #charset = msg.get_content_charset()
            for payload in msg.get_payload():
                    char = payload.get_content_charset()
                    if payload.get_content_type() == "text/plain":
                        print("----------------")
                        print(char)
                        if char == "iso-2022-jp":
                            rawbody = str(payload).encode(char)
                            body = quopri.decodestring(rawbody).decode('iso-2022-jp')
                            datalist.append({subject:body.split('\n')})
                        elif char == "utf-8":
                            bodylist = str(payload).split('\n\n')
                            rawbody = bodylist[1].encode()
                            body = base64.b64decode(rawbody).decode()
                            datalist.append({subject:body.split('\n')})

        else:
            #print(msg.get_content_type())
            if msg.get_content_type() == "text/plain":
                char = msg.get_content_charset()
                if char == "iso-2022-jp":
                    body = msg.get_payload().encode(char).decode(char)
                    datalist.append({subject:body.split('\n')})                
                elif char == 'utf-8':
                    rawbody = str(msg.get_payload()).encode()
                    body = base64.b64decode(rawbody).decode()
                    datalist.append({subject:body.split('\n')})
            
    
    # 終了処理
    gmail.close()
    gmail.logout()

    return datalist #データ型は[{'':[]},{'':[]},...]
#print(mail_analyze('nebotaka1@yahoo.co.jp'))

