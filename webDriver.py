from selenium import webdriver
from applog import logtrace
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import platform

from webparser import BasicHTMLProcessing

__author__ = 'gokul'

def ajax_complete(driver):
    try:
        return 0 == driver.execute_script("return jQuery.active")
    except WebDriverException:
        pass

class CustomDriver(BasicHTMLProcessing):
    FIREFOX=0
    CHROME=1

    def __init__(self, drvType, baseUrl, fromFile = None):
        super(CustomDriver, self).__init__()
        if platform.system() == 'Darwin':
            self.wDriver = webdriver.Safari()
        elif drvType == CustomDriver.FIREFOX:
            self.wDriver = webdriver.Firefox()
        elif drvType == CustomDriver.CHROME:
            if platform.system() == 'Linux':
                chromeDriver = '/usr/bin/chromedriver'
            else:
                chromeDriver = "C:\\Users\\gokul\\Desktop\\Software\\chromedriver.exe"
            self.wDriver = webdriver.Chrome(chromeDriver)
        else:
            assert(0)
        self._baseUrl = "http://" + baseUrl
        self.fromFile = fromFile
        self.pageTimeout = 30

    @property
    def baseUrl(self):
        return self._baseUrl

    @property
    def driver(self):
        return self.wDriver

    def initURL(self):
        self.wDriver.get(self.baseUrl)
        self.wDriver.maximize_window()

    def driverWait(self, cond=None):
        if cond is not None:
            WebDriverWait(self.wDriver, self.pageTimeout).until(cond)
        else:
            WebDriverWait(self.wDriver, self.pageTimeout).until(ajax_complete)
        time.sleep(30)

    @logtrace
    def getURL(self, url=None, cond=None):
        if self.fromFile is None:
            self.dumpLog.info(url)
            self.wDriver.get(url)
            self.driverWait(cond)
        return self.getSoup()

    @logtrace
    def getSoup(self):
        if self.fromFile is None:
            html_source = self.wDriver.page_source
            soup = BeautifulSoup(html_source, from_encoding=self.encoding)
        else:
            fd = open(self.fromFile)
            soup = BeautifulSoup(fd)
        self.logElement(soup)
        return soup

    def __del__(self):
        self.wDriver.close()
