# main file
"""
A small library to strip urls of tracking elements, with easy extensibility
"""

__all__ = [
    "Result",
    "Ok",
    "Err",
    "HttpUrl",
    "UrlError",
    "UrlParseError",
    "StripFunc",
    "StripFuncResult",
    "register",
    "strip_url",
    "special_cases",
    ]

from ._result import Result, Ok, Err
from ._types import HttpUrl, UrlError, UrlParseError, StripFunc, StripFuncResult
from ._special_cases import register, special_cases
from ._strip import strip_url
