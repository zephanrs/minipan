import os
from pangenome.graph import gfa2graph
from pangenome.seed import Seeder
from pangenome.filter import Filterer
from pangenome.visualize import graph2png, seeds2png, chain2png

# load graph
gfa_path = os.path.join(os.path.dirname(__file__), "data.gfa")
graph = gfa2graph(gfa_path)
print(f"Graph loaded: {len(graph.nodes)} nodes.")

query = "ACGTACGTACGT"
k = 3
w = 5
reward = 10

# build seeder + generate seeds
seeder = Seeder(graph, k=k, w=w)
seeds = seeder.seed(query)
print(f"Found {len(seeds)} seeds.")

# build filterer + generate filter
filterer = Filterer(graph, type="max", reward=reward, dists={})
chain = filterer.filter(seeds)
print(f"Found a chain of {len(chain)} seeds.")

# plain graph
graph2png(graph, "graph")

# 1. seeds
seeds2png(graph, query, seeds, k, "seeds")

# 2. filtered seeds
chain2png(graph, query, chain, k, "chain")

# 3. alignment