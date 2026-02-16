all = ['CryTask']

import ccxt as _ccxt
import time as _time

from .c_CryTask import\
    CryTask as _CryTask

class CryTaskTest(_CryTask):
    def _main(self, exchange:_ccxt.coinbase):
        _time.sleep(5.0)