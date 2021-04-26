"""
This is a result cleaner module.
"""

from typing import Set, Iterator
from dataclasses import dataclass
from urllib.parse import urlparse
from functools import cached_property

from .constants import Types


@dataclass
class ResultsCleaner:
    """
    Class Results Cleaner.
    It cleans results from duplicates.
    Extracts root url.
    Adds root url to results if needed.

    properties:
     - results: results object to work with
    """

    _results: Types.RESULTS

    @classmethod
    def clean(cls, results: Types.RESULTS) -> Types.RESULTS:
        """

        :param: Type.RESULTS
        :param results:
        """
        obj = cls(results)
        obj._clean()
        return obj.results

    def _clean(self) -> Types.RESULTS:
        self._clean_from_empty()
        self._add_root_url_if_needed()
        self._set_all_common_js_links()
        self._clean_js_links_from_common()
        self._clean_from_empty()

    def _clean_js_links_from_common(self) -> None:
        """
        Method to remove common links and left only unique
        :return: None
        """
        for index, result in enumerate(self.results):
            if result['url'] == 'root':
                continue
            self.results[index]['js_links']: Set[str] = self._get_difference_js_links(result['js_links'])

    def _get_difference_js_links(self, js_links: Set[str]) -> Set[str]:
        """
        Method to find difference between common urls and special to source urls
        :return: Set[str]
        """
        return js_links.difference(self.results[-1]['js_links'])

    def _set_all_common_js_links(self) -> None:
        """
        Method to add common js links to root field
        :return: None
        """
        self.results.append({'url': 'root', 'js_links': self._get_intersection_js_links})

    def _clean_from_empty(self) -> None:
        """
        Method to clean results from empty js_links
        :return:
        """
        self.results: Types.RESULTS = [u for u in self.results if u['js_links']]

    def _add_root_url_if_needed(self) -> None:
        """
        Method to ensure each js link has domain with schema attached to it
        :return: None
        """
        for index, result in enumerate(self.results):
            self.results[index]['js_links']: Set[str] = {
                f'{self._get_root_url_from_links}/{url.lstrip("/")}'
                for url in result['js_links']
                if self._get_root_url_from_links not in url
            }

    @cached_property
    def _get_intersection_js_links(self) -> Set[str]:
        """
        Cached property to return intersection of all sets with js links
        :return: Set[str]
        """
        return set.intersection(*self._all_js_links)

    @cached_property
    def _all_js_links(self) -> Iterator[Set[str]]:
        """
        Cached property to return generator with sets of js links
        :return: Iterator[Set[str]]
        """
        return (result['js_links'] for result in self.results)

    @cached_property
    def _get_root_url_from_links(self) -> str:
        parsed_url = urlparse(url=next(iter(self.results))['url'])
        return f'{parsed_url.scheme}//{parsed_url.netloc}'

    @property
    def results(self) -> Types.RESULTS:
        """
        Getter for results property
        :return:
        """
        return self._results

    @results.setter
    def results(self, results: Types.RESULTS) -> None:
        self._results: Types.RESULTS = results
