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
from .c_AppCRWaitUpdate import\
    AppCRWaitUpdate as _AppCRWaitUpdate
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

    def __init__(self, cry:_Cry, appio:_AppIO):
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
        self.__ddos_delay = 30
        self.__ddos_max = 4
        # net
        self.__net_delay = 5
        self.__net_max = 40
        # crsys
        self.__crsys = _AppCRSys()

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
            message += ' ' * (len(message) - w)
        self.__appio.print(0, y, message)
    
    def __wrap(self, action:_Callable[[], None]):
        def _catch(_attempts:int, _max:int, _delay:float, _msg:str):
            _attempts += 1
            if _attempts >= _max:
                return -1
            self.__print_line(2,\
                f"{_msg} Retrying in {_delay} seconds. {_attempts}")
            return _attempts
        ddos_attempts = 0
        net_attempts = 0
        error = None
        wait = 0
        while True:
            try:
                action()
                return
            except _CLIError as _error:
                match _error.etype:
                    case _CLIErrorType.DDOS:
                        ddos_attempts = _catch(\
                            ddos_attempts,\
                            self.__ddos_max,\
                            self.__ddos_delay,\
                            "DDOS error.")
                        if ddos_attempts < 0:
                            error = _error
                        else: wait = self.__ddos_delay
                    case _CLIErrorType.NETWORK:
                        net_attempts = _catch(\
                            net_attempts,\
                            self.__net_max,\
                            self.__net_delay,\
                            "Network error.")
                        if net_attempts < 0:
                            error = _error
                        else: wait = self.__net_delay
                    case _:
                        error = _error
            if error is None:
                for _i in range(wait):
                    yield _AppCRWaitUpdate()
            else: break
        raise error
    
    def __update_price(self):
        price = self.__cry.get_price('BTC/USD')
        dtnow = _datetime.now(_timezone.utc)
        self.appio.print(0, 0, f"{dtnow}")
        self.appio.print(0, 1, f"Current BTC price: {price}")

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
            # Check input
            for _input in params.input_loop():
                # Quit
                if _input == 27: # esc
                    self.__quit = True
                    return _AppUpdateResult()
            # Coroutines
            self.__crsys.update()
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