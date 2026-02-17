all = [\
    'attr_create',\
    'attr_color',\
    'attr_emp',\
    'ATTR_NORMAL']

def attr_create(color:int = 7, emp:bool = False):
    """
    Creates an text attribute value
    
    :param color:
        Text color (0-7)
    :param emp:
        Whether or not text should be emphasized
    :return:
        Created text attribute value
    """
    return (color & 0b111) | (0b1000 if emp else 0b0000)

def attr_color(attr:int):
    """
    Retrieves a text attribute's color info
    
    :param attr:
        Text attribute
    :return:
        Text attribute's color info
    """
    return attr & 0b111

def attr_emp(attr:int):
    """
    Retrieves a text attribute's emphasis info
    
    :param attr:
        Text attribute
    :return:
        Text attribute's emphasis info
    """
    return (attr & 0b1000) != 0

ATTR_NORMAL = attr_create()