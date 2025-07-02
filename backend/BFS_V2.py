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

    # Ajout des arêtes normales
    for edge in edges_data:
        a, b, poids = edge["node0"], edge["node1"], edge["weight"]
        graph[a][b] = poids
        graph[b][a] = poids

    # 🔁 Ajout des correspondances interlignes (même nom, lignes différentes)
    nom_to_ids = defaultdict(list)
    for station_id, nom in noms.items():
        nom_to_ids[nom].append(station_id)

    for ids in nom_to_ids.values():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                if b not in graph[a]:
                    graph[a][b] = 0
                    graph[b][a] = 0

    return graph, noms


import re


def proteger_id_graphviz(station_id):
    """
    Retourne un identifiant Graphviz protégé, sans guillemets doubles ni antislashs.
    """
    if not isinstance(station_id, str):
        station_id = str(station_id)
    # Nettoyage complet
    station_id = station_id.replace("\\", "/").replace('"', "'")
    station_id = re.sub(r"[^\w\-: ]", "", station_id)  # supprime les caractères non valides sauf `-`, `:`, espace
    return f'"{station_id}"'



def nettoyer_label(nom):
    nom = nom.replace('"', "'")              # remplace les guillemets doubles
    nom = nom.replace("\\", "/")             # remplace les antislashs par des slashs normaux
    nom = re.sub(r"[^\w\s\-\/]", "", nom)    # retire tout sauf lettres, chiffres, tirets, slashs et espaces
    return nom


def echapper_label_graphviz(label):
    """
    Nettoie et échappe un label pour Graphviz : évite les caractères invalides comme les guillemets non fermés ou les backslashes.
    """
    import html
    label = label.replace("\\", "/")
    label = label.replace('"', "'")
    label = html.escape(label)
    return label




def bfs(graph, start):
    visited = set()
    parcours = []
    niveaux = {start: 0}
    queue = deque([start])

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            parcours.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited and neighbor not in niveaux:
                    niveaux[neighbor] = niveaux[node] + 1
                    queue.append(neighbor)
    return visited, parcours, niveaux

# === Chemins ===

# On remonte d’un niveau depuis backend/
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Puis on descend dans flask_back/data/
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

# === Choix interactif ===
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
print("1. Explorer tout l'arbre BFS à partir de cette station")
print("2. Afficher uniquement les premières stations visitées")

mode = input("Entrez 1 ou 2 : ").strip()
while mode not in {"1", "2"}:
    mode = input("❌ Entrée invalide. Entrez 1 ou 2 : ").strip()

# === Parcours ===
visites, parcours, niveaux = bfs(graph, start_id)

if mode == "1":
    dot = Digraph(comment="Arbre BFS", format="png")
    
    for vid in parcours:
        nom_sain = nettoyer_label(noms.get(vid, vid))
        label = f"{nom_sain}\n(niveau {niveaux[vid]})"
        label = echapper_label_graphviz(label)
        dot.node(proteger_id_graphviz(vid), label)



        
    for vid in parcours:
        for neighbor in graph[vid]:
            if niveaux.get(neighbor, -1) == niveaux[vid] + 1:
                poids = graph[vid][neighbor]
                if poids == 0:
                    dot.edge(proteger_id_graphviz(vid), proteger_id_graphviz(neighbor), style="dashed", color="gray")
                else:
                    dot.edge(proteger_id_graphviz(vid), proteger_id_graphviz(neighbor))


    # 🔍 Sauvegarde du fichier .dot brut pour debug (si erreur ligne 785)
    dot_path = os.path.join(os.path.dirname(__file__), "debug_arbre.dot")
    with open(dot_path, "w", encoding="utf-8") as f:
        f.write(dot.source)
    print(f"\n🪪 Fichier DOT brut écrit dans : {dot_path}")

    # Le fichier est généré dans le dossier `backend/`
    output_path = os.path.join(os.path.dirname(__file__), "arbre_bfs_json")
    output_file = dot.render(output_path, cleanup=True)

    if os.path.exists(output_file):
        print(f"\n✅ Fichier généré : {output_file}")
    else:
        print(f"\n❌ Erreur lors de la création du fichier.")
else:
    print("\n🔍 Exemples de stations visitées (10 premières) :")
    for vid in parcours[:10]:
        print(f" - {vid} : {noms.get(vid, 'Inconnu')} (niveau {niveaux.get(vid, '?')})")


# === Analyse ===
total_aretes = sum(len(v) for v in graph.values()) // 2
print(f"\n🔁 Nombre total d’arêtes : {total_aretes}")

inaccessibles = set(noms.keys()) - visites
if inaccessibles:
    print("\n🚫 Stations inaccessibles :")
    for i in sorted(inaccessibles):
        print(f" - {i} : {noms.get(i, 'Inconnu')}")
else:
    print("\n🎉 Toutes les stations sont accessibles depuis ce point.")




def detecter_composantes_connexes(graph):
    composantes = []
    deja_vus = set()

    for station in graph:
        if station not in deja_vus:
            visites, *_ = bfs(graph, station)
            composantes.append(visites)
            deja_vus.update(visites)

    return composantes

composantes = detecter_composantes_connexes(graph)
print(f"\n🧩 Nombre de composantes connexes dans le graphe : {len(composantes)}")
for i, comp in enumerate(composantes):
    print(f"  - Composante {i+1} : {len(comp)} stations")
