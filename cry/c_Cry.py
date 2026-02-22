all = ['Cry']
    
import ccxt as _ccxt
import time as _time

from collections.abc import\
    Iterable as _Iterable
from enum import\
    auto as _auto,\
    Enum as _Enum
from typing import\
    Any as _Any,\
    cast as _cast

import engine.asynccr as _asynccr
import engine.coroutine as _coroutine
import engine.helper as _helper

from .c_CryAPI import\
    CryAPI as _CryAPI
from .c_CryOpParams import\
    CryOpParams as _CryOpParams

_DEF_OPPARAMS = _CryOpParams()

class Cry:
    """
    Represents a handler for crypto-related operations
    """

    #region nested
    
    class __ErrorEval(_Enum):
        UNEX = _auto()
        DDOS = _auto()
        NET = _auto()

    #endregion

    #region init

    def __init__(self, api:_CryAPI):
        """
        Initializer for Cry
        
        :param api:
            API information
        :raise CLIError:
            An error occurred
        """
        try:
            # Create exchange instance
            self.__exchange = _ccxt.coinbase({ \
                'apiKey': api.key, \
                'secret': api.secret, \
                'enableRateLimit': True, })
            # Setup options
            if not isinstance(self.__exchange.options, dict):
                raise _helper.CLIError("Failed to create interface.")
            option = 'createMarketSellOrderRequiresPrice'
            self.__exchange.options[option] = 'False' # type: ignore
            option = 'createMarketBuyOrderRequiresPrice'
            self.__exchange.options[option] = 'False' # type: ignore
            # Success!!!
            return
        except _helper.CLIError as _e:
            e = _e
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e

    #endregion

    #region task handling

    def __evalerror(self,\
            error:_helper.CLIError,\
            opparams:_CryOpParams,\
            ddos_retries:int, net_retries:int):
        def _retrymsg(\
                _msg:str,\
                _delay:float,\
                _retry:int,\
                _maxretries:int):
            return f"{_msg} Retrying in {_delay} seconds. {_retry}/{_maxretries}"
        # DDOS protection?
        if error.etype == _helper.CLIErrorType.DDOS:
            if ddos_retries >= opparams.ddos_max:
                return self.__ErrorEval.UNEX,\
                    ddos_retries, net_retries
            ddos_retries += 1
            msg = _retrymsg(\
                "DDOS protection error",\
                opparams.ddos_delay,\
                ddos_retries,\
                opparams.ddos_max)
            if opparams.printfunc is None: print(msg)
            else: opparams.printfunc(msg)
            return self.__ErrorEval.DDOS,\
                ddos_retries, net_retries
        # Network error?
        if error.etype == _helper.CLIErrorType.NETWORK:
            if net_retries >= opparams.net_max:
                return self.__ErrorEval.UNEX,\
                    ddos_retries, net_retries
            net_retries += 1
            msg = _retrymsg(\
                "Network error",\
                opparams.net_delay,\
                net_retries,\
                opparams.net_max)
            if opparams.printfunc is None: print(msg)
            else: opparams.printfunc(msg)
            return self.__ErrorEval.NET,\
                ddos_retries, net_retries
        # Unexpected?
        return self.__ErrorEval.UNEX,\
            ddos_retries, net_retries

    def _task_sync(self,\
            opparams:None|_CryOpParams,\
            func, *args, **kwargs):
        """
        Also accessed by CryBalance
        """
        if opparams is None: opparams = _DEF_OPPARAMS
        _ddos_retries = 0
        _net_retries = 0
        while True:
            try:
                return func(*args, **kwargs)
            except _helper.CLIError as _e:
                _eval, _ddos_retries, _net_retries =\
                    self.__evalerror(_e, opparams,\
                        _ddos_retries, _net_retries)
                if _eval == self.__ErrorEval.DDOS:
                    _time.sleep(opparams.ddos_delay)
                    continue
                if _eval == self.__ErrorEval.NET:
                    _time.sleep(opparams.net_delay)
                    continue
                e = _e
                break
        raise e

    def _task_async(self,\
            opparams:None|_CryOpParams,\
            result:None|_helper.Ptr,\
            func, *args, **kwargs):
        """
        Also accessed by CryBalance
        """
        if opparams is None: opparams = _DEF_OPPARAMS
        _ddos_retries = 0
        _net_retries = 0
        while True:
            # Queue task
            task = _asynccr.ACRTask(func, *args, **kwargs)
            _asynccr.queuetask(task)
            yield _asynccr.ACRTaskWait(task)
            # Check if successful
            if task.error is None:
                if result is not None:
                    result.value = task.result
                break
            # Evaluate error
            _eval, _ddos_retries, _net_retries =\
                self.__evalerror(task.error, opparams,\
                    _ddos_retries, _net_retries)
            if _eval == self.__ErrorEval.DDOS:
                yield _coroutine.CRWaitTime(opparams.ddos_delay)
                continue
            if _eval == self.__ErrorEval.NET:
                yield _coroutine.CRWaitTime(opparams.net_delay)
                continue
            raise task.error
    
    #endregion

    #region helper methods

    def __amount_to_precision(self,\
            symbol:str,\
            amount:float):
        try:
            return float(self.__exchange.amount_to_precision(symbol, amount)) # type: ignore
        except _ccxt.InvalidOrder as _e:
            e = _helper.CLIError(_e, etype = _helper.CLIErrorType.PRECISION)
        raise e

    def __load_markets(self,\
            reload:bool):
        try:
            return self.__exchange.load_markets(reload = reload)
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e
    
    def __get_symbols(self):
        try:
            return self.__exchange.get_symbols_for_market_type()
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e
    
    def __get_price(self,\
            symbol:str):
        try:
            ticker = self.__exchange.fetch_ticker(symbol)
            return float(ticker['last']) # type: ignore
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e

    def __fetch_balance(self):
        try:
            return self.__exchange.fetch_balance()
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e
    
    def __fetch_ticker(self,\
            symbol:str):
        try:
            return self.__exchange.fetch_ticker(symbol)
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e
        
    def __order_sell(self,\
            symbol:str,\
            amount:float)\
            -> dict:
        # Amount to precision
        _amount = self.__amount_to_precision(symbol, amount)
        # Sell
        try:
            return self.__exchange.create_market_sell_order(symbol, _amount)
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e
        
    def __order_buy(self,\
            symbol:str,\
            amount:float):
        # Amount to precision
        _amount = self.__amount_to_precision(symbol, amount)
        # Buy
        try:
            return _cast(dict, self.__exchange.create_market_buy_order_with_cost(symbol, _amount))
        except Exception as _e:
            e = _helper.CLIError(_e)
        raise e

    #endregion

    #region methods

    #region load_markets

    def load_markets(self,\
            reload:bool = False,\
            opparams:None|_CryOpParams = None):
        """
        Loads the markets

        :param reload:
            Whether or not to force a reload of the markets
        :param opparams:
            Operation parameters
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__load_markets, reload)
    
    def load_markets_cr(self,\
            reload:bool = False,\
            opparams:None|_CryOpParams = None):
        """
        Creates an async task to load the markets

        :param reload:
            Whether or not to force a reload of the markets
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, None,\
            self.__load_markets, reload)
        for _item in gen: yield _item
    
    #endregion

    #region get_symbols

    def get_symbols(self,\
            opparams:None|_CryOpParams = None):
        """
        Retrieves the symbols

        :param opparams:
            Operation parameters
        :return:
            Dictionary of the retrieved symbols
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__get_symbols)
    
    def get_symbols_cr(self,\
            result:_helper.Ptr[dict[str, str]],\
            opparams:None|_CryOpParams = None):
        """
        Creates an async task to retrieve the symbols

        :param result:
            Dictionary of the retrieved symbols
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, result,\
            self.__get_symbols)
        for _item in gen: yield _item
    
    #endregion

    #region get_price
    
    def get_price(self,\
            symbol:str,\
            opparams:None|_CryOpParams = None):
        """
        Gets the price for a pair\n
        Example: For the pair BTC/USD, this will fetch the BTC price.

        :param symbol:
            Symbol (ex: BTC/USD)
        :param opparams:
            Operation parameters
        :return:
            Price for the pair
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__get_price, symbol)
    
    def get_price_cr(self,\
            symbol:str,\
            result:_helper.Ptr[float],\
            opparams:None|_CryOpParams = None):
        """
        Creates an async task to get the price for a pair\n
        Example: For the pair BTC/USD, this will fetch the BTC price.

        :param symbol:
            Symbol (ex: BTC/USD)
        :param result:
            Price for the pair
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, result,\
            self.__get_price, symbol)
        for _item in gen: yield _item

    #endregion

    #region fetch_balance
    
    def fetch_balance(self,\
            opparams:None|_CryOpParams = None):
        """
        Fetches balance information

        :param opparams:
            Operation parameters
        :return:
            Balance information
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__fetch_balance)
    
    def fetch_balance_cr(self,\
            result:_helper.Ptr[dict],\
            opparams:None|_CryOpParams = None):
        """
        Fetches balance information

        :param result:
            Balance information
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, result,\
            self.__fetch_balance)
        for _item in gen: yield _item

    #endregion

    #region fetch_ticker
    
    def fetch_ticker(self,\
            symbol:str,\
            opparams:None|_CryOpParams = None):
        """
        Fetches a price ticker

        :param symbol:
            Symbol (ex: BTC/USD)
        :param opparams:
            Operation parameters
        :return:
            Price ticker
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__fetch_ticker, symbol)
    
    def fetch_ticker_cr(self,\
            symbol:str,\
            result:_helper.Ptr[dict],\
            opparams:None|_CryOpParams = None):
        """
        Fetches a price ticker

        :param symbol:
            Symbol (ex: BTC/USD)
        :param result:
            Price ticker
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, result,\
            self.__fetch_ticker, symbol)
        for _item in gen: yield _item

    #endregion

    #region order_sell
    
    def order_sell(self,\
            symbol:str,\
            amount:float,\
            opparams:None|_CryOpParams = None):
        """
        Creates an order to sell crypto

        :param symbol:
            Symbol (ex: BTC/USD)
        :param amount:
            Amount to sell
        :param opparams:
            Operation parameters
        :return:
            Order information
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__order_sell, symbol, amount)
    
    def order_sell_cr(self,\
            symbol:str,\
            amount:float,\
            result:_helper.Ptr[dict],\
            opparams:None|_CryOpParams = None):
        """
        Creates an order to sell crypto

        :param symbol:
            Symbol (ex: BTC/USD)
        :param amount:
            Amount to sell
        :param result:
            Order information
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, result,\
            self.__order_sell, symbol, amount)
        for _item in gen: yield _item

    #endregion

    #region order_buy
    
    def order_buy(self,\
            symbol:str,\
            amount:float,\
            opparams:None|_CryOpParams = None):
        """
        Creates an order to buy crypto

        :param symbol:
            Symbol (ex: BTC/USD)
        :param amount:
            Amount to buy
        :param opparams:
            Operation parameters
        :return:
            Order information
        :raise CLIError:
            An error occurred
        """
        return self._task_sync(opparams,\
            self.__order_buy, symbol, amount)
    
    def order_buy_cr(self,\
            symbol:str,\
            amount:float,\
            result:_helper.Ptr[dict],\
            opparams:None|_CryOpParams = None):
        """
        Creates an order to buy crypto

        :param symbol:
            Symbol (ex: BTC/USD)
        :param amount:
            Amount to buy
        :param result:
            Order information
        :param opparams:
            Operation parameters
        :raise BadOpError:
            Async task handler is not currently running
        :raise CLIError:
            An error occurred
        """
        gen = self._task_async(opparams, result,\
            self.__order_buy, symbol, amount)
        for _item in gen: yield _item

    #endregion

    #endregion