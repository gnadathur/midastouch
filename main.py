import argparse

from webDriver import CustomDriver

from appparser import TDPositions
from applog import AppLog


def main():
    p = argparse.ArgumentParser(description=
                                'Login to stock broker and extract relevant stock information')
    p.add_argument("-b", "--baseurl", dest="url", help="base URL of the site")
    p.add_argument("-u", "--userid", dest="userid", help="user ID of the account")
    opt = p.parse_args()

    mydriver = CustomDriver(CustomDriver.CHROME, opt.url)
    mydriver.initURL()
    tdps = TDPositions(opt.url, opt.userid, mydriver)
    df = tdps.getCannedStockReport()
    AppLog.out(df.to_string())


if __name__ == '__main__':
    main()
