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
import keyring


class PasswordProtect(object):
    def __init__(self, service):
        self.service = service

    def getPass(self, username):
        pswd = keyring.get_password(self.service, username)
        return pswd