all = ['AppUpdateParams']

class AppUpdateParams:
    """
    Represents parameters for running an update routine
    """

    #region init

    def __init__(self):
        """
        Initializer for AppUpdateParams
        """
        self.__input:list[int] = []

    #endregion

    #region methods

    def input_add(self, charcode:int):
        """
        Adds input to the input cache

        :param charcode:
            Character code
        """
        self.__input.append(charcode)
    
    def input_loop(self):
        """
        Loops thru all input in the input cache
        """
        for _input in self.__input:
            yield _input

    #endregion