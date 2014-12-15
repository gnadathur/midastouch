from __future__ import print_function
import getpass
import os
import tempfile
import logging
from decorator import decorator


@decorator
def logtrace(aFunc, *args, **kw):
    """

    :param aFunc:
    :param args:
    :param kw:
    :return: :raise:
    """
    AppLog.log.debug("enter %s", aFunc.__name__)
    try:
        result = aFunc(*args, **kw)
    except Exception, e:
        AppLog.log.exception("exception %s %s", aFunc.__name__, e)
        raise
    AppLog.log.debug("exit %s", aFunc.__name__)
    return result


class AppLog(object):
    def __init__(self):
        username = getpass.getuser()
        userpath = os.path.expanduser('~' + username)
        logdirpath = os.path.join(userpath, 'finalog')
        AppLog.gdrivepath = os.path.join(userpath, "Desktop", "gdrive")
        AppLog.outdir = os.path.join(AppLog.gdrivepath, "finase_reports")
        if not os.path.exists(logdirpath):
            os.makedirs(logdirpath)
        if not os.path.exists(AppLog.outdir):
            os.makedirs(AppLog.outdir)
        fd = tempfile.NamedTemporaryFile(dir=logdirpath,
                                         delete=False)
        print("Created ", fd.name)
        logname = fd.name
        fd.close()
        AppLog.log = logging.getLogger("Finase")
        handler = logging.FileHandler(logname)
        AppLog.log.addHandler(handler)
        AppLog.log.propagate = False
        AppLog.log.setLevel(logging.DEBUG)
        AppLog.outf = tempfile.NamedTemporaryFile(dir=AppLog.outdir,
                                                  prefix="finrep_",
                                                  delete=False)
        print("Output file is ", AppLog.outf.name)

    @staticmethod
    def out(*args):
        print(*args, file=AppLog.outf)
        AppLog.outf.flush()


AppLog()


@logtrace
def main():
    """
    test AppLog

    """
    AppLog.out("hello")


if __name__ == '__main__':
    main()
