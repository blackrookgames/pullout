import curses as _curses

from .c_BadOpError import\
    BadOpError as _BadOpError

class AppIO:
    """
    Represents a handler for outputting text
    """

    #region init/create/destroy

    def __init__(self):
        """
        Do NOT initialize directory. Call AppIO.create() instead.
        """
        self.__scr = _curses.initscr()
        # Setup
        _curses.noecho()
        _curses.cbreak()
        self.__setcursor(0)
        self.__scr.keypad(True)
        self.__scr.nodelay(True)
        self.__scr.clear()
        # Mark as not destroyed
        self.__destroyed = False
    
    @classmethod
    def create(cls):
        """
        Creates an output handler

        :return:
            Created output handler
        """
        return cls()

    def destroy(self):
        """
        Destroys the output handler
        """
        if self.__destroyed: return
        # Mark as destroyed
        self.__destroyed = True
        # Teardown
        self.__scr.nodelay(False)
        self.__scr.keypad(False)
        self.__setcursor(1)
        _curses.nocbreak()
        _curses.echo()
        _curses.endwin()

    #endregion

    #region helper methods

    @staticmethod
    def __setcursor(value):
        try: _curses.curs_set(value)
        except _curses.error: pass

    def __raiseif_destroyed(self):
        if self.__destroyed:
            raise _BadOpError("Object has already been destroyed.")

    #endregion

    #region methods

    def clear(self):
        """
        Clears the screen

        :raise BadOpError:
            Object has already been destroyed
        """
        self.__raiseif_destroyed()
        return self.__scr.clear()

    def refresh(self):
        """
        Refreshes the screen

        :raise BadOpError:
            Object has already been destroyed
        """
        self.__raiseif_destroyed()
        self.__scr.refresh()

    def timeout(self, delay:int):
        """
        Times out for a specified number of milliseconds
        
        :param delay: Number of milliseconds to timeout
        :raise BadOpError:
            Object has already been destroyed
        """
        self.__raiseif_destroyed()
        self.__scr.timeout(delay)

    def print(self, x:int, y:int, message:str):
        """
        Prints a message to the screen
        
        :param x: X-offset
        :param y: Y-offset
        :param message: Message to print
        :raise BadOpError:
            Object has already been destroyed
        """
        self.__raiseif_destroyed()
        self.__scr.addstr(y, x, message)

    def get_size(self):
        """
        Retrieves the screen size

        :return:
            Width and height of screen
        :raise BadOpError:
            Object has already been destroyed
        """
        self.__raiseif_destroyed()
        h, w = self.__scr.getmaxyx()
        return w, h
    
    def get_ch(self):
        """
        Gets a character code from the keyboard
        
        :return:
            Character code (or -1 if no character is pressed)
        :raise BadOpError:
            Object has already been destroyed
        """
        self.__raiseif_destroyed()
        return self.__scr.getch()

    #endregion