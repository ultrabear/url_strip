<!--
 WARNING: This file is automatically generated by genreadme.py
 To edit this file, make changes to {fname} instead
-->
# Url Strip 0.2.2b
A library for stripping urls of tracking and bloat
## Non Pythonic
Usage was designed around typesafety and zero runtime surprises, so instead of raising exceptions, url\_strip will return exceptions instead of results, this library works best with a typechecker because of this
## Usage
Some basic usage. These examples are all runnable and meet typing standards.
### Using is\_instance and unwrap
```py
"""
Uses is_instance and unwrap to parse a url
"""

from url_strip import Ok, strip_url

# Ok and Err provide the same 3 methods with fully typed outcomes for a Result[T, E]:
#  is_instance will TypeGuard the result to the variant
#  get will return an Optional[T] of the variant
#    (and is not suitable for cases where T or E are None)
#  unwrap with return the requested variant or raise an exception
if Ok.is_instance(
    v := strip_url(
        "https://youtube.com/watch?v=dQw4w9WgXcQ"
        "&trackerinfo=youraddresshere&mldata=whattimeyouwokeupthismorning"
        )
    ):
    # using unwrap is runtime safe here as we just typeguarded it is an Ok variant
    url = Ok.unwrap(v)
    # strip_url returns a Result[HttpUrl, UrlError], and HttpUrl provides a into_str method
    #  to get what most people expect as a final output
    value = url.into_str()

    print(value)  # -> https://youtu.be/dQw4w9WgXcQ
else:
    ...  # Insert error handling here
```
### Using get
```py
"""
Uses get and a None check to parse an invalid url
"""

from url_strip import strip_url, Ok, Err

if (v := Ok.get(result := strip_url("foo"))) is not None:
    v.into_str()
else:
    raise Err.unwrap(result)
```
### Writing extra domain rules
```py
"""
Uses register to add foo.com as a checked domain
"""
from url_strip import UrlError, Ok, Err, StripFuncResult, HttpUrl, register

@register(domain="foo.com")
def foo_com_strip( # pyright: ignore[reportUnusedFunction]
    url: HttpUrl
    ) -> StripFuncResult:  # ('ok', HttpUrl) | ('err', UrlError)

    if url.path == "/failure":
        return Err(UrlError("This is an awful failure state"))

    return Ok(url)  # dont change url at all, its perfect as is
```
## Popular Websites Supported
Some popular websites have pre-`register`'d rules, while any non registered websites will go to a default query stripper  
The pre registered domains are as follows:
| Site | Domains |
| --- | --- |
| amazon | `www.amazon.com`, `www.amazon.co.uk` | 
| ebay | `ebay.com`, `www.ebay.com`, `www.ebay.co.uk`, `www.ebay.it`, `www.ebay.de` | 
| reddit | `www.reddit.com` | 
| tiktok | `www.tiktok.com`, `vm.tiktok.com` | 
| twitter | `twitter.com` | 
| youtube | `youtube.com`, `www.youtube.com` | 
