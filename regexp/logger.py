import logging
import sys
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=os.path.basename(sys.argv[0]).replace(".py", ".log"),
    filemode='w')

_CONSOLE = logging.StreamHandler(sys.stdout)
_CONSOLE.setLevel(logging.INFO)
logging.getLogger('').addHandler(_CONSOLE)
