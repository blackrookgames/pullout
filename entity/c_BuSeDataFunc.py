all = ['func_buy', 'func_sell']

from typing import\
    Callable as _Callable

type func_buy = _Callable[[str], None]
type func_sell = _Callable[[str], None]