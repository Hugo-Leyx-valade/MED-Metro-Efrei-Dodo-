from flask import Flask, jsonify
from flask_cors import CORS
import heapq
from collections import defaultdict

app = Flask(__name__)
CORS(app)


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/edges', methods=['GET'])
def to_graph_edges():
    """
    Converts a text file to a graph representation.
    """
    txt_file = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\output.txt"

    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    tab_arretes = []
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
    f.close()
    print(tab_arretes)
    return tab_arretes

def load_station_positions(file_path):
    station_positions = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(';')
            if len(parts) >= 3:
                x, y = parts[0], parts[1]
                station_name = ';'.join(parts[2:]).replace('@', ' ')
                station_positions[station_name] = {'x': x, 'y': y}
    return station_positions

@app.route('/api/nodes', methods=['GET'])
def to_graph_nodes():
    """
    Converts a text file to a graph representation.
    """
    txt_file_nodes = "C:\\Users\\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\output.txt"
    txt_file_positions = "C:\\Users\hugol\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\flask_back\\data\\version 1\\pospoints.txt"  # Remplacez par le chemin réel

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
                "line": parts[-4],
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



from collections import defaultdict
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        self.parent[ry] = rx
        return True

@app.route('/api/acpm', methods=['GET'])
def kruskal_mst():
    edges = to_graph_edges()
    print(max(max(int(edge['node0']), int(edge['node1'])) for edge in edges) + 1)
    n = max(max(int(edge['node0']), int(edge['node1'])) for edge in edges) + 1
    uf = UnionFind(n)

    mst = []
    total_weight = 0

    for weight, a, b in sorted(edges):
        if uf.union(a, b):
            mst.append((a, b, weight))
            total_weight += weight

    return mst, total_weight



if __name__ == '__main__':
    app.run(debug=True)
