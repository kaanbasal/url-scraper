from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

import networkx as nx


class Graph(ABC):

    @abstractmethod
    def has_node(self, url: str) -> bool:
        pass

    @abstractmethod
    def add_node(self, url: str) -> bool:
        pass

    @abstractmethod
    def set_edges(self, url: str, edges: Dict[str, int]) -> bool:
        pass

    @abstractmethod
    def as_dict(self) -> Dict[str, Dict[str, int]]:
        pass

    @abstractmethod
    def all_nodes(self) -> List[str]:
        pass

    @staticmethod
    def types():
        return {
            DictGraph.TYPE: lambda: DictGraph(),
            NetworkXGraph.TYPE: lambda: NetworkXGraph(),
        }

    @staticmethod
    def build(_type: str) -> Graph:
        try:
            return Graph.types().get(_type)()
        except KeyError:
            raise Exception("Given Graph type is invalid!")


class DictGraph(Graph):
    TYPE = 'dict-graph'

    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[str, Dict[str, int]] = {}

    def has_node(self, url: str) -> bool:
        return True if url in self.nodes else False

    def add_node(self, url: str) -> bool:
        if self.has_node(url):
            return False

        self.nodes[url] = {}
        return True

    def set_edges(self, url: str, edges: Dict[str, int]) -> bool:
        if not self.has_node(url):
            return False

        self.nodes[url] = edges

        for (edge, _) in edges.items():
            self.add_node(edge)

        return True

    def as_dict(self) -> Dict[str, Dict[str, int]]:
        return self.nodes

    def all_nodes(self) -> List[str]:
        return list(self.nodes.keys())


class NetworkXGraph(Graph):
    TYPE = 'networkx-graph'

    def __init__(self) -> None:
        super().__init__()
        self.graph = nx.Graph()

    def has_node(self, url: str) -> bool:
        return True if url in self.graph.nodes else False

    def add_node(self, url: str) -> bool:
        if self.has_node(url):
            return False

        self.graph.add_node(url)

        return True

    def set_edges(self, url: str, edges: Dict[str, int]) -> bool:
        if not self.has_node(url):
            return False

        for (edge, weight) in edges.items():
            self.graph.add_edge(url, edge, weight=weight)

        return True

    def as_dict(self) -> Dict[str, Dict[str, int]]:
        return dict(self.graph.nodes(data="weight", default=1))

    def all_nodes(self) -> List[str]:
        return list(self.graph.nodes())
