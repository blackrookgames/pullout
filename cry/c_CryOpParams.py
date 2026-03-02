all = ['CryOpParams']
    
import ccxt as _ccxt

import engine.helper as _helper

class CryOpParams:
    """
    Represents parameters for a crypto-related operation
    """

    #region init

    def __init__(self):
        """
        Initializer for CryOpParams
        """
        self.__ddos_delay = 0.0
        self.__ddos_max = 0
        self.__net_delay = 0.0
        self.__net_max = 0
        self.__printer:None|_helper.PrintHandler = None
    
    def copy(self):
        """
        Creates a copy of CryOpParams
        """
        new = CryOpParams()
        new.__ddos_delay = self.__ddos_delay
        new.__ddos_max = self.__ddos_max
        new.__net_delay = self.__net_delay
        new.__net_max = self.__net_max
        new.__printer = self.__printer
        return new

    #endregion

    #region properties

    @property
    def ddos_delay(self):
        """
        Delay (in seconds) before retrying after 
        a DDOS protection error
        """
        return self.__ddos_delay
    @ddos_delay.setter
    def ddos_delay(self, value:float):
        self.__ddos_delay = value

    @property
    def ddos_max(self):
        """
        Maximum number of retries after 
        a DDOS protection error
        """
        return self.__ddos_max
    @ddos_max.setter
    def ddos_max(self, value:int):
        self.__ddos_max = value

    @property
    def net_delay(self):
        """
        Delay (in seconds) before retrying after 
        a network error
        """
        return self.__net_delay
    @net_delay.setter
    def net_delay(self, value:float):
        self.__net_delay = value

    @property
    def net_max(self):
        """
        Maximum number of retries after 
        a network error
        """
        return self.__net_max
    @net_max.setter
    def net_max(self, value:int):
        self.__net_max = value

    @property
    def printer(self):
        """
        Print handler
        """
        return self.__printer
    @printer.setter
    def printer(self, value:None|_helper.PrintHandler):
        self.__printer = value

    #endregion