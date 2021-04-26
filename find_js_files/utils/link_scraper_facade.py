"""
Link Scraper Facade Class
"""

from typing import Set, Iterator
from dataclasses import dataclass, field

from .constants import Types
from .request_manager import RequestManager
from .results_cleaner import ResultsCleaner
from .link_extractor import extract_links_with_beautiful_soup
from .cleaner import left_only_needle_extensions, clean_from_unwanted_extensions


@dataclass
class LinkScraperFacade:
    """
    Facade
    """
    _urls: Set[str]
    _results: Types.RESULTS = field(default_factory=list)

    @classmethod
    async def get_js_files(cls, urls: Iterator[str]) -> Types.RESULTS:
        """

        :param urls:
        :return:
        """
        obj = cls(set(urls))

        await obj._get_results()
        return obj._extract_js_links()

    async def _get_results(self) -> None:
        self.urls: Set[str] = clean_from_unwanted_extensions(self.urls)
        self.results: Types.ASYNCIO_GATHER = await RequestManager.create_make_requests(self.urls)

    def _extract_js_links(self) -> Types.RESULTS:
        extract_links_with_beautiful_soup(self.results)
        return self._clean_results()

    def _clean_results(self) -> Types.RESULTS:
        for index, result in enumerate(self.results):
            self.results[index]['js_links']: Set[str] = left_only_needle_extensions(result['js_links'])
        return ResultsCleaner.clean(self.results)

    @property
    def urls(self) -> Set[str]:
        """
        Getter for urls property
        :return: Set[str]
        """
        return self._urls

    @urls.setter
    def urls(self, value: Iterator[str]) -> None:
        self._urls: Set[str] = set(value)

    @property
    def results(self) -> Types.RESULTS:
        """
        Getter for results property
        :return:
        """
        return self._results

    @results.setter
    def results(self, value: Types.RESULTS) -> None:
        self._results: Types.RESULTS = value
