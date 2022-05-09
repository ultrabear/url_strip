"""
README generation tool that allows examples to be typechecked and special cases to be autodocumented
"""

import inspect
from typing import Callable, List, Dict, Protocol, Iterator


class examples:
    """
    Class containing examples
    """
    @staticmethod
    def is_instance_example() -> None:

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

    @staticmethod
    def get_example() -> None:

        from url_strip import strip_url, Ok, Err

        if (v := Ok.get(result := strip_url("foo"))) is not None:
            v.into_str()
        else:
            raise Err.unwrap(result)

    @staticmethod
    def domain_rules_example() -> None:
        from url_strip import UrlError, Ok, Err, StripFuncResult, HttpUrl, register

        @register(domain="foo.com")
        def foo_com_strip(
            url: HttpUrl
            ) -> StripFuncResult:  # Result[HttpUrl, UrlError] -> ('ok', HttpUrl) | ('err', UrlError)

            if url.path == "/failure":
                return Err(UrlError("This is an awful failure state"))

            else:
                return Ok(url)  # dont change url at all, its perfect as is


def wrap(f: Callable[..., None], /) -> str:
    source = "\n".join([i[8:].rstrip("\n") for i in inspect.getsourcelines(f)[0][2:]])
    return f"```py\n{source}\n```\n"


class StringWriter(Protocol):
    def write(self, data: str, /) -> int:
        ...


def unify(cases: Iterator[str], output: StringWriter) -> None:

    tree: Dict[str, List[str]] = {}

    def add_item(resolved: str, domain: str) -> None:
        try:
            tree[resolved].append(domain)
        except KeyError:
            tree[resolved] = [domain]

    for i in cases:
        resolve = i.split(".")
        # Assume its a .com/.net/etc endpoint
        if len(resolve) == 2:
            add_item(resolve[0], i)

        # take first item if its not www, or take second item
        elif len(resolve) >= 3:
            if resolve[0] == "www":
                add_item(resolve[1], i)
            else:
                add_item(resolve[0], i)
        else:
            add_item(i, i)

    output.write("| Site | Domains |\n")
    output.write("| --- | --- |\n")

    for k, v in tree.items():
        output.write(f"| {k} | `{'`, `'.join(v)}` | \n")


TITLE = "Url Strip"
DESCRIPTION = "A library for stripping urls of tracking and bloat"
PYTHONIC_CLAUSE = (
    "## Non Pythonic\n"
    "Usage was designed around typesafety and zero runtime surprises, so instead of "
    "raising exceptions, url\\_strip will return exceptions instead of results, "
    "this library works best with a typechecker because of this\n"
    )


def main() -> None:

    with open("README.md", "w") as fp:

        fp.write(f"# {TITLE}\n")
        fp.write(DESCRIPTION + "\n")
        fp.write(PYTHONIC_CLAUSE)

        fp.write("## Usage\nSome basic usage\n")

        fp.write("### Using is\\_instance and unwrap\n")
        fp.write(wrap(examples.is_instance_example))

        fp.write("### Using get\n")
        fp.write(wrap(examples.get_example))

        fp.write("### Writing extra domain rules\n")
        fp.write(wrap(examples.domain_rules_example))

        from url_strip import special_cases

        fp.write("## Popular websites supported are listed below:\n")
        unify(special_cases(), fp)


if __name__ == "__main__":
    main()
