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
    "StripFunc",
    "StripFuncResult",
    "register",
    "strip_url",
    ]

from ._types import Result, Ok, Err, HttpUrl, UrlError, StripFunc, StripFuncResult
from ._special_cases import register
from ._strip import strip_url
