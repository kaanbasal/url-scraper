from __future__ import annotations

import asyncio
import re
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlparse, urlunparse, urljoin

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession, BaseParser


class Scraper(ABC):

    @abstractmethod
    async def scrape_url(self, url: str) -> List[str]:
        pass

    @staticmethod
    def types():
        return {
            RegexScraper.TYPE: lambda: RegexScraper(),
            BSoupScraper.TYPE: lambda: BSoupScraper(),
            RequestsScraper.TYPE: lambda: RequestsScraper(),
        }

    @staticmethod
    def build(_type: str) -> Scraper:
        try:
            return Scraper.types().get(_type)()
        except KeyError:
            raise Exception("Given Scraper type is invalid!")


class RegexScraper(Scraper):
    TYPE = 'regex'

    def __init__(self) -> None:
        super().__init__()

    async def scrape_url(self, url: str) -> List[str]:
        async with ClientSession(loop=asyncio.get_running_loop()) as client:
            result = await client.get(url)

            if not result.ok:
                return []

            try:
                content = await result.read()
                links = re.findall(r'href=[\'"]?([^\'" >]+)', str(content))
                links = list(filter(lambda link: not link.startswith(('javascript:', 'mailto:', '#')), links))

                return [urljoin(url, link) for link in links]
            except UnicodeDecodeError:
                return []


class BSoupScraper(Scraper):
    TYPE = 'beautifulsoup'

    async def scrape_url(self, url: str) -> List[str]:
        async with ClientSession(loop=asyncio.get_running_loop()) as client:
            result = await client.get(url)

            if not result.ok:
                return []

            try:
                content = await result.read()
                soup = BeautifulSoup(str(content), 'lxml')

                links = [link.get('href') for link in soup.findAll('a')]
                links = list(filter(lambda link: link is not None and not link.startswith(('javascript:', 'mailto:', '#')), links))

                return [urljoin(url, link) for link in links]
            except UnicodeDecodeError:
                return []


class RequestsScraper(Scraper):
    TYPE = 'requests'

    def __init__(self) -> None:
        super().__init__()
        self.session = AsyncHTMLSession(loop=asyncio.get_running_loop())

    async def scrape_url(self, url: str) -> List[str]:
        result = await self.session.get(url)

        if not result.ok:
            return []

        return self.__links(result.html)

    # @see requests_html.py BaseParser.__links
    # original code is returning set of links instead of sending all to calculate how many times it occurs
    @staticmethod
    def __links(parser: BaseParser) -> List[str]:
        def gen():
            for link in parser.find('a'):
                try:
                    href = link.attrs['href'].strip()
                    if href and not (href.startswith('#') and parser.skip_anchors) and not href.startswith(('javascript:', 'mailto:')):
                        yield href
                except KeyError:
                    pass

        # noinspection PyProtectedMember
        return list([parser._make_absolute(link) for link in gen()])
