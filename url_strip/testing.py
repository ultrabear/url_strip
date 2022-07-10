"""
Testing library for url_strip that allows easily writing and running tests
"""
from typing import Callable, List, TypeVar
import traceback

_test_list: List[Callable[[], None]] = []

Func = TypeVar("Func", bound=Callable[[], None])


def test(c: Func, /) -> Func:
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
            traceback.print_exception(type(err), err, err.__traceback__)
            failure += 1

    return failure
