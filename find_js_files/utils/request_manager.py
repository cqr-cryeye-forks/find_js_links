"""
Request manager module
"""

import asyncio
import logging

from yarl import URL
from dataclasses import dataclass, field
from typing import Union, Dict, List, Set

from asyncio import BoundedSemaphore
# noinspection PyCompatibility
from asyncio.exceptions import TimeoutError

from aiohttp import ClientSession, ClientTimeout, InvalidURL, \
    ClientConnectorError, ClientResponseError, ServerTimeoutError, \
    TCPConnector, ServerDisconnectedError, ClientOSError

from .constants import Config, Types


@dataclass
class RequestManager:
    """
    Request Manager to make request to targets urls
    """
    _urls: List[URL]
    _timeout: ClientTimeout
    _session: ClientSession
    _semaphore: BoundedSemaphore
    _failed_requests_num: int = field(default=0)

    # _headers: Dict[str, str] = field(default_factory={'User-agent': Config.USER_AGENT})

    def __init__(self, urls: Set[str], timeout: int = Config.TIMEOUT_DEFAULT):
        self._urls: List[URL] = [URL(url) for url in urls]
        self._timeout: ClientTimeout = ClientTimeout(total=timeout)
        self._session: ClientSession = ClientSession(timeout=self.timeout, connector=TCPConnector(ssl=False))
        self._semaphore: asyncio.BoundedSemaphore = asyncio.BoundedSemaphore(Config.SIMULTANEOUS_CONCURRENT_TASKS)
        self._headers: Dict[str, str] = {'User-agent': Config.USER_AGENT}

    @classmethod
    async def create_make_requests(cls, urls: Set[str], timeout: int = Config.TIMEOUT_DEFAULT) -> Types.ASYNCIO_GATHER:
        """
        Class method to make requests
        :param urls: - Set[str] - set of urls
        :param timeout: int
        :return: Types.ASYNCIO_GATHER - request of the requests
        """
        obj: RequestManager = cls(urls=urls, timeout=timeout)
        logging.log(logging.DEBUG, f'{obj.__class__} created')
        results = await obj.make_requests()
        logging.log(logging.DEBUG, f'Number failed results: {obj.failed_requests_num}')
        return results

    async def _fetch(self, url: URL, session: ClientSession) -> Dict[str, Union[str, int]]:
        """
        Method to perform requests
        With retry functionality
        :return: Dict[str, Union[str, int]] - dictionary with results
        """
        logging.log(logging.DEBUG, f'Request to url: "{url}" stated')
        async with self.semaphore:
            result: Dict[str, Union[str, int]] = {
                'url': str(url), 'error': '', 'body': '',
                'status_code': Config.STATUS_CODE_DEFAULT,
            }
            left_of_attempts_to_retry: int = Config.LIMIT_OF_ATTEMPTS_TO_RETRY
            while left_of_attempts_to_retry:
                try:
                    async with session.get(url, headers=self.headers) as response:
                        result.update({
                            'status_code': response.status,
                            'body': await response.text(),
                        })
                except (
                        ClientConnectorError, ClientResponseError, ServerTimeoutError,
                        TimeoutError, InvalidURL, ServerDisconnectedError, ClientOSError,
                ) as e:
                    attempts = Config.LIMIT_OF_ATTEMPTS_TO_RETRY - left_of_attempts_to_retry + \
                               Config.REQUESTS_RETRIES_NUM_TO_REMOVE
                    logging.exception(f'Failed attempt num: {attempts} Error: {e}')
                    left_of_attempts_to_retry -= Config.REQUESTS_RETRIES_NUM_TO_REMOVE
                    self.failed_requests_num = Config.REQUESTS_RETRIES_NUM_TO_REMOVE
                    if not left_of_attempts_to_retry:
                        result.update({'error': e and str(e) or 'Something Went Wrong', })
                    else:
                        continue
                except UnicodeDecodeError:
                    break
                else:
                    logging.log(
                        logging.DEBUG,
                        f'Request to url: "{url}" succeed with possible retries: {left_of_attempts_to_retry}')
                    break
            return result

    async def make_requests(self) -> Types.ASYNCIO_GATHER:
        """
        Method to create coroutines with asyncio
        :return: Types.ASYNCIO_GATHER - request's coroutines
        """
        async with self.session as session:
            return await asyncio.gather(*[
                asyncio.create_task(
                    self._fetch(url=url, session=session)
                ) for url in self.urls
            ])

    @property
    def urls(self) -> List[URL]:
        """
        Getter for urls property
        :return: List[URL]
        """
        return self._urls

    @property
    def timeout(self) -> ClientTimeout:
        """
        Getter for timeout property for Client timeout
        :return: ClientTimeout
        """
        return self._timeout

    @property
    def session(self) -> ClientSession:
        """
        Getter for Client Session property
        :return: ClientSession
        """
        return self._session

    @property
    def semaphore(self) -> BoundedSemaphore:
        """
        Getter for BoundSemaphore property
        :return: BoundedSemaphore
        """
        return self._semaphore

    @property
    def headers(self) -> Dict[str, str]:
        """
        Getter for dictionary with headers
        :return: Dict[str, str]
        """
        return self._headers

    @property
    def failed_requests_num(self) -> int:
        """
        Getter for failed requests num
        How many times requests can fail
        before move to the next
        :return: int
        """
        return self._failed_requests_num

    @failed_requests_num.setter
    def failed_requests_num(self, num: int) -> None:
        self._failed_requests_num += num
