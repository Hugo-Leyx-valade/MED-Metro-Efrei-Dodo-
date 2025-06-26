from collections import defaultdict, deque
import os

from graphviz import Digraph
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

def charger_graphe(fichier):
    graph = defaultdict(dict)
    noms = {}

    with open(fichier, encoding="utf-8") as f:
        for ligne in f:
            if ligne.startswith("V"):
                parts = ligne.strip().split(";")
                id = int(parts[1])
                nom = " ".join(p for p in parts[2:5] if p)
                noms[id] = nom
                graph[id] = {}
            elif ligne.startswith("E"):
                parts = ligne.strip().split(";")
                a, b, poids = int(parts[1]), int(parts[2]), int(parts[3])
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
            for neighbor in reversed(sorted(graph[node])):
                if neighbor not in visited:
                    stack.append((neighbor, niveau + 1))

    return visited, parcours, niveaux

base_dir = os.path.dirname(os.path.abspath(__file__))
fichier_path = os.path.join(base_dir, "data", "version 1", "output.txt")

graph, noms = charger_graphe(fichier_path)

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

print("\nSouhaitez-vous :")
print("1. Explorer tout l'arbre en DFS (parcours en profondeur)")
print("2. Afficher uniquement les premières stations visitées")

mode = input("Entrez 1 ou 2 : ").strip()
while mode not in {"1", "2"}:
    mode = input("❌ Entrée invalide. Entrez 1 ou 2 : ").strip()

visites, parcours, niveaux = dfs(graph, start_id)
algo = "DFS"

if mode == "1":
    dot = Digraph(comment="Arbre DFS", format="png")

    for vid in parcours:
        nom_station = noms.get(vid, f"ID {vid}")
        label = f"{nom_station}\n(niveau {niveaux[vid]})"
        dot.node(str(vid), label)

    for vid in parcours:
        for neighbor in graph[vid]:
            if niveaux.get(neighbor, -1) == niveaux[vid] + 1:
                dot.edge(str(vid), str(neighbor))

    output_path = os.path.join(base_dir, f"arbre_{algo.lower()}")
    output_file = dot.render(output_path, cleanup=True)
    if os.path.exists(output_file):
        print(f"\n✅ Fichier Graphviz généré avec succès : {output_file}")
    else:
        print(f"\n❌ Erreur : le fichier {output_file} n'a pas été créé.")

if mode == "2":
    print("\n🔍 Exemples de stations visitées (10 premières) :")
    for vid in parcours[:10]:
        print(f" - {vid} : {noms.get(vid, 'Inconnu')} (niveau {niveaux.get(vid, '?')})")
else:
    print(f"\n📁 Arbre DFS généré avec {len(parcours)} stations. Voir le fichier PNG.")

total_aretes = sum(len(voisins) for voisins in graph.values()) // 2
print(f"\n🔁 Nombre total d’arêtes : {total_aretes}")

inaccessibles = set(graph.keys()) - visites
if inaccessibles:
    print("\n🚫 Stations inaccessibles :")
    for i in sorted(inaccessibles):
        print(f" - {i} : {noms.get(i, 'Inconnu')}")
else:
    print("\n🎉 Toutes les stations sont connectées au réseau.")
