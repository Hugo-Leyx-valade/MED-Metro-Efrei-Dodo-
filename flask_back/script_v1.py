import heapq
from collections import defaultdict

def to_graph():
    """
    Converts a text file to a graph representation.
    """
    txt_file = "C:/Users/hugol/Documents/projet/mastercamp/MED-Metro-Efrei-Dodo-/flask_back/data/version 1/output.txt"
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
    file_path = txt_file = "C:/Users/hugol/Documents/projet/mastercamp/MED-Metro-Efrei-Dodo-/flask_back/data/version 1/pospoints.txt"


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

print(to_graph())

