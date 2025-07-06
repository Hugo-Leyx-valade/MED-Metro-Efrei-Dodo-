# --- Import des librairies ---
import json
import heapq
from collections import defaultdict
from datetime import datetime, timedelta
import os
import random
import time
from codecarbon import EmissionsTracker

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
    file = [(heure_depart, depart_id, [], "?")]
    visites = {}

    id_to_name = {node_id: node_data.get("nom", node_id) for node_id, node_data in nodes.items()}
    transferts_par_station = defaultdict(list)
    for transfert in transferts:
        transferts_par_station[transfert["from"]].append(transfert)

    while file:
        heure_actuelle, station, chemin, ligne_prec = heapq.heappop(file)

        if id_to_name.get(station) == id_to_name.get(arrivee_id):
            return chemin + [(station, heure_actuelle.strftime("%H:%M:%S"), ligne_prec or "?", 0)]

        if station in visites and visites[station] <= heure_actuelle:
            continue
        visites[station] = heure_actuelle

        for traj in graphe_temporel.get(station, []):
            heure_dep_trajet = parse_time_to_datetime(traj["departure"])
            if heure_dep_trajet and heure_dep_trajet >= heure_actuelle:
                heure_arrivee = heure_dep_trajet + timedelta(seconds=traj["duree"])
                nouveau_chemin = chemin + [(station, heure_dep_trajet.strftime("%H:%M:%S"), traj["ligne"], 0)]
                heapq.heappush(file, (heure_arrivee, traj["to"], nouveau_chemin, traj["ligne"]))

        for transfert in transferts_par_station.get(station, []):
            to = transfert["to"]
            temps = transfert.get("min_transfer_time")
            ligne_actuelle = ligne_prec
            lignes_to = set(traj["ligne"] for traj in graphe_temporel.get(to, []))

            if ligne_actuelle is None or (lignes_to and ligne_actuelle not in lignes_to):
                heure_arrivee = heure_actuelle + timedelta(seconds=temps)
                nouveau_chemin = chemin + [(station, heure_arrivee.strftime("%H:%M:%S"), ligne_actuelle, 1)]
                heapq.heappush(file, (heure_arrivee, to, nouveau_chemin, "?"))

    return None

if __name__ == '__main__':
    base_path = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\"
    nodes = charger_json(os.path.join(base_path, "nodesV3.json"))
    graphe_temporel = charger_json(os.path.join(base_path, "graphe_temporel.json"))
    transferts = charger_json(os.path.join(base_path, "transferts_metro.json"))

    tracker = EmissionsTracker(output_file="co2_output.txt", log_level="error")
    tracker.start()

    resultats = []
    keys = list(nodes.keys())
    essais = 0

    while essais < 100:
        depart = random.choice(keys)
        arrivee = random.choice(keys)

        if depart == arrivee:
            continue

        heure_depart = "07:30:00"
        start_time = time.time()

        chemin = dijkstra_temporel(graphe_temporel, nodes, transferts, depart, arrivee, heure_depart)

        end_time = time.time()
        exec_time = end_time - start_time

        if chemin:
            essais += 1
            emissions = tracker.stop()  # mesuré à l'itération

            resultats.append((essais, depart, arrivee, exec_time, emissions))
            print(f"✔️ {essais}: {depart} ➜ {arrivee} | ⏱ {exec_time:.3f}s | CO₂: {emissions:.8f} kg")

    tracker.stop()

    # Moyennes
    moyenne_temps = sum(r[3] for r in resultats) / len(resultats)
    moyenne_co2 = sum(r[4] for r in resultats) / len(resultats)

    # Enregistrement dans un fichier texte
    with open("statistiques_100_tests.txt", "w", encoding="utf-8") as f:
        f.write("Test\tDépart\tArrivée\tTemps(s)\tCO2(kg)\n")
        for test, d, a, t, c in resultats:
            f.write(f"{test}\t{d}\t{a}\t{t:.3f}\t{c:.8f}\n")

        f.write("\n--- Moyennes ---\n")
        f.write(f"Temps moyen (s) : {moyenne_temps:.3f}\n")
        f.write(f"CO2 moyen (kg)  : {moyenne_co2:.8f}\n")

    print("\n✅ Tests terminés. Résultats dans 'statistiques_100_tests.txt'")
