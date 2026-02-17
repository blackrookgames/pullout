all = ['CryptoSignalEmitter']

from .c_CryptoSignalReceiver import\
    CryptoSignalReceiver as _CryptoSignalReceiver

class CryptoSignalEmitter():
    """
    Represents a signal
    """
    
    #region init

    def __init__(self, ):
        """
        Initializer for CryptoSignalEmitter
        """
        super().__init__()
        self.__receivers:set[_CryptoSignalReceiver] = set()

    #endregion

    #region helper methods

    def _connect(self, receiver:_CryptoSignalReceiver):
        """
        Also accessed by CryptoSignal
        """
        if not receiver in self.__receivers:
            self.__receivers.add(receiver)

    def _disconnect(self, receiver:_CryptoSignalReceiver):
        """
        Also accessed by CryptoSignal
        """
        if receiver in self.__receivers:
            self.__receivers.remove(receiver)

    #endregion

    #region methods

    def emit(self):
        """
        Emits the signal
        """
        for _receiver in self.__receivers:
            _receiver()

    #endregion