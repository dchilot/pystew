import logging
import sys
import os

def init():
    full = sys.argv[0].replace(".py", ".log")
    filename = os.path.basename(sys.argv[0]).replace(".py", ".log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=full,
        filemode='w')

#    print "full = '%s'" % full
#    print "filename = '%s'" % filename
    logging.debug("start logging")

    _CONSOLE = logging.StreamHandler(sys.stdout)
    _CONSOLE.setLevel(logging.INFO)
    logging.getLogger('').addHandler(_CONSOLE)

if (__name__ != "__main__"):
    init()