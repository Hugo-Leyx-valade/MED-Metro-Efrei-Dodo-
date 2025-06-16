import pandas as pd

# Charger les fichiers GTFS
routes = pd.read_csv("./data/routes.txt")
trips = pd.read_csv("data/trips.txt")
stop_times = pd.read_csv("data/stop_times.txt")
stops = pd.read_csv("data/stops.txt")

# 1. Identifier la ligne 7 (adapté selon le type de réseau)
ligne_7 = routes[
    (routes["agency_id"] == "IDFM:Operator_100") &
    (routes["route_type"] == 1) &
    (routes["route_short_name"] == "6")
]
print(ligne_7)
route_id = ligne_7.iloc[0]["route_id"]

# 2. Récupérer les trips associés
trips_ligne_7 = trips[trips["route_id"] == route_id]

# 3. Choisir un trip représentatif (ex : le 1er)
trip_id = trips_ligne_7.iloc[0]["trip_id"]

# 4. Récupérer les arrêts du trip
arrets_trip = stop_times[stop_times["trip_id"] == trip_id].sort_values("stop_sequence")

# 5. Fusionner avec les noms des arrêts
arrets_ligne_7 = arrets_trip.merge(stops, on="stop_id")[["stop_sequence", "stop_name", "stop_lat", "stop_lon"]]

# Résultat
print(arrets_ligne_7)
