import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='regexp.log',
    filemode='w')

_CONSOLE = logging.StreamHandler(sys.stdout)
_CONSOLE.setLevel(logging.INFO)
logging.getLogger('').addHandler(_CONSOLE)
