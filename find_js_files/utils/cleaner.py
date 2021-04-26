"""
A cleaner module
To cleanup set of url from unwanted extensions
"""

from os.path import splitext
from typing import Set, Tuple

from urllib.parse import urlparse

INCLUDE_EXTENSIONS: Tuple[str] = ('.js',)
EXCLUDE_EXTENSIONS: Tuple[str] = (
    '.css', '.png', '.jpeg', '.jpg', '.svg', '.gif',
    '.wolf', '.woff', '.woff2', '.eot', '.ttf', '.ico',
    '.tn', '.swf', '.exe',)


def clean_from_unwanted_extensions(urls: Set[str]) -> Set[str]:
    """
    Method to exclude unwanted extensions from a set of urls
    :return: Set[str]
    """
    return set(filter(lambda u: splitext(urlparse(u).path)[1] not in EXCLUDE_EXTENSIONS, urls))


def left_only_needle_extensions(urls: Set[str]) -> Set[str]:
    """
    Method to remove extensions from a set and left only needed ones.
    :param: Set[str]
    :return: Set[str]
    """
    return set(filter(lambda u: splitext(urlparse(u).path)[1] in INCLUDE_EXTENSIONS, urls))
