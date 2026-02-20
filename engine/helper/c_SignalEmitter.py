all = ['SignalEmitter']

from .c_SignalReceiver import\
    SignalReceiver as _SignalReceiver

class SignalEmitter():
    """
    Represents a signal
    """
    
    #region init

    def __init__(self, ):
        """
        Initializer for SignalEmitter
        """
        super().__init__()
        self.__receivers:set[_SignalReceiver] = set()

    #endregion

    #region helper methods

    def _connect(self, receiver:_SignalReceiver):
        """
        Also accessed by Signal
        """
        if not receiver in self.__receivers:
            self.__receivers.add(receiver)

    def _disconnect(self, receiver:_SignalReceiver):
        """
        Also accessed by Signal
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