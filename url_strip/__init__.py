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

import typing as _typing

from ._result import Result, Ok, Err
from ._types import HttpUrl, UrlError, UrlParseError, StripFunc, StripFuncResult
from ._special_cases import register, special_cases
from ._strip import strip_url


class _VersionInfo(_typing.NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: _typing.Literal["alpha", "beta", "candidate", "final"]
    serial: int

    def as_pep440_str(self) -> str:
        """
        Formats a _VersionInfo into a pep440 compliant a-b-rc string
        """
        _table = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}
        serial = str(self.serial) if self.serial else ""
        return f"{self.major}.{self.minor}.{self.micro}{_table[self.releaselevel]}{serial}"


version_info = _VersionInfo(0, 2, 1, "final", 0)
__version__ = version_info.as_pep440_str()
