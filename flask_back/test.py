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
    total_weight = sum(weight for _, _, weight in mst_edges)
    print("hugo :", total_weight)
    return mst_edges

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

import json
import networkx as nx

acpm_edges = kruskal_metro()

def verifier_connexite_et_completude(acpm_edges, nodes_path="C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\nodes.json"):
    def simplify(name):
        return name.split("::")[0].strip().lower()
    
    # 1. Chargement des stations
    with open(nodes_path, "r", encoding="utf-8") as f:
        raw_nodes = json.load(f)
    
    # Ensemble des noms de stations (simplifiés)
    all_nodes = set(simplify(name) for name in raw_nodes.keys())

    # 2. Création du graphe à partir des arêtes ACPM
    G = nx.Graph()
    for u, v, _ in acpm_edges:
        G.add_edge(u, v)

    # 3. Vérification de la connexité
    is_connected = nx.is_connected(G)

    # 4. Vérification de la couverture complète des nœuds
    graph_nodes = set(G.nodes)
    missing_nodes = all_nodes - graph_nodes
    extra_nodes = graph_nodes - all_nodes

    all_present = len(missing_nodes) == 0

    # 5. Résumé
    print("✅ Graphe connexe :", is_connected)
    print("✅ Tous les nœuds présents :", all_present)
    print(f"📦 Nœuds attendus : {len(all_nodes)} — Dans le graphe : {len(graph_nodes)}")
    if not all_present:
        print("❌ Nœuds manquants :", missing_nodes)
    if extra_nodes:
        print("⚠️ Nœuds non attendus dans le graphe :", extra_nodes)
    print("hugo ", len(all_nodes))
    return is_connected and all_present and len(all_nodes)


print(verifier_connexite_et_completude(kruskal_metro()))
