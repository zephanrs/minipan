# graph.py
from dataclasses import dataclass, field
from typing import List, Dict, Set
from collections import defaultdict

### Graph Construction

@dataclass(eq=True, frozen=True)
class Handle:
  node: str
  rev:  bool

@dataclass
class Graph:
  nodes: Dict[str, str] = field(default_factory=dict)
  edges: Dict[Handle, Set[Handle]] = field(default_factory=lambda: defaultdict(set))
  paths: Dict[str, List[Handle]] = field(default_factory=dict)

  def add_node(self, id: str, seq: str):
    self.nodes[id] = seq

  def add_edge(self, src: Handle, dst: Handle):
    self.edges[src].add(dst)

  def add_path(self, name: str, path: List[Handle]):
    self.paths[name] = path

### GFA Reading
def gfa2graph(file_path: str):
  graph = Graph()
  with open(file_path, 'r') as file:
    for line in file:
      line = line.rstrip()
      if line[0] in ['#', 'H'] or not line: continue
      components = line.split('\t')
      match components[0]:
        case "S": graph.add_node(components[1], components[2])
        
        case "L": graph.add_edge(
          Handle(components[1], (components[2] == '-')),
          Handle(components[3], (components[4] == '-'))
        )
        
        case "P": graph.add_path(
          components[1],
          [Handle(node[:-1], (node[-1] == '-')) for node in components[2].split(",")]
        )
        
        case _: raise ValueError("Unsupported")
    
  return graph

def graph2gfa(graph: Graph, file_path: str):
  with open(file_path, 'w') as file:
    file.write("H\tVN:Z:1.0\n")
    
    # nodes
    for node, seq in graph.nodes.items():
      file.write(f"S\t{node}\t{seq}\n")
    
    # edges
    for src, dsts in graph.edges.items():
      src_ori = '-' if src.rev else '+'
      for dst in dsts:
        dst_ori = '-' if dst.rev else '+'
        file.write(f"L\t{src.node}\t{src_ori}\t{dst.node}\t{dst_ori}\n")
    
    # paths
    for name, path in graph.paths.items():
      path_str = ",".join(f"{h.node}{'-' if h.rev else '+'}" for h in path)
      file.write(f"P\t{name}\t{path_str}\t*\n")