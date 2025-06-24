import json

def charger_json_edges():
    with open("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\edges.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def charger_json_nodes():
    with open("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\nodes.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def ajouter_correspondances(nodes, edges, poids_correspondance=90):
    correspondances = []

    # Crée un dictionnaire : nom -> liste des id ligne (ex: "Place d'Italie" -> ["Place d'Italie::6", "Place d'Italie::7"])
    noms_to_ids = {}
    for node_id, infos in nodes.items():
        nom = infos["nom"]
        noms_to_ids.setdefault(nom, []).append(node_id)

    # Pour chaque station ayant plusieurs lignes, ajouter des correspondances
    for node_ids in noms_to_ids.values():
        if len(node_ids) > 1:
            for i in range(len(node_ids)):
                for j in range(i + 1, len(node_ids)):
                    correspondances.append({
                        "node0": node_ids[i],
                        "node1": node_ids[j],
                        "weight": poids_correspondance
                    })

    return edges + correspondances

def api_shortest_pathV2(start_id, end_id):
    print(f"Recherche du chemin le plus court de {start_id} à {end_id}")
    
    nodes = charger_json_nodes()
    edges = charger_json_edges()

    # Ajouter les correspondances interlignes
    edges = ajouter_correspondances(nodes, edges)

    result = dijkstra_shortest_path(start_id, end_id, nodes, edges)

    for id in result["path"]:
        station = nodes.get(id)
        if station:
            print(f"{station['nom']} | Lignes: {', '.join(station['lignes'])}")
        else:
            print(f"[⚠] Station inconnue pour ID: {id}")

    return result



import heapq
def dijkstra_shortest_path(start_id, end_id, nodes, edges):
    # Construire le graphe sous forme de dictionnaire d'adjacence
    graph = {}
    for edge in edges:
        node0 = edge["node0"]
        node1 = edge["node1"]
        weight = edge["weight"]

        if node0 not in graph:
            graph[node0] = []
        if node1 not in graph:
            graph[node1] = []

        graph[node0].append((node1, weight))
        graph[node1].append((node0, weight))  # Graphe non orienté

    # Initialisation des distances et du tas de priorité
    distances = {node: float('inf') for node in nodes}
    previous_nodes = {node: None for node in nodes}
    distances[start_id] = 0
    queue = [(0, start_id)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == end_id:
            break

        if current_node not in graph:
            continue

        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Reconstruction du chemin
    path = []
    current = end_id
    while current is not None:
        path.insert(0, current)
        current = previous_nodes[current]

    # Vérification que le chemin est possible
    if not path or path[0] != start_id:
        return {"path": [], "total_weight": float('inf')}

    return {
        "path": path,
        "total_weight": distances[end_id]
    }

print(api_shortest_pathV2("Villejuif Léo Lagrange::7", "Charles de Gaulle - Etoile::1"))  # Exemple d'appel