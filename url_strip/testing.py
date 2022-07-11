"""
Testing library for url_strip that allows easily writing and running tests
"""
import typing as _typing
import traceback as _traceback

if _typing.TYPE_CHECKING:
    Func = _typing.TypeVar("Func", bound=_typing.Callable[[], None])

__all__ = [
    "test",
    "run_tests",
    ]

_test_list: _typing.List[_typing.Callable[[], None]] = []


def test(c: "Func", /) -> "Func":
    """
    Decorator to add a function to the testing library
    """

    _test_list.append(c)

    return c


def run_tests() -> int:
    """
    Runs all tests in the list, printing any exceptions, with the return int
     indicating how many tests failed.
    0 may be treated as no tests failing, or success.
    """

    failure = 0

    for i in _test_list:
        try:
            i()
        except Exception as err:  # pylint: disable=broad-except
            # allow catching broad exceptions here to allow running all tests
            _traceback.print_exception(type(err), err, err.__traceback__)
            failure += 1

    return failure
