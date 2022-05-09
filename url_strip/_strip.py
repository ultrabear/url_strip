"""
Strips a url
"""
from typing import Final
import copy

from ._special_cases import special_cases_map
from ._types import HttpUrl, Result, UrlError, Err, Ok


def strip_last_query(url: HttpUrl, /) -> Result[HttpUrl, UrlError]:
    """
    Strips all but the first query of a url, works for general cases
    """

    url = copy.copy(url)

    url.query = url.query[:1]

    return Ok(url)


def strip_url(url_str: str, /) -> Result[HttpUrl, UrlError]:
    """
    Strips a url of tracking elements and bloat
    """

    if not url_str.startswith("http"):
        return Err(UrlError("Url does not start with http(s)"))

    url: Final = HttpUrl.from_str(url_str)

    if url is None:
        return Err(UrlError("String passed could not parse into url"))

    if url.domain in special_cases_map:
        return special_cases_map[url.domain](url)

    return strip_last_query(url)
