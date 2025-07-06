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
    txt_file_positions = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\pospoints.txt"  # Remplacez par le chemin réel

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
        print(len(mst), total_weight)
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
    if test_connexite_reseau():
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
    else:
        print("Le réseau n'est pas connexe, impossible de trouver un chemin.")
        return {"path": [], "total_weight": float('inf')}


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


def test_connexite_reseau():
    # Charger les fichiers
    raw_nodes = charger_json_nodes()

    raw_edges = charger_json_edges()

    # Fonction pour extraire le nom sans ligne
    def simplify_name(full_name):
        return full_name.split("::")[0].strip().lower()

    # Construire le graphe unifié (en ignorant les lignes)
    graph = defaultdict(set)
    visited = set()
    
    for edge in raw_edges:
        n1 = simplify_name(edge["node0"])
        n2 = simplify_name(edge["node1"])
        graph[n1].add(n2)
        graph[n2].add(n1)
    start_node = next(iter(graph)) 

    stack = [start_node]
    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            stack.extend(neighbor for neighbor in graph[current] if neighbor not in visited)

    return len(visited) == len(graph)

def kruskalV2():
    # Simplification des noms (on ignore ::ligne)
    def simplify(name):
        return name.split("::")[0].strip().lower()
    
    raw_nodes = charger_json_nodes()
    raw_edges = charger_json_edges()

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
    print(f"Nombre d'arêtes dans l'ACPM : {len(mst_edges)}, Poids total : {total_weight}")
    return mst_edges



#================================== VERSION 3 ================================================


# --- Import des librairies ---
import json
import heapq
from collections import defaultdict
from datetime import datetime, timedelta
import os


def charger_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/api/nodesV3', methods=['GET'])
def charger_nodesV3():
    return charger_json("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\nodesV3.json")

@app.route('/api/edgesV3', methods=['GET'])
def charger_edgesV3():
    print("hugo")
    return charger_json("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\edgesV3.json")

def parse_time_to_datetime(hhmmss):
    try:
        h, m, s = map(int, hhmmss.split(":"))
        return datetime(1900, 1, 1, h, m, s)
    except:
        return None


def trouver_stop_id(nodes, nom_station, ligne):
    for stop_id, data in nodes.items():
        if data.get("nom", "").lower() == nom_station.lower() and ligne in data.get("lignes", []):
            return stop_id
    return None


def dijkstra_temporel(graphe_temporel, depart_id, arrivee_id, heure_depart_str):
    nodes = charger_nodesV3()
    transferts = charger_json("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\transferts_metro.json")
    heure_depart = parse_time_to_datetime(heure_depart_str)
    file = [(heure_depart, depart_id, [], "?")]  # (heure courante, stop_id, chemin, ligne)
    visites = {}

    id_to_name = {node_id: node_data.get("nom", node_id) for node_id, node_data in nodes.items()}

    transferts_par_station = defaultdict(list)
    for transfert in transferts:
        transferts_par_station[transfert["from"]].append(transfert)

    while file:
        heure_actuelle, station, chemin, ligne_prec = heapq.heappop(file)

        if id_to_name.get(station) == id_to_name.get(arrivee_id):
            return [
                (etape[0], etape[1].strftime("%H:%M:%S"), etape[2], int(etape[3]))
                for etape in chemin
            ] + [
                (station, heure_actuelle.strftime("%H:%M:%S"), ligne_prec or "?", 0)
            ]

        if station in visites and visites[station] <= heure_actuelle:
            continue
        visites[station] = heure_actuelle

        for traj in graphe_temporel.get(station, []):
            heure_dep_trajet = parse_time_to_datetime(traj["departure"])
            if heure_dep_trajet and (heure_dep_trajet >= heure_actuelle):
                heure_arrivee = heure_dep_trajet + timedelta(seconds=traj["duree"])
                nouveau_chemin = chemin + [(station, heure_dep_trajet, traj["ligne"], 0)]
                heapq.heappush(file, (heure_arrivee, traj["to"], nouveau_chemin, traj["ligne"]))

        for transfert in transferts_par_station.get(station, []):
            to = transfert["to"]
            temps = transfert.get("min_transfer_time")

            ligne_actuelle = ligne_prec
            lignes_to = set(traj["ligne"] for traj in graphe_temporel.get(to, []))

            if ligne_actuelle is None or (lignes_to and ligne_actuelle not in lignes_to):
                heure_arrivee = heure_actuelle + timedelta(seconds=temps)
                nouveau_chemin = chemin + [(station, heure_arrivee, ligne_actuelle,1)]
                heapq.heappush(file, (heure_arrivee, to, nouveau_chemin, "?"))


    return None



def trouver_stop_ligne(nodes, nom):
    lignes = None
    for stop_id, data in nodes.items():
        if data["nom"] == nom:
            lignes = data["lignes"][0]
    return lignes if lignes else None



from flask import Flask, request, jsonify
import os
from datetime import datetime

# Charge les données une seule fois au lancement du backend
base_path = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
nodes = charger_json(os.path.join(base_path, "nodesV3.json"))
graphe_temporel = charger_json(os.path.join(base_path, "graphe_temporel.json"))



@app.route('/api/pathV3', methods=['GET'])
def calcul_chemin_temporel():
    # Récupère les paramètres GET du frontend
    nom_depart = request.args.get('start_name')
    nom_arrivee = request.args.get('end_name')
    heure_depart = request.args.get('heure_depart')  # format attendu: "HH:MM:SS"
    # Vérifie que tous les paramètres sont présents
    if not all([nom_depart, nom_arrivee, heure_depart]):
        return jsonify({"error": "Paramètres manquants"}), 400  

    try:
        # Conversion de l'heure pour validation (facultatif mais recommandé)
        heure_depart_dt = datetime.strptime(heure_depart, "%H:%M:%S")
    except ValueError:
        return jsonify({"error": "Format de l'heure invalide, attendu HH:MM:SS"}), 400

    ligne_depart = trouver_stop_ligne(nodes, nom_depart)
    ligne_arrivee = trouver_stop_ligne(nodes, nom_arrivee)
    # Recherche des IDs dans les nodes
    depart_id = trouver_stop_id(nodes, nom_depart, ligne_depart)
    arrivee_id = trouver_stop_id(nodes, nom_arrivee, ligne_arrivee)

    

    if not depart_id or not arrivee_id:
        return jsonify({"error": "Station de départ ou d'arrivée introuvable"}), 404

    print(depart_id, arrivee_id, heure_depart)
    # Appel à ton algorithme temporel
    chemin = dijkstra_temporel(graphe_temporel, depart_id, arrivee_id, heure_depart)
    return jsonify({
        "chemin": formater_resultat_dijkstra(chemin),
    })


def formater_resultat_dijkstra(resultat):
    trajet_formate = []
    for i in range(len(resultat) - 1):
        id_from, heure_from, ligne_from, type_trajet = resultat[i]
        id_to, heure_to, ligne_to, _ = resultat[i + 1]
        trajet_formate.append([
            id_from,
            ligne_from,
            heure_from,
            id_to,
            ligne_to,
            heure_to,
            type_trajet
        ])
    return trajet_formate



import json
from collections import defaultdict, deque

import json
from collections import defaultdict, deque

def check_graph_connexityV3():
    # Charger les données
    with open("flask_back/data/edgesV3.json", encoding="utf-8") as f:
        edges_data = json.load(f)

    with open("flask_back/data/transferts_metro.json", encoding="utf-8") as f:
        transfers_data = json.load(f)

    # Construction du graphe non orienté
    graph = defaultdict(list)

    for edge in edges_data:
        a, b = edge["node0"], edge["node1"]
        graph[a].append(b)
        graph[b].append(a)

    for transfer in transfers_data:
        a, b = transfer["from"], transfer["to"]
        graph[a].append(b)
        graph[b].append(a)

    # BFS pour trouver la composante connexe
    visited = set()
    nodes = list(graph.keys())

    if not nodes:
        return 0  # graphe vide => non connexe

    queue = deque([nodes[0]])
    visited.add(nodes[0])

    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    # Si tous les sommets ont été visités, alors le graphe est connexe
    return 1 if len(visited) == len(graph) else 0




import json
from flask import jsonify
@app.route('/api/kruskalV3', methods=['GET'])
def ACPMV3():
    if check_graph_connexityV3():
        # Charger les arêtes classiques
        with open("flask_back/data/edgesV3.json", encoding="utf-8") as f:
            edges_data = json.load(f)
        edges = []
        for edge in edges_data:
            u, v, w = edge["node0"], edge["node1"], edge["weight"]
            edges.append((w, u, v))

        # Charger les transferts (facultatif)
        try:
            with open("flask_back/data/transferts_metro.json", encoding="utf-8") as f:
                transfers_data = json.load(f)
            for transfer in transfers_data:
                u, v, w = transfer["from"], transfer["to"], transfer["min_transfer_time"]
                edges.append((w, u, v))
        except FileNotFoundError:
            pass  # Ignore si le fichier n'existe pas=
        # Union-Find
        class UnionFind:
            def __init__(self, nodes):
                self.parent = {node: node for node in nodes}
                self.rank = {node: 0 for node in nodes}

            def find(self, u):
                if self.parent[u] != u:
                    self.parent[u] = self.find(self.parent[u])
                return self.parent[u]

            def union(self, u, v):
                u_root, v_root = self.find(u), self.find(v)
                if u_root == v_root:
                    return False
                if self.rank[u_root] < self.rank[v_root]:
                    self.parent[u_root] = v_root
                else:
                    self.parent[v_root] = u_root
                    if self.rank[u_root] == self.rank[v_root]:
                        self.rank[u_root] += 1
                return True
    # Récupérer tous les sommets
    nodes = set()
    for _, u, v in edges:
        nodes.add(u)
        nodes.add(v)
    uf = UnionFind(nodes)
    edges.sort()
    # Kruskal
    mst = []
    total_weight = 0
    for w, u, v in edges:
        if uf.union(u, v):
            mst.append({"from": u, "to": v, "weight": w})
            total_weight += w
    return {
        "total_weight": total_weight,
        "edge_count": len(mst),
        "mst": mst
    }


#PRIM
import json
import heapq
from collections import defaultdict

# Charger les données
with open("flask_back/data/edgesV3.json", encoding="utf-8") as f:
    edges_data = json.load(f)

with open("flask_back/data/transferts_metro.json", encoding="utf-8") as f:
    transfers_data = json.load(f)

# Construire le graphe sous forme d'adjacence
graph = defaultdict(list)

for edge in edges_data:
    u, v, w = edge["node0"], edge["node1"], edge["weight"]
    graph[u].append((w, v))
    graph[v].append((w, u))

for transfer in transfers_data:
    u, v, w = transfer["from"], transfer["to"], transfer["min_transfer_time"]
    graph[u].append((w, v))
    graph[v].append((w, u))


def prim(graph, start):
    visited = set([start])
    edges = graph[start][:]
    heapq.heapify(edges)
    mst = []
    total_weight = 0

    while edges and len(visited) < len(graph):
        w, v = heapq.heappop(edges)
        if v not in visited:
            visited.add(v)
            mst.append((start, v, w))
            total_weight += w
            for next_w, next_v in graph[v]:
                if next_v not in visited:
                    heapq.heappush(edges, (next_w, next_v))
            start = v  # continue depuis le dernier sommet ajouté

    return mst, total_weight


# Exécuter Prim à partir d’un sommet arbitraire
start_node = next(iter(graph))
mst, total_weight = prim(graph, start_node)

print(f"\n🌳 Arbre couvrant minimal trouvé avec {len(mst)} arêtes.")
print(f"⚖️ Poids total : {total_weight}")
print(f"📝 Exemple d'arêtes dans l'ACM : {mst[:10]}{'...' if len(mst) > 10 else ''}")



if __name__ == '__main__':
    app.run(debug=True)
