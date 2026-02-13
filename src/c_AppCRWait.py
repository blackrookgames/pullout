all = ['AppCRWait']

class AppCRWait:
    """
    Represents a yield routine for a coroutine
    """

    #region init

    def __init__(self):
        """
        Initializer for AppCRWait
        """
        self.__pause = True
        
    #endregion

    #region properties
    
    @property
    def pause(self):
        """
        Whether or not the yield is pausing the execution of the coroutine
        """
        return self.__pause

    #endregion

    #region helper methods

    def _unpause(self):
        self.__pause = False

    #endregion

    #region methods

    def update(self):
        """
        Update routine
        """
        raise NotImplementedError("update has not yet been implemented.")

    #endregion