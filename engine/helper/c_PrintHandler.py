all = ['PrintHandler']

from .c_PrintFunc import\
    PrintFunc as _PrintFunc

class PrintHandler:
    """
    Represents a handler for printing text, either to the screen or to a file
    """

    #region init

    def __init__(self, info:_PrintFunc, error:_PrintFunc, silent:_PrintFunc):
        """
        Initializer for PrintHandler

        :param info:
            Function for printing information
        :param error:
            Function for printing an error
        :param silent:
            Function for printing information "silently"
        """
        self.__info = info
        self.__error = error
        self.__silent = silent

    #endregion

    #region methods

    def info(self, *args):
        """
        Prints information
        """
        self.__info(args)

    def error(self, *args):
        """
        Prints an error
        """
        self.__error(args)

    def silent(self, *args):
        """
        Function for printing information "silently"
        """
        self.__silent(args)

    #endregion

