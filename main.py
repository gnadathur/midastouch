import optparse

from webDriver import CustomDriver

from appparser import TDPositions
from applog import AppLog


def main():
    p = optparse.OptionParser()
    p.add_option("-b", "--baseurl", type="string", action="store", dest="url")
    p.add_option("-u", "--userid", type="string", action="store", dest="userid")
    opt, args = p.parse_args()

    mydriver = CustomDriver(CustomDriver.CHROME, opt.url)
    mydriver.initURL()
    tdps = TDPositions(opt.url, opt.userid, mydriver)
    df = tdps.getCannedStockReport()
    AppLog.out(df.to_string())


if __name__ == '__main__':
    main()
