# ------------------------------------------------------------------------------
# Name:       PasswordProtect 
# Purpose:
#
# Author:      gokul
#
# Created:     24/01/2014
# Copyright:   (c) gokul 2014
# Licence:     <your licence>
# ------------------------------------------------------------------------------
import keyring
import optparse
import platform

class PasswordProtect(object):
    def __init__(self, service):
        self.service = service

    def getPass(self, username):
        if platform.system() == 'Linux':
            return 'omsakthi'
        pswd = keyring.get_password(self.service, username)
        return pswd

    def setPass(self, username, pswd):
        keyring.set_password(self.service, username, pswd)


def main():
    p = optparse.OptionParser()
    p.add_option("-b", "--baseurl", type="string", action="store", dest="url")
    p.add_option("-u", "--userid", type="string", action="store", dest="userid")
    p.add_option("-p", "--password", type="string", action="store", dest="pswd")
    opt, _ = p.parse_args()

    ps_pt = PasswordProtect(opt.url)
    ps_pt.setPass(opt.userid, opt.pswd)


if __name__ == '__main__':
    main()
