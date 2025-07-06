from collections import defaultdict
import heapq

def parse_stations(file_path):
    id_to_name = {}
    name_to_ids = defaultdict(list)

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("V;"):
                continue
            line = line.split("#")[0].strip()  # Ignore commentaires
            parts = line.split(";")
            if len(parts) >= 3:
                station_id = int(parts[1])
                station_name = ' '.join(p for p in parts[2:5] if p).strip()
                id_to_name[station_id] = station_name
                name_to_ids[station_name].append(station_id)

    return id_to_name, name_to_ids

def parse_graph(file_path):
    graph = defaultdict(list)

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("E;"):
                continue
            line = line.split("#")[0].strip()  # Ignore commentaires
            parts = line.split(";")
            if len(parts) >= 4:
                u = int(parts[1])
                v = int(parts[2])
                w = int(parts[3].split()[0])  # Ignore texte après le poids
                graph[u].append((v, w))
                graph[v].append((u, w))  # graphe non orienté

    return graph

def dijkstra(graph, start_id):
    distances = {node: float('inf') for node in graph}
    distances[start_id] = 0
    parent = {start_id: None}
    heap = [(0, start_id)]

    while heap:
        dist_u, u = heapq.heappop(heap)
        if dist_u > distances[u]:
            continue
        for v, weight in graph[u]:
            alt = dist_u + weight
            if alt < distances[v]:
                distances[v] = alt
                parent[v] = u
                heapq.heappush(heap, (alt, v))

    return distances, parent

def get_shortest_path(start_name, end_name, file_path):
    id_to_name, name_to_ids = parse_stations(file_path)
    graph = parse_graph(file_path)

    # Cherche tous les ID dont le nom commence par start_name ou end_name
    start_ids = [id for name, ids in name_to_ids.items() if name.startswith(start_name) for id in ids]
    end_ids = [id for name, ids in name_to_ids.items() if name.startswith(end_name) for id in ids]

    if not start_ids or not end_ids:
        print(f"⚠️ Station introuvable : '{start_name}' ou '{end_name}'")
        return

    best_path = None
    best_cost = float('inf')

    for start_id in start_ids:
        distances, parent = dijkstra(graph, start_id)
        for end_id in end_ids:
            if distances[end_id] < best_cost:
                best_cost = distances[end_id]
                path = []
                current = end_id
                while current is not None:
                    path.append(current)
                    current = parent.get(current)
                path.reverse()
                best_path = path

    if best_path:
        print(f"\nPlus court chemin de '{start_name}' à '{end_name}' ({best_cost} sec):")
        for station_id in best_path:
            print(f"- {id_to_name[station_id]} ({station_id})")
    else:
        print("Aucun chemin trouvé.")

# Exemple d'utilisation
if __name__ == "__main__":
    chemin_fichier = "../data/version 1/output.txt"  # Remplacez par le chemin réel de votre fichier

    get_shortest_path("Saint-Lazare", "Villejuif, Louis Aragon", chemin_fichier)


