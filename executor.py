from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import Counter, deque
from typing import Optional

import tldextract

from graph import Graph
from scraper import Scraper


class Executor(ABC):
    def __init__(self, graph: Graph, scraper: Scraper, url: str) -> None:
        super().__init__()
        self.graph = graph
        self.scraper = scraper
        self.url = self.normalize_url(url)
        self.domain = self.extract_domain(url)
        self.visited_nodes = []

    async def run(self):
        await self._execute(self.url)

    def is_node_visited(self, url: str) -> bool:
        return url in self.visited_nodes

    @abstractmethod
    async def _execute(self, url: str):
        pass

    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        try:
            result = tldextract.extract(url)
            return result.domain
        except RuntimeError:
            return None

    @staticmethod
    def normalize_url(url: str) -> str:
        return url.strip('/')

    @staticmethod
    def types():
        return {
            RecursiveExecutor.TYPE: lambda: RecursiveExecutor,
            IterationExecutor.TYPE: lambda: IterationExecutor,
        }

    @staticmethod
    def build(_type: str, graph: Graph, scraper: Scraper, url: str) -> Executor:
        try:
            return Executor.types().get(_type)()(graph, scraper, url)
        except KeyError:
            raise Exception("Given Executor type is invalid!")


class RecursiveExecutor(Executor):
    TYPE = 'recursive-executor'

    async def _execute(self, url: str):
        url = self.normalize_url(url)

        self.graph.add_node(url)

        if self.is_node_visited(url):
            return

        self.visited_nodes.append(url)

        links = await self.scraper.scrape_url(url)
        edges = dict(Counter(map(lambda link: self.normalize_url(link), links)))

        self.graph.set_edges(url, edges)

        tasks = []
        for (edge_url, _) in edges.items():
            if self.extract_domain(edge_url) != self.domain:
                continue
            task = self._execute(edge_url)
            tasks.append(task)

        await asyncio.gather(*tasks)


class IterationExecutor(Executor):
    TYPE = 'iteration-executor'

    async def _execute(self, url: str):
        url = self.normalize_url(url)

        queue = deque([url])

        while queue:
            url = queue.pop()

            self.graph.add_node(url)

            if self.is_node_visited(url):
                continue

            self.visited_nodes.append(url)

            links = await self.scraper.scrape_url(url)
            edges = dict(Counter(map(lambda link: self.normalize_url(link), links)))

            self.graph.set_edges(url, edges)

            for (edge_url, _) in edges.items():
                if self.extract_domain(edge_url) != self.domain or self.is_node_visited(edge_url):
                    continue
                queue.append(edge_url)

# Should have producer and consumer like mechanism for parallelism
# class QueueExecutor(Executor):
#     TYPE = 'queue-executor'
#
#     async def _execute(self, url: str):
#         pass
