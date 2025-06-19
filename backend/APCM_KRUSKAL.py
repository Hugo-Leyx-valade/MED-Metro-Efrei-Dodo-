from collections import defaultdict

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        self.parent[ry] = rx
        return True

def parse_edges(file_path):
    id_to_name = {}
    edges = []

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('V;'):
                parts = line.split(';')
                station_id = int(parts[1])
                station_name = ' '.join(p for p in parts[2:5] if p)
                id_to_name[station_id] = station_name
            elif line.startswith('E;'):
                parts = line.split(';')
                a = int(parts[1])
                b = int(parts[2])
                weight = int(parts[3])
                edges.append((weight, a, b))

    return edges, id_to_name

def kruskal_mst(edges, id_to_name):
    n = max(max(a, b) for _, a, b in edges) + 1
    uf = UnionFind(n)

    mst = []
    total_weight = 0

    for weight, a, b in sorted(edges):
        if uf.union(a, b):
            mst.append((a, b, weight))
            total_weight += weight

    return mst, total_weight

# Utilisation
file_path = "C:\\Users\\Hugo\\Documents\\Projet\\MED-Metro-Efrei-Dodo-\\backend\\data\\version 1\\output.txt"
edges, id_to_name = parse_edges(file_path)
mst, total_weight = kruskal_mst(edges, id_to_name)

print(f"Poids total de l’APCM (KRUSKAL) : {total_weight}")
print("Arêtes sélectionnées :")
for a, b, w in mst:
    nom_a = id_to_name.get(a, f"#{a}")
    nom_b = id_to_name.get(b, f"#{b}")
    print(f"{nom_a} <-> {nom_b} (poids {w})")
