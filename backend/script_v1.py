

def to_graph(txt_file):
    """
    Converts a text file to a graph representation.
    """
    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    tab_arretes = []
    tab_noeuds = []
    noeuds = {}
    for line in lines:
        parts = line.strip().split(';')
        arretes = {}
        noeuds = {}
        if len(parts) < 5:
            arretes["node0"] = parts[1]
            arretes["node1"]= parts[2]
            arretes["weight"] = parts[3]
            tab_arretes.append(arretes)
        elif len(parts) > 5:
            noeuds["node_number"] = parts[1]
            noeuds["name"] = " ".join(parts[2:-5])
            noeuds["line"] = parts[-3]
            noeuds["terminus"] = parts[-2]
            noeuds["branchement"] = parts[-1]
            tab_noeuds.append(noeuds)
    f.close()
    return tab_arretes , tab_noeuds



def get_map_points(file_path):
    points = []

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


print(get_map_points("data/version 1/pospoints.txt"))

