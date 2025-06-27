import json

def kruskal_metro(nodes_path="C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\nodes.json", edges_path="C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\edges.json"):
    # Simplification des noms (on ignore ::ligne)
    def simplify(name):
        return name.split("::")[0].strip().lower()
    
    # Chargement
    with open(nodes_path, "r", encoding="utf-8") as f:
        raw_nodes = json.load(f)
    with open(edges_path, "r", encoding="utf-8") as f:
        raw_edges = json.load(f)

    # Liste des arêtes pondérées, simplifiées
    edges = []
    for edge in raw_edges:
        a, b = simplify(edge["node0"]), simplify(edge["node1"])
        w = edge["weight"]
        if a != b:  # éviter les boucles
            edges.append((w, a, b))

    # Kruskal : tri des arêtes par poids
    edges.sort()

    # Structure Union-Find
    parent = {}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]  # compression de chemin
            u = parent[u]
        return u

    def union(u, v):
        pu, pv = find(u), find(v)
        if pu == pv:
            return False
        parent[pu] = pv
        return True

    # Initialisation des composants
    all_nodes = set()
    for _, a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)
    for node in all_nodes:
        parent[node] = node

    # Kruskal : construction de l’ACPM
    mst_edges = []
    for weight, u, v in edges:
        if union(u, v):
            mst_edges.append((u, v, weight))

    return mst_edges

print(len(kruskal_metro()))


import json
import heapq
from collections import defaultdict

def prim_metro(nodes_path="C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\nodes.json", edges_path="C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\edges.json"):
    def simplify(name):
        return name.split("::")[0].strip().lower()

    # Chargement
    with open(nodes_path, "r", encoding="utf-8") as f:
        raw_nodes = json.load(f)
    with open(edges_path, "r", encoding="utf-8") as f:
        raw_edges = json.load(f)

    # Construire le graphe pondéré (dictionnaire d'adjacence)
    graph = defaultdict(list)
    for edge in raw_edges:
        a = simplify(edge["node0"])
        b = simplify(edge["node1"])
        w = edge["weight"]
        if a != b:
            graph[a].append((w, b))
            graph[b].append((w, a))

    # Initialisation
    start = next(iter(graph))  # n'importe quel sommet
    visited = set()
    min_heap = []
    mst_edges = []

    visited.add(start)
    for w, neighbor in graph[start]:
        heapq.heappush(min_heap, (w, start, neighbor))

    while min_heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(min_heap)
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, w))
            for weight, neighbor in graph[v]:
                if neighbor not in visited:
                    heapq.heappush(min_heap, (weight, v, neighbor))

    return mst_edges

print(len(prim_metro()))