all = ['App']

import time as _time

from datetime import\
    datetime as _datetime,\
    timezone as _timezone
from typing import\
    Callable as _Callable

from .c_AppCRSys import\
    AppCRSys as _AppCRSys
from .c_AppCRType import\
    AppCRType as _AppCRType
from .c_AppCRWaitTime import\
    AppCRWaitTime as _AppCRWaitTime
from .c_AppUpdateParams import\
    AppUpdateParams as _AppUpdateParams
from .c_AppUpdateResult import\
    AppUpdateResult as _AppUpdateResult
from .inner.c_AppIO import\
    AppIO as _AppIO
from .inner.c_Cry import\
    Cry as _Cry
from .inner.c_CLIError import\
    CLIError as _CLIError
from .inner.c_CLIErrorType import\
    CLIErrorType as _CLIErrorType

class App:
    """
    Represents major functions for app
    """

    #region init

    def __init__(self, cry:_Cry, appio:_AppIO,\
            ddos_delay:float,\
            ddos_max:int,\
            net_delay:float,\
            net_max:int,\
            symbols:dict[str, str]):
        """
        Initializer for App

        :param cry:
            Crypto interface
        :param appio:
            I/O data
        """
        self.__cry = cry
        self.__appio = appio
        # quit
        self.__quit = False
        # ddos
        self.__ddos_delay = ddos_delay
        self.__ddos_max = ddos_max
        # net
        self.__net_delay = net_delay
        self.__net_max = net_max
        # symbols
        self.__symbols = symbols
        # crsys
        self.__crsys = _AppCRSys()
        # inputcache
        self.__inputcache:list[int] = []
        # delta
        self.__delta = 0.0

    #endregion

    #region properties

    @property
    def cry(self):
        """
        Crypto interface
        """
        return self.__cry

    @property
    def appio(self):
        """
        I/O data
        """
        return self.__appio

    @property
    def quit(self):
        """
        Whether or not user wants to quit
        """
        return self.__quit

    #endregion

    #region helper methods

    def __print_line(self, y:int, message:str):
        w, h = self.__appio.get_size()
        if len(message) < w:
            message += ' ' * (w - len(message))
        self.__appio.print(0, y, message)
    
    def __wrap(self, action:_Callable[[], None]):
        def _catch(_retries:int, _max:int, _delay:float, _msg:str):
            if _retries >= _max:
                return -1
            _retries += 1
            self.__print_line(2,\
                f"{_msg} Retrying in {_delay} seconds. {_retries}/{_max}")
            return _retries
        ddos_retries = 0
        net_retries = 0
        error = None
        wait = 0.0
        while True:
            try:
                action()
                return
            except _CLIError as _error:
                match _error.etype:
                    case _CLIErrorType.DDOS:
                        ddos_retries = _catch(\
                            ddos_retries,\
                            self.__ddos_max,\
                            self.__ddos_delay,\
                            "DDOS error.")
                        if ddos_retries < 0:
                            error = _error
                        else: wait = self.__ddos_delay
                    case _CLIErrorType.NETWORK:
                        net_retries = _catch(\
                            net_retries,\
                            self.__net_max,\
                            self.__net_delay,\
                            "Network error.")
                        if net_retries < 0:
                            error = _error
                        else: wait = self.__net_delay
                    case _:
                        error = _error
            if error is None:
                yield _AppCRWaitTime(wait)
            else: break
        raise error
    
    def __update_price(self):
        price = self.__cry.get_price('BTC/USD')
        dtnow = _datetime.now(_timezone.utc)
        self.__print_line(0, f"{self.__delta}")
        self.__print_line(1, f"Current BTC price: {price}")

    #endregion

    #region methods

    def update(self, params:_AppUpdateParams):
        """
        Update routine

        :params:
            Update parameters
        :return:
            Udpate result
        :raise CLIError:
            An error occurred
        """
        try:
            # Read parameters
            self.__inputcache.extend(params.input_loop())
            self.__delta = params.delta
            # Check input
            if len(self.__inputcache) > 0:
                _input = self.__inputcache.pop(0)
                # Quit
                if _input == 27: # esc
                    self.__quit = True
                    return _AppUpdateResult()
            # Coroutines
            self.__crsys.update(self.__delta)
            # Check price
            if not self.__crsys.running():
                self.__crsys.start(self.__wrap(self.__update_price))
            # Delay
            _time.sleep(1)
            # Success!!!
            return _AppUpdateResult()
        except _CLIError as _error:
            return _AppUpdateResult(error = _error)

    #endregion