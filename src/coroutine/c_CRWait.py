all = ['CRWait']

class CRWait:
    """
    Represents a wait period
    """

    #region init

    def __init__(self):
        """
        Initializer for CRWait
        """
        self.__waiting = True
        
    #endregion

    #region properties

    @property
    def waiting(self):
        """
        Whether or not wait period is active
        """
        return self.__waiting

    #endregion

    #region helper methods

    def _stopwait(self):
        self.__waiting = False

    def _update(self, delta:float):
        """
        Assume
        - delta >= 0.0
        \n
        Also accessed by CR
        """
        raise NotImplementedError("_update has not yet been implemented.")

    #endregion