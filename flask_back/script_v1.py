import json
import heapq
from collections import defaultdict
from datetime import datetime, timedelta
import os

def charger_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_time_to_datetime(hhmmss):
    try:
        h, m, s = map(int, hhmmss.split(":"))
        return datetime(1900, 1, 1, h, m, s)
    except:
        return None

def dijkstra_temporel(graphe_temporel, nodes, depart, arrivee, heure_depart_str, correspondance_duree=120):
    heure_depart = parse_time_to_datetime(heure_depart_str)
    file = [(heure_depart, depart, [], None)]  # (heure courante, stop_id, chemin, ligne)
    visites = {}

    # Mapping from station IDs to station names
    id_to_name = {node_id: node_data.get("nom", node_id) for node_id, node_data in nodes.items()}

    # Mapping from station names to their platform IDs
    station_to_platforms = defaultdict(list)
    for node_id, node_data in nodes.items():
        station_name = node_data.get("nom", "")
        station_to_platforms[station_name].append(node_id)

    while file:
        heure_actuelle, station, chemin, ligne_prec = heapq.heappop(file)

        if station == arrivee:
            # Return the path with station names instead of IDs
            return [(id_to_name[etape[0]], etape[1].strftime("%H:%M:%S"), etape[2]) for etape in chemin] + [(id_to_name[station], heure_actuelle.strftime("%H:%M:%S"), ligne_prec or "?")]

        if station in visites and visites[station] <= heure_actuelle:
            continue
        visites[station] = heure_actuelle

        for traj in graphe_temporel.get(station, []):
            heure_dep_trajet = parse_time_to_datetime(traj["departure"])
            if heure_dep_trajet and heure_dep_trajet >= heure_actuelle:
                attente = (heure_dep_trajet - heure_actuelle).total_seconds()
                if ligne_prec and traj["ligne"] != ligne_prec:
                    heure_dep_trajet += timedelta(seconds=correspondance_duree)
                heure_arrivee = heure_dep_trajet + timedelta(seconds=traj["duree"])
                nouveau_chemin = chemin + [(station, heure_dep_trajet, traj["ligne"])]
                heapq.heappush(file, (heure_arrivee, traj["to"], nouveau_chemin, traj["ligne"]))

        # Add transfers between platforms of the same station
        station_name = nodes.get(station, {}).get("nom", "")
        for platform_id in station_to_platforms.get(station_name, []):
            if platform_id != station:
                heure_transfert = heure_actuelle + timedelta(seconds=correspondance_duree)
                nouveau_chemin = chemin + [(station, heure_actuelle, "transfert")]
                heapq.heappush(file, (heure_transfert, platform_id, nouveau_chemin, None))

    return None

if __name__ == '__main__':
    base_path = "C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    nodes = charger_json(os.path.join(base_path, "nodesV3.json"))
    graphe_temporel = charger_json(os.path.join(base_path, "graphe_temporel.json"))

    depart = "IDFM:21935"
    arrivee = "IDFM:22399"
    heure_depart = "07:30:00"

    chemin = dijkstra_temporel(graphe_temporel, nodes, depart, arrivee, heure_depart)

    if chemin:
        print("\nItinéraire trouvé :")
        for etape in chemin:
            nom = etape[0]
            heure = etape[1]
            ligne = etape[2]
            print(f" - {nom} à {heure} via {ligne}")
    else:
        print("\nAucun itinéraire trouvé.")
