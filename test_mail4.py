import imaplib
import email
import base64
import quopri

def mail_analyze(address):

    UserName = "siryu20020809@gmail.com"
    PassName = "wwfw ojmd fcyn snqx"

    gmail = imaplib.IMAP4_SSL("imap.gmail.com", '993')
    gmail.login(UserName, PassName)
    gmail.select("[Gmail]/&MFkweTBmMG4w4TD8MOs-")

    search_option = '(FROM {} SENTSINCE "01-Sep-2022" SENTBEFORE "12-Sep-2023")'.format(address)
    # ALLでSearchすると指定したラベルの全てのメールを読み込む
    head, data = gmail.search(None, search_option)

    # 取得したメール一覧の処理
    for num in data[0].split():
        h, d = gmail.fetch(num, '(RFC822)')
        raw_email = d[0][1]
        # 文字コード取得
        msg = email.message_from_bytes(raw_email)
        msg_encoding = email.header.decode_header(msg.get('Subject'))[0][1] or 'iso-2022-jp'
        # タイトルの情報を抽出
        msg_subject = email.header.decode_header(msg.get('Subject'))[0][0]
        # エンコーディング
        subject = str(msg_subject.decode(msg_encoding))
        #print(subject)

        #本文を取得
        print(msg.get_content_type())
        if msg.is_multipart():
            #charset = msg.get_content_charset()
            for payload in msg.get_payload():
                    char = payload.get_content_charset()
                    if payload.get_content_type() == "text/html":
                        print("----------------")
                        print(char)
                        if char == "iso-2022-jp":
                            rawbody = str(payload).encode(char)
                            body = quopri.decodestring(rawbody).decode('iso-2022-jp')
                            print(body)
                        elif char == "utf-8":
                            bodylist = str(payload).split('\n\n')
                            rawbody = bodylist[1].encode()
                            body = base64.b64decode(rawbody).decode()
                            print(body)
                            

        else:
            #print(msg.get_content_type())
            if msg.get_content_type() == "text/html":
                char = msg.get_content_charset()
                if char == "iso-2022-jp":
                    body = msg.get_payload().encode(char).decode(char)
                elif char == 'utf-8':
                    rawbody = str(msg.get_payload()).encode()
                    body = base64.b64decode(rawbody).decode()
                print(body)
                

    # 終了処理
    gmail.close()
    gmail.logout()

    

mail_analyze('nebotaka1@yahoo.co.jp')