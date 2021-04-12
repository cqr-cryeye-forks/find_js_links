#!/usr/bin/env python
# coding=utf-8

import os
import logging

from .constants import Types


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info: Types.EXC_INFO) -> str:
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record: logging.LogRecord) -> str:
        # noinspection StrFormat
        result = super().format(record)
        if record.exc_text:
            result = result.replace('\n', '')
        return result

    @classmethod
    def logger_initialisation(cls, debug: bool = False) -> None:
        debug_level: bool = debug and 'DEBUG' or 'INFO'
        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: OneLineExceptionFormatter = cls(logging.BASIC_FORMAT)
        handler.setFormatter(formatter)
        root: logging.Logger = logging.getLogger()
        root.setLevel(os.environ.get('LOGLEVEL', debug_level))
        root.addHandler(handler)
