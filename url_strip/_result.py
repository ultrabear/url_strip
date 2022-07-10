"""
Definition of the Result type and accompanying classes
"""

__all__ = [
    "Result",
    "Ok",
    "Err",
    "UnwrapError",
    ]

import inspect

from typing import TypeVar, Union, Tuple, Literal, Optional, Callable
from typing_extensions import TypeGuard

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")

Result = Union[Tuple[Literal["ok"], T], Tuple[Literal["err"], E]]


class UnwrapError(Exception):
    """
    Error that is raised when unwrapping a Result fails
    """
    __slots__ = ()


class ClassOk:
    """
    Constructor and inspector class for getting the Ok variant of a Result type
    """
    __slots__ = ()

    @staticmethod
    def __call__(value: T, /) -> Tuple[Literal["ok"], T]:
        """
        Wraps a value in an Ok type
        """
        return ("ok", value)

    @staticmethod
    def is_instance(result: Result[T, E], /) -> TypeGuard[Tuple[Literal["ok"], T]]:
        """
        Returns True if Result is an Ok variant
        """
        return result[0] == "ok"

    @staticmethod
    def get(result: Result[T, E], /) -> Optional[T]:
        """
        Returns Ok variant from Result or returns None
        """
        if result[0] == "err":
            return None

        return result[1]

    @staticmethod
    def unwrap(result: Result[T, E], /) -> T:
        """
        Returns Ok variant from Result or raises
        """
        if result[0] == "err":
            # print lineno and fname of caller
            if (cur_frame := inspect.currentframe()
                ) is not None and (caller_frame := cur_frame.f_back) is not None:
                loc = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno} "
            else:
                loc = ""

            raise UnwrapError(
                f"{loc}Result type was Err variant, expected Ok variant\n"
                f"Err: {type(result[1]).__name__}='{result[1]}'"
                )

        return result[1]

    @staticmethod
    def map(result: Result[T, E], call: Callable[[T], U]) -> Result[U, E]:
        """
        Maps Ok value of result with function, or returns Err variant
        """
        if Ok.is_instance(result):
            return Ok(call(result[1]))
        if Err.is_instance(result):
            return result

        raise RuntimeError("Unreachable!")


class ClassErr:
    """
    Constructor and inspector class for getting the Err variant of a Result type
    """
    __slots__ = ()

    @staticmethod
    def __call__(value: E, /) -> Tuple[Literal["err"], E]:
        """
        Wraps a value in an Err type
        """
        return ("err", value)

    @staticmethod
    def is_instance(result: Result[T, E], /) -> TypeGuard[Tuple[Literal["err"], E]]:
        """
        Returns True if Result is an Err variant
        """
        return result[0] == "err"

    @staticmethod
    def get(result: Result[T, E], /) -> Optional[E]:
        """
        Returns Err variant from Result or returns None
        """
        if result[0] == "ok":
            return None

        return result[1]

    @staticmethod
    def unwrap(result: Result[T, E], /) -> E:
        """
        Returns Err variant of Result type or raises
        """
        if result[0] == "ok":
            # print lineno and fname of caller
            if (cur_frame := inspect.currentframe()
                ) is not None and (caller_frame := cur_frame.f_back) is not None:
                loc = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno} "
            else:
                loc = ""

            raise UnwrapError(
                f"{loc}Result type was Ok variant, expected Err variant\n"
                f"Ok: {type(result[1]).__name__}='{result[1]}'"
                )

        return result[1]


Ok: ClassOk = ClassOk()
Err: ClassErr = ClassErr()
