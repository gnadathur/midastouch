import smtplib
from applog import AppLog
from applog import logtrace


class MailIt(object):
    GMAIL = "GMAIL"

    @logtrace
    def __init__(self, user, pswd, mailServer=MailIt.GMAIL):
        self.mailConfig = {
            MailIt.GMAIL: {
                'smtp': ['smtp.gmail.com', 587]
            }
        }
        smtpServer = lambda t: self.mailConfig[t]['smtp'][0]
        smtpPort = lambda t: self.mailConfig[t]['smtp'][1]

        self.server = smtplib.SMTP(smtpServer(mailServer),
                                   smtpPort(mailServer))
        self.server.ehlo()
        self.server.starttls()
        self.server.login(user, pswd)

    @logtrace
    def sendMessage(self, fromAddr, toAddr, msg):
        self.server.sendmail(fromAddr, toAddr, msg)

    def close(self):
        self.server.close()