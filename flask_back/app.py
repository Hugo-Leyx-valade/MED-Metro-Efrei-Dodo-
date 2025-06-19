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


if __name__ == '__main__':
    app.run(debug=True)
