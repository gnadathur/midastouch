import unittest
from inspect import currentframe, getframeinfo

import webparser
from appparser import TDPositions


class WebParserTest(unittest.TestCase):
    fname = lambda self, f: f.function
    lineno = lambda self, f: f.lineno

    def feedParser(self, inpStr, finfo, ptype=webparser.WebParser.PSTYPE_DEFAULT):
        print inpStr
        wp = webparser.WebParser()
        parsed = wp.parse(inpStr, ptype)
        print ':'.join([self.fname(finfo), str(self.lineno(finfo))]), "=", parsed
        return parsed

    def testHTMLParsing(self):
        finfo = getframeinfo(currentframe())
        inpStr = '"ticker_format"'
        self.feedParser(inpStr, finfo)
        inpStr = '"<input type=\u0022checkbox\u0022 symbol=\u0022ONNN\u0022 /><a class=\u0022grid-symbol\u0022 href=\u0022/grid/wwws/stocks/overview/overview.asp?symbol=ONNN\u0022 symbolLink=\u0022ONNN\u0022 symbol=\u0022ONNN\u0022>ONNN</a>"'
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":"$9.42"}"""
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":9.42}"""
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":-9}"""
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":-9,42}"""
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":-9,42.00}"""
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":-9,"first":0}"""
        print inpStr[:15]
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)
        inpStr = """{"matches":-9,"first":0,"data":[{"Realtime":true,"StockExchange_format":"NASDAQ","PriceCurrent":9.42,"PriceCurrent_format":"$9.42","PriceCurrentDelayed":9.42,"PriceCurrentDelayed_format":"$9.42","PriceDlrChgSinceMarketOpen":0.14,"PriceDlrChgSinceMarketOpen_formatChart":"<img class=\u0022grid-upArrowImg\u0022 src=\u0022../../images/up.gif\u0022 />&nbsp;<span class=\u0022positive\u0022>0.14</span>","PriceDlrChgSinceMarketOpen_format":"<span class=\u0022positive\u0022>$0.14</span>","PricePctChgSinceMarketOpen":1.50862,"PricePctChgSinceMarketOpen_formatChart":"<span style=\u0022color:#00B624\u0022>(1.51%)</span>","PricePctChgSinceMarketOpen_format":"<span class=\u0022positive\u0022>+1.51%</span>","LastTradeTime":41684.666666666664,"LastTradeTime_format":"February 14, 2014","RTPreviousRating":3,"RTPreviousRating_format":"Hold","RTCurrentRating":2,"RTCurrentRating_format":"Accumulate","RTCurrentRatingDate":41682,"RTCurrentRatingDate_format":"2/12/14","CreditSuisseRating":"OUTPERFORM","CreditSuisseRating_format":"Outperform<a href=\u0022csPassthrough.asp?symbol=ONNN\u0022 class=\u0022iconbackground reportPDFLeft\u0022 onclick=\u0022pdf(this.href); return false;\u0022>Download</a>","SPStarRating":"5","SPStarRating_format":"<span class='mStarRatingsWrapper'><img src='/tdameritrade/grid/images/icons/icn_star.gif' /><img src='/tdameritrade/grid/images/icons/icn_star.gif' /><img src='/tdameritrade/grid/images/icons/icn_star.gif' /><img src='/tdameritrade/grid/images/icons/icn_star.gif' /><img src='/tdameritrade/grid/images/icons/icn_star.gif' /></span>","WeissRatingValue":3,"WeissRatingValue_format":"Buy","ConsRecValue":4,"ConsRecValue_format":"Buy","MarketEdgeCombined":"Long 0","MarketEdgeCombined_format":"Long/0","FordRatingValue":2,"FordRatingValue_format":"Buy","JaywalkConsensus5PtScore":2.4,"JaywalkConsensus5PtScore_format":"<div class=\u0022reportrating stocks_jaywalkBUY\u0022 style=\u0022margin-top:10px;float:right;\u0022><div id=\u0022jaywalkpointer\u0022 style=\u0022left:63px;\u0022></div><div id=\u0022jaywalkmin\u0022>1</div><div id=\u0022jaywalkmax\u0022>5</div><div id=\u0022jaywalkscore\u0022 style=\u0022left:71px;\u0022>2.4</div></div><div class=\u0022clear\u0022></div>","BUYSELL":-32768,"BUYSELL_format":"<a href=\u0022https://invest.ameritrade.com/cgi-bin/apps/u/ThirdPartyUrlLauncher/new?target=buyBttn&param=ONNN\u0022 target=\u0022vendorLinks\u0022 class=\u0022normal\u0022>Buy</a> <a href=\u0022https://invest.ameritrade.com/cgi-bin/apps/u/ThirdPartyUrlLauncher/new?target=sellBttn&param=ONNN\u0022 target=\u0022vendorLinks\u0022 class=\u0022normal\u0022>Sell</a> ","MORE":-32768,"MORE_format":"<div class=\u0022mi\u0022><a href=\u0022#\u0022 class=\u0022normal\u0022 id=\u0022morelink_ONNN\u0022 onMouseOver=\u0022showMoreTitle(this);\u0022 onClick=\u0022generateResearchMore('ONNN','ONNN','ON Semiconductor Corp','NASDAQ','','');return false;\u0022><div id=\u0022more_ONNN\u0022 class=\u0022moreicon\u0022></div></a></div>","isCommissionFree":false}]}"""
        finfo = getframeinfo(currentframe())
        self.feedParser(inpStr, finfo)

    def testDictParsing(self):
        inp_str = """
            {name:"watchlistSmall",  
                    mTitle:"Watch List",
                    refreshType: "html",
                    data: {"content" : {
            "label" : "symbol",
            "maxCustomWatchlist" : 49,
            "maxWatchlistSymbol" : "50",
            "stockDetailsURL":"/grid/p/site#r=jPage/https://research.ameritrade.com/grid/wwws/stocks/overview/overview.asp?c_name=invest_VENDOR",
            "watchlistId": "ACCT882232804",
            "watchlistType": "POSITION",
            "pref": "CHANGE",
            "sortColumn": "UNSPECIFIED",
            "sortIndicator": "UNSPECIFIED",
            "items": [
            {
            "id": "1.00",
            "isValidFlag": "yes",
            "isRealtimeFlag": "yes",
            "delayed":false,
            "isNonStdOption": [],
            "symbol": "HSCSX",
            "streamingSymbol": "HSCSX",
            "symbolDisplay": "HSCSX",
            "securityTypeDescription": "Fund",
            "securityTypeValue": "F",
            "exchangeName":"",
            "companyName":"HOMESTEAD SMALL-CO STOCK FUND",
            "last": "34.86",
            "change": "-0.15",
            "changePercentage": "-0.4284",
            "bid":"?",
            "ask":"?",
            "open":"?",
            "close":"35.01",
            "high":"0.00",
            "low":"0.00",
            "vol": "0.00"
            }
            ,
            {
            "id": "2.00",
            "isValidFlag": "yes",
            "isRealtimeFlag": "yes",
            "delayed":false,
            "isNonStdOption": false,
            "symbol": "PRBLX",
            "streamingSymbol": "PRBLX",
            "symbolDisplay": "PRBLX",
            "securityTypeDescription": "Fund",
            "securityTypeValue": "F",
            "exchangeName":"",
            "companyName":"PARNASSUS INCOME TRUST - EQUITY INCOME FUND (THE)",
            "last": "34.90",
            "change": "-0.17",
            "changePercentage": "-0.4847",
            "bid":"?",
            "ask":"?",
            "open":"?",
            "close":"35.07",
            "high":"0.00",
            "low":"0.00",
            "vol": "0.00"
            }
            ,
            {
            "id": "3.00",
            "isValidFlag": "yes",
            "isRealtimeFlag": "yes",
            "delayed":false,
            "isNonStdOption": false,
            "symbol": "ARTIX",
            "streamingSymbol": "ARTIX",
            "symbolDisplay": "ARTIX",
            "securityTypeDescription": "Fund",
            "securityTypeValue": "F",
            "exchangeName":"",
            "companyName":"ARTISAN INTL FUND INVEST SHARES",
            "last": "28.54",
            "change": "0.06",
            "changePercentage": "0.2107",
            "bid":"?",
            "ask":"?",
            "open":"?",
            "close":"28.48",
            "high":"0.00",
            "low":"0.00",
            "vol": "0.00"
            }
            ]
            }
            },
                    muuid:"A00b16c95-1b80-43ce-a95a-76372f68a294",
                    moduleId:"watchlistSmall-1"}        
            """
        wp = webparser.WebParser()
        parsed = wp.parse(inp_str)
        print parsed['data']['content']['items'][0]

    """
    def testRatings(self):
        print "Being testratings"
        wp = webparser.WebParser()
        for k in webparser.Ratings.ratingMaps.keys():
            parsed = wp.parse(k,webparser.WebParser.PSTYPE_RATINGS)
            print k, "=", parsed
    """

    def testJSFunctionParsing(self):
        fromFile = "C:\Users\gokul\workspace\\finase\\buyratings.txt"
        td = TDPositions(from_file=fromFile)
        df = td.getCannedStockReport()
        print df.to_string()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
