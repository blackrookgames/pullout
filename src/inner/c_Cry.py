all = ['Cry']

import ccxt as _ccxt

from typing import\
    cast as _cast

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
            # Options
            if not isinstance(self.__exchange.options, dict):
                raise _CLIError("Failed to create interface.")
            option = 'createMarketSellOrderRequiresPrice'
            self.__exchange.options[option] = 'False' # type: ignore
            option = 'createMarketBuyOrderRequiresPrice'
            self.__exchange.options[option] = 'False' # type: ignore
            # Success!!!
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion

    #region method

    def load_markets(self, reload:bool = False):
        """
        Loads the markets

        :param reload:
            Whether or not to force a reload of the markets
        :return:
            Dictionary of markets
        :raise CLIError:
            An error occurred
        """
        try:
            return self.__exchange.load_markets(reload = reload)
        except Exception as _e:
            e = _CLIError(_e)
        raise e
        
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

    def get_price(self, symbol:str):
        """
        Gets a price for a pair\n
        Example: For the pair BTC/USD, this will fetch the BTC price.
        
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :param amount:
            Amount
        :return:
            Price
        :raise CLIError:
            An error occurred
        """
        try:
            ticker = self.__exchange.fetch_ticker(symbol)
            return float(ticker['last']) # type: ignore
        except Exception as _e:
            e = _CLIError(_e)
        raise e
    
    def compute_to(self, symbol:str, amount:float):
        """
        Computes an amount using a pair\n
        Example: For the pair BTC/USD, this will compute the USD equivalent 
        of a BTC amount.
        
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :param amount:
            Input amount
        :return:
            Computed amount
        :raise CLIError:
            An error occurred
        """
        try:
            return amount * self.get_price(symbol)
        except Exception as _e:
            e = _CLIError(_e)
        raise e
    
    def compute_from(self, symbol:str, amount:float):
        """
        Computes an amount using a pair\n
        Example: For the pair BTC/USD, this will compute the BTC equivalent 
        of a USD amount.
        
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :param amount:
            Input amount
        :return:
            Computed amount
        :raise CLIError:
            An error occurred
        """
        try:
            return amount / self.get_price(symbol)
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    def order_buy(self, symbol:str, amount:float):
            """
            Creates a buy order
            
            :param symbol:
                Symbol (ex: 'BTC/USD')
            :param amount:
                Amount (ex: for 'BTC/USD' this is the USD amount)
            :return:
                order structure <https://docs.ccxt.com/?id=order-structure>
            :raise CLIError:
                An error occurred
            """
            try:
                amount = \
                    self.__exchange.amount_to_precision(\
                    symbol, amount) # type: ignore
                orderid = \
                    self.__exchange.create_market_buy_order_with_cost(\
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
                Amount (ex: for 'BTC/USD' this is the BTC amount)
            :return:
                order structure <https://docs.ccxt.com/?id=order-structure>
            :raise CLIError:
                An error occurred
            """
            try:
                amount = \
                    self.__exchange.amount_to_precision(\
                    symbol, amount) # type: ignore
                orderid = \
                    self.__exchange.create_market_sell_order_with_cost(\
                    symbol, amount) # type: ignore
                return orderid
            except Exception as _e:
                e = _CLIError(_e)
            raise e

    def order_get(self, orderid:str, symbol:None|str = None):
        """
        Retrieves an order with the specified ID
        
        :param orderid:
            Order ID
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :return:
            order structure <https://docs.ccxt.com/?id=order-structure>
        :raise CLIError:
            An error occurred
        """
        try:
            return self.__exchange.fetch_order(orderid, symbol)
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    def order_cancel(self, orderid:str, symbol:None|str = None):
        """
        Cancels an order with the specified ID
        
        :param orderid:
            Order ID
        :param symbol:
            Symbol (ex: 'BTC/USD')
        :raise CLIError:
            An error occurred
        """
        try:
            self.__exchange.cancel_order(orderid, symbol)
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    def order_cancel_all(self, symbol:None|str = None):
        """
        Cancels all open orders
        
        :param symbol:
            Symbol (ex: 'BTC/USD'); if not None, only orders for the 
            specified symbol are cancelled
        :raise CLIError:
            An error occurred
        """
        try:
            self.__exchange.cancel_all_orders(symbol)
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion