# --- Import des librairies ---
import json
import heapq
from collections import defaultdict
from datetime import datetime, timedelta
import os


# --- Chargement des données ---
def charger_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# --- Dijkstra temporel ---
def parse_time_to_datetime(hhmmss):
    try:
        h, m, s = map(int, hhmmss.split(":"))
        return datetime(1900, 1, 1, h % 24, m, s) + timedelta(hours=h // 24)
    except:
        return None


def dijkstra_temporel(graphe_temporel, nodes, depart, arrivee, heure_depart_str, correspondance_duree=120):
    heure_depart = parse_time_to_datetime(heure_depart_str)
    file = [(heure_depart, depart, [], None)]  # (heure courante, stop_id, chemin, ligne)
    visites = {}

    while file:
        heure_actuelle, station, chemin, ligne_prec = heapq.heappop(file)

        if station == arrivee:
            return chemin + [(station, heure_actuelle.time(), ligne_prec or "?")]

        if station in visites and visites[station] <= heure_actuelle:
            continue
        visites[station] = heure_actuelle

        for traj in graphe_temporel.get(station, []):
            heure_dep_trajet = parse_time_to_datetime(traj["departure"])
            if heure_dep_trajet and heure_dep_trajet >= heure_actuelle:
                attente = (heure_dep_trajet - heure_actuelle).total_seconds()
                if ligne_prec and traj["ligne"] != ligne_prec:
                    heure_dep_trajet += timedelta(seconds=correspondance_duree)
                heure_arrivee = parse_time_to_datetime(traj["arrival"])
                nouveau_chemin = chemin + [(station, heure_actuelle.time(), traj["ligne"])]
                heapq.heappush(file, (heure_arrivee, traj["to"], nouveau_chemin, traj["ligne"]))

        # Ajout des transferts inter-quais
        for nom_station, data in nodes.items():
            if station in data.get("ids_originaux", []):
                for autre_stop in data.get("ids_originaux", []):
                    if autre_stop != station:
                        heure_transfert = heure_actuelle + timedelta(seconds=correspondance_duree)
                        nouveau_chemin = chemin + [(station, heure_actuelle.time(), "transfert")]
                        heapq.heappush(file, (heure_transfert, autre_stop, nouveau_chemin, None))

    return None


# --- Exemple d'utilisation ---
if __name__ == '__main__':
    base_path = "C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    nodes = charger_json(os.path.join(base_path, "nodes.json"))
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
