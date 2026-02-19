all = ['BCSignal']

from typing import\
    Callable as _Callable,\
    Generic as _Generic,\
    TypeVarTuple as _TypeVarTuple

from .c_BCSignalEmitter import\
    BCSignalEmitter as _BCSignalEmitter

TArgs = _TypeVarTuple('TArgs')

class BCSignal(_Generic[*TArgs]):
    """
    Represents a signal
    """

    #region init

    def __init__(self, emitter:_BCSignalEmitter[*TArgs]):
        self.__emitter = emitter

    #endregion

    #region methods
    
    def connect(self, receiver:_Callable[[*TArgs], None]):
        """
        Connects a signal receiver
        """
        self.__emitter.connect(receiver)
    
    def disconnect(self, receiver:_Callable[[*TArgs], None]):
        """
        Disconnects a signal receiver
        """
        self.__emitter.disconnect(receiver)

    #endregion