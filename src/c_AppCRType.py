all = ['AppCRType']

from typing import\
    Any as _Any,\
    Generator as _Generator

from .c_AppCRWait import\
    AppCRWait as _AppCRWait

type AppCRType = _Generator[_AppCRWait, _Any, _Any]