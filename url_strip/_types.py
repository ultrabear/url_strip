"""
Base types for the url_strip library
"""

from dataclasses import dataclass
import io
from typing import Callable, Optional, Tuple, List, Type, Final

import re

from ._result import Result, Ok, Err

# chars unreserved (allowed) in a url and the expansion char
# based on https://www.ietf.org/rfc/rfc3986.txt
# added @ to allow capturing tiktok urls
URL_CHARS: Final = r"([a-zA-z0-9\-\.\_\-@]|%[0-9a-fA-F]{2})"

DOMAIN_CAPTURE: Final = f"(?P<domain>{URL_CHARS}+)"

# Colons are allowed in the path
PATH_CAPTURE: Final = f"(?P<path>(/({URL_CHARS}|\\:)*)+)"

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


class UrlParseError(UrlError):
    """
    An error relating to a url parse
    """
    __slots__ = ()


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

    @staticmethod
    def _expand_format_chars(s: str, /) -> Result[str, UrlParseError]:
        """
        Expands url format chars in a string
        """

        output = io.BytesIO()
        skip = 0

        for idx, char in enumerate(s):
            if skip != 0:
                skip -= 1
            elif char == "%":
                skip = 2
                val = s[idx + 1:idx + 3]
                if len(val) != 2:
                    return Err(
                        UrlParseError(
                            "Could not expand url element, not enough chars after % symbol"
                            )
                        )

                try:
                    data = int(val, 16)
                except ValueError:
                    print(val)
                    return Err(
                        UrlParseError(
                            "Could not expand url element, chars after % symbol are not hex encoded"
                            )
                        )

                output.write(bytes([data]))

            else:
                output.write(char.encode("utf8"))

        try:
            return Ok(output.getvalue().decode("utf8"))
        except UnicodeDecodeError as err:
            return Err(UrlParseError(err))

    def into_str(self, *, protocol: str = "https") -> str:
        """
        Returns a string representation of the HttpUrl
        """
        query_str = "?" + "&".join(f"{k}={v}" for k, v in self.query) if self.query else ""
        fragment_str = self.fragment if self.fragment is not None else ""

        return f"{protocol}://{self.domain}{self.path}{query_str}{fragment_str}"

    def path_decoded(self) -> Result[List[str], UrlError]:
        """
        Expands % format characters and returns path as a list
        """
        splitpath = self.path.split("/")

        out: List[str] = []

        for i in map(self._expand_format_chars, splitpath):

            if (val := Ok.get(i)) is not None:
                out.append(val)
            else:
                return Err(Err.unwrap(i))

        return Ok(out)

    @classmethod
    def from_str(cls: Type["HttpUrl"], url: str, /) -> Result["HttpUrl", UrlParseError]:
        """
        Parses an HttpUrl from a string
        """

        # remove any trailing path pieces
        url = url.rstrip("/")

        if (capture := URL_REGEX.match(url)) is None:
            return Err(UrlParseError("Regex could not find url match"))

        # Require entire field to be url
        if capture.span() != (0, len(url)):
            return Err(UrlParseError("Regex capture does not span entire string passed"))

        if (domain := capture.group("domain")) is None:
            return Err(UrlParseError("Could not capture domain group"))

        if (path := capture.group("path")) is None:
            path = ""

        query = cls._parse_query_str(capture.group("query"))

        fragment = capture.group("fragment")

        return Ok(cls(domain, path, query, fragment))


StripFuncResult = Result[HttpUrl, UrlError]
StripFunc = Callable[[HttpUrl], StripFuncResult]
