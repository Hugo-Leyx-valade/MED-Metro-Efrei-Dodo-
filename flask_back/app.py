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
    start_id = request.args.get('start_id')
    end_id = request.args.get('end_id')
    print(f"Recherche du chemin le plus court de {start_id} à {end_id}")
    nodes = to_graph_nodes()
    edges = to_graph_edges()
    
    result = dijkstra_shortest_path(start_id, end_id, nodes, edges)
    for id in result["path"]:
        print(nodes[int(id)]["name"] + " and " + nodes[int(id)]["line"])
    return result



#================================= VERSION 2 =================================

import pandas as pd

# Dictionnaire de correspondance entre mode de transport et code GTFS
GTFS_ROUTE_TYPE = {
    "tram": 0,
    "metro": 1,
    "rer": 2,
    "bus": 3,
    "ferry": 4,
    "cablecar": 5,
    "funicular": 7,
}

def afficher_stations_par_ligne(gtfs_folder, nom_ligne, mode_transport):
    # Vérifie si le mode est valide
    route_type = GTFS_ROUTE_TYPE.get(mode_transport.lower())
    if route_type is None:
        print(f"Mode de transport invalide : {mode_transport}")
        print(f"Modes valides : {list(GTFS_ROUTE_TYPE.keys())}")
        return

    # Chargement des fichiers GTFS
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt")
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt")
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt")
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt")

    # Recherche des lignes correspondant au nom + type de transport
    lignes_trouvees = routes[
        (routes['route_short_name'].astype(str).str.lower() == nom_ligne.lower()) &
        (routes['route_type'] == route_type)
    ]

    if lignes_trouvees.empty:
        print(f"Aucune ligne trouvée pour '{nom_ligne}' avec le mode '{mode_transport}'")
        return

    for _, ligne in lignes_trouvees.iterrows():
        print(f"\nLigne trouvée : {ligne['route_short_name']} ({ligne['route_long_name']})")

        # Récupération des trips liés à la ligne
        trips_ligne = trips[trips['route_id'] == ligne['route_id']]

        # Récupération des stop_ids liés à ces trips
        stop_ids = stop_times[stop_times['trip_id'].isin(trips_ligne['trip_id'])]['stop_id'].unique()

        # Recherche des noms de stations
        stations = stations = (
            stops[stops['stop_id'].isin(stop_ids)][['stop_name', 'stop_id']]
            .groupby('stop_name')
            .first()
            .reset_index()
            .sort_values('stop_name')
        )


# Exemple d’appel :
#afficher_stations_par_ligne("backend/data", "7", "metro")


import pandas as pd
def charger_stations():
    gtfs_folder = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    stops = pd.read_csv(f"{gtfs_folder}stops.txt")
    stop_times = pd.read_csv(f"{gtfs_folder}stop_times.txt")
    trips = pd.read_csv(f"{gtfs_folder}trips.txt")
    routes = pd.read_csv(f"{gtfs_folder}routes.txt")

    # Filtrer les lignes métro
    routes_metro = routes[routes['route_type'] == 1]
    trips_metro = trips[trips['route_id'].isin(routes_metro['route_id'])]
    stop_times_metro = stop_times[stop_times['trip_id'].isin(trips_metro['trip_id'])]

    # Associer stop_id -> trip_id -> route_id -> route_short_name
    trip_route = trips_metro[['trip_id', 'route_id']].merge(
        routes_metro[['route_id', 'route_short_name']], on='route_id'
    )
    stop_trip_route = stop_times_metro[['stop_id', 'trip_id']].merge(trip_route, on='trip_id')

    # Regrouper lignes par stop_id
    stop_lignes = stop_trip_route.groupby('stop_id')['route_short_name'].unique()

    # Filtrer stops métro
    stops_metro = stops[stops['stop_id'].isin(stop_lignes.index)].copy()

    # Ajouter les lignes par stop_id
    stops_metro['lignes'] = stops_metro['stop_id'].map(lambda sid: sorted(list(stop_lignes.get(sid, []))))

    # Construire dictionnaire stations, clé = stop_id (unique)
    dico_stations = {}
    for _, row in stops_metro.iterrows():
        dico_stations[row['stop_id']] = {
            'nom': row['stop_name'],
            'lignes': row['lignes'],
            'latitude': row['stop_lat'],
            'longitude': row['stop_lon']
        }
    print(f"Nombre de stations trouvées : {len(dico_stations)}")
    return dico_stations

# Exemple d'utilisation



import pandas as pd

def compter_stations():
    # Chargement des fichiers
    gtfs_folder = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"  # Chemin vers le dossier GTFS
    stops = pd.read_csv(f"{gtfs_folder}stops.txt")
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt")
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt")
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt")

    # Total de stops
    total_stops = stops['stop_id'].nunique()

    # Filtrer les routes de type métro
    routes_metro = routes[routes['route_type'] == 1]
    trips_metro = trips[trips['route_id'].isin(routes_metro['route_id'])]
    stop_times_metro = stop_times[stop_times['trip_id'].isin(trips_metro['trip_id'])]

    # Stops utilisés par le métro
    metro_stop_ids = stop_times_metro['stop_id'].unique()
    metro_stops = stops[stops['stop_id'].isin(metro_stop_ids)]

    # Nombre de stop_id (arrêts) utilisés pour le métro
    nb_stops_metro = len(metro_stops)

    # Nombre de noms uniques (stations sans doublon de direction)
    nb_stations_metro_uniques = metro_stops['stop_name'].nunique()

    # Affichage
# Exemple d'utilisation
#compter_stations("backend/data")


import pandas as pd
import os
from collections import defaultdict

def recuperer_edges_metro_sans_doublons():
    gtfs_folder = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    stop_times = pd.read_csv(os.path.join(gtfs_folder, "stop_times.txt"))
    trips = pd.read_csv(os.path.join(gtfs_folder, "trips.txt"))
    routes = pd.read_csv(os.path.join(gtfs_folder, "routes.txt"))

    metro_routes = routes[routes['route_type'] == 1]['route_id'].unique()
    metro_trips = trips[trips['route_id'].isin(metro_routes)]

    stop_times = stop_times[stop_times['trip_id'].isin(metro_trips['trip_id'])]
    stop_times.sort_values(by=["trip_id", "stop_sequence"], inplace=True)

    edge_weights = defaultdict(list)

    for trip_id, group in stop_times.groupby("trip_id"):
        group = group.reset_index(drop=True)
        for i in range(len(group) - 1):
            current_stop = group.iloc[i]
            next_stop = group.iloc[i + 1]

            node_a = str(current_stop["stop_id"])
            node_b = str(next_stop["stop_id"])

            try:
                t0 = pd.to_timedelta(current_stop["departure_time"])
                t1 = pd.to_timedelta(next_stop["arrival_time"])
                weight = int((t1 - t0).total_seconds())
                if weight <= 0 or weight > 3600:
                    continue
            except:
                continue

            # Clé non orientée (min, max)
            key = tuple(sorted([node_a, node_b]))
            edge_weights[key].append(weight)

    # Construction finale (moyenne ou min pour chaque paire)
    edges = []
    for (node0, node1), weights in edge_weights.items():
        avg_weight = int(sum(weights) / len(weights))
        edges.append({
            "node0": node0,
            "node1": node1,
            "weight": avg_weight
        })
    return edges

import json
@app.route('/api/edgesV2', methods=['GET'])
def charger_json_edges():
    with open("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\edges.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

@app.route('/api/nodesV2', methods=['GET'])
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

@app.route('/api/pathV2', methods=['GET'])
def api_shortest_pathV2():
    start_id = request.args.get('start_id')
    end_id = request.args.get('end_id')
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


import pandas as pd
import json
import os

def charger_stations_unique():
    gtfs_folder = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    stops = pd.read_csv(os.path.join(gtfs_folder, "stops.txt"))
    stop_times = pd.read_csv(os.path.join(gtfs_folder, "stop_times.txt"))
    trips = pd.read_csv(os.path.join(gtfs_folder, "trips.txt"))
    routes = pd.read_csv(os.path.join(gtfs_folder, "routes.txt"))

    # Lignes de métro uniquement
    routes_metro = routes[routes['route_type'] == 1]
    trips_metro = trips[trips['route_id'].isin(routes_metro['route_id'])]
    stop_times_metro = stop_times[stop_times['trip_id'].isin(trips_metro['trip_id'])]

    # Associer stop_id → trip_id → route_id → nom ligne
    trip_route = trips_metro[['trip_id', 'route_id']].merge(
        routes_metro[['route_id', 'route_short_name']], on='route_id'
    )
    stop_trip_route = stop_times_metro[['stop_id', 'trip_id']].merge(trip_route, on='trip_id')
    stop_lignes = stop_trip_route.groupby('stop_id')['route_short_name'].unique()

    stops_metro = stops[stops['stop_id'].isin(stop_lignes.index)].copy()
    stops_metro['lignes'] = stops_metro['stop_id'].map(lambda sid: sorted(list(stop_lignes.get(sid, []))))

    # Clé d’unification : nom + ligne principale
    station_map = {}
    for _, row in stops_metro.iterrows():
        nom = row['stop_name'].strip()
        ligne_principale = row['lignes'][0] if row['lignes'] else 'unknown'
        unique_key = f"{nom}::{ligne_principale}"

        if unique_key not in station_map:
            station_map[unique_key] = {
                'nom': nom,
                'lignes': row['lignes'],
                'latitude': row['stop_lat'],
                'longitude': row['stop_lon'],
                'ids_originaux': [row['stop_id']]
            }
        else:
            station_map[unique_key]['ids_originaux'].append(row['stop_id'])

    # Sauvegarde en JSON
    output_path = os.path.join(gtfs_folder, "nodes.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(station_map, f, indent=2, ensure_ascii=False)

    print(f"{len(station_map)} stations uniques écrites dans nodes.json")
    return station_map


from collections import defaultdict
import json
import os
import pandas as pd

def recuperer_edges_metro_unifies():
    gtfs_folder = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"

    # Charger mapping des stations unifiées
    with open(os.path.join(gtfs_folder, "nodes.json"), encoding="utf-8") as f:
        stations_uniques = json.load(f)

    stopid_to_uniqueid = {}
    for unique_id, data in stations_uniques.items():
        for stop_id in data['ids_originaux']:
            stopid_to_uniqueid[stop_id] = unique_id

    stop_times = pd.read_csv(os.path.join(gtfs_folder, "stop_times.txt"))
    trips = pd.read_csv(os.path.join(gtfs_folder, "trips.txt"))
    routes = pd.read_csv(os.path.join(gtfs_folder, "routes.txt"))

    metro_routes = routes[routes['route_type'] == 1]['route_id'].unique()
    metro_trips = trips[trips['route_id'].isin(metro_routes)]
    stop_times = stop_times[stop_times['trip_id'].isin(metro_trips['trip_id'])]

    stop_times.sort_values(by=["trip_id", "stop_sequence"], inplace=True)
    edge_weights = defaultdict(list)

    for trip_id, group in stop_times.groupby("trip_id"):
        group = group.reset_index(drop=True)
        for i in range(len(group) - 1):
            stop_a = group.iloc[i]
            stop_b = group.iloc[i + 1]

            stop_id_a = stop_a["stop_id"]
            stop_id_b = stop_b["stop_id"]

            if stop_id_a not in stopid_to_uniqueid or stop_id_b not in stopid_to_uniqueid:
                continue

            node_a = stopid_to_uniqueid[stop_id_a]
            node_b = stopid_to_uniqueid[stop_id_b]

            if node_a == node_b:
                continue

            try:
                t0 = pd.to_timedelta(stop_a["departure_time"])
                t1 = pd.to_timedelta(stop_b["arrival_time"])
                weight = int((t1 - t0).total_seconds())
                if weight <= 0 or weight > 3600:
                    continue
            except:
                continue

            key = tuple(sorted([node_a, node_b]))
            edge_weights[key].append(weight)

    edges = []
    for (node0, node1), weights in edge_weights.items():
        avg_weight = int(sum(weights) / len(weights))
        edges.append({
            "node0": node0,
            "node1": node1,
            "weight": avg_weight
        })

    # Sauvegarde
    output_path = os.path.join(gtfs_folder, "edges.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(edges, f, indent=2, ensure_ascii=False)

    print(f"{len(edges)} connexions écrites dans edges.json")
    return edges


if __name__ == '__main__':
    app.run(debug=True)
