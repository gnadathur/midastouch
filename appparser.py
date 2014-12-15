from urllib import urlencode

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import ystockquote
import pandas as pd

from webparser import BasicHTMLProcessing
from webparser import WebParser
from webparser import Ratings
from autologin import AutoLogin
from applog import logtrace


class TDPositions(BasicHTMLProcessing):
    ETF = "ETF"
    STOCKS = "STOCKS"
    CANNEDSTOCKS = "CANNEDSTOCKS"

    @logtrace
    def __init__(self, baseUrl=None, userid=None, driver=None, from_file=None):
        super(TDPositions, self).__init__()
        self.mydriver = driver
        self.diff52Col = "diff_52VsCurrent(%)"
        self.from_file = from_file
        if self.from_file is None:
            self.baseUrl = baseUrl
            self.userId = userid
            al = AutoLogin(self.baseUrl, self.userId, self.mydriver)
            al.logon()

    @logtrace
    def getCurrentBalancesAndPositions(self):
        bandp = "https://invest.ameritrade.com/cgi-bin/apps/u/BalancesAndPositions?mode=print"
        tblColName = "Symbol"
        tblClsName = "t0"
        cond = EC.presence_of_element_located((By.CLASS_NAME, tblClsName))
        self.soup = self.mydriver.getURL(bandp, cond)
        details = self.soup.find(lambda t: t.name == "td" and \
                                           unicode(t.string).strip() == tblColName)
        tblHeader = details.find_parent()
        tbl = tblHeader.find_parent()
        dfa = self.convertHTMLTableToDataFrame(tbl)
        return dfa

    @logtrace
    def __getAnyReport(self, investmentType, symbol):
        if self.from_file is not None:
            self.soup = self.mydriver.getURL()
            return
        customParams = {"savedName": symbol,
                        "c_name": "invest_VENDOR"
        }
        cannedParams = {
            "section": "stocks",
            "cannedName": symbol,
            "cannedSection": "Ratings",
            "c_name": "invest_VENDOR"
        }

        reportURL = {
            TDPositions.STOCKS: "https://invest.ameritrade.com/grid/p/site#r=jPage/https://research.ameritrade.com/grid/wwws/screener/stocks/results.asp?",
            TDPositions.ETF: "https://invest.ameritrade.com/grid/p/site#r=jPage/https://research.ameritrade.com/grid/wwws/screener/etfs/results.asp?"
        }
        reportPopupURL = {
            TDPositions.STOCKS: "https://research.ameritrade.com/grid/wwws/screener/stocks/resultsTearaway.asp?display=popup",
            TDPositions.ETF: "https://research.ameritrade.com/grid/wwws/screener/etfs/resultsTearaway.asp?display=popup"
        }
        reportURL[TDPositions.CANNEDSTOCKS] = reportURL[TDPositions.STOCKS]
        reportPopupURL[TDPositions.CANNEDSTOCKS] = \
            reportPopupURL[TDPositions.STOCKS]
        params = {
            TDPositions.STOCKS: customParams,
            TDPositions.CANNEDSTOCKS: cannedParams,
            TDPositions.ETF: customParams
        }
        # TODO: figure out wait conditions
        url = reportURL[investmentType] + urlencode(params[investmentType])
        self.soup = self.mydriver.getURL(url)
        url = reportPopupURL[investmentType]
        cond = EC.presence_of_element_located((By.ID, "screenerContainer"))
        self.soup = self.mydriver.getURL(url, cond)

    def getETFRatingReport(self, etfName):
        return self.__getAnyReport(TDPositions.ETF, etfName)

    @logtrace
    def getCannedStockReport(self, symbol="BuyRatings"):
        self.__getAnyReport(TDPositions.CANNEDSTOCKS, symbol)
        displayCols = ["CompanyName",
                       "GICSSector",
                       "PriceCurrent",
                       "total_score"]
        return self.processReport(displayCols=displayCols)

    @logtrace
    def ratingsGuide(self, allData):
        ratingCols = ["ConsRecValue_format",
                      "CreditSuisseRating",
                      "FordRatingValue_format",
                      "JaywalkConsensus5PtScore",
                      "MarketEdgeCombined",
                      "RTCurrentRating_format",
                      "WeissRatingValue_format"
        ]
        rtSubset = allData[ratingCols]
        for i in rtSubset.index:
            rtSubset.loc[i, "JaywalkConsensus5PtScore"] = \
                Ratings.processJaywalk(rtSubset.loc[i,
                                                    "JaywalkConsensus5PtScore"])
            rtSubset.loc[i, "MarketEdgeCombined"] = \
                Ratings.processMarketEdge(rtSubset.loc[i,
                                                       "MarketEdgeCombined"])

        def ratemapper(x):
            if type(x) is not float:
                return WebParser().parse(x, WebParser.PSTYPE_RATINGS)
            elif x < Ratings.NEUTRAL:
                return 0
            return x

        remapped = rtSubset.applymap(ratemapper)
        allData.loc[:, remapped.columns.values.tolist()] = remapped
        allData['total_score'] = remapped.sum(axis='columns')
        return allData

    @logtrace
    def diff52WeekHigh(self, df):
        allHighs = list()
        for symbol in df.index.values.tolist():
            try:
                baseVal = df.loc[symbol, "PriceCurrent"]
                high52 = float(ystockquote.get_52_week_high(symbol))
                high52 = round(((high52 - baseVal) * 100) / baseVal, 1)
            except:
                high52 = 0
            allHighs.append(high52)

        df[self.diff52Col] = pd.Series(allHighs, index=df.index)
        return df


    @logtrace
    def processReport(self, indexSymbol='ticker', diff_52=True,
                      displayCols=None):

        self.logon = False
        # self.__getSoup()
        divEle = self.soup.find("div", {"id": "screenerContainer"})
        colEle = divEle.find_parent()
        scr = colEle.find("script", text=True)
        self.logon = True
        inpStr = scr.string.strip()
        parsed = self.parser.parse(inpStr, WebParser.PSTYPE_JS)
        df = self.convertDictListToDataFrame(parsed[2]['data'],
                                             indexSymbol)
        df = self.ratingsGuide(df)
        sorters = ['total_score', 'PriceCurrent', 'SPStarRating']
        # 0 - descending 1 - ascending
        sortOrder = [0, 1, 0]
        if diff_52:
            df = self.diff52WeekHigh(df)
            sorters.insert(1, self.diff52Col)
            sortOrder.insert(1, 0)
            displayCols.append(self.diff52Col)
        dfsorted = df.sort(sorters, ascending=sortOrder)
        if displayCols is None:
            return dfsorted
        return dfsorted.filter(displayCols)
    
