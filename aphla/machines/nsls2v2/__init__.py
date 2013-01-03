"""
NSLS2 V2
---------
"""

import logging

#APHLA_LOG = os.path.join(tempfile.gettempdir(), "aphla.log")
APHLA_LOG = 'aphla.nsls2v2.log'
#logging.basicConfig(filename=APHLA_LOG,
#    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
#    level=logging.DEBUG)
_lgfmt = logging.Formatter("%(asctime)s - %(name)s [%(levelname)s]: %(message)s")
# set null handler when logging for a library.
_lghdl = logging.FileHandler(filename=APHLA_LOG)
_lghdl.setLevel(logging.DEBUG)
_lghdl.setFormatter(_lgfmt)

logging.getLogger('aphla').addHandler(_lghdl)

logger = logging.getLogger(__name__)
logger.info("Testing")

from lattice import *

