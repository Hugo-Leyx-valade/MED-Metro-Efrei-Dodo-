import pandas as pd
import json
import os

def extraire_transferts_metro(gtfs_path, sortie_json="transferts_metro.json"):
    # Chargement des fichiers
    transfers = pd.read_csv(os.path.join(gtfs_path, "transfers.txt"))
    stop_times = pd.read_csv(os.path.join(gtfs_path, "stop_times.txt"))
    trips = pd.read_csv(os.path.join(gtfs_path, "trips.txt"))
    routes = pd.read_csv(os.path.join(gtfs_path, "routes.txt"))

    # Récupérer les stop_ids utilisés par les lignes de métro (route_type == 1)
    routes_metro = routes[routes["route_type"] == 1]["route_id"].unique()
    trips_metro = trips[trips["route_id"].isin(routes_metro)]
    stop_ids_metro = stop_times[stop_times["trip_id"].isin(trips_metro["trip_id"])]["stop_id"].unique()

    # Filtrer les transferts entre arrêts de métro uniquement
    transferts_metro = transfers[
        transfers["from_stop_id"].isin(stop_ids_metro) &
        transfers["to_stop_id"].isin(stop_ids_metro)
    ]

    # On formate sous forme de liste de dicts
    resultat = []
    for _, row in transferts_metro.iterrows():
        ligne = {
            "from": row["from_stop_id"],
            "to": row["to_stop_id"],
            "type": row.get("transfer_type", 2),
            "min_transfer_time": int(row.get("min_transfer_time", 120))
        }
        resultat.append(ligne)

    # Export JSON
    with open(os.path.join(gtfs_path, sortie_json), "w", encoding="utf-8") as f:
        json.dump(resultat, f, indent=2, ensure_ascii=False)

    print(f"{len(resultat)} transferts métro extraits dans {sortie_json}")

# Exemple d'utilisation
if __name__ == "__main__":
    dossier_gtfs = "C:/Users/hugol/Documents/projet/mastercamp/MED-Metro-Efrei-Dodo-/flask_back/data/"
    extraire_transferts_metro(dossier_gtfs)
