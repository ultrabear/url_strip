"""
Special cases init handler and predefined domains
"""
from typing import Dict, TypeVar, Callable, Iterator, List, Union

from ._types import StripFunc, StripFuncResult, Ok, Err, HttpUrl, UrlError

_special_cases: Dict[str, StripFunc] = {}

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
    return iter(_special_cases)


def register(*, domain: Union[str, List[str]]) -> Callable[[F], F]:
    """
    Register a stripping function to run for a specific domain
    """
    def deco(f: F, /) -> F:
        if isinstance(domain, str):
            _special_cases[domain] = f
        else:
            if len(domain) == 0:
                raise NoDomainError(f"Function {f} registered with no domains")
            for i in domain:
                _special_cases[i] = f
        return f

    return deco


def _no_query(v: HttpUrl, /) -> HttpUrl:
    return HttpUrl(v.domain, v.path, [], v.fragment)


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
