all = ['HistoryData']

import engine.helper as _helper

from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper
from .c_HistoryDataEntry import\
    HistoryDataEntry as _HistoryDataEntry

class HistoryData:
    """
    Represents history data
    """

    #region init

    def __init__(self,\
            keeper:_CryptoKeeper,
            crypto:str):
        """
        Initializer for HistoryData

        :params keeper:
            Crypto keeper
        :params crypto:
            Crypto name
        """
        super().__init__()
        # Crypto keeper
        self.__keeper = keeper
        # Crypto name
        self.__crypto = crypto
        # History
        self.__entries_list:list[_HistoryDataEntry] = []
        self.__entries:_helper.LockedList[_HistoryDataEntry] = _helper.LockedList[_HistoryDataEntry](self.__entries_list)

    #endregion

    #region properties

    @property
    def crypto(self):
        """
        Crypto name
        """
        return self.__crypto

    @property
    def history(self):
        """
        History entries
        """
        return self.__entries

    #endregion

    #region helper methods

    def _refresh(self):
        """
        Also accessed by History
        """
        _MAXENTRIES = 100
        # Make sure crypto can be found
        if not (self.__crypto in self.__keeper.prices): return
        # Create entry
        entry = _HistoryDataEntry(\
            self.__keeper.refreshed_when,\
            self.__keeper.prices[self.__crypto].value)
        # Add entry
        if len(self.__entries_list) >= _MAXENTRIES:
            self.__entries_list.pop(0)
        self.__entries_list.append(entry)

    #endregion