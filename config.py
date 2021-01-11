from __future__ import annotations

import re
from typing import Dict, List

from attr import dataclass

from executor import Executor
from graph import Graph
from scraper import Scraper


@dataclass
class Config:
    url: str
    graph_type: str
    scraper_type: str
    executor_type: str

    # @see https://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python
    @staticmethod
    def is_valid_url(url: str) -> bool:
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        search = regex.search(url)
        return url is not None and url != '' and search is not None

    @staticmethod
    def questions() -> List[Dict]:
        return [
            {
                'type': 'input',
                'name': 'url',
                'message': 'URL to extract links',
                'validate': lambda url: Config.is_valid_url(url)
            },
            {
                'type': 'list',
                'name': 'graph',
                'message': 'Select Graph to use',
                'choices': Graph.types().keys()
            },
            {
                'type': 'list',
                'name': 'scraper',
                'message': 'Select Scraper to use',
                'choices': Scraper.types().keys()
            },
            {
                'type': 'list',
                'name': 'executor',
                'message': 'Select Executor to use',
                'choices': Executor.types().keys()
            },

        ]

    @staticmethod
    def build(answers: Dict) -> Config:
        return Config(
            url=answers['url'],
            graph_type=answers['graph'],
            scraper_type=answers['scraper'],
            executor_type=answers['executor']
        )
