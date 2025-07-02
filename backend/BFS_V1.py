from collections import defaultdict, deque
import os

#affichage arbre
from graphviz import Digraph
import os
# Ajout du chemin Graphviz
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"


def charger_graphe(fichier):
    graph = defaultdict(dict)
    noms = {}

    with open(fichier, encoding="utf-8") as f:
        for ligne in f:
            if ligne.startswith("V"):
                parts = ligne.strip().split(";")
                id = int(parts[1])
                nom = " ".join(p for p in parts[2:5] if p)  # Nom1 + Nom2
                noms[id] = nom
                graph[id] = {}  # Initialise la station
            elif ligne.startswith("E"):
                parts = ligne.strip().split(";")
                a, b, poids = int(parts[1]), int(parts[2]), int(parts[3])
                graph[a][b] = poids
                graph[b][a] = poids  # Graphe non orienté

    return graph, noms

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



# Construction du chemin vers output.txt de façon robuste
base_dir = os.path.dirname(os.path.abspath(__file__))
fichier_path = os.path.join(base_dir, "data", "version 1", "output.txt")

# Chargement
graph, noms = charger_graphe(fichier_path)

# Choix interactif du point de départ
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


# Demander si l'utilisateur veut tout le parcours ou un aperçu
print("\nSouhaitez-vous :")
print("1. Explorer tout l'arbre BFS à partir de cette station")
print("2. Afficher uniquement les premières stations visitées")

mode = input("Entrez 1 ou 2 : ").strip()
while mode not in {"1", "2"}:
    mode = input("❌ Entrée invalide. Entrez 1 ou 2 : ").strip()



# Lancement du BFS
visites, parcours, niveaux = bfs(graph, start_id)

# Si on a choisi l'option 1, on génère l'arbre avec Graphviz
if mode == "1":
    dot = Digraph(comment="Arbre BFS", format="png")
    
    # Ajouter tous les nœuds avec nom et niveau
    for vid in parcours:
        nom_station = noms.get(vid, f"ID {vid}")
        label = f"{nom_station}\n(niveau {niveaux[vid]})"
        dot.node(str(vid), label)

    # Ajouter les arêtes BFS (du parent vers enfant niveau +1)
    for vid in parcours:
        for neighbor in graph[vid]:
            if niveaux.get(neighbor, -1) == niveaux[vid] + 1:
                dot.edge(str(vid), str(neighbor))

    output_path = os.path.join(base_dir, "arbre_bfs")
    output_file = dot.render(output_path, cleanup=True)
    if os.path.exists(output_file):
        print(f"\n✅ Fichier Graphviz généré avec succès : {output_file}")
    else:
        print(f"\n❌ Erreur : le fichier {output_file} n'a pas été créé.")

    
# Afficher les premières stations visitées dans l'ordre réel du BFS
if mode == "2":
    print("\n🔍 Exemples de stations visitées (10 premières) :")
    for vid in parcours[:10]:
        print(f" - {vid} : {noms.get(vid, 'Inconnu')} (niveau {niveaux.get(vid, '?')})")
else:
    print(f"\n📁 Arbre BFS généré avec {len(parcours)} stations. Voir le fichier PNG.")




# Nombre total d’arêtes (chaque lien compte pour 2)
total_aretes = sum(len(voisins) for voisins in graph.values()) // 2
print(f"\n🔁 Nombre total d’arêtes (liaisons entre stations) : {total_aretes}")

# Vérification des stations inaccessibles
inaccessibles = set(graph.keys()) - visites
if inaccessibles:
    print("\n🚫 Stations inaccessibles :")
    for i in sorted(inaccessibles):
        print(f" - {i} : {noms.get(i, 'Inconnu')}")
else:
    print("\n🎉 Toutes les stations sont connectées au réseau.")
