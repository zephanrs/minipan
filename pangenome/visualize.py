# visualize.py
import graphviz
import matplotlib.pyplot as plt
from .graph import Graph
from .seed import Seed

def _palette(n: int):
  cmap = plt.get_cmap("tab10")
  return [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
          for r, g, b, _ in (cmap(i) for i in range(n))]

def create_graph(graph: Graph, name: str):
  dot = graphviz.Digraph(filename=name, engine='dot', format='png')
  dot.attr(rankdir='LR', nodesep='0.5', ranksep='0.8')
  dot.attr('node', shape='box', fontname='Helvetica',
           style='filled', fillcolor='white')
  dot.attr(dpi='300')

  # graph nodes
  for id, seq in graph.nodes.items():
    label = seq if len(seq) < 10 else f"{seq[:7]}..."
    dot.node(id, label=label)

  # graph edges
  for src, dsts in graph.edges.items():
    for dst in dsts:
      srcp = "w" if src.rev else "e"
      dstp = "e" if dst.rev else "w"
      dot.edge(f"{src.node}:{srcp}", f"{dst.node}:{dstp}", color="black")

  return dot

def graph2png(graph: Graph, name: str, view: bool = False):
  dot = create_graph(graph, name)
  dot.render(cleanup=True, view=view)

def draw_seeds(dot, graph, query, seeds, k, draw_links):
  colors = _palette(min(8, len(seeds)))

  # highlight seeds inside node labels
  node_spans = {}
  for color, seed in zip(colors, seeds[:8]):
    node_spans.setdefault(seed.node, []).append((seed.npos, seed.npos + k, color))

  for node, spans in node_spans.items():
    seq = graph.nodes[node]
    chars = list(seq)
    for a, b, color in spans:
      for i in range(a, b):
        chars[i] = f'<U><FONT COLOR="{color}">{chars[i]}</FONT></U>'
    dot.node(node, label=f'<<FONT FACE="Helvetica">{"".join(chars)}</FONT>>')

  # underline query kmers
  q = list(query)
  for color, seed in zip(colors, seeds[:8]):
    for i in range(seed.qpos, seed.qpos + k):
      q[i] = f'<U><FONT COLOR="{color}">{q[i]}</FONT></U>'

  # query node (bigger font, centered table)
  dot.node(
    "query",
    label=(
      '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="0">'
      f'<TR><TD><FONT FACE="Helvetica" POINT-SIZE="20">{"".join(q)}</FONT></TD></TR>'
      '</TABLE>>'
    ),
    shape="plaintext"
  )

  # force query below graph
  with dot.subgraph() as s:
    s.attr(rank="sink")
    s.node("query")

  if draw_links:
    for color, seed in zip(colors, seeds[:8]):
      dot.edge("query", seed.node, color=color, penwidth="2")

def seeds2png(graph: Graph, query: str, seeds: list[Seed],
              k: int, name: str, view=False):
  dot = create_graph(graph, name)
  draw_seeds(dot, graph, query, seeds, k, draw_links=False)
  dot.render(cleanup=True, view=view)

def chain2png(graph: Graph, query: str, chain: list[Seed],
              k: int, name: str, view=False):
  dot = create_graph(graph, name)
  draw_seeds(dot, graph, query, chain, k, draw_links=True)
  dot.render(cleanup=True, view=view)
