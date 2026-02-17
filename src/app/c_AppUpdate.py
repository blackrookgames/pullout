all = ['AppUpdate']

class AppUpdate:
    """
    Represents parameter for updating an application object
    """

    #region init

    def __init__(self, delta:float, key:int):
        """
        Initializer for AppUpdate

        :param delta:
            Time (in seconds) since last application update
        :param key:
            Keyboard input
        """
        self.__delta = delta
        self.__key = key

    #endregion

    #region properties

    @property
    def delta(self):
        """
        Time (in seconds) since last application update
        """
        return self.__delta

    @property
    def key(self):
        """
        Keyboard input
        """
        return self.__key

    #endregion