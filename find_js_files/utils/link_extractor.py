"""
Link Extractor module
extracts links from html

uses BeautifulSoup to perform this operation
"""

from bs4 import BeautifulSoup

from .constants import Types


def extract_links_with_beautiful_soup(objects: Types.RESULTS) -> None:
    """
    Private method to extract links from html with help of BeautifulSoup
    :return: List[Dict[str, Union[str, List[str], Set[str]]]]
    """
    for index, result in enumerate(objects):
        soup = BeautifulSoup(markup=result['body'], features='lxml')
        href_tags = soup.find_all(href=True)
        objects[index].update({'js_links': {tag.get('href') for tag in href_tags}})
