import asyncio
import logging

from yarl import URL
from dataclasses import dataclass, field
from typing import Union, Dict, List, Set

from asyncio import BoundedSemaphore
# noinspection PyCompatibility
from asyncio.exceptions import TimeoutError

from aiohttp import ClientSession, ClientTimeout, InvalidURL, \
    ClientConnectorError, ClientResponseError, ServerTimeoutError, TCPConnector

from .constants import Config, Types


@dataclass
class RequestManager:
    _urls: List[URL]
    _timeout: ClientTimeout
    _session: ClientSession
    _semaphore: BoundedSemaphore
    _headers: Dict[str, str]
    _failed_requests_num: int = field(default=0)

    def __init__(self, urls: Set[str], timeout: int = Config.TIMEOUT_DEFAULT):
        self._urls = [URL(url) for url in urls]
        self._timeout = ClientTimeout(total=timeout)
        self._session = ClientSession(timeout=self.timeout, connector=TCPConnector(ssl=False))
        self._semaphore = asyncio.BoundedSemaphore(Config.SIMULTANEOUS_CONCURRENT_TASKS)
        self._headers = {'User-agent': Config.USER_AGENT}

    @classmethod
    async def create_make_requests(cls, urls: Set[str], timeout: int = Config.TIMEOUT_DEFAULT) \
            -> Types.ASYNCIO_GATHER:

        obj: RequestManager = cls(urls=urls, timeout=timeout)
        logging.log(logging.DEBUG, f'{obj.__class__} created')
        results = await obj.make_requests()
        logging.log(logging.DEBUG, f'Number failed results: {obj.failed_requests_num}')
        return results

    async def _fetch(self, url: URL, session: ClientSession) -> Dict[str, Union[str, int]]:
        logging.log(logging.DEBUG, f'Request to url: "{url}" stated')
        async with self.semaphore:
            result: Dict[str, str] = {'url': str(url), 'error': '', 'body': '', }
            left_of_attempts_to_retry: int = Config.LIMIT_OF_ATTEMPTS_TO_RETRY
            while left_of_attempts_to_retry:
                try:
                    async with session.get(url, headers=self.headers) as response:
                        result.update({
                            'status_code': response.status,
                            'body': await response.text(),
                        })
                except (ClientConnectorError, ClientResponseError, ServerTimeoutError, TimeoutError, InvalidURL) as e:
                    attempts = Config.LIMIT_OF_ATTEMPTS_TO_RETRY - left_of_attempts_to_retry + \
                               Config.REQUESTS_RETRIES_NUM_TO_REMOVE
                    logging.exception(f'Failed attempt num: {attempts} Error: {e}')
                    left_of_attempts_to_retry -= Config.REQUESTS_RETRIES_NUM_TO_REMOVE
                    self.failed_requests_num = Config.REQUESTS_RETRIES_NUM_TO_REMOVE
                    if not left_of_attempts_to_retry:
                        result.update({
                            'status_code': Config.STATUS_CODE_DEFAULT,
                            'error': e and str(e) or 'Something Went Wrong',
                        })
                    else:
                        continue
                except UnicodeDecodeError:
                    continue
                else:
                    logging.log(
                        logging.DEBUG,
                        f'Request to url: "{url}" succeed with possible retries: {left_of_attempts_to_retry}')
                    break
            return result

    async def make_requests(self) -> Types.ASYNCIO_GATHER:
        async with self.session as session:
            return await asyncio.gather(*[
                asyncio.create_task(
                    self._fetch(url=url, session=session)
                ) for url in self.urls
            ])

    @property
    def urls(self) -> List[URL]:
        return self._urls

    @property
    def timeout(self) -> ClientTimeout:
        return self._timeout

    @property
    def session(self) -> ClientSession:
        return self._session

    @property
    def semaphore(self) -> BoundedSemaphore:
        return self._semaphore

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def failed_requests_num(self) -> int:
        return self._failed_requests_num

    @failed_requests_num.setter
    def failed_requests_num(self, num: int) -> None:
        self._failed_requests_num += num
