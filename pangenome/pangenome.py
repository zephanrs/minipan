# pangenome.py
from copy import deepcopy
from collections import defaultdict
from .graph import Graph, Handle
from .align import Edit

def add_alignment(graph: Graph, query: str, edits: list[Edit], name: str) -> Graph:
  g = deepcopy(graph)
  
  # cuts (breaking nodes)
  cuts = defaultdict(set)
  for e in edits: 
    if e.op != 'I': cuts[e.node].update({e.npos, e.npos+1})

  # map old handles to new handles
  remap = {}
  new_edges = defaultdict(set)

  for node, points in cuts.items():
    seq = g.nodes.pop(node)
    splits = sorted(list(points | {0, len(seq)}))
    frags = [Handle(f"{node}.{s}", False) for s in splits[:-1] if s < len(seq)]
    remap[Handle(node, False)] = frags
    
    for i, h in enumerate(frags):
      g.nodes[h.node] = seq[splits[i]:splits[i+1]]
      if i > 0: new_edges[frags[i-1]].add(h) # link fragments

  # redirect old edges to fragments
  for handle, dsts in g.edges.items():
    new_u = remap[handle][-1] if handle in remap else handle
    for node in dsts:
      new_node = remap[node][0] if node in remap else node
      new_edges[new_u].add(new_node)
  g.edges = new_edges

  # update paths
  for k, path in g.paths.items():
    g.paths[k] = [h for old in path for h in remap.get(old, [old])]

  path = []
  for e in edits:
    if e.op == 'M': path.append(Handle(f"{e.node}.{e.npos}", False))
    elif e.op in 'XI':
      new = Handle(f"new.{len(g.nodes)}", False)
      g.nodes[new.node] = query[e.qpos]
      path.append(new)
  
  for u, v in zip(path, path[1:]): g.add_edge(u, v)
  g.add_path(name, path)
  
  compress(g)
  return g

def compress(g: Graph):
  while True:
    # find mergeable u->v pairs (u has 1 out-degree, v has 1 in-degree)
    pairs = [(u, list(ds)[0]) for u, ds in g.edges.items() if len(ds) == 1]
    pairs = [(u, v) for u, v in pairs if u.node != v.node and 
             sum(1 for ds in g.edges.values() if v in ds) == 1]
    if not pairs: break
    
    u, v = pairs[0]
    new = Handle(f"{u.node}+{v.node}", False)
    g.nodes[new.node] = g.nodes.pop(u.node) + g.nodes.pop(v.node)
    
    # merge and update topology
    if v in g.edges: g.edges[new] = g.edges.pop(v)
    del g.edges[u]
    for ds in g.edges.values():
      if u in ds: ds.remove(u); ds.add(new)
    
    for p in g.paths.values():
      p[:] = [new if h == u else h for h in p if h != v]