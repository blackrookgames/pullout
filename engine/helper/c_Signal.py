all = ['Signal']

from .c_SignalEmitter import\
    SignalEmitter as _SignalEmitter
from .c_SignalReceiver import\
    SignalReceiver as _SignalReceiver

class Signal():
    """
    Represents a signal
    """
    
    #region init

    def __init__(self, emitter:_SignalEmitter):
        """
        Initializer for Signal

        :param emitter:
            Signal emitter
        """
        super().__init__()
        self.__emitter = emitter

    #endregion

    #region methods

    def connect(self, receiver:_SignalReceiver):
        """
        Connects a receiver to the signal

        :param receiver:
            Receiver to connect
        """
        self.__emitter._connect(receiver)

    def disconnect(self, receiver:_SignalReceiver):
        """
        Disconnects a receiver from the signal

        :param receiver:
            Receiver to disconnect
        """
        self.__emitter._disconnect(receiver)

    #endregion