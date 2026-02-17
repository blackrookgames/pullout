all = ['CryptoStat']

import math as _math

from collections.abc import\
    Iterable as _Iterable
from typing import\
    Callable as _Callable,\
    cast as _cast

import engine.app as _app
import engine.boacon as _boacon
import engine.coroutine as _coroutine
import engine.cry as _cry
import engine.helper as _helper

class CryptoStat:
    """
    Represents the stat of a currency
    """
    
    #region init

    def __init__(self, currency:str):
        """
        Initializer for CryptoStat
        
        :param currency:
            Currency
        """
        super().__init__()
        self.__currency = currency
        self.__price = 0.0

    #endregion

    #region properties

    @property
    def currency(self):
        """
        Currency
        """
        return self.__currency

    @property
    def price(self):
        """
        Price
        """
        return self.__price

    #endregion

    #region helper methods

    def _update(self, price:float):
        """
        Also accessed by CryptoStats
        """
        self.__price = price

    #endregion