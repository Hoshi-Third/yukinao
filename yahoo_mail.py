import imaplib
import email
import base64
import quopri

UserName = "sarutaka27"
PassName = "a19781227"

yahoomail = imaplib.IMAP4_SSL("imap.mail.yahoo.com", '993')
yahoomail.login(UserName, PassName)
print(yahoomail.list())

