all = ['BCCoord']

class BCCoord:
    """
    Represents coordinates for a single axis
    """

    #region init

    def __init__(self, dis0:None|int = None, dis1:None|int = None, len:None|int = None):
        """
        Initializer for BCCoord
        
        :param dis0:
            For X-axis: Distance from the left edge of console to left edge of pane\n
            For Y-axis: Distance from the top edge of console to top edge of pane
        :param dis1:
            For X-axis: Distance from the right edge of console to right edge of pane\n
            For Y-axis: Distance from the bottom edge of console to bottom edge of pane
        :param len:
            For X-axis: Width of pane\n
            For Y-axis: Height of pane
        """
        self.__dis0 = dis0
        self.__dis1 = dis1
        self.__len = len
        self.__first = True
        self.__prev_dis0:None|int = None
        self.__prev_dis1:None|int = None
        self.__prev_len:None|int = None
        self.__pnt0:int = 0
        self.__pnt1:int = 0
        self.__pntlen:int = 0
        self.__clip0:int = 0
        self.__clip1:int = 0
        self.__cliplen:int = 0
        self.__clipoff:int = 0

    #endregion

    #region properties

    @property
    def dis0(self):
        """
        For X-axis: Distance from the left edge of console to left edge of pane\n
        For Y-axis: Distance from the top edge of console to top edge of pane
        """
        return self.__dis0

    @property
    def dis1(self):
        """
        For X-axis: Distance from the right edge of console to right edge of pane\n
        For Y-axis: Distance from the bottom edge of console to bottom edge of pane
        """
        return self.__dis1

    @property
    def len(self):
        """
        For X-axis: Width of pane\n
        For Y-axis: Height of pane
        """
        return self.__len

    @property
    def pnt0(self):
        """
        For X-axis: X-coordinate of left edge\n
        For Y-axis: Y-coordinate of top edge
        """
        return self.__pnt0
    
    @property
    def pnt1(self):
        """
        For X-axis: X-coordinate of right edge\n
        For Y-axis: Y-coordinate of bottom edge
        """
        return self.__pnt1
    
    @property
    def pntlen(self):
        """
        Distance between pnt0 and pnt1\n
        For X-axis: Resolved width\n
        For Y-axis: Resolved height
        """
        return self.__pntlen

    @property
    def clip0(self):
        """
        For X-axis: X-coordinate of left clip\n
        For Y-axis: Y-coordinate of top clip
        """
        return self.__clip0
    
    @property
    def clip1(self):
        """
        For X-axis: X-coordinate of right clip\n
        For Y-axis: Y-coordinate of bottom clip
        """
        return self.__clip1
    
    @property
    def cliplen(self):
        """
        Distance between clip0 and clip1\n
        For X-axis: Clip width\n
        For Y-axis: Clip height
        """
        return self.__cliplen

    @property
    def clipoff(self):
        """
        This is the offset from pnt0 to clip0
        """
        return self.__clipoff

    @dis0.setter
    def dis0(self, value:None|int): self.__dis0 = value

    @dis1.setter
    def dis1(self, value:None|int): self.__dis1 = value

    @len.setter
    def len(self, value:None|int): self.__len = value

    #endregion
    
    #region helper methods

    def _m_resolve(self, force:bool, containlen:int):
        """
        Also accessed by TPPane
        """
        if not (force or self.__first or\
                self.__prev_dis0 != self.__dis0 or\
                self.__prev_dis1 != self.__dis1 or\
                self.__prev_len != self.__len):
            return False
        # Update previous
        self.__first = False
        self.__prev_dis0 = self.__dis0
        self.__prev_dis1 = self.__dis1
        self.__prev_len = self.__len
        # Resolve
        pnt0 = self.dis0
        pnt1 = None if (self.dis1 is None) else (containlen - self.dis1)
        pntlen = self.len
        if pnt0 is not None:
            if pnt1 is not None:
                pntlen = pnt1 - pnt0
            elif pntlen is not None:
                pnt1 = pnt0 + pntlen
            else:
                pnt1 = pnt0
                pntlen = 0
        elif pnt1 is not None:
            if pntlen is not None:
                pnt0 = pnt1 - pntlen
            else:
                pnt0 = pnt1
                pntlen = 0
        elif pntlen is not None:
            pnt0 = 0
            pnt1 = pntlen
        else:
            pnt0 = 0
            pnt1 = 0
            pntlen = 0
        self.__pnt0 = pnt0
        self.__pnt1 = pnt1
        self.__pntlen = pntlen
        self.__clip0 = max(0, min(containlen, self.__pnt0))
        self.__clip1 = max(0, min(containlen, self.__pnt1))
        self.__cliplen = self.__clip1 - self.__clip0
        self.__clipoff = self.__clip0 - self.pnt0
        return True

    #endregion