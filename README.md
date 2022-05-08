# Url Strip
A library for stripping urls of tracking and bloat
## Non Pythonic
Usage was designed around typesafety and zero runtime surprises, so instead of raising exceptions, url\_strip will return exceptions instead of results, this library works best with a typechecker because of this
## Usage
Some basic usage
### Using is\_instance and unwrap
```py

from url_strip import Ok, strip_url

# Ok and Err provide the same 3 methods with fully typed outcomes for a Result[T, E]:
#  is_instance will TypeGuard the result to the variant
#  get will return an Optional[T] of the variant (and is not suitable for cases where T or E are None)
#  unwrap with return the requested variant or raise an exception
if Ok.is_instance(
    v := strip_url(
        "https://youtube.com/watch?v=dQw4w9WgXcQ&trackerinfo=youraddresshere&mldata=whattimeyouwokeupthismorning"
        )
    ):
    # using unwrap is runtime safe here as we just typeguarded it is an Ok variant
    url = Ok.unwrap(v)
    # strip_url returns a Result[HttpUrl, UrlError], and HttpUrl provides a into_str method to get what most people expect as a final output
    # NOTE: A bug in mypy causes the is_instance TypeGuard to change the type from ('ok', HttpUrl) to ('ok', T`-1)
    # We ignore the error for now, see: https://github.com/python/mypy/issues/12753 (current status: patched on master, awaiting next release)
    value = url.into_str()  # type: ignore[attr-defined]

    print(value)  # -> https://youtu.be/dQw4w9WgXcQ
else:
    ...  # Insert error handling here
```
### Using get
```py

from url_strip import strip_url, Ok, Err

if (v := Ok.get(result := strip_url("foo"))) is not None:
    v.into_str()
else:
    raise Err.unwrap(result)
```
### Writing extra domain rules
```py
from url_strip import UrlError, Ok, Err, StripFuncResult, HttpUrl, register

@register(domain="foo.com")
def foo_com_strip(
    url: HttpUrl
    ) -> StripFuncResult:  # Result[HttpUrl, UrlError] -> ('ok', HttpUrl) | ('err', UrlError)

    if url.path == "/failure":
        return Err(UrlError("This is an awful failure state"))

    else:
        return Ok(url)  # dont change url at all, its perfect as is
```
