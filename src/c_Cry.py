all = ['Cry']

import ccxt as _ccxt

from .c_APIInfo import\
    APIInfo as _APIInfo
from .c_CLIError import\
    CLIError as _CLIError

class Cry:
    """
    Represents an interface for crypto
    """

    #region init

    def __init__(self, api:_APIInfo):
        """
        Initializer for Cry

        :param api:
            API info
        :raise CLIError:
            An error occurred
        """
        try:
            self.__exchange = _ccxt.coinbase({ \
                'apiKey': api.key, \
                'secret': api.secret, \
                'enableRateLimit': True, })
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion

    #region method

    def get_balance(self, currency:str):
        """
        Gets the total for balance for the specified currency

        :param currency:
            currency key
        :raise CLIError:
            An error occurred
        """
        try:
            balance = self.__exchange.fetch_balance()
            total = balance.get(currency, {}).get('total', 0)
            return float(total) # type: ignore
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    def order_buy(self, symbol:str, amount:float):
        """
        Creates a buy order
        
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :param amount:
            Amount
        :return:
            Order ID
        :raise CLIError:
            An error occurred
        """
        try:
            amount = self.__exchange.amount_to_precision(\
                symbol, amount) # type: ignore
            orderid = self.__exchange.create_market_buy_order(\
                symbol, amount) # type: ignore
            return orderid
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    def order_sell(self, symbol:str, amount:float):
        """
        Creates a sell order
        
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :param amount:
            Amount
        :return:
            Order ID
        :raise CLIError:
            An error occurred
        """
        try:
            amount = self.__exchange.amount_to_precision(\
                symbol, amount) # type: ignore
            orderid = self.__exchange.create_market_sell_order(\
                symbol, amount) # type: ignore
            return orderid
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    def order_status(self, orderid, symbol:str):
        """
        Retrieves the status of an order
        
        :param orderid:
            Order ID
        :param symbol:
            Symbol (ex: 'BTC/USD')
        """
        self.__exchange.fetch_order(orderid, symbol)

    #endregion