all = ['BuSe']

from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.coroutine as _coroutine
import engine.helper as _helper

from .c_BuSeData import\
    BuSeData as _BuSeData
from .c_BuSeDataRefreshArgs import\
    BuSeDataRefreshArgs as _BuSeDataRefreshArgs
from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper
from .c_StatusTable import\
    StatusTable as _StatusTable

_SPACE = _boacon.BCChar(0x20)

class BuSe(_app.AppPaneObject):
    """
    Represents a handler for buying and selling
    """

    #region nested

    class __QueueItem:
        def __init__(self, func:_Callable, *args, **pargs):
            self.__func = func
            self.__args = args
            self.__pargs = pargs
        @property
        def func(self): return self.__func
        @property
        def args(self): return self.__args
        @property
        def pargs(self): return self.__pargs

    #endregion

    #region init

    def __init__(self,\
            crypto:_cry.Cry,\
            opparams:_cry.CryOpParams,\
            keeper:_CryptoKeeper,\
            table:_StatusTable,\
            trlen:int,\
            bsmax:float,\
            bsmin:float,\
            dtformat:_helper.DTFormat,\
            printer:_helper.PrintHandler):
        """
        Initializer for BuSe

        :params crypto:
            Crypto operation handler
        :params opparams:
            Parameters for Crypto-related operations
        :params keeper:
            Crypto keeper
        :params table:
            Crypto status table
        :param trlen:
            Length of time (in microseconds) to look back before making a decision to buy or sell
        :param bsmax:
            Maximum "fractional" difference before buying crypto
        :param bsmin:
            Minimum "fractional" difference before selling crypto
        :param dtformat:
            Date/time format
        :param printer:
            Print handler
        """
        super().__init__()
        self.focusable = True
        # Crypto operation handler
        self.__crypto = crypto
        self.__opparams = opparams
        # Crypto keeper
        self.__keeper = keeper
        self.__keeper.refreshed.connect(self.__r_keeper_refreshed)
        # Status table
        self.__table = table
        self.__table.selection_changed.connect(self.__r_table_selection_changed)
        # Train interval
        self.__trlen = max(1, trlen)
        # Refresh args
        self.__refreshargs = _BuSeDataRefreshArgs(\
            bsmax, bsmax if (bsmin > bsmax) else bsmin,\
            self.__buy, self.__sell)
        # Date/time format
        self.__dtformat = dtformat
        # Print handler
        self.__printer = printer
        # Crypto entries
        self.__entries:dict[str, _BuSeData] = {}
        # Active crypto (one being displayed)
        self.__active:None|str = None
        # Queue
        self.__queue:list[BuSe.__QueueItem] = []

    #endregion

    #region receivers

    def __r_keeper_refreshed(self):
        # Add entries (if needed)
        if len(self.__entries) == 0:
            # Gather information about cryptos
            nobalance = 0
            for _c_balance in self.__keeper.balances:
                # Does it have a balance?
                if _c_balance.value == 0.0: nobalance += 1
            # Compute balance ration
            balration = 0.0 if (nobalance == 0) else (1.0 / nobalance)
            # Create entries
            for _c_price in self.__keeper.prices:
                # Retrieve balance
                _c_balance = self.__keeper.balances[_c_price.name]
                _balration = 0.0 if (_c_balance.value != 0.0) else balration
                # Create/add entry
                self.__entries[_c_price.name] = _BuSeData(\
                    self.__keeper, _c_price.name, self.__trlen,\
                    _c_balance.value, _balration)
        # Update entries
        for _c_price in self.__keeper.prices:
            self.__entries[_c_price.name]._refresh(self.__refreshargs)
        # Execute queue
        _oldqueue = self.__queue
        self.__queue = []
        _coroutine.create(self.__c_runqueue(_oldqueue))
        # If no crypto is active, find one to be active
        if self.__active is None:
            if len(self.__keeper.prices) > 0:
                self.__active = self.__keeper.prices[0].name
        # Update character buffer
        self._update_chrs()

    def __r_table_selection_changed(self):
        # Only change active is a crypto is being selected
        if self.__table.selcrypto is None: return
        # Change active crypto
        self.__active = self.__table.selcrypto
        # Update character buffer
        self._update_chrs()

    #endregion

    #region coroutines

    def __c_runqueue(self, queue:list[__QueueItem]):
        for _item in queue:
            _cr = _item.func(*_item.args, **_item.pargs)
            for _yield in _cr: yield _yield

    def __c_balance(self, crypto:str, result:_helper.Ptr[float]):
        # Fetch balance
        _ptr = _helper.Ptr[dict]()
        _task = self.__crypto.fetch_balance_cr(_ptr,\
            opparams = self.__opparams)
        for _yield in _task: yield _yield
        # Get free
        new_balance = _cast(dict, _ptr.value)["free"]
        # Find balance of specific crypto
        result.value = new_balance[crypto] if (crypto in new_balance) else 0.0

    def __c_buy(self, crypto:str):
        if not (crypto in self.__entries): return
        data = self.__entries[crypto]
        symbol = f"{crypto}/{self.__keeper.noncrypto}"
        self.__printer.info(f"Buying {crypto}") # Do NOT make silent
        # Get non-crypto balance
        self.__printer.silent(f"  Getting non-crypto balance")
        cr_result = _helper.Ptr[float]()
        cr = self.__c_balance(self.__keeper.noncrypto, cr_result)
        for _yield in cr: yield _yield
        if cr_result.value is None: return
        ncbalance = cr_result.value
        self.__printer.silent(f"    Balance: {ncbalance}")
        if ncbalance <= 0.000001:
            self.__printer.silent(f"    CAN'T BUY")
            return
        # Buy
        buyamount = ncbalance * data.balration
        self.__printer.silent(f"  Buying {buyamount} {self.__keeper.noncrypto} worth of {crypto}")
        cr_result = _helper.Ptr[dict]()
        cr = self.__crypto.order_buy_cr(symbol, buyamount, cr_result,\
            opparams = self.__opparams)
        for _yield in cr: yield _yield
        # Refresh crypto balance
        self.__printer.silent(f"  Refreshing crypto balance")
        cr_result = _helper.Ptr[float]()
        cr = self.__c_balance(crypto, cr_result)
        for _yield in cr: yield _yield
        if cr_result.value is None: return
        data._set_balance(cr_result.value)
        self.__printer.silent(f"    Balance: {data.balance}")
        # Fix rations
        self.__printer.silent(f"  Fixing rations")
        def _fixrations():
            nonlocal self
            # Determine ration total
            _total = 0.0
            for _entry in self.__entries.values():
                if _entry.balance > 0.0: continue
                _total += _entry.balration
            if _total == 0.0: return
            self.__printer.silent(f"    Dirty Total: {_total}")
            # Scale so ration total equals 1.0
            _scale = 1.0 / _total
            self.__printer.silent(f"    Scale {_scale}")
            for _entry in self.__entries.values():
                if _entry.balance > 0.0: continue
                _entry._set_balration(_entry.balration * _scale)
                self.__printer.silent(f"    Fixed {_entry.crypto}: {_entry.balration}")
        _fixrations()

    def __c_sell(self, crypto:str):
        if not (crypto in self.__entries): return
        data = self.__entries[crypto]
        symbol = f"{crypto}/{self.__keeper.noncrypto}"
        self.__printer.info(f"Selling {crypto}") # Do NOT make silent
        # Get non-crypto balance before sell
        self.__printer.silent(f"  Getting non-crypto balance")
        cr_result = _helper.Ptr[float]()
        cr = self.__c_balance(self.__keeper.noncrypto, cr_result)
        for _yield in cr: yield _yield
        if cr_result.value is None: return
        ncbalance_before = cr_result.value
        self.__printer.silent(f"    Balance: {ncbalance_before}")
        # Get crypto balance before sell
        self.__printer.silent(f"  Getting crypto balance")
        cr_result = _helper.Ptr[float]()
        cr = self.__c_balance(crypto, cr_result)
        for _yield in cr: yield _yield
        if cr_result.value is None: return
        balance = cr_result.value
        self.__printer.silent(f"    Balance: {balance}")
        if balance <= 0.000001:
            self.__printer.silent(f"    CAN'T SELL")
            return
        # Sell crypto
        self.__printer.silent(f"  Selling {balance} {crypto}")
        cr_result = _helper.Ptr[dict]()
        cr = self.__crypto.order_sell_cr(symbol, balance, cr_result,\
            opparams = self.__opparams)
        for _yield in cr: yield _yield
        # Refresh crypto balance
        self.__printer.silent(f"  Refreshing crypto balance")
        cr_result = _helper.Ptr[float]()
        cr = self.__c_balance(crypto, cr_result)
        for _yield in cr: yield _yield
        if cr_result.value is None: return
        data._set_balance(cr_result.value)
        self.__printer.silent(f"    Balance: {data.balance}")
        # Get non-crypto balance after sell
        self.__printer.silent(f"  Getting non-crypto balance")
        cr_result = _helper.Ptr[float]()
        cr = self.__c_balance(self.__keeper.noncrypto, cr_result)
        for _yield in cr: yield _yield
        if cr_result.value is None: return
        ncbalance_after = cr_result.value
        self.__printer.silent(f"    Balance: {ncbalance_after}")
        # Fix rations
        self.__printer.silent(f"  Fixing rations")
        if data.balance == 0.0 : # Make sure balance has been cleared and 
            # Determine ration amount for crypto
            data._set_balration((ncbalance_after - ncbalance_before) / ncbalance_after)
            self.__printer.silent(f"    Balration: {data.balration}")
            # Scale ration of others
            _scale = 1.0 - data.balration
            self.__printer.silent(f"    Scale {_scale}")
            for _entry in self.__entries.values():
                if _entry.crypto == crypto: continue
                if _entry.balance > 0.0: continue
                _entry._set_balration(_entry.balration * _scale)
                self.__printer.silent(f"    Fixed {_entry.crypto}: {_entry.balration}")

    #endregion

    #region helper methods

    def __buy(self, crypto:str):
        self.__queue.append(self.__QueueItem(self.__c_buy, crypto))

    def __sell(self, crypto:str):
        self.__queue.append(self.__QueueItem(self.__c_sell, crypto))

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        if len(self._chars) > 0 and self.__active is not None:
            active = self.__entries[self.__active]
            oindex = 0
            def _print(_text:str):
                nonlocal self, oindex
                _rest = min(len(self._chars) - oindex, self._chars.width)
                for _i in range(min(len(_text), _rest)):
                    self._chars[oindex] = _boacon.BCChar(ord(_text[_i]))
                    oindex += 1
                    _rest -= 1
                while _rest > 0:
                    self._chars[oindex] = _SPACE
                    oindex += 1
                    _rest -= 1
            def _print_space():
                nonlocal self, oindex
                for _i in range(min(len(self._chars) - oindex, self._chars.width)):
                    self._chars[oindex] = _SPACE
                    oindex += 1
            def _percent(_value:float):
                _DECIMALS = 4
                # Check if zero
                if _value == 0.0: return "0.0%"
                # Convert to percent
                _value *= 100
                _round = round(_value, _DECIMALS)
                if _round != 0.0: return f"{_round}%"
                # Use scientific notation
                _power = 0
                while abs(_round) < 1.0:
                    _value *= 10
                    _round = round(_value, _DECIMALS)
                    _power -= 1
                return f"{_round}(E{_power})%"
            # Name
            _print(f" {self.__active}")
            _print_space()
            # Difference
            _print(" -" if (active.diff_price is None) else f" {active.diff_price}")
            _print(" -" if (active.diff_fract is None) else f" {_percent(active.diff_fract)}")
            _print_space()
            # Balance
            if active.balance == 0.0:
                _print(" Non-crypto ration:")
                _print(f"   {_percent(active.balration)}")
            else:
                _print(" Balance:")
                _print(f"   {active.balance}")
            _print_space()
            # Current
            _print(" Current:")
            _print(f"   {self.__dtformat.create(active.curr_date)}")
            _print(f"   {active.curr_price}")
            # Previous
            _print(" Previous:")
            _print("   -" if (active.prev_date is None) else f"   {self.__dtformat.create(active.prev_date)}")
            _print("   -" if (active.prev_price is None) else f"   {active.prev_price}")
            # Fill rest
            if oindex < len(self._chars):
                self._chars[oindex] = _SPACE
                oindex += 1
        else: self._chars.clear

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)

    def _activated(self):
        super()._activated()

    def _deactivated(self):
        super()._deactivated()

    #endregion