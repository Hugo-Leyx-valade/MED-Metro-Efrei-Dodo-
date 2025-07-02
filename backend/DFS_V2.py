import json
from collections import defaultdict, deque
from graphviz import Digraph
import os

# Ajout du chemin Graphviz
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

def charger_graphe_json(edges_path, nodes_path):
    graph = defaultdict(dict)

    with open(nodes_path, encoding="utf-8") as f:
        nodes_data = json.load(f)
    noms = {key: val["nom"] for key, val in nodes_data.items()}

    with open(edges_path, encoding="utf-8") as f:
        edges_data = json.load(f)

    for edge in edges_data:
        a, b, poids = edge["node0"], edge["node1"], edge["weight"]
        graph[a][b] = poids
        graph[b][a] = poids

    return graph, noms

def dfs(graph, start):
    visited = set()
    parcours = []
    niveaux = {start: 0}
    stack = [(start, 0)]

    while stack:
        node, niveau = stack.pop()
        if node not in visited:
            visited.add(node)
            parcours.append(node)
            niveaux[node] = niveau
            for neighbor in reversed(sorted(graph[node])):  # pour un ordre déterministe
                if neighbor not in visited:
                    stack.append((neighbor, niveau + 1))

    return visited, parcours, niveaux

# === Chemins ===
# On remonte depuis backend vers MED..., puis on descend vers flask_back/data
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(base_dir, "flask_back", "data")

edges_path = os.path.join(data_dir, "edges.json")
nodes_path = os.path.join(data_dir, "nodes.json")

if not os.path.exists(nodes_path):
    print("❌ ERREUR : nodes.json introuvable !")
    exit()
if not os.path.exists(edges_path):
    print("❌ ERREUR : edges.json introuvable !")
    exit()

graph, noms = charger_graphe_json(edges_path, nodes_path)

# === Choix de station ===
nom_recherche = input("🔎 Entrez le nom de la station de départ (partiel autorisé) : ").lower()
matches = [(id, nom) for id, nom in noms.items() if nom_recherche in nom.lower()]

if not matches:
    print(f"❌ Aucune station ne correspond à '{nom_recherche}'")
    exit()

print("\n🔽 Correspondances trouvées :")
for idx, (id, nom) in enumerate(matches):
    print(f"{idx}. {nom} (ID: {id})")

choix = input(f"\nEntrez le numéro de la station à utiliser comme départ [0-{len(matches)-1}] : ")
try:
    index = int(choix)
    start_id = matches[index][0]
except (ValueError, IndexError):
    print("❌ Choix invalide.")
    exit()

# === Mode d'affichage ===
print("\nSouhaitez-vous :")
print("1. Explorer tout l'arbre en DFS (parcours en profondeur)")
print("2. Afficher uniquement les premières stations visitées")

mode = input("Entrez 1 ou 2 : ").strip()
while mode not in {"1", "2"}:
    mode = input("❌ Entrée invalide. Entrez 1 ou 2 : ").strip()

# === Exécution DFS ===
visites, parcours, niveaux = dfs(graph, start_id)

if mode == "1":
    dot = Digraph(comment="Arbre DFS", format="png")
    for vid in parcours:
        label = f"{noms.get(vid, vid)}\n(niveau {niveaux[vid]})"
        dot.node(vid, label)

    for vid in parcours:
        for neighbor in graph[vid]:
            if niveaux.get(neighbor, -1) == niveaux[vid] + 1:
                dot.edge(vid, neighbor)

    output_path = os.path.join(os.path.dirname(__file__), "arbre_dfs_json")
    output_file = dot.render(output_path, cleanup=True)
    if os.path.exists(output_file):
        print(f"\n✅ Fichier Graphviz généré avec succès : {output_file}")
    else:
        print(f"\n❌ Erreur : le fichier {output_file} n'a pas été créé.")

elif mode == "2":
    print("\n🔍 Exemples de stations visitées (10 premières) :")
    for vid in parcours[:10]:
        print(f" - {vid} : {noms.get(vid, 'Inconnu')} (niveau {niveaux.get(vid, '?')})")
else:
    print(f"\n📁 Arbre DFS généré avec {len(parcours)} stations. Voir le fichier PNG.")

# === Analyse ===
total_aretes = sum(len(voisins) for voisins in graph.values()) // 2
print(f"\n🔁 Nombre total d’arêtes : {total_aretes}")

inaccessibles = set(graph.keys()) - visites
if inaccessibles:
    print("\n🚫 Stations inaccessibles :")
    for i in sorted(inaccessibles):
        print(f" - {i} : {noms.get(i, 'Inconnu')}")
else:
    print("\n🎉 Toutes les stations sont accessibles depuis ce point.")
