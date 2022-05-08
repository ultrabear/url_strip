import threading
import sys
import subprocess
import time
from queue import Queue

from dataclasses import dataclass

from typing import Dict, Union, List, Iterator


# Wrapper around string to make the command run in sh instead of pexec
class Shell(str):
    __slots__ = ()


# Represents a ascii escaped color string
class Color:
    __slots__ = ()
    red = "\033[91m"
    blue = "\033[94m"
    reset = "\033[0m"
    green = "\033[92m"


@dataclass
class RunningProc:
    args: str
    stdout: bytes
    stderr: bytes
    duration_ns: int
    returncode: int


def into_str(args: Union[List[str], str]) -> str:

    if isinstance(args, list):
        return " ".join(args)

    return args


def run(args: Union[List[str], str], shell: bool, q: "Queue[RunningProc]") -> None:
    start = time.monotonic_ns()
    ret = subprocess.run(args, shell=shell, capture_output=True)

    q.put(
        RunningProc(
            into_str(args), ret.stdout, ret.stderr,
            time.monotonic_ns() - start, ret.returncode
            )
        )


def initjobs(tests: Dict[str, Union[str, Shell]]) -> "Queue[RunningProc]":

    testout: "Queue[RunningProc]" = Queue(maxsize=len(tests))

    for _, v in tests.items():

        flag = isinstance(v, Shell)
        args = v if flag else v.split()

        t = threading.Thread(target=run, args=(args, flag, testout))
        t.start()

    return testout


def lim_yield(q: "Queue[RunningProc]", lim: int) -> Iterator[RunningProc]:

    for _ in range(lim):
        yield q.get()


def finishjobs(testout: "Queue[RunningProc]", tests_c: int) -> int:

    errno = 0

    for v in lim_yield(testout, tests_c):

        err = v.stdout.decode("utf8") + v.stderr.decode("utf8")

        cmdfmt = f"{Color.blue}{v.args}{Color.green} {v.duration_ns//1000//1000}ms{Color.reset}"
        isshell = f'{Color.red}sh -c ' * isinstance(v.args, Shell)

        print(isshell + cmdfmt)
        if err: print(err, end="")

        if v.returncode != 0:
            errno = 1

    return errno


def main() -> int:

    tests: Dict[str, Union[str, Shell]] = {
        "pyflakes": "pyflakes .",
        "mypy": "mypy . --ignore-missing-imports --strict --warn-unreachable --python-version 3.8",
        "yapf": "yapf -drp .",
        "pylint": "pylint ./url_strip -j2 --py-version=3.8",
        "pyright": "pyright",
        #"pytype": "pytype .",
        }

    nottest = set(sys.argv[1:])

    for i in list(tests):
        if i in nottest:
            del tests[i]

    return finishjobs(initjobs(tests), len(tests))


if __name__ == "__main__":
    sys.exit(main())
