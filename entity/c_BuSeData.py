all = ['BuSeData']

from io import StringIO # TODO: Remove

from datetime import\
    datetime as _datetime

import engine.helper as _helper

from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper
from .c_BuSeDataEntry import\
    BuSeDataEntry as _BuSeDataEntry

class BuSeData:
    """
    Represents buy/sell data
    """

    #region init

    def __init__(self,\
            keeper:_CryptoKeeper,\
            crypto:str,\
            trlen:int,\
            balance:float,\
            balration:float):
        """
        Initializer for BuSeData

        :param keeper:
            Crypto keeper
        :param crypto:
            Crypto name
        :param trlen:
            Length of time (in microseconds) to look back before making a decision to buy or sell
        :param balance:
            Crypto balance
        :param balration:
            What portion of the non-crypto balance gets to be used to buy crypto
        """
        super().__init__()
        # Crypto keeper
        self.__keeper = keeper
        # Crypto info
        self.__crypto = crypto
        self.__curr_date = _datetime(1990, 1, 1)
        self.__curr_price = 0.0
        self.__prev_date:None|_datetime = None
        self.__prev_price:None|float = None
        self.__diff_price:None|float = None
        self.__diff_fract:None|float = None
        self.__balance = balance
        self.__balration = balration
        # Train interval
        self.__trlen = max(1, trlen)
        # History
        self.__entries_list:list[_BuSeDataEntry] = []
        self.__entries:_helper.LockedList[_BuSeDataEntry] = _helper.LockedList[_BuSeDataEntry](self.__entries_list)
        self.__entries_delta:list[int] = []
        self.__entries_tdelta = 0
        # Update info
        self.__last = -1

    #endregion

    #region properties

    @property
    def crypto(self):
        """
        Crypto name
        """
        return self.__crypto
    
    @property
    def curr_date(self):
        """
        Date/time of most recent update
        """
        return self.__curr_date
    
    @property
    def curr_price(self):
        """
        Price from most recent update
        """
        return self.__curr_price
    
    @property
    def prev_date(self):
        """
        Date/time trlen microseconds before curr_date
        """
        return self.__prev_date
    
    @property
    def prev_price(self):
        """
        Rough price at prev_date
        """
        return self.__prev_price
    
    @property
    def diff_price(self):
        """
        Rough price difference
        """
        return self.__diff_price
    
    @property
    def diff_fract(self):
        """
        Rough "fractional" difference
        """
        return self.__diff_fract
    
    @property
    def balance(self):
        """
        Crypto balance
        """
        return self.__balance
    
    @property
    def balration(self):
        """
        What portion of the non-crypto balance gets to be used to buy crypto
        """
        return self.__balration
    
    @property
    def trlen(self):
        """
        Length of time (in microseconds) to look back before making a decision to buy or sell
        """
        return self.__trlen

    @property
    def history(self):
        """
        BuSe entries (newest to oldest)
        """
        return self.__entries

    #endregion

    #region helper methods

    def _refresh(self, bsmax:float, bsmin:float):
        """
        Assume
        - bsmax >= bsmin
        \n
        Also accessed by BuSe
        """
        # Make sure crypto can be found
        if not (self.__crypto in self.__keeper.prices): return
        # Get current crypto info
        self.__curr_date = self.__keeper.refreshed_when
        self.__curr_price = self.__keeper.prices[self.__crypto].value
        self.__balance = self.__keeper.balances[self.__crypto].value
        # Determine delta
        _curr_date = _helper.DTUtil.to_micro2000(self.__curr_date)
        delta = 0 if (self.__last < 0) else (_curr_date - self.__last)
        self.__last = _curr_date
        # Create history entry
        _hentry = _BuSeDataEntry(self.__curr_price)
        # Add entry
        self.__entries_list.insert(0, _hentry)
        # Add delta
        if len(self.__entries) > 1:
            self.__entries_delta.append(delta)
            self.__entries_tdelta += delta
        # Check if oldest entry can be removed
        if len(self.__entries_delta) > 0:
            _olddelta = self.__entries_delta[len(self.__entries_delta) - 1]
            _tdeltawo = self.__entries_tdelta - _olddelta
            if _tdeltawo > self.__trlen:
                self.__entries_list.pop()
                self.__entries_delta.pop()
                self.__entries_tdelta = _tdeltawo
        # Get previous price (do this after updating history entries)
        self.__prev_price = self.__getprice(self.__trlen)
        if self.__prev_price is not None:
            self.__prev_date = _helper.DTUtil.from_micro2000(_curr_date - self.__trlen)
        # Compute price difference
        if self.__prev_price is not None:
            self.__diff_price = self.__curr_price - self.__prev_price
            self.__diff_fract = self.__diff_price / self.__prev_price
    
    def _set_balance(self, value:float):
        """
        Also accessed by BuSe
        """
        self.__balance = value
    
    def _set_balration(self, value:float):
        """
        Also accessed by BuSe
        """
        self.__balration = value

    def __getprice(self, t:int):
        # Make sure there's sufficient data
        if self.__entries_tdelta <= t:
            return None
        # Which two entries is this point between?
        _i = 0
        _delta = self.__entries_delta[_i]
        while t >= _delta:
            t -= _delta
            _i += 1
            _delta = self.__entries_delta[_i]
        entry0 = self.__entries_list[_i]
        entry1 = self.__entries_list[_i + 1]
        # Interpolate
        return entry1.price + (t / _delta) * (entry0.price - entry1.price)
    
    #endregion