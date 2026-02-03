# filter.py
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from collections import defaultdict
from graph import Graph
from seed import Seed

@dataclass
class Filter:
  graph: Graph
  type: str # 'mean' or 'max'
  reward: int
  edges: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
  dists: Dict[str, int]

  def __post_init__(self):
    self.find_edges()
    self.linearize()

  def find_edges(self):
    for handle, neighbors in self.graph.edges.items():
      self.edges[handle.node].extend([neighbor.node for neighbor in neighbors])

  def linearize(self) -> None:
    topological = self.toposort()
    costs: defaultdict[str, list[int]] = defaultdict(list)
    for node in topological:
      if not costs[node]: costs[node].append(0) # in case no in-degree
      self.dists[node] = max(costs[node]) if self.type == 'max' else sum(costs[node]) // len(costs[node])
      for neighbor in self.edges[node]:
        costs[neighbor].append(self.dists[node] + len(self.graph.nodes[node]))
  
  def toposort(self) -> List[str]:
    sorted = []
    unvisited = [name for name in self.graph.nodes.keys()]
    visiting = set()

    def visit(node):
      if node in visiting:
        raise ValueError("Graph not a DAG")
      if node not in unvisited:
        return
      unvisited.remove(node)
      visiting.add(node)
      for neighbor in self.edges[node]:
        visit(neighbor)
      visiting.remove(node)
      sorted.insert(0, node)

    while unvisited:
      visit(unvisited[0])

    return sorted
  
  def filter(self, seeds: List[Seed]) -> List[Seed]:
    colinear = sorted([(seed.qpos, self.dists[seed.node] + seed.npos, seed) for seed in seeds])

    def diff(i : int, j : int):
      a = colinear[i]
      b = colinear[j]
      return abs(a[0] - b[0] - a[1] + b[1])

    # chain
    dp = [0] * len(colinear)
    tb = [0] * len(colinear)

    for i in range(len(seeds)):
      max_score = self.reward
      prev_seed = -1
      for j in range(i):
        score = self.reward + dp[j] - diff(i, j)
        if score > max_score:
          max_score = score
          prev_seed = j
      dp[i] = max_score
      tb[i] = prev_seed

    chain = []

    # traceback
    idx = dp.index(max(dp))
    while idx != -1:
      chain.insert(0, colinear[idx][2])
      idx = tb[idx]

    return chain
