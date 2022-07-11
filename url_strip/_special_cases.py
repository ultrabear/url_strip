"""
Special cases init handler and predefined domains
"""
from typing import Dict, TypeVar, Callable, Iterator, List, Union

from ._result import Ok, Err, Result
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


def _takes_str(c: Callable[[HttpUrl], StripFuncResult],
               /) -> Callable[[str], Result[str, UrlError]]:
    def takes_str(s: str, /) -> Result[str, UrlError]:
        return Ok.map(c(Ok.unwrap(HttpUrl.from_str(s))), HttpUrl.into_str)

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
    assert stripfunc("https://youtube.com/watch?v=abcdefg1234&tracker=345345"
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


@test
def test_amazon_url() -> None:
    """
    Tests amazon urls
    """
    stripfunc = _takes_str(amazon_strip)

    # real amazon url btw
    res = stripfunc(
        "https://www.amazon.com/KONNWEI-Bluetooth-Wireless-Diagnostic-compatible/dp/B073F57QT3/"
        "?content-id=amzn1.sym.bbb6bbd8-d236-47cb-b42f-734cb0cacc1f"
        )

    assert res == Ok("https://www.amazon.com/dp/B073F57QT3")


@register(domain="twitter.com")
@register(domain="www.reddit.com")
@register(domain=["ebay.com", "www.ebay.com", "www.ebay.co.uk"])
@register(domain=["www.tiktok.com", "vm.tiktok.com"])
def no_queryable(v: HttpUrl, /) -> StripFuncResult:
    """
    Strips collection of domains that can be effectively stripped by
     removing the query string on them
    """

    return Ok(_no_query(v))


@test
def test_no_query() -> None:
    """
    Tests that no_queryable removes queries
    """

    func = _takes_str(no_queryable)

    assert func("https://google.com/search?v=among") == Ok("https://google.com/search")

    assert Ok.is_instance(
        func("https://www.tiktok.com/@amqsinc/video/7118107323461094699?_t=8TshIG8gDyQ&_r=1")
        )
