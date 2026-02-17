all = ['CryptoSignal']

from .c_CryptoSignalEmitter import\
    CryptoSignalEmitter as _CryptoSignalEmitter
from .c_CryptoSignalReceiver import\
    CryptoSignalReceiver as _CryptoSignalReceiver

class CryptoSignal():
    """
    Represents a signal
    """
    
    #region init

    def __init__(self, emitter:_CryptoSignalEmitter):
        """
        Initializer for CryptoSignal

        :param emitter:
            Signal emitter
        """
        super().__init__()
        self.__emitter = emitter

    #endregion

    #region methods

    def connect(self, receiver:_CryptoSignalReceiver):
        """
        Connects a receiver to the signal

        :param receiver:
            Receiver to connect
        """
        self.__emitter._connect(receiver)

    def disconnect(self, receiver:_CryptoSignalReceiver):
        """
        Disconnects a receiver from the signal

        :param receiver:
            Receiver to disconnect
        """
        self.__emitter._disconnect(receiver)

    #endregion