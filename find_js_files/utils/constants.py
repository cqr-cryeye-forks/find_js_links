#!/usr/bin/env python

from types import TracebackType
from typing import Union, Tuple, Type, Optional, Any, Dict, List, Set


class Config:
    TIMEOUT: int = 5
    TIMEOUT_DEFAULT: int = 60
    LIMIT_OF_ATTEMPTS_TO_RETRY: int = 5
    SIMULTANEOUS_CONCURRENT_TASKS: int = 51
    REQUESTS_RETRIES_NUM_TO_REMOVE: int = 1

    STATUS_CODE_DEFAULT: int = 0

    DEFAULT_DEBUGGING: bool = False

    USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                      ' Chrome/85.0.4183.102 Safari/537.36'

    RESULT_FILE_NAME: str = '../result.json'


class Types:
    RESULT: Type = Dict[str, Union[str, Set[str]]]
    RESULTS: Type = List[Dict[str, Union[str, Set[str]]]]
    JSON_RESULTS: Type = List[Dict[str, Union[str, List[str]]]]

    EXC_INFO: Type = Union[Tuple[type, BaseException, Optional[TracebackType]], tuple[None, None, None]]

    ASYNCIO_GATHER: Type = Tuple[
        Union[BaseException, Any], Union[BaseException, Any],
        Union[BaseException, Any], Union[BaseException, Any], Union[BaseException, Any]
    ]
