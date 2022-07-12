from typing import List
from setuptools import setup, find_packages


def get_requires() -> List[str]:
    return ["typing_extensions >= 3.10.0.0, < 5"]


def support_pyvers(major: int, minor: range) -> List[str]:
    return [f"Programming Language :: Python :: {major}.{i}" for i in minor]


setup(
    name="url_strip",
    version="0.2.1",
    description=
    "Library to strip http urls of tracking elements, and use shorthand variants of urls",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="ultrabear",
    author_email="bearodark@gmail.com",
    packages=find_packages(),
    install_requires=get_requires(),
    extras_require={
        # yapf requires toml to load pyproject.toml
        "dev": ["mypy", "pylint", "yapf", "toml", "pyflakes", "pyright"],
        },
    python_requires=">=3.8.0",
    classifiers=[
        *support_pyvers(3, range(8, 11)), "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta", "Intended Audience :: Developers",
        "Natural Language :: English", "Operating System :: OS Independent",
        "Topic :: Text Processing :: Filters", "Typing :: Typed",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        ],
    )
