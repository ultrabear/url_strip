from typing import List
from setuptools import setup, find_packages


def get_requires() -> List[str]:
    with open("requirements.txt", "r") as fp:
        return [i.strip("\n") for i in fp.readlines()]

def support_pyvers(major: int, minor: range) -> List[str]:
    return [f"Programming Language :: Python :: {major}.{i}" for i in minor]
        



setup(
    name="url_strip",
    version="0.0.1",
    description="Library to strip http urls of tracking elements, and use shorthand variants of urls",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="ultrabear",
    author_email="bearodark@gmail.com",
    packages=find_packages(),
    install_requires=get_requires(),
    classifiers=[
        *support_pyvers(3, range(8,12)),
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Filters",
        "Typing :: Typed",
    ],
    )
