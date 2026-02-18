all = ['ACRTask']

from typing import\
    Any as _Any

from ..helper.c_CLIError import\
    CLIError as _CLIError
from .c_ACRTaskStatus import\
    ACRTaskStatus as _ACRTaskStatus

class ACRTask:
    """
    Represents an asyncronous task
    """

    #region init

    def __init__(self, func, *args, **kwargs):
        """
        Initializer for ACRTask
        """
        self.__status = _ACRTaskStatus.INIT
        self.__error:None|_CLIError = None
        self.__result:_Any = None
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    #endregion

    #region properties

    @property
    def status(self):
        """
        Task status
        """
        return self.__status

    @property
    def error(self):
        """
        Error that occurred during execution. 
        If task completed successfully, this value is None.
        """
        return self.__error
    
    @property
    def result(self):
        """
        Task result. This is the return value of the input function.
        """
        return self.__result

    #endregion

    #region helper methods

    def _run(self):
        """
        Also accessed by ./__init__.py

        :raise CLIError:
            An error occurred
        """
        if self.__status != _ACRTaskStatus.INIT: return
        self.__status = _ACRTaskStatus.RUN
        try:
            self.__result = self.__func(\
                *self.__args, **self.__kwargs)
            self.__status = _ACRTaskStatus.SUCCESS
        except _CLIError as _e:
            self.__status = _ACRTaskStatus.ERROR
            self.__error = _e

    #endregion

    #region methods

    def stillrunning(self):
        """
        Checks if the task is still executing (or waiting to be executed)
        
        :return:
            False if status == SUCCESS or status == ERROR; otherwise True
        """
        if self.__status == _ACRTaskStatus.SUCCESS: return False
        if self.__status == _ACRTaskStatus.ERROR: return False
        return True

    #endregion