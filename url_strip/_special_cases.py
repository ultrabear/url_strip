"""
Special cases init handler and predefined domains
"""
from typing import Dict, TypeVar, Callable, Iterator, List, Union

from ._result import Ok, Err
from ._types import StripFunc, StripFuncResult, HttpUrl, UrlError
from .testing import test

special_cases_map: Dict[str, StripFunc] = {}

F = TypeVar("F", bound=StripFunc)


class NoDomainError(Exception):
    """
    Exception raised when a function is passed to register with no domains
    """
    __slots__ = ()


def special_cases() -> Iterator[str]:
    """
    Returns an iterator of all special case domain names
    """
    return iter(special_cases_map)


def register(*, domain: Union[str, List[str]]) -> Callable[[F], F]:
    """
    Register a stripping function to run for a specific domain
    """
    def deco(f: F, /) -> F:
        if isinstance(domain, str):
            special_cases_map[domain] = f
        else:
            if len(domain) == 0:
                raise NoDomainError(f"Function {f} registered with no domains")
            for i in domain:
                special_cases_map[i] = f
        return f

    return deco


def _no_query(v: HttpUrl, /) -> HttpUrl:
    return HttpUrl(v.domain, v.path, [], v.fragment)


def _takes_str(c: Callable[[HttpUrl], StripFuncResult], /) -> Callable[[str], StripFuncResult]:
    def takes_str(s: str, /) -> StripFuncResult:
        return c(Ok.unwrap(HttpUrl.from_str(s)))

    return takes_str


@register(domain=["youtube.com", "www.youtube.com"])
def youtube_strip(v: HttpUrl, /) -> StripFuncResult:
    """
    Strip function for youtube domains
    """

    quer = dict(v.query)

    if v.path == "/watch":

        if "v" not in quer:
            return Err(UrlError("Address was a watch link, but could not find video id"))

        return Ok(HttpUrl("youtu.be", f"/{quer['v']}", [], v.fragment))

    return Ok(_no_query(v))


@test
def test_yt_url() -> None:
    """
    Tests youtube stripfunc
    """
    stripfunc = _takes_str(youtube_strip)
    assert Ok.map(
        stripfunc("https://youtube.com/watch?v=abcdefg1234&tracker=345345"), HttpUrl.into_str
        ) == Ok("https://youtu.be/abcdefg1234")


@register(domain=["www.amazon.com", "www.amazon.co.uk"])
def amazon_strip(v: HttpUrl, /) -> StripFuncResult:
    """
    Strip function for amazon domains
    """

    splitpath = v.path.split("/")

    if (idx := splitpath.index("dp")) != -1:
        try:
            product_id = splitpath[idx + 1]
        except IndexError:
            return Ok(_no_query(v))

        return Ok(HttpUrl(v.domain, f"/dp/{product_id}", [], v.fragment))

    return Ok(_no_query(v))


@register(domain=["ebay.com", "www.ebay.com", "www.ebay.co.uk"])
def ebay_strip(v: HttpUrl, /) -> StripFuncResult:
    """
    Strip function for ebay domains
    """

    return Ok(_no_query(v))


@register(domain="twitter.com")
def twitter_strip(v: HttpUrl, /) -> StripFuncResult:
    """
    Strip function for twitter domains
    """

    return Ok(_no_query(v))
