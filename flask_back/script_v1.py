# --- Import des librairies ---
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


def trouver_stop_id(nodes, nom_station, ligne):
    for stop_id, data in nodes.items():
        if data.get("nom", "").lower() == nom_station.lower() and ligne in data.get("lignes", []):
            return stop_id
    return None


def dijkstra_temporel(graphe_temporel, nodes, transferts, depart_id, arrivee_id, heure_depart_str):
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
            if heure_dep_trajet and heure_dep_trajet >= heure_actuelle:
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




if __name__ == '__main__':
    base_path = "C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    nodes = charger_json(os.path.join(base_path, "nodesV3.json"))
    graphe_temporel = charger_json(os.path.join(base_path, "graphe_temporel.json"))

    # L'utilisateur donne les noms et lignes (ex : Alma-Marceau ligne 9 → Assemblée Nationale ligne 12)
    nom_depart = "Alma - Marceau"
    ligne_depart = "9"
    nom_arrivee = "Villejuif Léo Lagrange"
    ligne_arrivee = "7"
    heure_depart = "07:30:00"

    depart_id = trouver_stop_id(nodes, nom_depart, ligne_depart)
    arrivee_id = trouver_stop_id(nodes, nom_arrivee, ligne_arrivee)

    if not depart_id or not arrivee_id:
        print("\nErreur : l'une des stations n'a pas été trouvée.")
    else:
        transferts = charger_json(os.path.join(base_path, "transferts_metro.json"))
        chemin = dijkstra_temporel(graphe_temporel, nodes, transferts, depart_id, arrivee_id, heure_depart)

        if chemin:
            print(chemin)
        else:
            print("\nAucun itinéraire trouvé.")
