all = ['c_MiscOps']

import engine.app as _app
import engine.coroutine as _coroutine
import engine.helper as _helper

class MiscOps(_app.AppObject):
    """
    Represents a handler for miscellaneous operations 
    """

    #region init

    def __init__(self):
        super().__init__()
        self.__key = -1
        # Prompting
        self.__prompting = False
        self.__prompt_start_e = _helper.SignalEmitter()
        self.__prompt_start = _helper.Signal(self.__prompt_start_e)
        self.__prompt_finish_e = _helper.SignalEmitter()
        self.__prompt_finish = _helper.Signal(self.__prompt_finish_e)

    #endregion

    #region properties/signals

    @property
    def prompting(self):
        """
        Whether or not the user is currently being prompted
        """
        return self.__prompting
    
    @property
    def prompt_start(self):
        """
        Emitted when starting a prompt for the user 
        """
        return self.__prompt_start
    
    @property
    def prompt_finish(self):
        """
        Emitted when finishing a prompt for the user 
        """
        return self.__prompt_finish

    #endregion

    #region coroutines

    def cr_quit(self):
        # Start prompting
        self.__prompting = True
        self.__prompt_start_e.emit()
        # Prompt
        _app.console().print("Quit program? YN")
        yield _coroutine.CRWaitWhile(lambda: self.__key != -1)
        while True:
            yield _coroutine.CRWaitWhile(lambda: self.__key == -1)
            # Yes?
            if self.__key == 0x79 or self.__key == 0x0A:
                _app.console().print("Quitting")
                _app.quit()
                break
            # No?
            elif self.__key == 0x6E or self.__key == 0x1B:
                _app.console().print("Not quitting")
                break
        # Stop prompting
        self.__prompting = False
        self.__prompt_finish_e.emit()

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        self.__key = params.key
        if not self.__prompting:
            # Quit?
            if self.__key == 0x1B:
                _coroutine.create(self.cr_quit())

    #endregion