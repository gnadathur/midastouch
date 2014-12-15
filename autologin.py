# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      gokul
#
# Created:     24/01/2014
# Copyright:   (c) gokul 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Following are optional required
from selenium.common import exceptions as selex
from fysom import Fysom

from securify import PasswordProtect


class AutoLogin(object):
    def __init__(self, login_service, username, mydriver):
        self.baseurl = login_service
        self.username = username
        self.mydriver = mydriver
        self.login_timeout = "5000"

    def logon(self):
        self.psget = PasswordProtect(self.baseurl)
        self.logon_fsm = Fysom({
            'initial': {'state': 'start'
            },
            'events': [
                {'name': 'userid',
                 'src': 'start',
                 'dst': 'username_sent'
                },
                {'name': 'password',
                 'src': 'username_sent',
                 'dst': 'password_sent'
                },
                {'name': 'logon',
                 'src': 'password_sent',
                 'dst': 'logged_on'
                }],
            'final': 'logged_on',
            'callbacks': {
                'onuserid': self.send_userid,
                'onpassword': self.send_password,
                'onlogon': self.send_logon
            }
        })
        self.logon_fsm.userid(html_id='userid')
        self.logon_fsm.password(html_id='password')
        self.logon_fsm.logon(html_id='logon')

    def __clear_and_send(self, ele_id, val, sim=False):
        if sim is True:
            print "element = ", ele_id, "val =", val
            return
        try:
            #Clear Username TextBox if already allowed "Remember Me"
            try:
                web_obj = self.mydriver.driver.find_element_by_id(ele_id)
            except selex.NoSuchElementException:
                self.log.error("%s not found", ele_id)
            web_obj.clear()

            #Write Username in Username TextBox
            web_obj.send_keys(val)
        except:
            pass

    def send_userid(self, e):
        self.__clear_and_send(e.html_id, self.username)

    def send_password(self, e):
        pswd = self.psget.getPass(self.username)
        assert (pswd is not None)
        self.__clear_and_send(e.html_id, pswd)

    def send_logon(self, e):
        #Click Login button
        self.mydriver.driver.find_element_by_id(e.html_id).click()
        self.mydriver.driverWait()
