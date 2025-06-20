from flask import Flask, jsonify, request
from flask_cors import CORS
import heapq
from collections import defaultdict

app = Flask(__name__)
CORS(app)


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/edges', methods=['GET'])
def to_graph_edges():
    """
    Converts a text file to a graph representation.
    """
    txt_file = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\output.txt"

    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    tab_arretes = []
    noeuds = {}
    for line in lines:
        parts = line.strip().split(';')
        arretes = {}
        noeuds = {}
        if len(parts) < 5:
            arretes["node0"] = parts[1]
            arretes["node1"]= parts[2]
            arretes["weight"] = parts[3]
            tab_arretes.append(arretes)
    f.close()
    return tab_arretes

def load_station_positions(file_path):
    station_positions = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(';')
            if len(parts) >= 3:
                x, y = parts[0], parts[1]
                station_name = ';'.join(parts[2:]).replace('@', ' ')
                station_positions[station_name] = {'x': x, 'y': y}
    return station_positions

@app.route('/api/nodes', methods=['GET'])
def to_graph_nodes():
    """
    Converts a text file to a graph representation.
    """
    txt_file_nodes = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\output.txt"
    txt_file_positions = "C:\\Users\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\pospoints.txt"  # Remplacez par le chemin réel

    station_positions = load_station_positions(txt_file_positions)

    with open(txt_file_nodes, 'r') as f:
        lines = f.readlines()

    tab_noeuds = []
    for line in lines:
        parts = line.strip().split(';')
        if len(parts) > 5:
            node = {
                "id": parts[1],
                "name": " ".join(parts[2:-5]),
                "line": parts[-4],
                "terminus": parts[-2],
                "branchement": parts[-1]
            }
            # Ajouter les coordonnées x et y si disponibles
            station_name = " ".join(parts[2:-5])
            if station_name in station_positions:
                node["x"] = station_positions[station_name]['x']
                node["y"] = station_positions[station_name]['y']
            else:
                node["x"] = None
                node["y"] = None
            tab_noeuds.append(node)
    f.close()
    return tab_noeuds


@app.route('/api/acpm', methods=['GET'])
def kruskal():
    stations = to_graph_nodes()  # Récupérer les noeuds
    connections = to_graph_edges()
    if connexity(stations, connections):
        # Nombre de noeuds
        n = len(stations)

        # Union-Find (Disjoint Set Union) structure pour détecter les cycles
        parent = [i for i in range(n)]
        rank = [0 for _ in range(n)]

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])  # Path compression
            return parent[u]

        def union(u, v):
            ru, rv = find(u), find(v)
            if ru == rv:
                return False  # déjà connectés
            # union par rang
            if rank[ru] < rank[rv]:
                parent[ru] = rv
            else:
                parent[rv] = ru
                if rank[ru] == rank[rv]:
                    rank[ru] += 1
            return True

        # Tri des connexions par poids croissant
        sorted_connections = sorted(connections, key=lambda c: int(c["weight"]))

        mst = []  # Arbre couvrant minimal (ACPM)
        total_weight = 0

        for conn in sorted_connections:
            u = int(conn["node0"])
            v = int(conn["node1"])
            w = int(conn["weight"])
            if union(u, v):
                mst.append(conn)
                total_weight += w
            # Stop si on a ajouté n - 1 arêtes
            if len(mst) == n - 1:
                break
        return {"mst": mst, "total_weight": total_weight}


def connexity(stations, connections):
    """
    Trouve le chemin le plus court entre deux stations.
    """
    edges = connections
    nodes = stations
    all_nodes = set()
    for edge in edges:
        all_nodes.add(edge["node0"])
        all_nodes.add(edge["node1"])
    print(len(all_nodes)== len(nodes))
    return len(all_nodes) == len(nodes)


def dijkstra_shortest_path(start_id, end_id, nodes, edges):
    import heapq

    # Conversion des IDs en int partout
    graph = {int(node["id"]): [] for node in nodes}
    for edge in edges:
        node0 = int(edge["node0"])
        node1 = int(edge["node1"])
        weight = int(edge["weight"])
        graph[node0].append((node1, weight))
        graph[node1].append((node0, weight))  # Si le graphe est non orienté

    # Initialisation
    distances = {int(node["id"]): float('inf') for node in nodes}
    previous = {int(node["id"]): None for node in nodes}
    start_id = int(start_id)
    end_id = int(end_id)
    distances[start_id] = 0
    queue = [(0, start_id)]

    while queue:
        current_dist, current_id = heapq.heappop(queue)
        if current_id == end_id:
            break
        for neighbor_id, weight in graph[current_id]:
            distance = current_dist + weight
            if distance < distances[neighbor_id]:
                distances[neighbor_id] = distance
                previous[neighbor_id] = current_id
                heapq.heappush(queue, (distance, neighbor_id))

    # Reconstruction du chemin
    path = []
    current = end_id
    while current is not None:
        path.insert(0, current)
        current = previous[current]
    if not path or path[0] != start_id:
        return {"path": [], "total_weight": float('inf')}
    return {"path": path, "total_weight": distances[end_id]}


@app.route('/api/path', methods=['GET'])
def api_shortest_path():
    print("triks")
    start_id = request.args.get('start_id')
    end_id = request.args.get('end_id')
    print(f"Recherche du chemin le plus court de {start_id} à {end_id}")
    nodes = to_graph_nodes()
    edges = to_graph_edges()
    
    result = dijkstra_shortest_path(start_id, end_id, nodes, edges)
    for id in result["path"]:
        print(nodes[int(id)]["name"])
    return result



if __name__ == '__main__':
    app.run(debug=True)
