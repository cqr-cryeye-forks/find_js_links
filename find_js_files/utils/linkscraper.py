#!/usr/bin/env python

from os.path import splitext
from typing import Set, Tuple, Iterator

from urllib.parse import urlparse
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from .constants import Types
from .request_manager import RequestManager


@dataclass
class LinkScraper:
    _urls: Set[str]
    _root_url: str
    _request_manager: RequestManager
    _results: Types.RESULTS = field(default_factory=list)
    _include_extensions: Tuple[str] = ('.js',)
    _exclude_extensions: Tuple[str] = (
        '.css', '.png', '.jpeg', '.jpg', '.svg', '.gif',
        '.wolf', '.woff', '.woff2', '.eot', '.ttf', '.ico',
    )

    def __init__(self, urls: Iterator[str]) -> None:
        self.urls: Iterator[str] = urls
        self._root_url: str = self._get_root_url_from_links

    @classmethod
    async def get_js_files(cls, urls: Iterator[str]) -> Types.RESULTS:
        obj = cls(urls)
        await obj._get_results()
        obj._extract_js_links()
        return obj.results

    async def _get_results(self) -> None:
        self._clean_from_unwanted_extensions()
        await self._get_html()

    def _clean_results(self) -> None:
        self._clean_from_empty()
        self._set_all_common_js_links()
        self._clean_js_links_from_common()

    def _clean_from_empty(self) -> None:
        self.results: Types.RESULTS = [u for u in self.results if u['js_links']]

    def _set_all_common_js_links(self) -> None:
        if self.results:
            self.results.append({'url': 'root', 'js_links': self._get_intersection_js_links})

    def _clean_js_links_from_common(self) -> None:
        root_index = self._get_root_index
        for index, result in enumerate(self.results):
            if result['url'] == 'root':
                continue
            self.results[index]['js_links']: Set[str] = self._get_difference_js_links(result['js_links'], root_index)

    def _get_difference_js_links(self, js_links: Set[str], root_index: int) -> Set[str]:
        return js_links.difference(self.results[root_index]['js_links'])

    def _extract_js_links(self) -> None:
        self._extract_from_html()
        self._add_root_url_if_needed()
        self._clean_results()

    def _extract_from_html(self) -> None:
        for index, result in enumerate(self.results):
            soup = BeautifulSoup(markup=result['body'], features='lxml')
            href_tags = soup.find_all(href=True)
            self.results[index].update({'js_links': self._left_only_needle({tag.get('href') for tag in href_tags})})

    def _clean_from_unwanted_extensions(self) -> None:
        self.urls: Set[str] = set(
            filter(lambda u: splitext(urlparse(u).path)[1] not in self.exclude_extensions, self.urls))

    def _left_only_needle(self, urls: Set[str]) -> Set[str]:
        return set(filter(lambda u: splitext(urlparse(u).path)[1] in self.include_extensions, urls))

    async def _get_html(self) -> None:
        self.results: Types.ASYNCIO_GATHER = await RequestManager.create_make_requests(urls=self.urls)

    def _add_root_url_if_needed(self) -> None:
        for index, result in enumerate(self.results):
            self.results[index]['js_links']: Set[str] = {
                f'{self.root_url}/{url.lstrip("/")}'
                for url in result['js_links']
                if self.root_url not in url
            }

    def _js_links_without_root_and_current(self) -> Iterator[str]:
        return map(lambda v: v['js_links'], filter(lambda v: v['url'] != 'root', self.results))

    @property
    def _get_root_index(self) -> int:
        return next(iter(index for index, result in enumerate(self.results) if result['url'] == 'root'), None)

    @property
    def _get_intersection_js_links(self) -> Set[str]:
        return set.intersection(*self._all_js_links)

    @property
    def _get_root_url_from_links(self) -> str:
        parsed_url = urlparse(url=next(iter(self.urls)))
        return f'{parsed_url.scheme}//{parsed_url.netloc}'

    @property
    def _all_js_links(self) -> Iterator[str]:
        return map(lambda v: v['js_links'], self.results)

    @property
    def urls(self) -> Set[str]:
        return self._urls

    @urls.setter
    def urls(self, value: Iterator[str]) -> None:
        self._urls: Set[str] = set(value)

    @property
    def results(self) -> Types.RESULTS:
        return self._results

    @results.setter
    def results(self, value: Types.RESULTS) -> None:
        self._results: Types.RESULTS = value

    @property
    def root_url(self) -> str:
        return self._root_url

    @property
    def request_manager(self) -> RequestManager:
        return self._request_manager

    @request_manager.setter
    def request_manager(self, value: RequestManager) -> None:
        self._request_manager: RequestManager = value

    @property
    def include_extensions(self) -> Tuple[str]:
        return self._include_extensions

    @property
    def exclude_extensions(self) -> Tuple[str]:
        return self._exclude_extensions
