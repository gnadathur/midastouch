from autologin import AutoLogin
from webDriver import CustomDriver

__author__ = 'gokul'


def main():
    url0="https://invest.ameritrade.com/grid/p/site#r=jPage/cgi-bin/apps/u/GainskeeperStart"
    url = "https://invest.ameritrade.com/grid/p/site#r=jPage/https://gainskeeper.ameritrade.com/amtdGP/GainLoss.aspx?c_name=invest_VENDOR"
    baseurl = "www.tdameritrade.com"
    userid = "36205503"
    mydriver = CustomDriver(CustomDriver.CHROME, baseurl)
    mydriver.initURL()
    al = AutoLogin(baseurl, userid, mydriver)
    al.logon()
    mydriver.getURL(url0)

if __name__ == '__main__':
    main()
