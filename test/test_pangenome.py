import os
from pangenome.graph import gfa2graph
from pangenome.seed import Seeder
from pangenome.filter import Filterer
from pangenome.align import Aligner
from pangenome.visualize import graph2png, alignment_strings
from pangenome.pangenome import add_alignment 

# 1. dummy gfa file
gfa_content = """H\tVN:Z:1.0
S\t1\tGATTACATCCAGT
"""
with open("data.gfa", "w") as f:
    f.write(gfa_content)

# 2. load and visualize before
graph = gfa2graph("data.gfa")
print(f"Graph loaded: {len(graph.nodes)} node(s).")
graph2png(graph, "graph_before")

# 3. define query
query = "GATTAAGCCAGT"
k, w, reward = 3, 5, 10

print(f"Query: {query}")

# 4. run through seed-filter-align
seeder = Seeder(graph, k=k, w=w)
seeds = seeder.seed(query)
print(f"Found {len(seeds)} seeds.")

filterer = Filterer(graph, type="max", reward=reward, dists={})
chain = filterer.filter(seeds)
print(f"Chain length: {len(chain)}")

aligner = Aligner(graph)
edits = aligner.align(query, chain)
print(f"Edits: {''.join(e.op for e in edits)}")

# 5. visualize alignment
q_aln, r_aln = alignment_strings(graph, query, edits)
print("query:     ", q_aln)
print("reference: ", r_aln)

# 6. add alignment
graph = add_alignment(graph, query, edits, "read1")

# 7. visualize after
print(f"Graph updated: {len(graph.nodes)} nodes.")
graph2png(graph, "graph_after")

# 8. cleanup
if os.path.exists("data.gfa"):
    os.remove("data.gfa")