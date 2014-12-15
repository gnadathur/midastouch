from pyparsing import QuotedString, Suppress, delimitedList, Optional, \
    Word, alphas, alphanums, Regex, Forward, Group, Dict, \
    CaselessKeyword, MatchFirst, Or, Keyword, FollowedBy, \
    Literal, nums, Combine, ZeroOrMore
import pandas as pd
import numpy as  np

from applog import AppLog
from applog import logtrace


class Ratings(object):
    NEUTRAL = 0
    BETTER = 1
    BEST = 2
    BAD = -1
    WORSE = -2

    NEUTRAL_STR = "hold"
    BETTER_STR = "buy"
    BEST_STR = "strong buy"
    BAD_STR = "reduce"
    WORSE_STR = "strong sell"

    ratingMaps = {"buy": BETTER,
                  "strong buy": BEST,
                  "hold": NEUTRAL,
                  "reduce": BAD,
                  "outperform": BETTER,
                  "neutral": NEUTRAL,
                  "underperform": BAD,
                  "accumulate": BETTER,
                  "strong sell": WORSE
    }

    jwRatingsMap = [None, BEST_STR, BETTER_STR, NEUTRAL_STR,
                    BAD_STR, WORSE_STR]

    @staticmethod
    def processMarketEdge(v):
        (cat, value) = v.split()
        cat = cat.lower()
        value = int(value)
        if cat == "long":
            if value == 0 or value == -1:
                return Ratings.BETTER_STR
            return Ratings.NEUTRAL_STR
        elif cat == "long/neutral":
            if value == -3:
                return Ratings.BAD_STR
            if value == -4:
                return Ratings.WORSE_STR
        elif cat == "avoid":
            if value == 3 or value == 4:
                return Ratings.BETTER_STR
            return Ratings.BAD_STR
        elif cat == "avoid/neutral":
            if value == 3 or value == 4:
                return Ratings.BETTER_STR
        return Ratings.NEUTRAL_STR

    @staticmethod
    def processJaywalk(v):
        y = int(round(float(v), 0))
        try:
            return Ratings.jwRatingsMap[y]
        except:
            AppLog.log.warning("Could not understand %d",y)
            return Ratings.NEUTRAL_STR


class WebParser(object):
    boolMaps = {"false": False, "true": True, "yes": True, "no": False}

    PSTYPE_DEFAULT = "DEFAULT"
    PSTYPE_JS = "JS"
    PSTYPE_DICT = "dict"
    PSTYPE_RATINGS = "ratings"

    def __init__(self, fromFile=False):
        self.fromFile = fromFile
        self.parseTypes = dict()
        self.__defineBasicTypes()
        self.__defineDictGrammar()
        self.__defineJSGrammar()

    quoteit = lambda self, v, lq='"', rq=None: \
        Suppress(lq) + Optional(v) + Suppress(rq) \
            if rq is not None else \
            Suppress(lq) + v + Suppress(lq)

    quoteitno = lambda self, v, lq='"', rq=None: \
        Suppress(lq) + v + Suppress(rq) \
            if rq is not None else \
            Suppress(lq) + v + Suppress(lq)

    datatypeAndQuote = lambda self, v, lq='"', rq=None: \
        MatchFirst([v, self.quoteitno(v, lq, rq)])

    completeType = lambda self, bt, name="", fn=None, lq='"', rq=None: \
        (self.datatypeAndQuote(bt, lq, rq)).setName(name).setParseAction(fn) \
            if fn is not None else \
            (self.datatypeAndQuote(bt, lq, rq)).setName(name)

    @logtrace
    def __defineBasicTypes(self):
        self.KDELIM = Suppress(":")
        sign = Word("+-", max=1) + FollowedBy(Word(nums))
        crncy = Word(nums) + ZeroOrMore(Suppress(",") + Word(nums)) + \
                Optional(Literal(".") + Word(nums))
        baseUnknownValue = Keyword("?")
        self.unknown = self.completeType(baseUnknownValue, "UNKNOWN_VAL",
                                         lambda t: np.nan)

        floatNumberBasic = Combine(Optional(sign) + \
                                   Or([Word(nums),
                                       crncy,
                                       Regex(r'[0-9]+(\.\d*)?([eE]\d+)?')])) + \
                           Optional(Suppress("%"))
        self.floatNumber = self.completeType(floatNumberBasic, "float",
                                             lambda t: float(t[0]))

        baseBoolValue = Or([CaselessKeyword("false"), CaselessKeyword("true"),
                            CaselessKeyword("yes"), CaselessKeyword("no")])
        self.boolean = self.completeType(baseBoolValue, "bool",
                                         lambda t: WebParser.boolMaps[t[0]])

        ratingKeywords = [CaselessKeyword(k).setParseAction( \
            lambda t: Ratings.ratingMaps[t[0].lower()]) \
                          for k in Ratings.ratingMaps.keys()]
        ratingKeywords.append(Keyword("--").setParseAction(lambda t: np.nan))
        self.ratings = self.completeType(Or(ratingKeywords), "ratings")
        self.parseTypes[WebParser.PSTYPE_RATINGS] = self.ratings

    @logtrace
    def __defineDictGrammar(self):
        """Function defines the grammar for parsing a string(mainly) into:
        1. Value: Value could be any one of the following
            1. Simple types such as:
                a. numbers: all are floating point
                b. boolean: [true,false], [yes, no]
                c. Strings within double quotes
                d. alphanumerics
            2. Dictionary
            3. List
        2. Dictionary: Set of key value pairs. ':' delimits values from keys.
        ',' delimites different pairs. '{}' delimits a dictionary.
        3. List: Ordered list of values delimited by ','
        pyparsing parse actions are used to convert the tokens into pyton native
        datatype such 'float' for floating point, 'dict' for dictionary and 
        'list' for list. The parser supports arbitrary nesting of the above 
        tokens. Both the nesting and datastructure type integrity is preserved
        in the resulting python representation.
        Application: 
        One of the main use of the grammar is to scrap web pages and extract a
        combination of JSON and javascript-like HTML attributes into python
        data structures. Simpler use cases include extracting supported simple 
        data types from say, HTML tables.  
        """
        dictDefn = Forward()
        listDefn = Forward()
        key = (QuotedString('"') | Word(alphas)) + FollowedBy(Literal(":"))
        key.setName("key")
        self.value = MatchFirst([self.unknown, self.floatNumber,
                                 self.boolean, QuotedString('"'),
                                 Word(alphanums), dictDefn, listDefn])
        self.value.setName("value")
        # dict_element = Group(key + self.KDELIM + self.value)
        dict_element = Group(key + self.KDELIM + self.value) + \
                       FollowedBy(Or([Literal(","), Literal("}")]))
        lde = Group(Dict(delimitedList(dict_element)))
        dictDefn << ((self.quoteit(lde, '{', '}')) | lde)
        self.dictDefn = dictDefn
        self.dictDefn.setName("Dictionary")
        listDefn << self.quoteit(Group(delimitedList(self.value)), '[', ']')
        self.listDefn = listDefn
        self.listDefn.setName("List")
        self.topElement = Or([self.dictDefn, self.listDefn, self.value])
        self.parseTypes[WebParser.PSTYPE_DEFAULT] = self.topElement
        self.parseTypes[WebParser.PSTYPE_DICT] = self.dictDefn
        return

    @logtrace
    def __defineJSGrammar(self):
        identifier = Word(alphas + "_", alphanums + "_")
        jsFn = identifier + Suppress(".") + identifier
        jsArgs = Suppress("(") + self.topElement + Suppress(")")
        jsStmt = jsFn + jsArgs + Suppress(";")
        self.jsStmt = jsStmt.setName("JS_Statement")
        self.parseTypes[WebParser.PSTYPE_JS] = self.jsStmt

    @logtrace
    def __parse(self, inputStr, parseType):
        if self.fromFile:
            parsed = self.parseTypes[parseType].parseFile(inputStr)
        else:
            parsed = self.parseTypes[parseType].parseString(inputStr)
        if parseType == WebParser.PSTYPE_DEFAULT or \
                        parseType == WebParser.PSTYPE_RATINGS:
            return parsed[0]
        return parsed

    @logtrace
    def parse(self, inputStr, parseType=None):
        if parseType is None:
            parseType = WebParser.PSTYPE_DEFAULT
        return self.__parse(inputStr, parseType)


class BasicHTMLProcessing(object):
    def __init__(self):
        self.soup = None
        self.encoding = 'utf-8'
        self.top_delim = ','
        self.key_delim = ':'
        self.logon = True
        self.dumpLog = AppLog.log
        self.parser = WebParser()
        return

    @logtrace
    def logElement(self, ele, to_console=True):
        if self.logon:
            self.dumpLog.info("%s", ele.prettify(encoding=self.encoding))

    @logtrace
    def convertStrToStructuredData(self, inputStr,
                                   klist=[]):
        parsed = self.parser.parse(inputStr)
        p = parsed
        for k in klist:
            p = p[k]
        return p

    @logtrace
    def convertDictListToDataFrame(self, ldict, index_key):
        srs_list = []
        for l in ldict:
            name = l[index_key]
            local_dict = {k: l[k] for k in l.keys() if k != index_key}
            srs = pd.Series(local_dict, name=name)
            srs_list.append(srs)
        df = pd.DataFrame(srs_list)
        return df

    @logtrace
    def convertHTMLTableToDataFrame(self, tblBody,
                                    hdrAttr={"class": "header"}):
        stripit = lambda c: c.string.strip()
        nonzero = lambda s: len(s) != 0
        nzands = lambda l: filter(nonzero, map(stripit, l))
        coltxts = lambda wp, r: [wp.parse('"' + colstr + '"') for colstr in \
                                 nzands(r.find_all("td", text=True,
                                                   recursive=False))]
        checkAttrNotInList = lambda r, l, a: r.has_attr(l) and \
                                             a not in r.attrs[l]

        hdrRow = tblBody.find("tr", hdrAttr)
        dfCol = coltxts(self.parser, hdrRow)
        numCols = len(dfCol)
        dfa = pd.DataFrame(columns=dfCol[1:])
        dfa.index.name = dfCol[0]

        rows = tblBody.find_all("tr", recursive=False)
        for r in rows:
            if checkAttrNotInList(r, "class", "header"):
                cols = coltxts(self.parser, r)
                assert (len(cols) == numCols)
                dfa = dfa.append(pd.Series(cols[1:], name=cols[0],
                                           index=dfCol[1:]))
        return dfa
