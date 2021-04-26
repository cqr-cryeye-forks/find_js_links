#!/usr/bin/env python

"""
Entrypoint to script.
The main goal of the script to gather js links
from set of urls.
It uses BeautifulSoup to extract links from html
"""

import sys
import json
import logging

import asyncio
import argparse

from time import time
from typing import NamedTuple, Iterator

from utils.constants import Config, Types
from utils.link_scraper_facade import LinkScraperFacade
from utils.logger_formatter import OneLineExceptionFormatter


class RunConfig(NamedTuple):
    """
    Run Config for script args
    """
    verbose: bool = Config.DEFAULT_DEBUGGING
    output: str = Config.RESULT_FILE_NAME


def write_results_to_file(results: Types.ASYNCIO_GATHER) -> None:
    """
    Method to save results in json into a file
    :param results:
    """
    with open(Config.RESULT_FILE_NAME, 'w') as file:
        file.write(to_json_serializable(results))
    logging.log(logging.DEBUG, f'Wrote results to file with name: {Config.RESULT_FILE_NAME}')


def to_json_serializable(results: Types.ASYNCIO_GATHER) -> Types.JSON_RESULTS:
    """
    Method to make results json serializable and reverse results
    :param results: Types.ASYNCIO_GATHER - results
    :return: Types.JSON_RESULTS - results in json
    """
    for index, result in enumerate(results):
        for i, r in result.items():
            if type(r) == set:
                results[index][i] = list(r)
            if i == 'body':
                results[index][i] = ''
    return json.dumps(results[::-1])


def define_config_from_cmd(parsed_args: 'argparse.Namespace') -> RunConfig:
    """
    parsing config from args
    :param parsed_args: argparse.Namespace
    :return: RunConfig
    """
    return RunConfig(
        verbose=parsed_args.verbose,
        output=parsed_args.output,
    )


def cli() -> argparse.Namespace:
    """
    here we define args to run the script with
    :return: argparse.Namespace
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='scan list of urls')
    # Add the arguments to the parser
    parser.add_argument('-v', '--verbose', action='store_true', default=Config.DEFAULT_DEBUGGING,
                        required=False, help='Verbose debug messages')
    parser.add_argument('-o', '--output', type=str, default=Config.RESULT_FILE_NAME,
                        required=False, help='Output file name')

    return parser.parse_args()


def get_input() -> Iterator[str]:
    """
    Get input from stdin
    :return: Iterator[str] - line by line
    """
    # if not select.select([sys.stdin, ], [], [], 0.0)[0]:
    #     raise ValueError('stdin can\'t be empty')
    return map(lambda u: u.strip('\n'), sys.stdin.readlines())


async def main() -> None:
    """
    Entrypoint to run program
    """
    args: argparse.Namespace = cli()
    config: RunConfig = define_config_from_cmd(args)

    OneLineExceptionFormatter.logger_initialisation(config.verbose)
    logging.log(logging.DEBUG, 'Main Started')

    urls: Iterator[str] = get_input()

    results: Types.RESULTS = await LinkScraperFacade.get_js_files(urls=urls)
    write_results_to_file(results)


if __name__ == '__main__':
    try:
        start_time = time()
        asyncio.run(main(), debug=Config.DEFAULT_DEBUGGING)
        logging.log(logging.DEBUG, f'Time consumption: {time() - start_time: 0.3f}s')
    except Exception as error:
        logging.exception(f'Failed with: {error}')
