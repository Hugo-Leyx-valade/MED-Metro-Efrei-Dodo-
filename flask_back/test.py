import json

def charger_json_edges():
    with open("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\edges.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def charger_json_nodes():
    with open("C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\nodes.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data



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




def api_shortest_pathV2(start_id, end_id):
    print(f"Recherche du chemin le plus court de {start_id} à {end_id}")
    
    # Chargement des données
    nodes = charger_json_nodes()  # dict {id: {nom, latitude, longitude, lignes}}
    edges = charger_json_edges()  # liste [{node0, node1, weight}]

    result = dijkstra_shortest_path(start_id, end_id, nodes, edges)

    # Affichage des étapes du chemin
    for id in result["path"]:
        station = nodes.get(id)
        if station:
            print(f"{station['nom']} | Lignes: {', '.join(station['lignes'])}")
        else:
            print(f"[⚠] Station inconnue pour ID: {id}")

    return result


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

recuperer_edges_metro_unifies()