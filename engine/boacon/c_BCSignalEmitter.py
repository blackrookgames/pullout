all = ['BCSignalEmitter']

from typing import\
    Callable as _Callable,\
    Generic as _Generic,\
    TypeVarTuple as _TypeVarTuple

TArgs = _TypeVarTuple('TArgs')

class BCSignalEmitter(_Generic[*TArgs]):
    """
    Represents a signal emitter
    """

    #region init

    def __init__(self):
        self.__receivers:set[_Callable[[*TArgs], None]] = set()

    #endregion

    #region methods

    def emit(self, args:tuple[*TArgs]):
        """
        Emits a signal
        """
        for _receiver in self.__receivers:
            _receiver(*args)
    
    def connect(self, receiver:_Callable[[*TArgs], None]):
        """
        Connects a signal receiver
        """
        if receiver in self.__receivers:
            return
        self.__receivers.add(receiver)
    
    def disconnect(self, receiver:_Callable[[*TArgs], None]):
        """
        Disconnects a signal receiver
        """
        if not (receiver in self.__receivers):
            return
        self.__receivers.remove(receiver)

    #endregion