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

def charger_stations_metro_sans_doublons(gtfs_folder):
    # Charger les fichiers GTFS
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt")
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt")
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt")
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt")

    # Garder uniquement les lignes de métro
    routes_metro = routes[routes['route_type'] == 1]
    trips_metro = trips[trips['route_id'].isin(routes_metro['route_id'])]
    stop_times_metro = stop_times[stop_times['trip_id'].isin(trips_metro['trip_id'])]

    # Associer stop_id -> trip_id -> route_id -> route_short_name
    trip_route = trips_metro[['trip_id', 'route_id']].merge(
        routes_metro[['route_id', 'route_short_name']], on='route_id'
    )
    stop_trip_route = stop_times_metro[['stop_id', 'trip_id']].merge(trip_route, on='trip_id')

    # Regrouper les lignes par stop_id
    stop_lignes = stop_trip_route.groupby('stop_id')['route_short_name'].unique()

    # Conserver seulement les stops de métro
    stops_metro = stops[stops['stop_id'].isin(stop_lignes.index)]

    # Fusionner les doublons par stop_name
    stops_metro['lignes'] = stops_metro['stop_id'].map(lambda sid: list(stop_lignes.get(sid, [])))
    grouped = stops_metro.groupby('stop_name').agg({
        'lignes': lambda x: sorted(set(l for sublist in x for l in sublist)),  # fusionne les lignes
        'stop_lat': 'mean',  # moyenne des coordonnées si doublon
        'stop_lon': 'mean'
    }).reset_index()

    # Créer un dictionnaire final
    dico_stations = {}
    for _, row in grouped.iterrows():
        dico_stations[row['stop_id']] = {
            'nom': row['stop_name'],
            'lignes': row['lignes'],
            'latitude': row['stop_lat'],
            'longitude': row['stop_lon']
        }

    return dico_stations

# Exemple d'utilisation



import pandas as pd

def compter_stations(gtfs_folder):
    # Chargement des fichiers
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt")
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

def recuperer_edges_metro_sans_doublons(gtfs_folder):
    # Charger uniquement les colonnes nécessaires
    stop_times = pd.read_csv(os.path.join(gtfs_folder, "stop_times.txt"), usecols=["trip_id", "stop_id", "stop_sequence", "departure_time", "arrival_time"])
    trips = pd.read_csv(os.path.join(gtfs_folder, "trips.txt"), usecols=["trip_id", "route_id"])
    routes = pd.read_csv(os.path.join(gtfs_folder, "routes.txt"), usecols=["route_id", "route_type"])

    # Filtrer les routes métro
    metro_route_ids = routes.loc[routes['route_type'] == 1, 'route_id'].unique()
    metro_trips = trips.loc[trips['route_id'].isin(metro_route_ids), 'trip_id']

    # Filtrer stop_times pour ne garder que les trips métro
    stop_times = stop_times[stop_times['trip_id'].isin(metro_trips)].copy()
    stop_times.sort_values(by=["trip_id", "stop_sequence"], inplace=True)

    # Convertir les temps en timedelta une fois pour toutes
    # fonction auxiliaire pour convertir hh:mm:ss en secondes
    def to_seconds(t):
        try:
            h, m, s = t.split(':')
            return int(h)*3600 + int(m)*60 + int(float(s))
        except:
            return None

    stop_times['dep_sec'] = stop_times['departure_time'].map(to_seconds)
    stop_times['arr_sec'] = stop_times['arrival_time'].map(to_seconds)

    edge_weights = defaultdict(list)

    # Regrouper par trip_id
    for trip_id, group in stop_times.groupby("trip_id"):
        group = group.reset_index(drop=True)
        for i in range(len(group) - 1):
            current_stop = group.iloc[i]
            next_stop = group.iloc[i + 1]

            node_a = str(current_stop["stop_id"])
            node_b = str(next_stop["stop_id"])

            t0 = current_stop["dep_sec"]
            t1 = next_stop["arr_sec"]

            if t0 is None or t1 is None:
                continue

            weight = t1 - t0
            if weight <= 0 or weight > 3600:
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

    return edges

import json

def charger_stations():
    gtfs_folder = "C:\\Users\\jungk\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\backend\\data\\"
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

edges = charger_stations()
with open('nodes.json', 'w', encoding='utf-8') as f:
    json.dump(edges, f, ensure_ascii=False, indent=2)

recuperer_edges_metro_sans_doublons("backend\\data")