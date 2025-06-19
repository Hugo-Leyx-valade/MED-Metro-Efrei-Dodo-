import heapq
from collections import defaultdict

def parse_edges(file_path):
    edges = []
    graph = defaultdict(list)
    
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith("E;"):
                parts = line.strip().split(";")
                u = int(parts[1])
                v = int(parts[2])
                w = int(parts[3])
                edges.append((u, v, w))
                graph[u].append((v, w))
                graph[v].append((u, w))  # non orienté

    return graph

def prim(graph):
    visited = set()
    total_weight = 0
    mst_edges = []

    # Commencer depuis un sommet quelconque
    start = next(iter(graph))
    min_heap = [(0, start, None)]  # (poids, sommet_courant, sommet_parent)

    while min_heap and len(visited) < len(graph):
        weight, u, parent = heapq.heappop(min_heap)
        if u in visited:
            continue
        visited.add(u)
        if parent is not None:
            mst_edges.append((parent, u, weight))
            total_weight += weight
        for neighbor, w in graph[u]:
            if neighbor not in visited:
                heapq.heappush(min_heap, (w, neighbor, u))

    return total_weight, mst_edges

# Exemple d’utilisation
file_path = "C:\\Users\\Hugo\\Documents\\Projet\\MED-Metro-Efrei-Dodo-\\backend\\data\\version 1\\output.txt"
graph = parse_edges(file_path)
total, edges = prim(graph)

print(f"Poids total de l’APCM (Prim) : {total}")
print("Arêtes sélectionnées :")
for u, v, w in edges:
    print(f"{u} <-> {v} (poids {w})")
