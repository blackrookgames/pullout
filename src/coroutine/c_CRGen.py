all = ['CRGen']

from typing import\
    Any as _Any,\
    Generator as _Generator

from .c_CRWait import\
    CRWait as _CRWait

type CRGen = _Generator[_CRWait, _Any, _Any]