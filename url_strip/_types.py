"""
Base types for the url_strip library
"""

from dataclasses import dataclass
import inspect
from typing import Callable, Union, Optional, TypeVar, Literal, Tuple, List, Type, Final

import re

from typing_extensions import TypeGuard

# chars unreserved (allowed) in a url and the expansion char
# based on https://www.ietf.org/rfc/rfc3986.txt
URL_CHARS: Final = r"([a-zA-z0-9\-\.\_\-]|%[0-9a-fA-F]{2})"

DOMAIN_CAPTURE: Final = f"(?P<domain>{URL_CHARS}+)"

PATH_CAPTURE: Final = f"(?P<path>(/{URL_CHARS}*)+)"

QUERY_KV: Final = f"{URL_CHARS}+={URL_CHARS}+"
QUERY_CAPTURE: Final = f"(\\?(?P<query>{QUERY_KV}(&{QUERY_KV})*))"

FRAGMENT_CAPTURE: Final = f"(?P<fragment>#{URL_CHARS}+)"

# This regex will capture something that is intended to be a url
URL_REGEX: Final = re.compile(
    f"\\b(?:https?://){DOMAIN_CAPTURE}{PATH_CAPTURE}?{QUERY_CAPTURE}?{FRAGMENT_CAPTURE}?\\b"
    )


class UrlError(Exception):
    """
    A url related error
    """
    __slots__ = ()


T = TypeVar("T")
E = TypeVar("E")

Result = Union[Tuple[Literal["ok"], T], Tuple[Literal["err"], E]]


class UnwrapError(Exception):
    """
    Error that is raised when unwrapping a Result fails
    """
    __slots__ = ()


class _Ok:
    """
    Constructor and inspector class for getting the Ok variant of a Result type
    """
    __slots__ = ()

    @staticmethod
    def __call__(value: T, /) -> Tuple[Literal["ok"], T]:
        """
        Wraps a value in an Ok type
        """
        return ("ok", value)

    @staticmethod
    def is_instance(result: Result[T, E], /) -> TypeGuard[Tuple[Literal["ok"], T]]:
        """
        Returns True if Result is an Ok variant
        """
        return result[0] == "ok"

    @staticmethod
    def get(result: Result[T, E], /) -> Optional[T]:
        """
        Returns Ok variant from Result or returns None
        """
        if result[0] == "err":
            return None

        return result[1]

    @staticmethod
    def unwrap(result: Result[T, E], /) -> T:
        """
        Returns Ok variant from Result or raises
        """
        if result[0] == "err":
            # print lineno and fname of caller
            if (cur_frame := inspect.currentframe()
                ) is not None and (caller_frame := cur_frame.f_back) is not None:
                loc = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno} "
            else:
                loc = ""

            raise UnwrapError(f"{loc}Result type was Err variant, expected Ok variant")

        return result[1]


class _Err:
    """
    Constructor and inspector class for getting the Err variant of a Result type
    """
    __slots__ = ()

    @staticmethod
    def __call__(value: E, /) -> Tuple[Literal["err"], E]:
        """
        Wraps a value in an Err type
        """
        return ("err", value)

    @staticmethod
    def is_instance(result: Result[T, E], /) -> TypeGuard[Tuple[Literal["err"], E]]:
        """
        Returns True if Result is an Err variant
        """
        return result[0] == "err"

    @staticmethod
    def get(result: Result[T, E], /) -> Optional[E]:
        """
        Returns Err variant from Result or returns None
        """
        if result[0] == "ok":
            return None

        return result[1]

    @staticmethod
    def unwrap(result: Result[T, E], /) -> E:
        """
        Returns Err variant of Result type or raises
        """
        if result[0] == "ok":
            # print lineno and fname of caller
            if (cur_frame := inspect.currentframe()
                ) is not None and (caller_frame := cur_frame.f_back) is not None:
                loc = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno} "
            else:
                loc = ""

            raise UnwrapError(f"{loc}Result type was Ok variant, expected Err variant")

        return result[1]


Ok = _Ok()
Err = _Err()


@dataclass
class HttpUrl:
    """
    An HttpUrl is a dataclass of a url representing its base parts, making it easier to modify
    """
    __slots__ = "domain", "path", "query", "fragment"
    domain: str
    path: str
    query: List[Tuple[str, str]]
    fragment: Optional[str]

    @staticmethod
    def _parse_query_str(query_str: Optional[str], /) -> List[Tuple[str, str]]:
        """
        Parses a query string into its ast value
        """
        query: List[Tuple[str, str]] = []

        if query_str is not None:
            for i in query_str.split("&"):
                key, value = i.split("=")
                query.append((key, value), )

        return query

    def into_str(self, *, protocol: str = "https") -> str:
        """
        Returns a string representation of the HttpUrl
        """
        query_str = "?" + "&".join(f"{k}={v}" for k, v in self.query) if self.query else ""
        fragment_str = self.fragment if self.fragment is not None else ""

        return f"{protocol}://{self.domain}{self.path}{query_str}{fragment_str}"

    @classmethod
    def from_str(cls: Type["HttpUrl"], url: str, /) -> Optional["HttpUrl"]:
        """
        Parses an HttpUrl from a string
        """

        # remove any trailing path pieces
        url = url.rstrip("/")

        if (capture := URL_REGEX.match(url)) is None:
            return None

        # Require entire field to be url
        if capture.span() != (0, len(url)):
            return None

        if (domain := capture.group("domain")) is None:
            return None

        if (path := capture.group("path")) is None:
            path = ""

        query = cls._parse_query_str(capture.group("query"))

        fragment = capture.group("fragment")

        return cls(domain, path, query, fragment)


StripFuncResult = Result[HttpUrl, UrlError]
StripFunc = Callable[[HttpUrl], StripFuncResult]
