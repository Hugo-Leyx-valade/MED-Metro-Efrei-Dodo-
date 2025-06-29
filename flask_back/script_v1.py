import heapq
from collections import defaultdict

def to_graph():
    """
    Converts a text file to a graph representation.
    """
    txt_file = "C:\\Users\\jungk\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\backend\\data/version 1/output.txt"
    with open(txt_file, 'r') as f:
        lines = f.readlines()

    tab_arretes = []
    tab_noeuds = []

    for line in lines:
        parts = line.strip().split(';')

        if len(parts) <= 4:  # Ensure there are enough parts to form an edge
            arretes = {
                "node0": parts[1],
                "node1": parts[2],
                "weight": parts[3]
            }
            tab_arretes.append(arretes)


    return tab_arretes, tab_noeuds




def get_map_points():
    points = []
    file_path = txt_file = "C:\\Users\\jungk\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\backend\\data/version 1/pospoints.txt"


    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(";")
            if len(parts) != 3:
                continue

            x = int(parts[0])
            y = int(parts[1])
            name = parts[2].replace("@", " ")
            points.append({
                "x": x,
                "y": y,
                "name": name
            })

    return points
import heapq
from collections import defaultdict

def to_graph_nodes():
    """
    Converts a text file to a graph representation.
    """
    txt_file_nodes = "C:\\Users\\jungk\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\backend\\data\\version 1\\output.txt"
    txt_file_positions = "C:\\Users\\jungk\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\backend\\data\\version 1\\pospoints.txt"  # Remplacez par le chemin réel

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
                "line": parts[-3],
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

    return jsonify(tab_noeuds)

print(to_graph())
