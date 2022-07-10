"""
Strips a url
"""
import copy

from ._special_cases import special_cases_map
from ._result import Result, Err, Ok
from ._types import HttpUrl, UrlError
from .testing import test


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

    parsed: Result[HttpUrl, UrlError] = HttpUrl.from_str(url_str)

    if (err := Err.get(parsed)) is not None:
        return Err(err)

    url = Ok.unwrap(parsed)

    if url.domain in special_cases_map:
        return special_cases_map[url.domain](url)

    return strip_last_query(url)


@test
def test_error_url() -> None:
    """
    Tests url parsing erroring correctly
    """

    assert Err.is_instance(strip_url("s\\gfadhbgjdkshfgb"))
